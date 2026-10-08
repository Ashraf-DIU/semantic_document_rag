import numpy as np

from tests.conftest import FakeEmbedder


def test_embeddings_are_unit_length_and_similar_texts_score_higher():
    e = FakeEmbedder()
    docs = e.embed_passages(["transformer self attention model", "banana bread recipe"])
    q = e.embed_query("self attention transformer")
    assert np.allclose(np.linalg.norm(docs, axis=1), 1.0, atol=1e-5)
    assert docs[0] @ q > docs[1] @ q
