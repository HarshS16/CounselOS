export interface Matter {
  id: string;
  title: string;
  reference: string | null;
  jurisdiction: string | null;
  matter_type: string | null;
  status: "active" | "archived" | "deleted";
  party_names: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  document_count: number;
  finding_count: number;
  pending_review_count: number;
}

export interface MatterCreate {
  title: string;
  reference?: string;
  jurisdiction?: string;
  matter_type?: string;
  party_names?: string;
  notes?: string;
}

export interface MatterUpdate {
  title?: string;
  reference?: string;
  jurisdiction?: string;
  matter_type?: string;
  party_names?: string;
  notes?: string;
  status?: string;
}

export interface MatterListResponse {
  matters: Matter[];
  total: number;
}

export interface Document {
  id: string;
  matter_id: string;
  original_name: string;
  sha256: string;
  mime_type: string;
  size_bytes: number;
  imported_at: string;
  processing_status:
    | "imported"
    | "queued"
    | "processing"
    | "indexed"
    | "partially_processed"
    | "failed"
    | "needs_review";
  parser_version: string | null;
  ocr_version: string | null;
  page_count: number | null;
  is_scanned: boolean;
  extraction_warnings: string | null;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface DocumentUploadResponse {
  id: string;
  original_name: string;
  sha256: string;
  processing_status: string;
  duplicate_of: string | null;
  message: string;
}

export interface DocumentPage {
  id: string;
  document_id: string;
  page_number: number;
  extracted_text: string | null;
  extraction_method: string | null;
  quality_indicator: number | null;
  processing_status: string;
}

export interface Chunk {
  id: string;
  document_id: string;
  page_start: number;
  page_end: number;
  paragraph_start: number | null;
  paragraph_end: number | null;
  text: string;
  chunk_index: number;
  language: string | null;
}

export interface SearchResult {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_start: number;
  page_end: number;
  text: string;
  score: number;
  highlight: string | null;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  mode: string;
  total_results: number;
}

export interface Citation {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_start: number;
  page_end: number;
  quote: string;
  is_valid: boolean;
}

export interface QAResponse {
  answer: string;
  citations: Citation[];
  confidence: string | null;
  abstained: boolean;
  conflicts_detected: boolean;
  conflict_explanation: string | null;
  model_version: string | null;
  analysis_run_id: string | null;
}

export interface ClaimSource {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_start: number;
  page_end: number;
  quote_text: string | null;
  evidence_role: string;
}

export interface Claim {
  id: string;
  matter_id: string;
  claim_text: string;
  claim_type: string;
  speaker_entity_id: string | null;
  date_value: string | null;
  date_precision: string | null;
  review_status: string;
  uncertainty_note: string | null;
  analysis_run_id: string | null;
  created_at: string;
  sources: ClaimSource[];
}

export interface EntityAlias {
  id: string;
  alias_text: string;
  source_chunk_id: string | null;
  review_status: string;
}

export interface Entity {
  id: string;
  matter_id: string;
  entity_type: string;
  canonical_label: string | null;
  status: string;
  created_at: string;
  aliases: EntityAlias[];
}

export interface EventSource {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_start: number;
  page_end: number;
  support_type: string;
}

export interface TimelineEvent {
  id: string;
  matter_id: string;
  event_date: string | null;
  date_precision: string | null;
  description: string;
  review_status: string;
  analysis_run_id: string | null;
  sort_key: string | null;
  created_at: string;
  sources: EventSource[];
}

export interface ChronologyResponse {
  matter_id: string;
  events: TimelineEvent[];
  total_events: number;
  ambiguous_date_count: number;
  analysis_run_id: string | null;
}

export interface FindingSource {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_start: number;
  page_end: number;
  text: string;
  relationship_type: string;
}

export interface Finding {
  id: string;
  matter_id: string;
  analysis_run_id: string | null;
  finding_type: string;
  summary: string;
  explanation: string | null;
  claim_a_id: string | null;
  claim_b_id: string | null;
  review_status: string;
  reviewer_note: string | null;
  created_at: string;
  sources: FindingSource[];
}

export interface FindingReviewRequest {
  review_status: string;
  reviewer_note?: string;
}

export interface DiscrepancyResult {
  finding_type: string;
  summary: string;
  explanation: string | null;
  claim_a: Claim | null;
  claim_b: Claim | null;
  uncertainty: string | null;
  review_status: string;
}

export interface ComparisonResponse {
  matter_id: string;
  discrepancies: DiscrepancyResult[];
  total_claims_compared: number;
  analysis_run_id: string | null;
}

export interface AnalysisRun {
  id: string;
  matter_id: string;
  workflow_type: string;
  workflow_version: string;
  model_manifest_id: string | null;
  prompt_version: string | null;
  status: string;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface ReviewEvent {
  id: string;
  finding_id: string | null;
  claim_id: string | null;
  event_id: string | null;
  action: string;
  previous_value: string | null;
  new_value: string | null;
  timestamp: string;
}

export interface AuditEvent {
  id: string;
  event_type: string;
  matter_id: string | null;
  timestamp: string;
  metadata_json: string | null;
}

export interface ExportRequest {
  format?: string;
  include_findings?: boolean;
  include_chronology?: boolean;
  include_sources?: boolean;
  finding_statuses?: string[];
}

export interface ExportResponse {
  file_path: string;
  file_name: string;
  format: string;
  matter_id: string;
  export_timestamp: string;
  finding_count: number;
  event_count: number;
}

export interface ModelStatus {
  llm_loaded: boolean;
  llm_model_name: string | null;
  embedding_loaded: boolean;
  embedding_model_name: string | null;
  llm_context_length: number | null;
  memory_usage_mb: number | null;
}

export interface HealthResponse {
  status: string;
  version: string;
  db_connected: boolean;
  llm_available: boolean;
  embedding_available: boolean;
  data_dir: string;
  uptime_seconds: number;
}
