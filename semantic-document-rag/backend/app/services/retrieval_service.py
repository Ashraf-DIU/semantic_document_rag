import numpy as np
from rank_bm25 import BM25Okapi

from app.models.chunk import RetrievedChunk
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.utils.helpers import tokenize

RRF_K = 60  # standard constant for Reciprocal Rank Fusion


class RetrievalService:
    """Semantic (FAISS) search, optionally fused with keyword (BM25) search via RRF."""

    def __init__(self, embedder: EmbeddingService, store: VectorStore, use_hybrid: bool = True):
        self.embedder = embedder
        self.store = store
        self.use_hybrid = use_hybrid

    def _bm25(self) -> BM25Okapi | None:
        cached = self.store.cache.get("bm25")
        if cached is None and self.store.chunks:
            cached = BM25Okapi([tokenize(c.text) or ["_"] for c in self.store.chunks])
            self.store.cache["bm25"] = cached
        return cached

    def _keyword_rank(self, query: str, n: int, document_ids: list[str] | None) -> list[int]:
        bm25 = self._bm25()
        tokens = tokenize(query)
        if bm25 is None or not tokens:
            return []
        scores = np.array(bm25.get_scores(tokens))
        mask = self.store.allowed_mask(document_ids)
        if mask is not None:
            scores = np.where(mask, scores, -np.inf)
        order = np.argsort(-scores)[:n]
        return [int(i) for i in order if np.isfinite(scores[i]) and scores[i] > 0]

    def retrieve(
        self, query: str, top_k: int = 5, document_ids: list[str] | None = None
    ) -> list[RetrievedChunk]:
        with self.store.lock:
            if not self.store.chunks:
                return []
            q_vec = self.embedder.embed_query(query)
            pool = max(top_k * 4, 20)
            semantic = [row for row, _ in self.store.search(q_vec, pool, document_ids)]

            if self.use_hybrid:
                keyword = self._keyword_rank(query, pool, document_ids)
                fused: dict[int, float] = {}
                for ranking in (semantic, keyword):
                    for rank, row in enumerate(ranking):
                        fused[row] = fused.get(row, 0.0) + 1.0 / (RRF_K + rank + 1)
                rows = sorted(fused, key=fused.get, reverse=True)[:top_k]
            else:
                rows = semantic[:top_k]

            scores = self.store.cosine(rows, q_vec)
            return [RetrievedChunk(self.store.chunks[r], s) for r, s in zip(rows, scores)]
