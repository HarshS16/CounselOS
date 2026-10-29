import { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Upload,
  FileText,
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  Eye,
  Trash2,
  RotateCw,
} from "lucide-react";
import { useDocuments, useUploadDocument, useDeleteDocument } from "@/hooks/useApi";
import { clsx } from "clsx";
import { format } from "date-fns";
import type { Document } from "@/types";

const statusConfig: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  indexed: { icon: CheckCircle2, color: "var(--color-success)", label: "Indexed" },
  imported: { icon: Clock, color: "var(--color-text-muted)", label: "Imported" },
  queued: { icon: Clock, color: "var(--color-info)", label: "Queued" },
  processing: { icon: Loader2, color: "var(--color-warning)", label: "Processing" },
  partially_processed: { icon: AlertCircle, color: "var(--color-warning)", label: "Partial" },
  failed: { icon: AlertCircle, color: "var(--color-danger)", label: "Failed" },
  needs_review: { icon: Eye, color: "var(--color-warning)", label: "Needs Review" },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = statusConfig[status] || statusConfig.imported;
  const Icon = cfg.icon;
  return (
    <span className="flex items-center gap-1.5 text-xs" style={{ color: cfg.color }}>
      <Icon size={12} className={status === "processing" ? "animate-spin" : ""} />
      {cfg.label}
    </span>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentList() {
  const { matterId } = useParams();
  const { data: documents, isLoading, refetch } = useDocuments(matterId);
  const upload = useUploadDocument(matterId!);
  const deleteDoc = useDeleteDocument(matterId!);
  const [dragOver, setDragOver] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);

  const handleFiles = useCallback(
    async (files: FileList) => {
      for (const file of Array.from(files)) {
        await upload.mutateAsync(file);
      }
    },
    [upload]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">Documents</h1>
        <label className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-accent)] text-white text-sm font-medium hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer">
          <Upload size={16} />
          Upload Files
          <input
            type="file"
            multiple
            accept=".pdf,.docx"
            className="hidden"
            onChange={(e) => e.target.files && handleFiles(e.target.files)}
          />
        </label>
      </div>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={clsx(
          "border-2 border-dashed rounded-xl p-8 mb-6 text-center transition-colors",
          dragOver
            ? "border-[var(--color-accent)] bg-[color-mix(in_srgb,var(--color-accent)_5%,transparent)]"
            : "border-[var(--color-border-primary)] hover:border-[var(--color-border-secondary)]"
        )}
      >
        <Upload size={24} className="mx-auto mb-2 text-[var(--color-text-muted)]" />
        <p className="text-sm text-[var(--color-text-muted)]">
          Drag and drop PDF or DOCX files here
        </p>
      </div>

      {upload.isPending && (
        <div className="flex items-center gap-2 mb-4 p-3 rounded-lg bg-[var(--color-bg-tertiary)]">
          <Loader2 size={16} className="animate-spin text-[var(--color-accent)]" />
          <span className="text-sm">Uploading and processing...</span>
        </div>
      )}

      {isLoading ? (
        <div className="text-center text-[var(--color-text-muted)] py-8">Loading documents...</div>
      ) : !documents?.length ? (
        <div className="text-center py-12">
          <FileText size={40} className="mx-auto mb-3 text-[var(--color-text-muted)] opacity-50" />
          <p className="text-sm text-[var(--color-text-muted)]">
            No documents yet. Upload PDF or DOCX files to begin analysis.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className={clsx(
                "flex items-center gap-4 p-4 rounded-xl border transition-colors cursor-pointer",
                selectedDoc?.id === doc.id
                  ? "bg-[var(--color-bg-elevated)] border-[var(--color-accent)]"
                  : "bg-[var(--color-bg-secondary)] border-[var(--color-border-primary)] hover:border-[var(--color-border-secondary)]"
              )}
              onClick={() => setSelectedDoc(selectedDoc?.id === doc.id ? null : doc)}
            >
              <FileText size={20} className="text-[var(--color-accent)] flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium truncate">{doc.original_name}</h3>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-xs text-[var(--color-text-muted)]">
                    {formatSize(doc.size_bytes)}
                  </span>
                  <span className="text-xs text-[var(--color-text-muted)]">
                    {doc.page_count ? `${doc.page_count} pages` : ""}
                  </span>
                  {doc.is_scanned && (
                    <span className="text-xs text-[var(--color-warning)]">Scanned/OCR</span>
                  )}
                  <span className="text-xs text-[var(--color-text-muted)]">
                    {format(new Date(doc.imported_at), "dd MMM yyyy HH:mm")}
                  </span>
                </div>
              </div>
              <StatusBadge status={doc.processing_status} />
            </div>
          ))}
        </div>
      )}

      {selectedDoc && (
        <div className="mt-4 p-4 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
          <h3 className="text-sm font-semibold mb-3">{selectedDoc.original_name}</h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div><span className="text-[var(--color-text-muted)]">SHA-256:</span> <span className="font-mono">{selectedDoc.sha256.substring(0, 16)}...</span></div>
            <div><span className="text-[var(--color-text-muted)]">MIME:</span> {selectedDoc.mime_type}</div>
            <div><span className="text-[var(--color-text-muted)]">Parser:</span> {selectedDoc.parser_version || "N/A"}</div>
            <div><span className="text-[var(--color-text-muted)]">OCR:</span> {selectedDoc.ocr_version || "N/A"}</div>
          </div>
          {selectedDoc.extraction_warnings && (
            <div className="mt-3 p-2 rounded bg-[color-mix(in_srgb,var(--color-warning)_10%,transparent)] text-xs text-[var(--color-warning)]">
              {selectedDoc.extraction_warnings}
            </div>
          )}
          <div className="flex gap-2 mt-3">
            <button
              onClick={() => refetch()}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--color-bg-tertiary)] text-xs hover:bg-[var(--color-bg-hover)] transition-colors"
            >
              <RotateCw size={12} /> Reprocess
            </button>
            <button
              onClick={async () => {
                if (confirm("Delete this document and all associated data?")) {
                  await deleteDoc.mutateAsync(selectedDoc.id);
                  setSelectedDoc(null);
                }
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-[var(--color-danger)] hover:bg-[color-mix(in_srgb,var(--color-danger)_10%,transparent)] transition-colors"
            >
              <Trash2 size={12} /> Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
