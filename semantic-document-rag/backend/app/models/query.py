from dataclasses import dataclass, field


@dataclass
class Query:
    text: str
    top_k: int = 5
    document_ids: list[str] = field(default_factory=list)
