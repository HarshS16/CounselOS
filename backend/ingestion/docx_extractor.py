from __future__ import annotations

import logging
from pathlib import Path

from docx import Document as DocxDocument

from backend.ingestion.pdf_extractor import PageResult

logger = logging.getLogger(__name__)

CHARS_PER_PAGE = 3000


def extract_docx(file_path: Path, document_id: str) -> list[PageResult]:
    """Extract text from a DOCX file, grouping paragraphs into logical pages."""
    try:
        doc = DocxDocument(str(file_path))
    except Exception:
        logger.exception("Failed to open DOCX: %s", file_path)
        return [PageResult(page_number=1, text="", extraction_method="failed", quality_indicator=0)]

    paragraphs = [p.text for p in doc.paragraphs]

    if not paragraphs or all(not p.strip() for p in paragraphs):
        return [PageResult(
            page_number=1,
            text="",
            extraction_method="failed",
            quality_indicator=0.0,
        )]

    pages: list[PageResult] = []
    current_text = ""
    page_num = 1

    for para in paragraphs:
        candidate = (current_text + "\n" + para).strip() if current_text else para.strip()
        if len(candidate) > CHARS_PER_PAGE and current_text:
            pages.append(PageResult(
                page_number=page_num,
                text=current_text,
                extraction_method="digital",
                quality_indicator=100.0,
            ))
            page_num += 1
            current_text = para.strip()
        else:
            current_text = candidate

    if current_text.strip():
        pages.append(PageResult(
            page_number=page_num,
            text=current_text,
            extraction_method="digital",
            quality_indicator=100.0,
        ))

    return pages
