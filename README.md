# DocuMind — Semantic Document Search & RAG Assistant

AI-powered document search and question answering using Retrieval-Augmented Generation.
Upload PDFs, ask questions, get answers with **document + page citations**.

## Features

- Multi-PDF upload (duplicate files detected by hash)
- PDF text extraction (PyMuPDF) with light cleaning (headers/footers, hyphenation)
- Overlapping chunking that remembers page numbers
- Local ONNX embeddings (`BAAI/bge-small-en-v1.5` via fastembed — no PyTorch, no API key)
- FAISS vector search + BM25 keyword search fused with Reciprocal Rank Fusion (hybrid retrieval)
- Per-document filtering
- LLM answers with page-level citations (any OpenAI-compatible provider)
- FastAPI REST API, Next.js + Tailwind frontend

## Architecture

```text
Next.js (Vercel)  ──HTTPS──▶  FastAPI (Render)  ──▶  FAISS + metadata (disk)
                                    └────────────▶  LLM API
```

Upload: PDF → extract → clean → chunk → embed → FAISS
Question: embed → FAISS top-N + BM25 top-N → RRF fusion → top-K → LLM → answer + sources

## Repository layout

```text
backend/    FastAPI app (app/api, app/services, app/models, app/schemas), tests/
frontend/   Next.js app (app/, components/, lib/)
docs/       architecture, API, pipeline, evaluation notes
render.yaml Optional Render blueprint
```

## Run locally

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then set LLM_API_KEY
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000/docs. The embedding model (~130 MB) downloads on first start.

Run tests: `cd backend && pip install -r requirements-dev.txt && python -m pytest`

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local        # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```
Open http://localhost:3000.

### Docker (backend only)
```bash
cp backend/.env.example backend/.env
docker compose up --build
```

## Deployment (GitHub → Render + Vercel)

The frontend goes on **Vercel**. The backend (FAISS, embeddings, PDF parsing) does **not** fit
Vercel's serverless limits, so it goes on **Render** (free tier works for a demo).

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: DocuMind"
git branch -M main
git remote add origin https://github.com/<you>/semantic-document-rag.git
git push -u origin main
```
Check that `.env` is NOT in the repo (only `.env.example`).

### 2. Deploy the backend on Render
1. render.com → **New → Web Service** → connect the GitHub repo.
2. Settings:
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/api/health`
3. Environment variables:
   | Key | Value |
   |---|---|
   | `PYTHON_VERSION` | `3.11.9` |
   | `LLM_API_KEY` | your provider key |
   | `LLM_MODEL` | e.g. `gpt-4o-mini` |
   | `LLM_BASE_URL` | empty for OpenAI, or your provider's OpenAI-compatible URL |
   | `FRONTEND_URL` | (set after step 3) your Vercel URL |
   | `CORS_ORIGIN_REGEX` | `https://.*\.vercel\.app` |
4. Deploy. Copy the URL, e.g. `https://documind-backend.onrender.com`. Check `/api/health`.

(Alternative: **New → Blueprint** uses `render.yaml` from the repo root.)

### 3. Deploy the frontend on Vercel
1. vercel.com → **Add New → Project** → import the same repo.
2. **Root Directory: `frontend`** (Framework preset auto-detects Next.js).
3. Environment variable: `NEXT_PUBLIC_API_URL` = your Render URL (no trailing slash).
4. Deploy. Copy the production URL.

### 4. Connect them
In Render, set `FRONTEND_URL` to the Vercel URL (e.g. `https://documind.vercel.app`) and redeploy.
If you change `NEXT_PUBLIC_API_URL` later, redeploy the frontend (it is baked in at build time).

### Free-tier caveats
- Render free services sleep after ~15 min idle; the first request takes ~30–60 s.
- The free disk is ephemeral: uploaded documents are lost on restart/redeploy. For persistence use a
  Render persistent disk (paid) mounted at `DATA_DIR`, or move to pgvector / Qdrant.
- The index is shared by all visitors. Put a spending limit on your LLM key before sharing the link publicly.

## Alternative: one Vercel project with two services

`vercel.json` (repo root) deploys `backend` (FastAPI) and `frontend` (Next.js) as services of a single
Vercel project on one domain. `/api/*` is routed to the backend, everything else to the frontend, so the
browser calls the API on the same origin (no `NEXT_PUBLIC_API_URL`, no CORS). No bindings are needed because
the services never call each other server-side. Test locally with `vercel dev`.

**Serverless limits that affect this app** (the Render setup above does not have them):
- Function request bodies are limited to ~4.5 MB, so larger PDFs are rejected by the platform.
- Only `/tmp` is writable and it is per-instance and ephemeral: the FAISS index and uploaded documents are not
  shared between invocations, so an upload can be invisible to the next request.
- The embedding model is downloaded again on cold starts; the Python bundle must fit Vercel's size limit.
Use this layout for a demo only if you move storage to an external service (Postgres + pgvector, Qdrant, ...).
