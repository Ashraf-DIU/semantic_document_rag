import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM (any OpenAI-compatible API)
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = ""

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Storage
    # On Vercel only /tmp is writable (and it is ephemeral, per instance).
    data_dir: Path = Path("/tmp/documind") if os.getenv("VERCEL") else Path("./data")

    # Retrieval / chunking (sizes are in words; ~1 word = 1.3 tokens)
    top_k: int = 5
    chunk_size_words: int = 350
    chunk_overlap_words: int = 60
    use_hybrid: bool = True

    # Uploads
    max_upload_mb: int = 20

    # CORS
    frontend_url: str = "http://localhost:3000"
    cors_origin_regex: str = ""

    @property
    def vector_dir(self) -> Path:
        return self.data_dir / "vector_store"

    @property
    def model_cache_dir(self) -> Path:
        return self.data_dir / "models"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.frontend_url.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
