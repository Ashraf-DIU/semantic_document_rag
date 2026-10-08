import json
import os
import threading
from pathlib import Path

import faiss
import numpy as np

from app.models.chunk import Chunk
from app.models.document import DocumentRecord


class VectorStore:
    """FAISS (inner product on normalised vectors == cosine) + JSON metadata on disk.

    Vectors are kept in a .npy file so that deleting a document simply rebuilds the index.
    Fine for demo-scale corpora (thousands of chunks).
    """

    def __init__(self, directory: Path):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.vectors = np.zeros((0, 0), dtype="float32")
        self.chunks: list[Chunk] = []
        self.documents: dict[str, DocumentRecord] = {}
        self.index: faiss.Index | None = None
        self.version = 0
        self.cache: dict = {}  # derived data (e.g. BM25) invalidated on every change
        self._load()

    # ---------- persistence ----------
    @property
    def _vec_path(self) -> Path:
        return self.dir / "vectors.npy"

    @property
    def _meta_path(self) -> Path:
        return self.dir / "metadata.json"

    def _load(self) -> None:
        if not (self._vec_path.exists() and self._meta_path.exists()):
            return
        meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
        self.vectors = np.load(self._vec_path)
        self.chunks = [Chunk.from_dict(c) for c in meta["chunks"]]
        self.documents = {d["document_id"]: DocumentRecord.from_dict(d) for d in meta["documents"]}
        self._rebuild_index()

    def _save(self) -> None:
        meta = {
            "documents": [d.to_dict() for d in self.documents.values()],
            "chunks": [c.to_dict() for c in self.chunks],
        }
        tmp_meta = self._meta_path.with_suffix(".json.tmp")
        tmp_meta.write_text(json.dumps(meta), encoding="utf-8")
        os.replace(tmp_meta, self._meta_path)

        tmp_vec = self.dir / "vectors.tmp.npy"
        np.save(tmp_vec, self.vectors)
        os.replace(tmp_vec, self._vec_path)

    def _rebuild_index(self) -> None:
        if len(self.chunks) == 0:
            self.index = None
        else:
            self.index = faiss.IndexFlatIP(self.vectors.shape[1])
            self.index.add(self.vectors)
        self.version += 1
        self.cache.clear()

    # ---------- documents ----------
    def has_document(self, document_id: str) -> bool:
        return document_id in self.documents

    def list_documents(self) -> list[DocumentRecord]:
        with self.lock:
            return sorted(self.documents.values(), key=lambda d: d.uploaded_at)

    def add_document(self, record: DocumentRecord, chunks: list[Chunk], vectors: np.ndarray) -> None:
        with self.lock:
            if self.vectors.shape[0] == 0:
                self.vectors = vectors.astype("float32")
            else:
                self.vectors = np.vstack([self.vectors, vectors.astype("float32")])
            self.chunks.extend(chunks)
            self.documents[record.document_id] = record
            self._rebuild_index()
            self._save()

    def delete_document(self, document_id: str) -> bool:
        with self.lock:
            if document_id not in self.documents:
                return False
            keep = [i for i, c in enumerate(self.chunks) if c.document_id != document_id]
            self.chunks = [self.chunks[i] for i in keep]
            self.vectors = self.vectors[keep] if keep else np.zeros((0, 0), dtype="float32")
            del self.documents[document_id]
            self._rebuild_index()
            self._save()
            return True

    # ---------- search ----------
    def allowed_mask(self, document_ids: list[str] | None) -> np.ndarray | None:
        if not document_ids:
            return None
        wanted = set(document_ids)
        return np.array([c.document_id in wanted for c in self.chunks], dtype=bool)

    def search(
        self, query_vec: np.ndarray, n: int, document_ids: list[str] | None = None
    ) -> list[tuple[int, float]]:
        """Return [(row_index, cosine_score)] best-first."""
        with self.lock:
            if self.index is None:
                return []
            mask = self.allowed_mask(document_ids)
            # When filtering we search everything and filter afterwards (simple + exact).
            k = len(self.chunks) if mask is not None else min(n, len(self.chunks))
            scores, ids = self.index.search(query_vec.reshape(1, -1).astype("float32"), k)
            out: list[tuple[int, float]] = []
            for score, idx in zip(scores[0], ids[0]):
                if idx < 0 or (mask is not None and not mask[idx]):
                    continue
                out.append((int(idx), float(score)))
                if len(out) >= n:
                    break
            return out

    def cosine(self, rows: list[int], query_vec: np.ndarray) -> list[float]:
        with self.lock:
            return [float(self.vectors[r] @ query_vec) for r in rows]
