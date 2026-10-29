import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.schemas import (
    FindingResponse,
    FindingReviewRequest,
    FindingSourceResponse,
    ReviewEventResponse,
)
from backend.auth.session_auth import verify_session
from backend.db.models import (
    Chunk,
    Document,
    Finding,
    FindingSource,
    Matter,
    ReviewEvent,
    gen_id,
)
from backend.db.session import get_db
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/matters/{matter_id}/findings",
    tags=["findings"],
    dependencies=[Depends(verify_session)],
)


def _validate_matter(db: Session, matter_id: str) -> Matter:
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.status != "deleted").first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter


def _build_finding_response(db: Session, finding: Finding) -> FindingResponse:
    sources_raw = (
        db.query(FindingSource, Chunk, Document)
        .join(Chunk, FindingSource.chunk_id == Chunk.id)
        .join(Document, Chunk.document_id == Document.id)
        .filter(FindingSource.finding_id == finding.id)
        .all()
    )
    sources = [
        FindingSourceResponse(
            chunk_id=fs.chunk_id,
            document_id=doc.id,
            document_name=doc.original_name,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            text=chunk.text[:500],
            relationship_type=fs.relationship_type,
        )
        for fs, chunk, doc in sources_raw
    ]
    return FindingResponse(
        id=finding.id,
        matter_id=finding.matter_id,
        analysis_run_id=finding.analysis_run_id,
        finding_type=finding.finding_type,
        summary=finding.summary,
        explanation=finding.explanation,
        claim_a_id=finding.claim_a_id,
        claim_b_id=finding.claim_b_id,
        review_status=finding.review_status,
        reviewer_note=finding.reviewer_note,
        created_at=finding.created_at,
        sources=sources,
    )


@router.get("/", response_model=list[FindingResponse])
def list_findings(
    matter_id: str,
    finding_type: str | None = None,
    review_status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    query = db.query(Finding).filter(Finding.matter_id == matter_id)
    if finding_type:
        query = query.filter(Finding.finding_type == finding_type)
    if review_status:
        query = query.filter(Finding.review_status == review_status)
    findings = query.order_by(Finding.created_at.desc()).offset(skip).limit(limit).all()
    return [_build_finding_response(db, f) for f in findings]


@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(matter_id: str, finding_id: str, db: Session = Depends(get_db)):
    _validate_matter(db, matter_id)
    finding = db.query(Finding).filter(Finding.id == finding_id, Finding.matter_id == matter_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return _build_finding_response(db, finding)


@router.put("/{finding_id}/review", response_model=FindingResponse)
def review_finding(
    matter_id: str,
    finding_id: str,
    body: FindingReviewRequest,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    finding = db.query(Finding).filter(Finding.id == finding_id, Finding.matter_id == matter_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    previous_status = finding.review_status
    previous_note = finding.reviewer_note

    finding.review_status = body.review_status
    if body.reviewer_note is not None:
        finding.reviewer_note = body.reviewer_note

    review_event = ReviewEvent(
        id=gen_id(),
        finding_id=finding.id,
        action=f"status_changed_to_{body.review_status}",
        previous_value=previous_status,
        new_value=body.review_status,
    )
    db.add(review_event)

    log_audit_event(
        db, "finding_reviewed",
        matter_id=matter_id,
        metadata={
            "finding_id": finding_id,
            "previous_status": previous_status,
            "new_status": body.review_status,
        },
    )
    db.commit()
    return _build_finding_response(db, finding)


@router.get("/{finding_id}/history", response_model=list[ReviewEventResponse])
def get_finding_history(
    matter_id: str, finding_id: str, db: Session = Depends(get_db)
):
    _validate_matter(db, matter_id)
    finding = db.query(Finding).filter(Finding.id == finding_id, Finding.matter_id == matter_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    events = (
        db.query(ReviewEvent)
        .filter(ReviewEvent.finding_id == finding_id)
        .order_by(ReviewEvent.timestamp.desc())
        .all()
    )
    return [ReviewEventResponse.model_validate(e) for e in events]
