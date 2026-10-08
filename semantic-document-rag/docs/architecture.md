# Architecture

| Layer | Files | Responsibility |
|---|---|---|
| API | `app/api/*` | HTTP routes, validation, error mapping |
| Services | `app/services/*` | PDF parsing, cleaning, chunking, embeddings, vector store, retrieval, LLM, RAG orchestration |
| Models | `app/models/*` | Plain dataclasses (Chunk, DocumentRecord) |
| Schemas | `app/schemas/*` | Pydantic request/response models |
| Storage | `data/vector_store/` | `vectors.npy` + `metadata.json`; FAISS index rebuilt in memory on load |

Design choices
- **fastembed (ONNX)** instead of sentence-transformers: avoids PyTorch, fits small free instances.
- **FAISS IndexFlatIP** on L2-normalised vectors = exact cosine similarity.
- **LLM provider is replaceable**: `LLMService` talks to any OpenAI-compatible endpoint (`LLM_BASE_URL`).
- Dependency injection (`app/dependencies.py`) makes every service swappable in tests.
