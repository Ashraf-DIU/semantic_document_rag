"""Light-touch cleaning. We deliberately avoid aggressive rewriting so that
scientific content (numbers, symbols, formulas) is not lost."""
import re
from collections import Counter

PAGE_NUMBER_RE = re.compile(r"^\s*(page\s+)?\d{1,4}(\s*(/|of)\s*\d{1,4})?\s*$", re.IGNORECASE)


def normalize(text: str) -> str:
    text = text.replace("\u00ad", "")                 # soft hyphens
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)      # re-join words split across lines
    text = re.sub(r"[ \t\u00a0]+", " ", text)         # collapse spaces
    text = re.sub(r"\n{3,}", "\n\n", text)            # collapse blank lines
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)      # single newline -> space
    return text.strip()


def clean_pages(pages: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """pages: [(page_number, raw_text)] -> cleaned pages, empty pages dropped.

    Removes short lines that repeat on more than half of the pages
    (running headers / footers) and bare page numbers.
    """
    repeated: set[str] = set()
    if len(pages) >= 4:
        counter: Counter[str] = Counter()
        for _, text in pages:
            counter.update({ln.strip() for ln in text.splitlines() if 0 < len(ln.strip()) <= 80})
        repeated = {ln for ln, c in counter.items() if c > len(pages) * 0.5}

    cleaned: list[tuple[int, str]] = []
    for number, text in pages:
        lines = [
            ln for ln in text.splitlines()
            if ln.strip() not in repeated and not PAGE_NUMBER_RE.match(ln)
        ]
        result = normalize("\n".join(lines))
        if result:
            cleaned.append((number, result))
    return cleaned
