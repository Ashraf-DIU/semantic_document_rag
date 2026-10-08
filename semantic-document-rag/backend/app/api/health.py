from fastapi import APIRouter, Depends

from app.dependencies import get_vector_store
from app.services.vector_store import VectorStore

router = APIRouter()


@router.get("/health")
def health(store: VectorStore = Depends(get_vector_store)):
    return {"status": "ok", "documents": len(store.documents), "chunks": len(store.chunks)}
