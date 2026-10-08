# RAG pipeline

1. **Extract** – PyMuPDF, page by page (page numbers are kept).
2. **Clean** – drop repeated headers/footers and bare page numbers, re-join hyphenated words, collapse whitespace.
3. **Chunk** – sliding window of 350 words (~450 tokens), 60-word overlap; each chunk stores `page_start`/`page_end`.
4. **Embed** – `BAAI/bge-small-en-v1.5` (384-d). Passages and queries use their respective embedding modes.
5. **Index** – FAISS inner-product index over normalised vectors.
6. **Retrieve** – semantic top-N and BM25 top-N (N = max(4·K, 20)), fused with Reciprocal Rank Fusion (k=60), top-K returned. Set `USE_HYBRID=false` for pure semantic search.
7. **Generate** – context labelled `[file.pdf, p. 7]`; the prompt tells the model to answer only from context, admit when the answer is missing, and cite labels.

Tunables (env): `CHUNK_SIZE_WORDS`, `CHUNK_OVERLAP_WORDS`, `TOP_K`, `USE_HYBRID`, `EMBEDDING_MODEL`.
Changing the embedding model or chunk settings requires re-uploading documents.
