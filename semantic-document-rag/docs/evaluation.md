# Evaluation ideas

Build a small test set (20–50 questions) over a few PDFs, each with the expected document + page.

- **Retrieval hit@K** – is the expected page among the top-K chunks? Compare `USE_HYBRID` on/off and different chunk sizes.
- **MRR** – reciprocal rank of the first correct chunk.
- **Faithfulness** – manually check that answers are supported by cited sources.
- **Abstention** – ask questions that are NOT in the documents; the assistant should say it was not found.
- **Latency** – measure upload time per page and answer time.

Record the results in a table in the README; it is a strong portfolio addition.
