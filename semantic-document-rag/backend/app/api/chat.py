from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_rag_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMNotConfigured
from app.services.rag_service import RAGService
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, rag: RAGService = Depends(get_rag_service)):
    try:
        return rag.answer(req.question, req.top_k, req.document_ids)
    except LLMNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception:
        log.exception("LLM request failed")
        raise HTTPException(status_code=502, detail="The language model request failed. Please try again.")
