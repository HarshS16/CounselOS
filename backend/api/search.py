import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.api.schemas import (
    Citation,
    QARequest,
    QAResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from backend.auth.session_auth import verify_session
from backend.db.models import Chunk, Document, Matter
from backend.db.session import get_db
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/matters/{matter_id}",
    tags=["search"],
    dependencies=[Depends(verify_session)],
)


def _validate_matter(db: Session, matter_id: str) -> Matter:
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.status != "deleted").first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter


@router.post("/search", response_model=SearchResponse)
def search_documents(
    matter_id: str,
    body: SearchRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)

    retriever = getattr(request.app.state, "retriever", None)
    if retriever is None:
        raise HTTPException(status_code=503, detail="Search service not available")

    from backend.retrieval.hybrid_search import HybridRetriever, RetrievalResult

    retriever_instance = HybridRetriever(
        request.app.state.embedding_service,
        request.app.state.vector_store,
        db,
    )

    results = retriever_instance.search(matter_id, body.query, k=body.max_results)

    search_results = []
    for r in results:
        doc = db.query(Document).filter(Document.id == r.document_id).first()
        doc_name = doc.original_name if doc else "unknown"
        search_results.append(
            SearchResult(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                document_name=doc_name,
                page_start=r.page_start,
                page_end=r.page_end,
                text=r.text,
                score=r.score,
            )
        )

    log_audit_event(
        db, "search_executed",
        matter_id=matter_id,
        metadata={"query_length": len(body.query), "mode": body.mode, "result_count": len(search_results)},
    )
    db.commit()

    return SearchResponse(
        results=search_results,
        query=body.query,
        mode=body.mode,
        total_results=len(search_results),
    )


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    matter_id: str,
    body: QARequest,
    request: Request,
    db: Session = Depends(get_db),
):
    _validate_matter(db, matter_id)

    qa_service = getattr(request.app.state, "qa_service", None)
    if qa_service is None:
        raise HTTPException(status_code=503, detail="QA service not available — LLM may not be loaded")

    try:
        result = await qa_service.answer_question(db, matter_id, body.question)
    except Exception as e:
        logger.error("QA failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Question answering failed: {e}")

    citations = []
    for c in result.citations:
        chunk = db.query(Chunk).filter(Chunk.id == c.chunk_id).first() if c.chunk_id else None
        citations.append(
            Citation(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                document_name=c.document_name,
                page_start=chunk.page_start if chunk else (c.page_number or 0),
                page_end=chunk.page_end if chunk else (c.page_number or 0),
                quote=c.quote,
                is_valid=c.valid,
            )
        )

    return QAResponse(
        answer=result.answer,
        citations=citations,
        confidence=result.confidence,
        abstained=result.abstained,
        conflicts_detected=result.conflicts_noted,
        analysis_run_id=result.analysis_run_id,
    )
