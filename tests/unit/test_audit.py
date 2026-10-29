from backend.db.models import Matter, AuditEvent, gen_id
from backend.security.audit import log_audit_event


def test_log_audit_event(db_session):
    matter = Matter(id=gen_id(), title="Audit Test")
    db_session.add(matter)
    db_session.commit()

    log_audit_event(
        db_session,
        event_type="matter_created",
        matter_id=matter.id,
        metadata={"title": matter.title},
    )

    events = db_session.query(AuditEvent).filter(
        AuditEvent.matter_id == matter.id
    ).all()
    assert len(events) == 1
    assert events[0].event_type == "matter_created"


def test_audit_event_without_matter(db_session):
    log_audit_event(
        db_session,
        event_type="backup_created",
        metadata={"backup_file": "backup_20261028.enc"},
    )

    events = db_session.query(AuditEvent).filter(
        AuditEvent.event_type == "backup_created"
    ).all()
    assert len(events) == 1
    assert events[0].matter_id is None


def test_audit_filters_sensitive_keys(db_session):
    import json

    log_audit_event(
        db_session,
        event_type="document_imported",
        metadata={
            "filename": "evidence.pdf",
            "password": "should_be_filtered",
            "secret_key": "should_be_filtered",
        },
    )

    events = db_session.query(AuditEvent).filter(
        AuditEvent.event_type == "document_imported"
    ).all()
    assert len(events) == 1

    meta = json.loads(events[0].metadata_json)
    assert meta["filename"] == "evidence.pdf"
    assert "should_be_filtered" not in json.dumps(meta)
