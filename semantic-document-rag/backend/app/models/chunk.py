from dataclasses import asdict, dataclass


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    page_start: int
    page_end: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Chunk":
        return cls(**data)


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float
