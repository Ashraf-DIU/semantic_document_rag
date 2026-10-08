import hashlib
from datetime import datetime, timezone

from app.models.document import DocumentRecord
from app.services.chunker import chunk_pages
from app.services.embedding_service import EmbeddingService
from app.services.pdf_service import PDFError, extract_pages
from app.services.text_cleaner import clean_pages
from app.services.vector_store import VectorStore


class IngestionService:
    def __init__(
        self,
        embedder: EmbeddingService,
        store: VectorStore,
        chunk_size: int,
        chunk_overlap: int,
    ):
        self.embedder = embedder
        self.store = store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def ingest(self, filename: str, data: bytes) -> DocumentRecord:
        """Parse -> clean -> chunk -> embed -> store. Re-uploading identical bytes is a no-op."""
        sha = hashlib.sha256(data).hexdigest()
        document_id = f"doc_{sha[:10]}"
        if self.store.has_document(document_id):
            return self.store.documents[document_id]

        raw_pages = extract_pages(data)
        pages = clean_pages(raw_pages)
        if not pages:
            raise PDFError("no extractable text (scanned PDFs need OCR, which is not supported)")

        chunks = chunk_pages(pages, document_id, filename, self.chunk_size, self.chunk_overlap)
        vectors = self.embedder.embed_passages([c.text for c in chunks])

        record = DocumentRecord(
            document_id=document_id,
            filename=filename,
            sha256=sha,
            pages=len(raw_pages),
            chunks=len(chunks),
            uploaded_at=datetime.now(timezone.utc).isoformat(),
        )
        self.store.add_document(record, chunks, vectors)
        return record
