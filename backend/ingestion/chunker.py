from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from backend.ingestion.pdf_extractor import PageResult

SENTENCE_SPLIT = re.compile(r"(?<=[.!?।])\s+")


@dataclass
class ChunkResult:
    text: str
    page_start: int
    page_end: int
    paragraph_start: int | None
    paragraph_end: int | None
    chunk_index: int
    content_hash: str


def _split_sentences(text: str) -> list[str]:
    parts = SENTENCE_SPLIT.split(text)
    return [p for p in parts if p.strip()]


def chunk_pages(
    pages: list[PageResult],
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[ChunkResult]:
    """Split page texts into overlapping chunks, respecting sentence boundaries."""
    if not pages:
        return []

    # Build a list of (sentence, page_number) pairs
    sentence_page: list[tuple[str, int]] = []
    for page in pages:
        if not page.text.strip():
            continue
        for sent in _split_sentences(page.text):
            sentence_page.append((sent, page.page_number))

    if not sentence_page:
        return []

    chunks: list[ChunkResult] = []
    idx = 0
    chunk_index = 0

    while idx < len(sentence_page):
        current_chars = 0
        current_sentences: list[str] = []
        page_start = sentence_page[idx][1]
        page_end = page_start
        start_idx = idx

        while idx < len(sentence_page):
            sent, pg = sentence_page[idx]
            added_len = len(sent) + (1 if current_sentences else 0)
            if current_chars + added_len > chunk_size and current_sentences:
                break
            current_sentences.append(sent)
            current_chars += added_len
            page_end = pg
            idx += 1

        text = " ".join(current_sentences)
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        chunks.append(ChunkResult(
            text=text,
            page_start=page_start,
            page_end=page_end,
            paragraph_start=None,
            paragraph_end=None,
            chunk_index=chunk_index,
            content_hash=content_hash,
        ))
        chunk_index += 1

        # Move back for overlap
        if idx < len(sentence_page):
            overlap_chars = 0
            back = idx - 1
            while back > start_idx and overlap_chars < chunk_overlap:
                overlap_chars += len(sentence_page[back][0]) + 1
                back -= 1
            idx = back + 1

    return chunks
