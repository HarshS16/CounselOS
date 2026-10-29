import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from backend.db.models import AuditEvent

VALID_EVENT_TYPES = frozenset({
    "matter_created",
    "matter_updated",
    "matter_archived",
    "matter_deleted",
    "document_imported",
    "document_processed",
    "document_deleted",
    "search_executed",
    "analysis_started",
    "analysis_completed",
    "analysis_failed",
    "finding_reviewed",
    "export_created",
    "backup_created",
    "backup_restored",
})


def log_audit_event(
    db: Session,
    event_type: str,
    matter_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> AuditEvent:
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Unknown audit event type: {event_type}")

    meta_json = None
    if metadata is not None:
        sanitized = {k: v for k, v in metadata.items() if not _is_sensitive_key(k)}
        meta_json = json.dumps(sanitized, default=str)

    audit = AuditEvent(
        event_type=event_type,
        matter_id=matter_id,
        metadata_json=meta_json,
    )
    db.add(audit)
    db.flush()
    return audit


def _is_sensitive_key(key: str) -> bool:
    lower = key.lower()
    blocked = ("password", "secret", "token", "key", "credential", "ssn", "aadhaar", "pan_number")
    return any(term in lower for term in blocked)
