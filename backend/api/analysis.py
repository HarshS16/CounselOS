import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.api.schemas import (
    ChronologyResponse,
    ClaimResponse,
    ClaimSourceResponse,
    ComparisonRequest,
    ComparisonResponse,
    DiscrepancyResult,
    EntityAliasResponse,
    EntityResponse,
    EventResponse,
    EventSourceResponse,
)
from backend.auth.session_auth import verify_session
from backend.db.models import (
    Chunk,
    Claim,
    ClaimSource,
    Document,
    Entity,
    EntityAlias,
    Event,
    EventSource,
    Matter,
    ReviewEvent,
    gen_id,
)
from backend.db.session import get_db
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/matters/{matter_id}",
    tags=["analysis"],
    dependencies=[Depends(verify_session)],
)


def _validate_matter(db: Session, matter_id: str) -> Matter:
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.status != "deleted").first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter


def _build_claim_response(db: Session, claim: Claim) -> ClaimResponse:
    sources_raw = (
        db.query(ClaimSource, Chunk, Document)
        .join(Chunk, ClaimSource.chunk_id == Chunk.id)
        .join(Document, Chunk.document_id == Document.id)
        .filter(ClaimSource.claim_id == claim.id)
        .all()
    )
    sources = [
        ClaimSourceResponse(
            chunk_id=cs.chunk_id,
            document_id=doc.id,
            document_name=doc.original_name,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            quote_text=cs.quote_text,
            evidence_role=cs.evidence_role,
        )
        for cs, chunk, doc in sources_raw
    ]
    return ClaimResponse(
        id=claim.id,
        matter_id=claim.matter_id,
        claim_text=claim.claim_text,
        claim_type=claim.claim_type,
        speaker_entity_id=claim.speaker_entity_id,
        date_value=claim.date_value,
        date_precision=claim.date_precision,
        review_status=claim.review_status,
        uncertainty_note=claim.uncertainty_note,
        analysis_run_id=claim.analysis_run_id,
        created_at=claim.created_at,
        sources=sources,
    )


def _build_event_response(db: Session, event: Event) -> EventResponse:
    sources_raw = (
        db.query(EventSource, Chunk, Document)
        .join(Chunk, EventSource.chunk_id == Chunk.id)
        .join(Document, Chunk.document_id == Document.id)
        .filter(EventSource.event_id == event.id)
        .all()
    )
    sources = [
        EventSourceResponse(
            chunk_id=es.chunk_id,
            document_id=doc.id,
            document_name=doc.original_name,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            support_type=es.support_type,
        )
        for es, chunk, doc in sources_raw
    ]
    return EventResponse(
        id=event.id,
        matter_id=event.matter_id,
        event_date=event.event_date,
        date_precision=event.date_precision,
        description=event.description,
        review_status=event.review_status,
        analysis_run_id=event.analysis_run_id,
        sort_key=event.sort_key,
        created_at=event.created_at,
        sources=sources,
    )


# ── Extraction ─────────────────────────────────────────────────────────────

@router.post("/extract")
def run_extraction(
    matter_id: str,
    request: Request,
    document_ids: list[str] | None = None,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)

    llm_service = getattr(request.app.state, "llm_service", None)
    if llm_service is None or not llm_service.is_loaded:
        raise HTTPException(status_code=503, detail="LLM not available")

    query = db.query(Chunk, Document).join(Document, Chunk.document_id == Document.id).filter(
        Document.matter_id == matter_id
    )
    if document_ids:
        for did in document_ids:
            if not db.query(Document).filter(Document.id == did, Document.matter_id == matter_id).first():
                raise HTTPException(status_code=404, detail=f"Document {did} not found in this matter")
        query = query.filter(Document.id.in_(document_ids))

    rows = query.order_by(Chunk.chunk_index).all()
    chunks_data = [
        {
            "chunk_id": chunk.id,
            "document_id": doc.id,
            "document_name": doc.original_name,
            "text": chunk.text,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
        }
        for chunk, doc in rows
    ]

    if not chunks_data:
        raise HTTPException(status_code=400, detail="No indexed chunks found for the selected documents")

    from backend.workflows.extraction import run_extraction as do_extraction

    log_audit_event(db, "analysis_started", matter_id=matter_id, metadata={"workflow": "extraction"})
    db.commit()

    result = do_extraction(db, llm_service, matter_id, chunks_data, document_ids)

    if result.error:
        log_audit_event(db, "analysis_failed", matter_id=matter_id, metadata={"workflow": "extraction"})
    else:
        log_audit_event(
            db, "analysis_completed",
            matter_id=matter_id,
            metadata={"workflow": "extraction", "claims": len(result.claims), "entities": len(result.entities)},
        )
    db.commit()

    return {
        "analysis_run_id": result.analysis_run_id,
        "claims_extracted": len(result.claims),
        "entities_extracted": len(result.entities),
        "error": result.error,
    }


# ── Claims ─────────────────────────────────────────────────────────────────

@router.get("/claims", response_model=list[ClaimResponse])
def list_claims(
    matter_id: str,
    claim_type: str | None = None,
    review_status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    query = db.query(Claim).filter(Claim.matter_id == matter_id)
    if claim_type:
        query = query.filter(Claim.claim_type == claim_type)
    if review_status:
        query = query.filter(Claim.review_status == review_status)
    claims = query.order_by(Claim.created_at.desc()).offset(skip).limit(limit).all()
    return [_build_claim_response(db, c) for c in claims]


@router.put("/claims/{claim_id}", response_model=ClaimResponse)
def update_claim(
    matter_id: str,
    claim_id: str,
    review_status: str | None = None,
    claim_text: str | None = None,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    claim = db.query(Claim).filter(Claim.id == claim_id, Claim.matter_id == matter_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    prev_status = claim.review_status
    if review_status:
        claim.review_status = review_status
    if claim_text is not None:
        claim.claim_text = claim_text

    db.add(ReviewEvent(
        id=gen_id(),
        claim_id=claim.id,
        action="claim_reviewed",
        previous_value=prev_status,
        new_value=claim.review_status,
    ))
    db.commit()
    return _build_claim_response(db, claim)


# ── Entities ───────────────────────────────────────────────────────────────

@router.get("/entities", response_model=list[EntityResponse])
def list_entities(
    matter_id: str,
    entity_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    query = db.query(Entity).filter(Entity.matter_id == matter_id)
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
    entities = query.order_by(Entity.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for ent in entities:
        aliases = db.query(EntityAlias).filter(EntityAlias.entity_id == ent.id).all()
        result.append(
            EntityResponse(
                id=ent.id,
                matter_id=ent.matter_id,
                entity_type=ent.entity_type,
                canonical_label=ent.canonical_label,
                status=ent.status,
                created_at=ent.created_at,
                aliases=[EntityAliasResponse.model_validate(a) for a in aliases],
            )
        )
    return result


@router.put("/entities/{entity_id}", response_model=EntityResponse)
def update_entity(
    matter_id: str,
    entity_id: str,
    canonical_label: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    entity = db.query(Entity).filter(Entity.id == entity_id, Entity.matter_id == matter_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    if canonical_label is not None:
        entity.canonical_label = canonical_label
    if status is not None:
        entity.status = status
    db.commit()
    aliases = db.query(EntityAlias).filter(EntityAlias.entity_id == entity.id).all()
    return EntityResponse(
        id=entity.id,
        matter_id=entity.matter_id,
        entity_type=entity.entity_type,
        canonical_label=entity.canonical_label,
        status=entity.status,
        created_at=entity.created_at,
        aliases=[EntityAliasResponse.model_validate(a) for a in aliases],
    )


# ── Chronology ─────────────────────────────────────────────────────────────

@router.post("/chronology", response_model=ChronologyResponse)
def build_chronology(
    matter_id: str,
    request: Request,
    claim_ids: list[str] | None = None,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)

    llm_service = getattr(request.app.state, "llm_service", None)
    if llm_service is None or not llm_service.is_loaded:
        raise HTTPException(status_code=503, detail="LLM not available")

    from backend.workflows.chronology import build_chronology as do_chronology

    log_audit_event(db, "analysis_started", matter_id=matter_id, metadata={"workflow": "chronology"})
    db.commit()

    result = do_chronology(db, llm_service, matter_id, claim_ids)

    if result.error:
        log_audit_event(db, "analysis_failed", matter_id=matter_id, metadata={"workflow": "chronology"})
    else:
        log_audit_event(db, "analysis_completed", matter_id=matter_id, metadata={"workflow": "chronology", "events": len(result.events)})
    db.commit()

    events_response = []
    for evt in result.events:
        if evt.event_id:
            db_event = db.query(Event).filter(Event.id == evt.event_id).first()
            if db_event:
                events_response.append(_build_event_response(db, db_event))

    ambiguous = sum(1 for e in result.events if e.date_precision in ("approximate", "range", "inferred", "unknown"))

    return ChronologyResponse(
        matter_id=matter_id,
        events=events_response,
        total_events=len(events_response),
        ambiguous_date_count=ambiguous,
        analysis_run_id=result.analysis_run_id,
    )


@router.get("/chronology", response_model=ChronologyResponse)
def get_chronology(
    matter_id: str,
    review_status: str | None = None,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    query = db.query(Event).filter(Event.matter_id == matter_id)
    if review_status:
        query = query.filter(Event.review_status == review_status)
    events = query.order_by(Event.sort_key).all()

    events_response = [_build_event_response(db, e) for e in events]
    ambiguous = sum(1 for e in events if e.date_precision in ("approximate", "range", "inferred", "unknown"))

    return ChronologyResponse(
        matter_id=matter_id,
        events=events_response,
        total_events=len(events_response),
        ambiguous_date_count=ambiguous,
    )


@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    matter_id: str,
    event_id: str,
    review_status: str | None = None,
    description: str | None = None,
    event_date: str | None = None,
    date_precision: str | None = None,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)
    event = db.query(Event).filter(Event.id == event_id, Event.matter_id == matter_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    prev_status = event.review_status
    if review_status:
        event.review_status = review_status
    if description is not None:
        event.description = description
    if event_date is not None:
        event.event_date = event_date
    if date_precision is not None:
        event.date_precision = date_precision

    db.add(ReviewEvent(
        id=gen_id(),
        event_id=event.id,
        action="event_reviewed",
        previous_value=prev_status,
        new_value=event.review_status,
    ))
    db.commit()
    return _build_event_response(db, event)


# ── Comparison ─────────────────────────────────────────────────────────────

@router.post("/compare", response_model=ComparisonResponse)
def compare_documents(
    matter_id: str,
    body: ComparisonRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)

    llm_service = getattr(request.app.state, "llm_service", None)
    if llm_service is None or not llm_service.is_loaded:
        raise HTTPException(status_code=503, detail="LLM not available")

    for did in body.document_ids:
        if not db.query(Document).filter(Document.id == did, Document.matter_id == matter_id).first():
            raise HTTPException(status_code=404, detail=f"Document {did} not found in this matter")

    from backend.workflows.comparison import compare_document_claims

    log_audit_event(db, "analysis_started", matter_id=matter_id, metadata={"workflow": "comparison"})
    db.commit()

    doc_a = db.query(Document).filter(Document.id == body.document_ids[0]).first()
    doc_b = db.query(Document).filter(Document.id == body.document_ids[1]).first()

    result = compare_document_claims(
        db,
        llm_service,
        matter_id,
        body.document_ids[0],
        body.document_ids[1],
        doc_a.original_name if doc_a else "Document A",
        doc_b.original_name if doc_b else "Document B",
    )

    if result.error:
        log_audit_event(db, "analysis_failed", matter_id=matter_id, metadata={"workflow": "comparison"})
    else:
        log_audit_event(db, "analysis_completed", matter_id=matter_id, metadata={"workflow": "comparison", "findings": len(result.findings)})
    db.commit()

    discrepancies = []
    for f in result.findings:
        claim_a_resp = None
        claim_b_resp = None
        if f.claim_a_id:
            claim_a = db.query(Claim).filter(Claim.id == f.claim_a_id).first()
            if claim_a:
                claim_a_resp = _build_claim_response(db, claim_a)
        if f.claim_b_id:
            claim_b = db.query(Claim).filter(Claim.id == f.claim_b_id).first()
            if claim_b:
                claim_b_resp = _build_claim_response(db, claim_b)

        discrepancies.append(
            DiscrepancyResult(
                finding_type=f.finding_type,
                summary=f.summary,
                explanation=f.explanation,
                claim_a=claim_a_resp,
                claim_b=claim_b_resp,
                review_status="pending",
            )
        )

    total_claims = db.query(Claim).filter(Claim.matter_id == matter_id).count()

    return ComparisonResponse(
        matter_id=matter_id,
        discrepancies=discrepancies,
        total_claims_compared=total_claims,
        analysis_run_id=result.analysis_run_id,
    )
