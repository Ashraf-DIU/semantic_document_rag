from app.services.ingestion_service import IngestionService
from app.services.retrieval_service import RetrievalService
from app.services.vector_store import VectorStore
from tests.conftest import FakeEmbedder, make_pdf


def _setup(tmp_path):
    embedder, store = FakeEmbedder(), VectorStore(tmp_path / "vs")
    ing = IngestionService(embedder, store, chunk_size=40, chunk_overlap=5)
    ing.ingest("vision.pdf", make_pdf(["Convolutional neural networks segment medical images with U-Net."]))
    ing.ingest("cooking.pdf", make_pdf(["Sourdough bread needs flour water salt and a long fermentation."]))
    return embedder, store


def test_semantic_and_hybrid_find_right_document(tmp_path):
    embedder, store = _setup(tmp_path)
    for hybrid in (False, True):
        r = RetrievalService(embedder, store, use_hybrid=hybrid).retrieve("segmenting medical images", top_k=1)
        assert r[0].chunk.filename == "vision.pdf"


def test_document_filter(tmp_path):
    embedder, store = _setup(tmp_path)
    cooking_id = next(d.document_id for d in store.documents.values() if d.filename == "cooking.pdf")
    r = RetrievalService(embedder, store).retrieve("medical images", top_k=5, document_ids=[cooking_id])
    assert r and all(x.chunk.filename == "cooking.pdf" for x in r)


def test_store_persists_and_deletes(tmp_path):
    embedder, store = _setup(tmp_path)
    reloaded = VectorStore(tmp_path / "vs")
    assert len(reloaded.documents) == 2
    doc_id = next(iter(reloaded.documents))
    assert reloaded.delete_document(doc_id)
    assert len(reloaded.documents) == 1
    assert all(c.document_id != doc_id for c in reloaded.chunks)
