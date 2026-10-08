from app.schemas.chat import ChatResponse, Source
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService

NO_DOCS_ANSWER = "No relevant information was found in the uploaded documents."


def make_snippet(text: str, limit: int = 300) -> str:
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


class RAGService:
    def __init__(self, retrieval: RetrievalService, llm: LLMService):
        self.retrieval = retrieval
        self.llm = llm

    def answer(self, question: str, top_k: int, document_ids: list[str] | None) -> ChatResponse:
        results = self.retrieval.retrieve(question, top_k, document_ids)
        if not results:
            return ChatResponse(answer=NO_DOCS_ANSWER, sources=[])

        answer = self.llm.generate(question, results)
        sources = [
            Source(
                document_id=r.chunk.document_id,
                document=r.chunk.filename,
                page_start=r.chunk.page_start,
                page_end=r.chunk.page_end,
                score=round(r.score, 4),
                snippet=make_snippet(r.chunk.text),
            )
            for r in results
        ]
        return ChatResponse(answer=answer, sources=sources)
