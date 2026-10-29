import time

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from backend.api.schemas import (
    AuditEventResponse,
    HealthResponse,
    ModelStatusResponse,
)
from backend.auth.session_auth import get_session_token, verify_session
from backend.config import settings
from backend.db.models import AuditEvent
from backend.db.session import get_db

router = APIRouter(prefix="/api/system", tags=["system"])

_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request, db: Session = Depends(get_db)):
    db_ok = False
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    llm_service = getattr(request.app.state, "llm_service", None)
    llm_available = llm_service is not None and llm_service.is_loaded if llm_service else False

    embedding_service = getattr(request.app.state, "embedding_service", None)
    embedding_available = embedding_service is not None and getattr(embedding_service, "is_available", False)

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        version=settings.app_version,
        db_connected=db_ok,
        llm_available=llm_available,
        embedding_available=embedding_available,
        data_dir=str(settings.data_dir),
        uptime_seconds=round(time.time() - _start_time, 1),
    )


@router.get("/session-token")
def session_token(request: Request):
    """Return the session token. Only accessible from loopback — no auth required."""
    host = request.client.host if request.client else ""
    if host not in ("127.0.0.1", "::1", "localhost"):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Only accessible from localhost")
    return {"token": get_session_token()}


@router.get("/model-status", response_model=ModelStatusResponse, dependencies=[Depends(verify_session)])
def model_status(request: Request):
    llm_service = getattr(request.app.state, "llm_service", None)
    embedding_service = getattr(request.app.state, "embedding_service", None)

    llm_loaded = False
    llm_model_name = None
    llm_context_length = None

    if llm_service:
        llm_loaded = llm_service.is_loaded
        info = llm_service.model_info
        llm_model_name = info.get("model_path", "")
        llm_context_length = info.get("context_length")

    embedding_loaded = False
    embedding_model_name = None
    if embedding_service:
        embedding_loaded = getattr(embedding_service, "is_available", False)
        embedding_model_name = settings.embedding_model_name

    return ModelStatusResponse(
        llm_loaded=llm_loaded,
        llm_model_name=llm_model_name,
        embedding_loaded=embedding_loaded,
        embedding_model_name=embedding_model_name,
        llm_context_length=llm_context_length,
    )


@router.get("/audit-log", response_model=list[AuditEventResponse], dependencies=[Depends(verify_session)])
def list_audit_events(
    matter_id: str | None = None,
    event_type: str | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(AuditEvent)
    if matter_id:
        query = query.filter(AuditEvent.matter_id == matter_id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    events = query.order_by(AuditEvent.timestamp.desc()).offset(skip).limit(limit).all()
    return [AuditEventResponse.model_validate(e) for e in events]
