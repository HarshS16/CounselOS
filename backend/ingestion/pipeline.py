from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.orm import Session

from backend.config import settings
from backend.db.models import Chunk, Document, DocumentPage, gen_id
from backend.ingestion.chunker import chunk_pages
from backend.ingestion.docx_extractor import extract_docx
from backend.ingestion.file_validator import validate_file
from backend.ingestion.pdf_extractor import extract_pdf

logger = logging.getLogger(__name__)


async def ingest_document(
    db: Session,
    matter_id: str,
    filename: str,
    content: bytes,
) -> Document:
    """Full ingestion pipeline: validate, store, extract, chunk, persist."""
    doc_id = gen_id()
    doc = Document(
        id=doc_id,
        matter_id=matter_id,
        original_name=filename,
        storage_key="",
        sha256="",
        mime_type="",
        size_bytes=len(content),
        processing_status="imported",
    )
    db.add(doc)
    db.flush()

    # Step 1 — validate
    mime_type, sha256, error = validate_file(filename, content)
    if error:
        doc.processing_status = "failed"
        doc.extraction_warnings = error
        db.commit()
        return doc

    doc.mime_type = mime_type
    doc.sha256 = sha256

    # Check for byte-identical duplicate
    existing = (
        db.query(Document)
        .filter(Document.matter_id == matter_id, Document.sha256 == sha256, Document.id != doc_id)
        .first()
    )
    if existing:
        doc.extraction_warnings = (
            f"Byte-identical document already exists: {existing.original_name} ({existing.id})"
        )

    # Step 2 — store original
    doc.processing_status = "processing"
    db.flush()

    storage_dir = settings.originals_dir / matter_id / doc_id
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_path = storage_dir / filename
    storage_path.write_bytes(content)
    doc.storage_key = str(storage_path.relative_to(settings.data_dir))

    # Step 3 — extract pages
    try:
        if mime_type == "application/pdf":
            pages = extract_pdf(storage_path, doc_id)
        else:
            pages = extract_docx(storage_path, doc_id)
    except Exception:
        logger.exception("Extraction failed for document %s", doc_id)
        doc.processing_status = "failed"
        doc.extraction_warnings = (doc.extraction_warnings or "") + " Extraction failed."
        db.commit()
        return doc

    doc.page_count = len(pages)
    doc.is_scanned = any(p.extraction_method in ("ocr", "mixed") for p in pages)
    doc.parser_version = "1.0.0"
    if doc.is_scanned:
        doc.ocr_version = "tesseract-1.0"

    # Collect quality warnings
    failed_pages = [p for p in pages if p.extraction_method == "failed"]
    low_quality = [p for p in pages if 0 < p.quality_indicator < settings.ocr_quality_threshold]
    warnings: list[str] = []
    if doc.extraction_warnings:
        warnings.append(doc.extraction_warnings)
    if failed_pages:
        warnings.append(f"{len(failed_pages)} page(s) failed extraction.")
    if low_quality:
        warnings.append(
            f"{len(low_quality)} page(s) have low OCR quality "
            f"(below {settings.ocr_quality_threshold}%)."
        )
    doc.extraction_warnings = " ".join(warnings) if warnings else None

    # Step 4 — save pages
    for page in pages:
        db.add(DocumentPage(
            document_id=doc_id,
            page_number=page.page_number,
            extracted_text=page.text,
            extraction_method=page.extraction_method,
            quality_indicator=page.quality_indicator,
            processing_status="completed" if page.text else "failed",
        ))

    # Step 5 — chunk
    try:
        chunk_results = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
    except Exception:
        logger.exception("Chunking failed for document %s", doc_id)
        doc.processing_status = "partially_processed"
        doc.extraction_warnings = (doc.extraction_warnings or "") + " Chunking failed."
        db.commit()
        return doc

    for cr in chunk_results:
        db.add(Chunk(
            document_id=doc_id,
            page_start=cr.page_start,
            page_end=cr.page_end,
            paragraph_start=cr.paragraph_start,
            paragraph_end=cr.paragraph_end,
            text=cr.text,
            content_hash=cr.content_hash,
            chunk_index=cr.chunk_index,
        ))

    # Final status
    if failed_pages and len(failed_pages) == len(pages):
        doc.processing_status = "failed"
    elif failed_pages or low_quality:
        doc.processing_status = "partially_processed"
    else:
        doc.processing_status = "indexed"

    db.commit()
    logger.info(
        "Ingested document %s: %d pages, %d chunks, status=%s",
        doc_id, len(pages), len(chunk_results), doc.processing_status,
    )
    return doc
