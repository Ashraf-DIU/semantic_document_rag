import fitz  # PyMuPDF


class PDFError(ValueError):
    """Raised for unreadable / unsupported PDFs."""


def extract_pages(data: bytes) -> list[tuple[int, str]]:
    """Return [(page_number starting at 1, raw_text)] for a PDF given as bytes."""
    if not data.startswith(b"%PDF"):
        raise PDFError("not a valid PDF file")
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:  # corrupt file
        raise PDFError(f"could not open PDF ({exc})") from exc

    try:
        if doc.needs_pass:
            raise PDFError("PDF is password protected")
        return [(i + 1, page.get_text("text")) for i, page in enumerate(doc)]
    finally:
        doc.close()
