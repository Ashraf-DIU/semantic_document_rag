from app.models.chunk import Chunk


def chunk_pages(
    pages: list[tuple[int, str]],
    document_id: str,
    filename: str,
    size: int = 350,
    overlap: int = 60,
) -> list[Chunk]:
    """Sliding-window chunking by words that remembers which pages each chunk spans."""
    if overlap >= size:
        raise ValueError("overlap must be smaller than chunk size")

    words: list[tuple[str, int]] = [(w, page) for page, text in pages for w in text.split()]
    chunks: list[Chunk] = []
    step = size - overlap
    start = 0
    index = 0
    while start < len(words):
        window = words[start:start + size]
        chunks.append(
            Chunk(
                chunk_id=f"{document_id}_c{index:04d}",
                document_id=document_id,
                filename=filename,
                chunk_index=index,
                page_start=window[0][1],
                page_end=window[-1][1],
                text=" ".join(w for w, _ in window),
            )
        )
        if start + size >= len(words):
            break
        start += step
        index += 1
    return chunks
