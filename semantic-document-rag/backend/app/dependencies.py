from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService
from app.services.vector_store import VectorStore


@lru_cache
def get_embedding_service() -> EmbeddingService:
    s = get_settings()
    return EmbeddingService(s.embedding_model, s.model_cache_dir)


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore(get_settings().vector_dir)


@lru_cache
def get_llm_service() -> LLMService:
    s = get_settings()
    return LLMService(s.llm_api_key, s.llm_model, s.llm_base_url)


def get_retrieval_service(
    embedder: EmbeddingService = Depends(get_embedding_service),
    store: VectorStore = Depends(get_vector_store),
    settings: Settings = Depends(get_settings),
) -> RetrievalService:
    return RetrievalService(embedder, store, settings.use_hybrid)


def get_ingestion_service(
    embedder: EmbeddingService = Depends(get_embedding_service),
    store: VectorStore = Depends(get_vector_store),
    settings: Settings = Depends(get_settings),
) -> IngestionService:
    return IngestionService(embedder, store, settings.chunk_size_words, settings.chunk_overlap_words)


def get_rag_service(
    retrieval: RetrievalService = Depends(get_retrieval_service),
    llm: LLMService = Depends(get_llm_service),
) -> RAGService:
    return RAGService(retrieval, llm)
