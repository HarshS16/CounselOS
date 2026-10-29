import logging

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.api.schemas import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
    PageResponse,
)
from backend.auth.session_auth import verify_session
from backend.config import settings
from backend.db.models import Document, DocumentPage, Matter
from backend.db.session import get_db
from backend.ingestion.pipeline import ingest_document
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/matters/{matter_id}/documents",
    tags=["documents"],
    dependencies=[Depends(verify_session)],
)


def _validate_matter(db: Session, matter_id: str) -> Matter:
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.status != "deleted").first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter


def _validate_document(db: Session, matter_id: str, document_id: str) -> Document:
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.matter_id == matter_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found in this matter")
    return doc


@router.post("/", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    matter_id: str,
    file: UploadFile,
    request: Request,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.max_file_size_mb} MB",
        )

    doc = await ingest_document(db, matter_id, file.filename or "unnamed", content)

    retriever = getattr(request.app.state, "retriever", None)
    if retriever and doc.processing_status in ("indexed", "partially_processed"):
        try:
            retriever.index_document(doc.id)
        except Exception:
            logger.warning("Failed to index document %s in retriever", doc.id)

    log_audit_event(
        db, "document_imported",
        matter_id=matter_id,
        metadata={"document_id": doc.id, "filename": doc.original_name, "status": doc.processing_status},
    )
    db.commit()

    duplicate_of = None
    if doc.extraction_warnings and "Byte-identical" in doc.extraction_warnings:
        duplicate_of = doc.extraction_warnings

    return DocumentUploadResponse(
        id=doc.id,
        original_name=doc.original_name,
        sha256=doc.sha256,
        processing_status=doc.processing_status,
        duplicate_of=duplicate_of,
        message=f"Document imported with status: {doc.processing_status}",
    )


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    matter_id: str,
    processing_status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    query = db.query(Document).filter(Document.matter_id == matter_id)
    if processing_status:
        query = query.filter(Document.processing_status == processing_status)
    total = query.count()
    docs = query.order_by(Document.imported_at.desc()).offset(skip).limit(limit).all()
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in docs],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(matter_id: str, document_id: str, db: Session = Depends(get_db)):
    doc = _validate_document(db, matter_id, document_id)
    return DocumentResponse.model_validate(doc)


@router.get("/{document_id}/pages", response_model=list[PageResponse])
def list_pages(matter_id: str, document_id: str, db: Session = Depends(get_db)):
    _validate_document(db, matter_id, document_id)
    pages = (
        db.query(DocumentPage)
        .filter(DocumentPage.document_id == document_id)
        .order_by(DocumentPage.page_number)
        .all()
    )
    return [PageResponse.model_validate(p) for p in pages]


@router.get("/{document_id}/pages/{page_number}", response_model=PageResponse)
def get_page(
    matter_id: str, document_id: str, page_number: int, db: Session = Depends(get_db)
):
    _validate_document(db, matter_id, document_id)
    page = (
        db.query(DocumentPage)
        .filter(DocumentPage.document_id == document_id, DocumentPage.page_number == page_number)
        .first()
    )
    if not page:
        raise HTTPException(status_code=404, detail=f"Page {page_number} not found")
    return PageResponse.model_validate(page)


@router.get("/{document_id}/original")
def download_original(matter_id: str, document_id: str, db: Session = Depends(get_db)):
    doc = _validate_document(db, matter_id, document_id)
    file_path = settings.data_dir / doc.storage_key
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found on disk")
    return FileResponse(
        path=str(file_path),
        filename=doc.original_name,
        media_type=doc.mime_type,
    )


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document(
    matter_id: str, document_id: str, request: Request, db: Session = Depends(get_db)
):
    doc = _validate_document(db, matter_id, document_id)
    file_path = settings.data_dir / doc.storage_key
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found on disk")

    content = file_path.read_bytes()

    db.query(DocumentPage).filter(DocumentPage.document_id == document_id).delete()

    from backend.db.models import Chunk
    db.query(Chunk).filter(Chunk.document_id == document_id).delete()
    db.commit()

    retriever = getattr(request.app.state, "retriever", None)
    if retriever:
        try:
            retriever.remove_document(document_id)
        except Exception:
            logger.warning("Failed to remove document %s from indexes", document_id)

    new_doc = await ingest_document(db, matter_id, doc.original_name, content)

    if retriever and new_doc.processing_status in ("indexed", "partially_processed"):
        try:
            retriever.index_document(new_doc.id)
        except Exception:
            logger.warning("Failed to re-index document %s", new_doc.id)

    log_audit_event(
        db, "document_processed",
        matter_id=matter_id,
        metadata={"document_id": doc.id, "action": "reprocess"},
    )
    db.commit()
    return DocumentResponse.model_validate(new_doc)


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    matter_id: str, document_id: str, request: Request, db: Session = Depends(get_db)
):
    doc = _validate_document(db, matter_id, document_id)

    retriever = getattr(request.app.state, "retriever", None)
    if retriever:
        try:
            retriever.remove_document(document_id)
        except Exception:
            logger.warning("Failed to remove document %s from indexes", document_id)

    log_audit_event(
        db, "document_deleted",
        matter_id=matter_id,
        metadata={"document_id": doc.id, "filename": doc.original_name},
    )

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted", "document_id": document_id}
