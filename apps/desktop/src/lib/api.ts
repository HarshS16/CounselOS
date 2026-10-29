import type {
  Matter,
  MatterCreate,
  MatterUpdate,
  MatterListResponse,
  Document,
  DocumentListResponse,
  DocumentUploadResponse,
  DocumentPage,
  SearchResponse,
  QAResponse,
  Claim,
  Entity,
  TimelineEvent,
  ChronologyResponse,
  Finding,
  FindingReviewRequest,
  ComparisonResponse,
  ExportRequest,
  ExportResponse,
  ReviewEvent,
  AuditEvent,
  ModelStatus,
  HealthResponse,
} from "@/types";

const BASE_URL = "http://127.0.0.1:8741";

let sessionToken = "";

export function setSessionToken(token: string) {
  sessionToken = token;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (sessionToken) {
    headers["Authorization"] = `Bearer ${sessionToken}`;
  }

  if (
    !(options.body instanceof FormData) &&
    !headers["Content-Type"]
  ) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body = await res.text();
    let message: string;
    try {
      const parsed = JSON.parse(body);
      message = parsed.detail || parsed.message || body;
    } catch {
      message = body;
    }
    throw new Error(`${res.status}: ${message}`);
  }

  if (res.status === 204) return undefined as T;

  const contentType = res.headers.get("Content-Type") || "";
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res.blob() as unknown as T;
}

// --- Matters ---

export async function listMatters(): Promise<Matter[]> {
  const resp = await request<MatterListResponse>("/api/matters/");
  return resp.matters;
}

export async function getMatter(id: string): Promise<Matter> {
  return request<Matter>(`/api/matters/${id}`);
}

export async function createMatter(data: MatterCreate): Promise<Matter> {
  return request<Matter>("/api/matters/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateMatter(
  id: string,
  data: MatterUpdate
): Promise<Matter> {
  return request<Matter>(`/api/matters/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function archiveMatter(id: string): Promise<Matter> {
  return request<Matter>(`/api/matters/${id}/archive`, { method: "POST" });
}

export async function deleteMatter(id: string): Promise<void> {
  return request<void>(`/api/matters/${id}`, { method: "DELETE" });
}

// --- Documents ---

export async function listDocuments(matterId: string): Promise<Document[]> {
  const resp = await request<DocumentListResponse>(
    `/api/matters/${matterId}/documents/`
  );
  return resp.documents;
}

export async function getDocument(
  matterId: string,
  docId: string
): Promise<Document> {
  return request<Document>(`/api/matters/${matterId}/documents/${docId}`);
}

export async function uploadDocument(
  matterId: string,
  file: File
): Promise<DocumentUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<DocumentUploadResponse>(
    `/api/matters/${matterId}/documents/`,
    {
      method: "POST",
      body: form,
    }
  );
}

export async function getDocumentPages(
  matterId: string,
  docId: string
): Promise<DocumentPage[]> {
  return request<DocumentPage[]>(
    `/api/matters/${matterId}/documents/${docId}/pages`
  );
}

export async function getOriginalDocument(
  matterId: string,
  docId: string
): Promise<Blob> {
  return request<Blob>(
    `/api/matters/${matterId}/documents/${docId}/original`
  );
}

export async function reprocessDocument(
  matterId: string,
  docId: string
): Promise<Document> {
  return request<Document>(
    `/api/matters/${matterId}/documents/${docId}/reprocess`,
    { method: "POST" }
  );
}

export async function deleteDocument(
  matterId: string,
  docId: string
): Promise<void> {
  return request<void>(`/api/matters/${matterId}/documents/${docId}`, {
    method: "DELETE",
  });
}

// --- Search & QA ---

export async function searchDocuments(
  matterId: string,
  query: string,
  limit: number = 10
): Promise<SearchResponse> {
  return request<SearchResponse>(
    `/api/matters/${matterId}/search`,
    {
      method: "POST",
      body: JSON.stringify({ matter_id: matterId, query, max_results: limit }),
    }
  );
}

export async function askQuestion(
  matterId: string,
  question: string
): Promise<QAResponse> {
  return request<QAResponse>(`/api/matters/${matterId}/ask`, {
    method: "POST",
    body: JSON.stringify({ matter_id: matterId, question }),
  });
}

// --- Analysis ---

export async function extractClaims(
  matterId: string,
  documentIds?: string[]
): Promise<{ claims_count: number; entities_count: number; analysis_run_id: string }> {
  return request(`/api/matters/${matterId}/extract`, {
    method: "POST",
    body: JSON.stringify({ document_ids: documentIds }),
  });
}

export async function getClaims(matterId: string): Promise<Claim[]> {
  return request<Claim[]>(`/api/matters/${matterId}/claims`);
}

export async function updateClaim(
  matterId: string,
  claimId: string,
  data: { review_status: string; note?: string }
): Promise<Claim> {
  return request<Claim>(`/api/matters/${matterId}/claims/${claimId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getEntities(matterId: string): Promise<Entity[]> {
  return request<Entity[]>(`/api/matters/${matterId}/entities`);
}

export async function buildChronology(
  matterId: string,
  claimIds?: string[]
): Promise<ChronologyResponse> {
  return request<ChronologyResponse>(`/api/matters/${matterId}/chronology`, {
    method: "POST",
    body: JSON.stringify({ claim_ids: claimIds }),
  });
}

export async function getChronology(
  matterId: string
): Promise<ChronologyResponse> {
  return request<ChronologyResponse>(`/api/matters/${matterId}/chronology`);
}

export async function updateEvent(
  matterId: string,
  eventId: string,
  data: { review_status: string; description?: string; event_date?: string }
): Promise<TimelineEvent> {
  return request<TimelineEvent>(
    `/api/matters/${matterId}/events/${eventId}`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    }
  );
}

export async function compareDocuments(
  matterId: string,
  documentAId: string,
  documentBId: string
): Promise<ComparisonResponse> {
  return request<ComparisonResponse>(`/api/matters/${matterId}/compare`, {
    method: "POST",
    body: JSON.stringify({
      matter_id: matterId,
      document_ids: [documentAId, documentBId],
    }),
  });
}

// --- Findings ---

export async function listFindings(
  matterId: string,
  status?: string
): Promise<Finding[]> {
  const params = status ? `?status=${status}` : "";
  return request<Finding[]>(`/api/matters/${matterId}/findings/${params}`);
}

export async function getFinding(
  matterId: string,
  findingId: string
): Promise<Finding> {
  return request<Finding>(
    `/api/matters/${matterId}/findings/${findingId}`
  );
}

export async function reviewFinding(
  matterId: string,
  findingId: string,
  data: FindingReviewRequest
): Promise<Finding> {
  return request<Finding>(
    `/api/matters/${matterId}/findings/${findingId}/review`,
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}

export async function getFindingHistory(
  matterId: string,
  findingId: string
): Promise<ReviewEvent[]> {
  return request<ReviewEvent[]>(
    `/api/matters/${matterId}/findings/${findingId}/history`
  );
}

// --- Export ---

export async function createExport(
  matterId: string,
  options?: ExportRequest
): Promise<ExportResponse> {
  return request<ExportResponse>(`/api/matters/${matterId}/exports/`, {
    method: "POST",
    body: JSON.stringify({ matter_id: matterId, ...options }),
  });
}

export async function listExports(matterId: string): Promise<ExportResponse[]> {
  return request<ExportResponse[]>(`/api/matters/${matterId}/exports/`);
}

export async function downloadExport(
  matterId: string,
  filename: string
): Promise<Blob> {
  return request<Blob>(
    `/api/matters/${matterId}/exports/${encodeURIComponent(filename)}`
  );
}

// --- System ---

export async function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/system/health");
}

export async function getModelStatus(): Promise<ModelStatus> {
  return request<ModelStatus>("/api/system/model-status");
}

export async function getAuditLog(
  matterId?: string,
  limit: number = 50
): Promise<AuditEvent[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (matterId) params.set("matter_id", matterId);
  return request<AuditEvent[]>(`/api/system/audit-log?${params}`);
}
