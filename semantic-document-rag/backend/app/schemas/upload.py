from pydantic import BaseModel


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    pages: int
    chunks: int
    uploaded_at: str


class UploadResponse(BaseModel):
    documents: list[DocumentInfo]
    skipped: list[str] = []  # human-readable reasons, e.g. "a.pdf: no extractable text"
