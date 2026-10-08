import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, documents, health, search, upload
from app.config import get_settings
from app.dependencies import get_embedding_service, get_vector_store
from app.utils.logger import get_logger

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    get_vector_store()
    # Load the embedding model in the background so the server starts accepting requests immediately.
    threading.Thread(target=get_embedding_service().load, daemon=True).start()
    yield


settings = get_settings()
app = FastAPI(title="DocuMind API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (health, upload, documents, search, chat):
    app.include_router(module.router, prefix="/api")


@app.get("/")
def root():
    return {"name": "DocuMind API", "docs": "/docs", "health": "/api/health"}
