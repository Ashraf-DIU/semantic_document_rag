import threading
from pathlib import Path

import numpy as np

from app.utils.logger import get_logger

log = get_logger(__name__)


def _normalize(vectors: np.ndarray) -> np.ndarray:
    vectors = vectors.astype("float32")
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


class EmbeddingService:
    """Local ONNX embeddings through fastembed (no PyTorch -> small enough for free hosting)."""

    def __init__(self, model_name: str, cache_dir: Path | None = None):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self._model = None
        self._lock = threading.Lock()

    def load(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    from fastembed import TextEmbedding

                    log.info("Loading embedding model %s", self.model_name)
                    kwargs = {"cache_dir": str(self.cache_dir)} if self.cache_dir else {}
                    self._model = TextEmbedding(model_name=self.model_name, **kwargs)
                    log.info("Embedding model ready")
        return self._model

    def embed_passages(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        model = self.load()
        vectors = list(model.passage_embed(texts, batch_size=batch_size))
        return _normalize(np.array(vectors))

    def embed_query(self, query: str) -> np.ndarray:
        model = self.load()
        vector = next(iter(model.query_embed([query])))
        return _normalize(np.array([vector]))[0]
