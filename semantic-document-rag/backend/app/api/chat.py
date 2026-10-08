from fastapi import APIRouter, Depends, HTTPException
from openai import APIConnectionError, APIStatusError

from app.dependencies import get_rag_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMNotConfigured
from app.services.rag_service import RAGService
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


def _short(exc: Exception) -> str:
    return str(getattr(exc, "message", None) or exc)[:300]


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, rag: RAGService = Depends(get_rag_service)):
    try:
        return rag.answer(req.question, req.top_k, req.document_ids)
    except LLMNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except APIStatusError as exc:
        log.exception("LLM provider returned an error")
        raise HTTPException(status_code=502, detail=f"LLM provider error {exc.status_code}: {_short(exc)}")
    except APIConnectionError as exc:
        log.exception("Could not reach LLM provider")
        raise HTTPException(status_code=502, detail="Could not connect to the LLM provider. Check LLM_BASE_URL.")
    except Exception as exc:
        log.exception("LLM request failed")
        raise HTTPException(status_code=502, detail=f"LLM request failed ({type(exc).__name__}): {_short(exc)}")
