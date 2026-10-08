from fastapi import APIRouter, Depends

from app.dependencies import get_retrieval_service
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(req: SearchRequest, retrieval: RetrievalService = Depends(get_retrieval_service)):
    items = retrieval.retrieve(req.query, req.top_k, req.document_ids)
    return SearchResponse(
        results=[
            SearchResult(
                document_id=i.chunk.document_id,
                document=i.chunk.filename,
                page_start=i.chunk.page_start,
                page_end=i.chunk.page_end,
                score=round(i.score, 4),
                text=i.chunk.text,
            )
            for i in items
        ]
    )
