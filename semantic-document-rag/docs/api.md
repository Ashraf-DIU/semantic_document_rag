# API

Base path: `/api`. Interactive docs at `/docs`.

| Method | Path | Body | Notes |
|---|---|---|---|
| GET | `/health` | – | `{status, documents, chunks}` |
| POST | `/upload` | multipart `files` (PDF, repeated) | `{documents[], skipped[]}`; 400 if nothing usable |
| GET | `/documents` | – | list indexed documents |
| DELETE | `/documents/{document_id}` | – | 404 if unknown |
| POST | `/search` | `{query, top_k=5, document_ids?}` | retrieved chunks with similarity |
| POST | `/chat` | `{question, top_k=5, document_ids?}` | `{answer, sources[]}`; 503 if `LLM_API_KEY` missing, 502 if the LLM call fails |
