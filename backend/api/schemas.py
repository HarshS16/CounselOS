from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Matter ───────────────────────────────────────────────────────────────

class MatterCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    reference: Optional[str] = Field(None, max_length=200)
    jurisdiction: Optional[str] = Field(None, max_length=200)
    matter_type: Optional[str] = Field(None, max_length=100)
    party_names: Optional[str] = None
    notes: Optional[str] = None


class MatterUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    reference: Optional[str] = Field(None, max_length=200)
    jurisdiction: Optional[str] = Field(None, max_length=200)
    matter_type: Optional[str] = Field(None, max_length=100)
    party_names: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class MatterResponse(BaseModel):
    id: str
    title: str
    reference: Optional[str] = None
    jurisdiction: Optional[str] = None
    matter_type: Optional[str] = None
    status: str
    party_names: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    finding_count: int = 0
    pending_review_count: int = 0

    model_config = {"from_attributes": True}


class MatterListResponse(BaseModel):
    matters: list[MatterResponse]
    total: int


# ── Document ─────────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    id: str
    matter_id: str
    original_name: str
    sha256: str
    mime_type: str
    size_bytes: int
    imported_at: datetime
    processing_status: str
    parser_version: Optional[str] = None
    ocr_version: Optional[str] = None
    page_count: Optional[int] = None
    is_scanned: bool = False
    extraction_warnings: Optional[str] = None

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: str
    original_name: str
    sha256: str
    processing_status: str
    duplicate_of: Optional[str] = None
    message: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


# ── Page ─────────────────────────────────────────────────────────────────

class PageResponse(BaseModel):
    id: str
    document_id: str
    page_number: int
    extracted_text: Optional[str] = None
    extraction_method: Optional[str] = None
    quality_indicator: Optional[float] = None
    processing_status: str = "pending"

    model_config = {"from_attributes": True}


# ── Chunk ────────────────────────────────────────────────────────────────

class ChunkResponse(BaseModel):
    id: str
    document_id: str
    page_start: int
    page_end: int
    paragraph_start: Optional[int] = None
    paragraph_end: Optional[int] = None
    text: str
    chunk_index: int
    language: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Search ───────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    matter_id: str
    query: str = Field(..., min_length=1, max_length=2000)
    mode: str = Field("hybrid", pattern=r"^(keyword|semantic|hybrid)$")
    max_results: int = Field(10, ge=1, le=50)
    document_ids: Optional[list[str]] = None


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_start: int
    page_end: int
    text: str
    score: float
    highlight: Optional[str] = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str
    mode: str
    total_results: int


# ── Question Answering ───────────────────────────────────────────────────

class Citation(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_start: int
    page_end: int
    quote: str
    is_valid: bool = True


class QARequest(BaseModel):
    matter_id: str
    question: str = Field(..., min_length=1, max_length=5000)
    max_sources: int = Field(10, ge=1, le=25)
    document_ids: Optional[list[str]] = None


class QAResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: Optional[str] = None
    abstained: bool = False
    conflicts_detected: bool = False
    conflict_explanation: Optional[str] = None
    model_version: Optional[str] = None
    analysis_run_id: Optional[str] = None


# ── Claims ───────────────────────────────────────────────────────────────

class ClaimCreate(BaseModel):
    matter_id: str
    claim_text: str
    claim_type: str
    speaker_entity_id: Optional[str] = None
    date_value: Optional[str] = None
    date_precision: Optional[str] = None
    uncertainty_note: Optional[str] = None
    source_chunk_ids: list[str] = []


class ClaimSourceResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_start: int
    page_end: int
    quote_text: Optional[str] = None
    evidence_role: str = "supports"

    model_config = {"from_attributes": True}


class ClaimResponse(BaseModel):
    id: str
    matter_id: str
    claim_text: str
    claim_type: str
    speaker_entity_id: Optional[str] = None
    date_value: Optional[str] = None
    date_precision: Optional[str] = None
    review_status: str
    uncertainty_note: Optional[str] = None
    analysis_run_id: Optional[str] = None
    created_at: datetime
    sources: list[ClaimSourceResponse] = []

    model_config = {"from_attributes": True}


# ── Entities ─────────────────────────────────────────────────────────────

class EntityAliasResponse(BaseModel):
    id: str
    alias_text: str
    source_chunk_id: Optional[str] = None
    review_status: str = "proposed"

    model_config = {"from_attributes": True}


class EntityResponse(BaseModel):
    id: str
    matter_id: str
    entity_type: str
    canonical_label: Optional[str] = None
    status: str
    created_at: datetime
    aliases: list[EntityAliasResponse] = []

    model_config = {"from_attributes": True}


# ── Events / Chronology ─────────────────────────────────────────────────

class EventSourceResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_start: int
    page_end: int
    support_type: str = "direct"

    model_config = {"from_attributes": True}


class EventCreate(BaseModel):
    matter_id: str
    event_date: Optional[str] = None
    date_precision: Optional[str] = None
    description: str
    source_chunk_ids: list[str] = []


class EventResponse(BaseModel):
    id: str
    matter_id: str
    event_date: Optional[str] = None
    date_precision: Optional[str] = None
    description: str
    review_status: str
    analysis_run_id: Optional[str] = None
    sort_key: Optional[str] = None
    created_at: datetime
    sources: list[EventSourceResponse] = []

    model_config = {"from_attributes": True}


class ChronologyResponse(BaseModel):
    matter_id: str
    events: list[EventResponse]
    total_events: int
    ambiguous_date_count: int
    analysis_run_id: Optional[str] = None


# ── Findings ─────────────────────────────────────────────────────────────

class FindingSourceResponse(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_start: int
    page_end: int
    text: str
    relationship_type: str

    model_config = {"from_attributes": True}


class FindingResponse(BaseModel):
    id: str
    matter_id: str
    analysis_run_id: Optional[str] = None
    finding_type: str
    summary: str
    explanation: Optional[str] = None
    claim_a_id: Optional[str] = None
    claim_b_id: Optional[str] = None
    review_status: str
    reviewer_note: Optional[str] = None
    created_at: datetime
    sources: list[FindingSourceResponse] = []

    model_config = {"from_attributes": True}


class FindingReviewRequest(BaseModel):
    review_status: str = Field(
        ...,
        pattern=r"^(accepted|rejected|needs_evidence|ambiguous|corrected|irrelevant)$",
    )
    reviewer_note: Optional[str] = None


# ── Comparison / Discrepancy ─────────────────────────────────────────────

class DiscrepancyResult(BaseModel):
    finding_type: str
    summary: str
    explanation: Optional[str] = None
    claim_a: Optional[ClaimResponse] = None
    claim_b: Optional[ClaimResponse] = None
    uncertainty: Optional[str] = None
    review_status: str = "pending"


class ComparisonRequest(BaseModel):
    matter_id: str
    document_ids: list[str] = Field(..., min_length=2)
    claim_ids: Optional[list[str]] = None
    focus_areas: Optional[list[str]] = None


class ComparisonResponse(BaseModel):
    matter_id: str
    discrepancies: list[DiscrepancyResult]
    total_claims_compared: int
    analysis_run_id: Optional[str] = None


# ── Analysis Run ─────────────────────────────────────────────────────────

class AnalysisRunResponse(BaseModel):
    id: str
    matter_id: str
    workflow_type: str
    workflow_version: str
    model_manifest_id: Optional[str] = None
    prompt_version: Optional[str] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Review Events ────────────────────────────────────────────────────────

class ReviewEventResponse(BaseModel):
    id: str
    finding_id: Optional[str] = None
    claim_id: Optional[str] = None
    event_id: Optional[str] = None
    action: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


# ── Audit ────────────────────────────────────────────────────────────────

class AuditEventResponse(BaseModel):
    id: str
    event_type: str
    matter_id: Optional[str] = None
    timestamp: datetime
    metadata_json: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Export ───────────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    matter_id: str
    format: str = Field("docx", pattern=r"^(docx|pdf)$")
    include_findings: bool = True
    include_chronology: bool = True
    include_sources: bool = True
    finding_statuses: Optional[list[str]] = None


class ExportResponse(BaseModel):
    file_path: str
    file_name: str
    format: str
    matter_id: str
    export_timestamp: datetime
    finding_count: int
    event_count: int


# ── System ───────────────────────────────────────────────────────────────

class ModelStatusResponse(BaseModel):
    llm_loaded: bool
    llm_model_name: Optional[str] = None
    embedding_loaded: bool
    embedding_model_name: Optional[str] = None
    llm_context_length: Optional[int] = None
    memory_usage_mb: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    db_connected: bool
    llm_available: bool
    embedding_available: bool
    data_dir: str
    uptime_seconds: float
