import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.api.schemas import ExportRequest, ExportResponse
from backend.auth.session_auth import verify_session
from backend.config import settings
from backend.db.models import Event, Finding, Matter
from backend.db.session import get_db
from backend.exports.report_generator import ExportOptions, generate_evidence_report
from backend.security.audit import log_audit_event

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/matters/{matter_id}/exports",
    tags=["exports"],
    dependencies=[Depends(verify_session)],
)


def _validate_matter(db: Session, matter_id: str) -> Matter:
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.status != "deleted").first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return matter


@router.post("/", response_model=ExportResponse)
def create_export(matter_id: str, body: ExportRequest, db: Session = Depends(get_db)):
    _validate_matter(db, matter_id)

    options = ExportOptions(
        include_findings=body.include_findings,
        include_chronology=body.include_chronology,
        include_sources=body.include_sources,
        finding_statuses=body.finding_statuses,
        format=body.format,
    )

    try:
        filepath = generate_evidence_report(db, matter_id, options)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Export failed: %s", e)
        raise HTTPException(status_code=500, detail="Report generation failed")

    finding_count = db.query(Finding).filter(Finding.matter_id == matter_id).count()
    event_count = db.query(Event).filter(Event.matter_id == matter_id).count()

    log_audit_event(
        db, "export_created",
        matter_id=matter_id,
        metadata={"format": body.format, "filename": filepath.name},
    )
    db.commit()

    return ExportResponse(
        file_path=str(filepath),
        file_name=filepath.name,
        format=body.format,
        matter_id=matter_id,
        export_timestamp=datetime.now(timezone.utc),
        finding_count=finding_count,
        event_count=event_count,
    )


@router.get("/")
def list_exports(matter_id: str, db: Session = Depends(get_db)):
    _validate_matter(db, matter_id)
    exports_dir = settings.exports_dir
    if not exports_dir.exists():
        return {"exports": []}

    files = []
    for f in sorted(exports_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if f.is_file() and f.suffix in (".docx", ".pdf"):
            files.append({
                "filename": f.name,
                "size_bytes": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
            })
    return {"exports": files}


@router.get("/{filename}")
def download_export(matter_id: str, filename: str, db: Session = Depends(get_db)):
    _validate_matter(db, matter_id)

    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    filepath = settings.exports_dir / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Export file not found")

    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if filepath.suffix == ".pdf":
        media_type = "application/pdf"

    return FileResponse(path=str(filepath), filename=filename, media_type=media_type)
