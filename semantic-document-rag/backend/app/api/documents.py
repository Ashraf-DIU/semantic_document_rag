from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_vector_store
from app.schemas.upload import DocumentInfo
from app.services.vector_store import VectorStore

router = APIRouter()


@router.get("/documents", response_model=list[DocumentInfo])
def list_documents(store: VectorStore = Depends(get_vector_store)):
    return [DocumentInfo(**{k: getattr(d, k) for k in DocumentInfo.model_fields}) for d in store.list_documents()]


@router.delete("/documents/{document_id}")
def delete_document(document_id: str, store: VectorStore = Depends(get_vector_store)):
    if not store.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": document_id}
