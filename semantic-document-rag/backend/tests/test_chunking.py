import pytest

from app.services.chunker import chunk_pages


def test_chunks_overlap_and_track_pages():
    pages = [(1, " ".join(f"a{i}" for i in range(100))), (2, " ".join(f"b{i}" for i in range(100)))]
    chunks = chunk_pages(pages, "doc_x", "x.pdf", size=60, overlap=10)
    assert chunks[0].page_start == 1
    assert chunks[-1].page_end == 2
    assert chunks[0].text.split()[-10:] == chunks[1].text.split()[:10]
    assert len(chunks) == 4  # 200 words, step 50
    assert all(len(c.text.split()) <= 60 for c in chunks)


def test_short_document_gives_one_chunk():
    chunks = chunk_pages([(1, "just a few words")], "d", "f.pdf", size=50, overlap=5)
    assert len(chunks) == 1


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_pages([(1, "x y z")], "d", "f.pdf", size=10, overlap=10)
