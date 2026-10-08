from app.models.chunk import RetrievedChunk

SYSTEM_PROMPT = """You are a document question-answering assistant.

Answer the user's question using ONLY the provided context excerpts.
If the answer is not contained in the context, say that the information was not found in the uploaded documents. Do not guess.
Cite every claim with the source in square brackets using the exact label given, for example [paper.pdf, p. 7].
Be concise and precise."""


class LLMNotConfigured(RuntimeError):
    pass


def source_label(item: RetrievedChunk) -> str:
    c = item.chunk
    pages = f"p. {c.page_start}" if c.page_start == c.page_end else f"pp. {c.page_start}-{c.page_end}"
    return f"{c.filename}, {pages}"


def build_context(contexts: list[RetrievedChunk]) -> str:
    return "\n\n".join(f"[{source_label(item)}]\n{item.chunk.text}" for item in contexts)


class LLMService:
    """Provider-agnostic wrapper: works with any OpenAI-compatible chat completions API."""

    def __init__(self, api_key: str, model: str, base_url: str = ""):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or None
        self._client = None

    def _get_client(self):
        if not self.api_key:
            raise LLMNotConfigured("LLM_API_KEY is not set on the server")
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def generate(self, question: str, contexts: list[RetrievedChunk]) -> str:
        client = self._get_client()
        user_prompt = f"CONTEXT:\n\n{build_context(contexts)}\n\nQUESTION:\n{question}"
        response = client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            max_tokens=2000,  # reasoning models (e.g. gpt-oss) also spend tokens on thinking
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = (response.choices[0].message.content or "").strip()
        return text or "The model returned an empty answer. Please try again."
