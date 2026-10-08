from dataclasses import asdict, dataclass


@dataclass
class DocumentRecord:
    document_id: str
    filename: str
    sha256: str
    pages: int
    chunks: int
    uploaded_at: str  # ISO 8601, UTC

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentRecord":
        return cls(**data)
