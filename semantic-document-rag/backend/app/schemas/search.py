from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[str] | None = None


class SearchResult(BaseModel):
    document_id: str
    document: str
    page_start: int
    page_end: int
    score: float
    text: str


class SearchResponse(BaseModel):
    results: list[SearchResult]
