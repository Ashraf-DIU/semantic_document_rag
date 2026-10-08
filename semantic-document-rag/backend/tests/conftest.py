import hashlib
import re

import fitz
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_embedding_service, get_llm_service, get_vector_store
from app.main import app
from app.services.vector_store import VectorStore

DIM = 256


class FakeEmbedder:
    """Deterministic bag-of-words hashing embedder so tests need no model download."""

    def _vec(self, text: str) -> np.ndarray:
        v = np.zeros(DIM, dtype="float32")
        for tok in re.findall(r"\w+", text.lower()):
            v[int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM] += 1.0
        n = np.linalg.norm(v)
        return v / n if n else v

    def load(self):
        return None

    def embed_passages(self, texts, batch_size=32):
        return np.array([self._vec(t) for t in texts], dtype="float32")

    def embed_query(self, query):
        return self._vec(query)


class FakeLLM:
    def generate(self, question, contexts):
        return f"Answer based on {len(contexts)} chunks. [{contexts[0].chunk.filename}]"


def make_pdf(pages: list[str]) -> bytes:
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_textbox(fitz.Rect(50, 50, 550, 780), text, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture
def client(tmp_path):
    store = VectorStore(tmp_path / "vs")
    app.dependency_overrides[get_embedding_service] = lambda: FakeEmbedder()
    app.dependency_overrides[get_vector_store] = lambda: store
    app.dependency_overrides[get_llm_service] = lambda: FakeLLM()
    yield TestClient(app)
    app.dependency_overrides.clear()
