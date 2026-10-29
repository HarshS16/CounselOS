import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def gen_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Matter(Base):
    __tablename__ = "matters"

    id = Column(String(32), primary_key=True, default=gen_id)
    title = Column(String(500), nullable=False)
    reference = Column(String(200), nullable=True)
    jurisdiction = Column(String(200), nullable=True)
    matter_type = Column(String(100), nullable=True)
    status = Column(
        Enum("active", "archived", "deleted", name="matter_status"),
        default="active",
        nullable=False,
    )
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    party_names = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    documents = relationship("Document", back_populates="matter", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="matter", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="matter", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="matter", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="matter", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="matter", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="matter", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(32), primary_key=True, default=gen_id)
    matter_id = Column(String(32), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    original_name = Column(String(500), nullable=False)
    storage_key = Column(String(500), nullable=False)
    sha256 = Column(String(64), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    imported_at = Column(DateTime, default=utcnow, nullable=False)
    processing_status = Column(
        Enum(
            "imported", "queued", "processing", "indexed",
            "partially_processed", "failed", "needs_review",
            name="processing_status",
        ),
        default="imported",
        nullable=False,
    )
    parser_version = Column(String(50), nullable=True)
    ocr_version = Column(String(50), nullable=True)
    page_count = Column(Integer, nullable=True)
    is_scanned = Column(Boolean, default=False)
    extraction_warnings = Column(Text, nullable=True)

    matter = relationship("Matter", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_documents_matter_id", "matter_id"),
        Index("ix_documents_sha256", "sha256"),
    )


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(String(32), primary_key=True, default=gen_id)
    document_id = Column(String(32), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=True)
    extraction_method = Column(
        Enum("digital", "ocr", "mixed", "failed", name="extraction_method"),
        nullable=True,
    )
    quality_indicator = Column(Float, nullable=True)
    processing_status = Column(String(50), default="pending")

    document = relationship("Document", back_populates="pages")

    __table_args__ = (
        UniqueConstraint("document_id", "page_number", name="uq_doc_page"),
        Index("ix_document_pages_document_id", "document_id"),
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String(32), primary_key=True, default=gen_id)
    document_id = Column(String(32), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_start = Column(Integer, nullable=False)
    page_end = Column(Integer, nullable=False)
    paragraph_start = Column(Integer, nullable=True)
    paragraph_end = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    language = Column(String(10), nullable=True)
    embedding_id = Column(Integer, nullable=True)

    document = relationship("Document", back_populates="chunks")
    claim_sources = relationship("ClaimSource", back_populates="chunk")
    event_sources = relationship("EventSource", back_populates="chunk")
    finding_sources = relationship("FindingSource", back_populates="chunk")

    __table_args__ = (
        Index("ix_chunks_document_id", "document_id"),
        Index("ix_chunks_content_hash", "content_hash"),
    )


class Entity(Base):
    __tablename__ = "entities"

    id = Column(String(32), primary_key=True, default=gen_id)
    matter_id = Column(String(32), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(
        Enum("person", "organization", "location", "amount", "date", "other", name="entity_type"),
        nullable=False,
    )
    canonical_label = Column(String(500), nullable=True)
    status = Column(
        Enum("proposed", "accepted", "rejected", "merged", name="entity_status"),
        default="proposed",
    )
    created_at = Column(DateTime, default=utcnow, nullable=False)

    matter = relationship("Matter", back_populates="entities")
    aliases = relationship("EntityAlias", back_populates="entity", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_entities_matter_id", "matter_id"),)


class EntityAlias(Base):
    __tablename__ = "entity_aliases"

    id = Column(String(32), primary_key=True, default=gen_id)
    entity_id = Column(String(32), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    alias_text = Column(String(500), nullable=False)
    source_chunk_id = Column(String(32), ForeignKey("chunks.id", ondelete="SET NULL"), nullable=True)
    review_status = Column(
        Enum("proposed", "accepted", "rejected", name="alias_review_status"),
        default="proposed",
    )

    entity = relationship("Entity", back_populates="aliases")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(32), primary_key=True, default=gen_id)
    matter_id = Column(String(32), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    claim_text = Column(Text, nullable=False)
    claim_type = Column(
        Enum(
            "factual_assertion", "temporal_claim", "financial_claim",
            "attribution", "legal_assertion", "other",
            name="claim_type",
        ),
        nullable=False,
    )
    speaker_entity_id = Column(
        String(32), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True
    )
    date_value = Column(String(50), nullable=True)
    date_precision = Column(
        Enum("exact", "approximate", "range", "inferred", "unknown", name="date_precision"),
        nullable=True,
    )
    review_status = Column(
        Enum(
            "pending", "accepted", "rejected", "needs_evidence",
            "ambiguous", "corrected",
            name="claim_review_status",
        ),
        default="pending",
    )
    analysis_run_id = Column(
        String(32), ForeignKey("analysis_runs.id", ondelete="SET NULL"), nullable=True
    )
    uncertainty_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    matter = relationship("Matter", back_populates="claims")
    sources = relationship("ClaimSource", back_populates="claim", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_claims_matter_id", "matter_id"),)


class ClaimSource(Base):
    __tablename__ = "claim_sources"

    id = Column(String(32), primary_key=True, default=gen_id)
    claim_id = Column(String(32), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(String(32), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False)
    quote_text = Column(Text, nullable=True)
    quote_start = Column(Integer, nullable=True)
    quote_end = Column(Integer, nullable=True)
    evidence_role = Column(
        Enum("supports", "contradicts", "context", "attribution", name="evidence_role"),
        default="supports",
    )

    claim = relationship("Claim", back_populates="sources")
    chunk = relationship("Chunk", back_populates="claim_sources")


class Event(Base):
    __tablename__ = "events"

    id = Column(String(32), primary_key=True, default=gen_id)
    matter_id = Column(String(32), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    event_date = Column(String(50), nullable=True)
    date_precision = Column(
        Enum("exact", "approximate", "range", "inferred", "unknown", name="event_date_precision"),
        nullable=True,
    )
    description = Column(Text, nullable=False)
    review_status = Column(
        Enum(
            "pending", "accepted", "rejected", "needs_evidence",
            "ambiguous", "corrected",
            name="event_review_status",
        ),
        default="pending",
    )
    analysis_run_id = Column(
        String(32), ForeignKey("analysis_runs.id", ondelete="SET NULL"), nullable=True
    )
    sort_key = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    matter = relationship("Matter", back_populates="events")
    sources = relationship("EventSource", back_populates="event", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_events_matter_id", "matter_id"),)


class EventSource(Base):
    __tablename__ = "event_sources"

    id = Column(String(32), primary_key=True, default=gen_id)
    event_id = Column(String(32), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(String(32), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False)
    support_type = Column(
        Enum("direct", "inferred", "corroborating", name="support_type"),
        default="direct",
    )

    event = relationship("Event", back_populates="sources")
    chunk = relationship("Chunk", back_populates="event_sources")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(32), primary_key=True, default=gen_id)
    matter_id = Column(String(32), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    analysis_run_id = Column(
        String(32), ForeignKey("analysis_runs.id", ondelete="SET NULL"), nullable=True
    )
    finding_type = Column(
        Enum(
            "contradiction", "date_discrepancy", "amount_discrepancy",
            "attribution_difference", "omission", "ambiguity",
            "corroboration", "other",
            name="finding_type",
        ),
        nullable=False,
    )
    summary = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    claim_a_id = Column(String(32), ForeignKey("claims.id", ondelete="SET NULL"), nullable=True)
    claim_b_id = Column(String(32), ForeignKey("claims.id", ondelete="SET NULL"), nullable=True)
    review_status = Column(
        Enum(
            "pending", "accepted", "rejected", "needs_evidence",
            "ambiguous", "corrected", "irrelevant",
            name="finding_review_status",
        ),
        default="pending",
    )
    reviewer_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    matter = relationship("Matter", back_populates="findings")
    sources = relationship("FindingSource", back_populates="finding", cascade="all, delete-orphan")
    review_events = relationship("ReviewEvent", back_populates="finding", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_findings_matter_id", "matter_id"),)


class FindingSource(Base):
    __tablename__ = "finding_sources"

    id = Column(String(32), primary_key=True, default=gen_id)
    finding_id = Column(String(32), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(String(32), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(
        Enum("claim_a_source", "claim_b_source", "context", name="finding_source_type"),
        nullable=False,
    )

    finding = relationship("Finding", back_populates="sources")
    chunk = relationship("Chunk", back_populates="finding_sources")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(32), primary_key=True, default=gen_id)
    matter_id = Column(String(32), ForeignKey("matters.id", ondelete="CASCADE"), nullable=False)
    workflow_type = Column(String(100), nullable=False)
    workflow_version = Column(String(50), nullable=False)
    model_manifest_id = Column(String(100), nullable=True)
    prompt_version = Column(String(50), nullable=True)
    retrieval_config = Column(Text, nullable=True)
    status = Column(
        Enum("running", "completed", "failed", "cancelled", name="analysis_status"),
        default="running",
    )
    started_at = Column(DateTime, default=utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    document_ids = Column(Text, nullable=True)

    matter = relationship("Matter", back_populates="analysis_runs")

    __table_args__ = (Index("ix_analysis_runs_matter_id", "matter_id"),)


class ReviewEvent(Base):
    __tablename__ = "review_events"

    id = Column(String(32), primary_key=True, default=gen_id)
    finding_id = Column(String(32), ForeignKey("findings.id", ondelete="CASCADE"), nullable=True)
    claim_id = Column(String(32), ForeignKey("claims.id", ondelete="CASCADE"), nullable=True)
    event_id = Column(String(32), ForeignKey("events.id", ondelete="CASCADE"), nullable=True)
    action = Column(String(50), nullable=False)
    previous_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utcnow, nullable=False)

    finding = relationship("Finding", back_populates="review_events")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(32), primary_key=True, default=gen_id)
    event_type = Column(String(100), nullable=False)
    matter_id = Column(String(32), ForeignKey("matters.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=utcnow, nullable=False)
    metadata_json = Column(Text, nullable=True)

    matter = relationship("Matter", back_populates="audit_events")

    __table_args__ = (Index("ix_audit_events_matter_id", "matter_id"),)
