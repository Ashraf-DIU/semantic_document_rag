import pytest

from app.services.pdf_service import PDFError, extract_pages
from app.services.text_cleaner import clean_pages, normalize
from tests.conftest import make_pdf


def test_extract_pages_returns_page_numbers():
    pages = extract_pages(make_pdf(["First page about transformers.", "Second page about CNNs."]))
    assert [p for p, _ in pages] == [1, 2]
    assert "transformers" in pages[0][1]


def test_rejects_non_pdf():
    with pytest.raises(PDFError):
        extract_pages(b"hello world")


def test_normalize_joins_hyphenated_and_wrapped_lines():
    assert normalize("segmen-\ntation of   images\nand more") == "segmentation of images and more"


def test_clean_pages_removes_repeated_headers_and_page_numbers():
    pages = [(i, f"My Journal Header\nreal content {i}\n{i}") for i in range(1, 6)]
    cleaned = clean_pages(pages)
    assert len(cleaned) == 5
    assert all("Journal" not in text for _, text in cleaned)
    assert cleaned[0][1] == "real content 1"
