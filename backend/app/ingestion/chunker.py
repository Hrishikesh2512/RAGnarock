"""Split plain text into overlapping chunks."""

import re

DEFAULT_MAX_CHARS = 1200
DEFAULT_OVERLAP = 200


def chunk_text(
    text: str, max_chars: int = DEFAULT_MAX_CHARS, overlap: int = DEFAULT_OVERLAP
) -> list[str]:
    """Split text on paragraphs, then hard-split paragraphs that are too long."""
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        start = 0
        step = max(1, max_chars - overlap)
        while start < len(paragraph):
            chunks.append(paragraph[start : start + max_chars].strip())
            start += step

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk]
