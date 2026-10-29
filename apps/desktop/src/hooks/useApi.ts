import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
} from "@tanstack/react-query";
import * as api from "@/lib/api";
import type {
  Matter,
  MatterCreate,
  MatterUpdate,
  Document,
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
  ModelStatus,
  HealthResponse,
} from "@/types";

// --- Matters ---

export function useMatters(): UseQueryResult<Matter[]> {
  return useQuery({
    queryKey: ["matters"],
    queryFn: api.listMatters,
  });
}

export function useMatter(id: string | undefined): UseQueryResult<Matter> {
  return useQuery({
    queryKey: ["matters", id],
    queryFn: () => api.getMatter(id!),
    enabled: !!id,
  });
}

export function useCreateMatter() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: MatterCreate) => api.createMatter(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["matters"] }),
  });
}

export function useUpdateMatter(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: MatterUpdate) => api.updateMatter(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["matters"] });
      qc.invalidateQueries({ queryKey: ["matters", id] });
    },
  });
}

export function useArchiveMatter() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.archiveMatter(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["matters"] }),
  });
}

export function useDeleteMatter() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteMatter(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["matters"] }),
  });
}

// --- Documents ---

export function useDocuments(
  matterId: string | undefined
): UseQueryResult<Document[]> {
  return useQuery({
    queryKey: ["documents", matterId],
    queryFn: () => api.listDocuments(matterId!),
    enabled: !!matterId,
  });
}

export function useDocument(
  matterId: string | undefined,
  docId: string | undefined
): UseQueryResult<Document> {
  return useQuery({
    queryKey: ["documents", matterId, docId],
    queryFn: () => api.getDocument(matterId!, docId!),
    enabled: !!matterId && !!docId,
  });
}

export function useDocumentPages(
  matterId: string | undefined,
  docId: string | undefined
): UseQueryResult<DocumentPage[]> {
  return useQuery({
    queryKey: ["documentPages", matterId, docId],
    queryFn: () => api.getDocumentPages(matterId!, docId!),
    enabled: !!matterId && !!docId,
  });
}

export function useUploadDocument(matterId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => api.uploadDocument(matterId, file),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["documents", matterId] });
      qc.invalidateQueries({ queryKey: ["matters", matterId] });
    },
  });
}

export function useDeleteDocument(matterId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (docId: string) => api.deleteDocument(matterId, docId),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["documents", matterId] }),
  });
}

// --- Search & QA ---

export function useSearch(matterId: string | undefined, query: string) {
  return useQuery<SearchResponse>({
    queryKey: ["search", matterId, query],
    queryFn: () => api.searchDocuments(matterId!, query),
    enabled: !!matterId && query.length > 0,
  });
}

export function useAsk(matterId: string) {
  return useMutation<QAResponse, Error, string>({
    mutationFn: (question: string) => api.askQuestion(matterId, question),
  });
}

// --- Claims & Entities ---

export function useClaims(
  matterId: string | undefined
): UseQueryResult<Claim[]> {
  return useQuery({
    queryKey: ["claims", matterId],
    queryFn: () => api.getClaims(matterId!),
    enabled: !!matterId,
  });
}

export function useExtractClaims(matterId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (documentIds?: string[]) =>
      api.extractClaims(matterId, documentIds),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", matterId] });
      qc.invalidateQueries({ queryKey: ["entities", matterId] });
    },
  });
}

export function useUpdateClaim(matterId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      claimId,
      data,
    }: {
      claimId: string;
      data: { review_status: string; note?: string };
    }) => api.updateClaim(matterId, claimId, data),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["claims", matterId] }),
  });
}

export function useEntities(
  matterId: string | undefined
): UseQueryResult<Entity[]> {
  return useQuery({
    queryKey: ["entities", matterId],
    queryFn: () => api.getEntities(matterId!),
    enabled: !!matterId,
  });
}

// --- Chronology ---

export function useChronology(
  matterId: string | undefined
): UseQueryResult<ChronologyResponse> {
  return useQuery({
    queryKey: ["chronology", matterId],
    queryFn: () => api.getChronology(matterId!),
    enabled: !!matterId,
  });
}

export function useBuildChronology(matterId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (claimIds?: string[]) =>
      api.buildChronology(matterId, claimIds),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["chronology", matterId] }),
  });
}

export function useUpdateEvent(matterId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      eventId,
      data,
    }: {
      eventId: string;
      data: {
        review_status: string;
        description?: string;
        event_date?: string;
      };
    }) => api.updateEvent(matterId, eventId, data),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["chronology", matterId] }),
  });
}

// --- Comparison ---

export function useCompareDocuments(matterId: string) {
  const qc = useQueryClient();
  return useMutation<
    ComparisonResponse,
    Error,
    { documentAId: string; documentBId: string }
  >({
    mutationFn: ({ documentAId, documentBId }) =>
      api.compareDocuments(matterId, documentAId, documentBId),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["findings", matterId] }),
  });
}

// --- Findings ---

export function useFindings(
  matterId: string | undefined,
  status?: string
): UseQueryResult<Finding[]> {
  return useQuery({
    queryKey: ["findings", matterId, status],
    queryFn: () => api.listFindings(matterId!, status),
    enabled: !!matterId,
  });
}

export function useFinding(
  matterId: string | undefined,
  findingId: string | undefined
): UseQueryResult<Finding> {
  return useQuery({
    queryKey: ["findings", matterId, findingId],
    queryFn: () => api.getFinding(matterId!, findingId!),
    enabled: !!matterId && !!findingId,
  });
}

export function useReviewFinding(matterId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      findingId,
      data,
    }: {
      findingId: string;
      data: FindingReviewRequest;
    }) => api.reviewFinding(matterId, findingId, data),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["findings", matterId] }),
  });
}

export function useFindingHistory(
  matterId: string | undefined,
  findingId: string | undefined
) {
  return useQuery({
    queryKey: ["findingHistory", matterId, findingId],
    queryFn: () => api.getFindingHistory(matterId!, findingId!),
    enabled: !!matterId && !!findingId,
  });
}

// --- Export ---

export function useCreateExport(matterId: string) {
  const qc = useQueryClient();
  return useMutation<ExportResponse, Error, ExportRequest | undefined>({
    mutationFn: (options) => api.createExport(matterId, options),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["exports", matterId] }),
  });
}

export function useExports(
  matterId: string | undefined
): UseQueryResult<ExportResponse[]> {
  return useQuery({
    queryKey: ["exports", matterId],
    queryFn: () => api.listExports(matterId!),
    enabled: !!matterId,
  });
}

// --- System ---

export function useHealth(): UseQueryResult<HealthResponse> {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.getHealth,
    refetchInterval: 30_000,
  });
}

export function useModelStatus(): UseQueryResult<ModelStatus> {
  return useQuery({
    queryKey: ["modelStatus"],
    queryFn: api.getModelStatus,
  });
}
