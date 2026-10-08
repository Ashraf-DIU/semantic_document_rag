import os
import re


def safe_filename(name: str) -> str:
    """Strip any directory part and unusual characters from an uploaded filename."""
    base = os.path.basename(name or "document.pdf")
    base = re.sub(r"[^\w.\- ()]", "_", base).strip()
    return base or "document.pdf"


def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())
