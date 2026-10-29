from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.api.schemas import (
    MatterCreate,
    MatterListResponse,
    MatterResponse,
    MatterUpdate,
)
from backend.auth.session_auth import verify_session
from backend.db.models import Document, Finding, Matter
from backend.db.session import get_db
from backend.security.audit import log_audit_event

router = APIRouter(prefix="/api/matters", tags=["matters"], dependencies=[Depends(verify_session)])


def _matter_to_response(db: Session, matter: Matter) -> MatterResponse:
    doc_count = db.query(func.count(Document.id)).filter(Document.matter_id == matter.id).scalar() or 0
    finding_count = db.query(func.count(Finding.id)).filter(Finding.matter_id == matter.id).scalar() or 0
    pending_count = (
        db.query(func.count(Finding.id))
        .filter(Finding.matter_id == matter.id, Finding.review_status == "pending")
        .scalar()
        or 0
    )
    return MatterResponse(
        id=matter.id,
        title=matter.title,
        reference=matter.reference,
        jurisdiction=matter.jurisdiction,
        matter_type=matter.matter_type,
        status=matter.status,
        party_names=matter.party_names,
        notes=matter.notes,
        created_at=matter.created_at,
        updated_at=matter.updated_at,
        document_count=doc_count,
        finding_count=finding_count,
        pending_review_count=pending_count,
    )


@router.post("/", response_model=MatterResponse, status_code=status.HTTP_201_CREATED)
def create_matter(body: MatterCreate, db: Session = Depends(get_db)):
    matter = Matter(
        title=body.title,
        reference=body.reference,
        jurisdiction=body.jurisdiction,
        matter_type=body.matter_type,
        party_names=body.party_names,
        notes=body.notes,
    )
    db.add(matter)
    db.commit()
    db.refresh(matter)
    log_audit_event(db, "matter_created", matter_id=matter.id, metadata={"title": matter.title})
    db.commit()
    return _matter_to_response(db, matter)


@router.get("/", response_model=MatterListResponse)
def list_matters(
    status_filter: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Matter)
    if status_filter:
        query = query.filter(Matter.status == status_filter)
    else:
        query = query.filter(Matter.status != "deleted")
    if search:
        query = query.filter(Matter.title.ilike(f"%{search}%"))
    total = query.count()
    matters = query.order_by(Matter.updated_at.desc()).offset(skip).limit(limit).all()
    return MatterListResponse(
        matters=[_matter_to_response(db, m) for m in matters],
        total=total,
    )


@router.get("/{matter_id}", response_model=MatterResponse)
def get_matter(matter_id: str, db: Session = Depends(get_db)):
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.status != "deleted").first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    return _matter_to_response(db, matter)


@router.put("/{matter_id}", response_model=MatterResponse)
def update_matter(matter_id: str, body: MatterUpdate, db: Session = Depends(get_db)):
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.status != "deleted").first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(matter, key, value)

    db.commit()
    db.refresh(matter)
    log_audit_event(db, "matter_updated", matter_id=matter.id, metadata={"fields": list(update_data.keys())})
    db.commit()
    return _matter_to_response(db, matter)


@router.post("/{matter_id}/archive", response_model=MatterResponse)
def archive_matter(matter_id: str, db: Session = Depends(get_db)):
    matter = db.query(Matter).filter(Matter.id == matter_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    if matter.status == "deleted":
        raise HTTPException(status_code=400, detail="Cannot archive a deleted matter")

    matter.status = "archived"
    db.commit()
    db.refresh(matter)
    log_audit_event(db, "matter_archived", matter_id=matter.id)
    db.commit()
    return _matter_to_response(db, matter)


@router.delete("/{matter_id}", status_code=status.HTTP_200_OK)
def delete_matter(matter_id: str, confirm: bool = False, db: Session = Depends(get_db)):
    matter = db.query(Matter).filter(Matter.id == matter_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Deletion requires confirm=true. This will remove all documents, "
            "indexes, reports, and associated metadata. Backups are not automatically "
            "removed — check your backup directory.",
        )

    log_audit_event(db, "matter_deleted", matter_id=matter.id, metadata={"title": matter.title})
    matter.status = "deleted"
    db.commit()
    return {"message": "Matter deleted", "matter_id": matter_id}
