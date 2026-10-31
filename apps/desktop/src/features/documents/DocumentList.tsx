import { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import { useDocuments, useUploadDocument, useDeleteDocument } from "@/hooks/useApi";
import { clsx } from "clsx";
import { format } from "date-fns";
import type { Document } from "@/types";

type FilterStatus = "all" | "indexed" | "processing" | "failed";

const statusConfig: Record<
  string,
  { icon: string; label: string; bgClass: string; textClass: string; spin?: boolean }
> = {
  indexed: {
    icon: "check_circle",
    label: "Indexed",
    bgClass: "bg-tertiary-fixed",
    textClass: "text-on-tertiary-fixed",
  },
  imported: {
    icon: "schedule",
    label: "Imported",
    bgClass: "bg-surface-container-high",
    textClass: "text-on-surface-variant",
  },
  queued: {
    icon: "schedule",
    label: "Queued",
    bgClass: "bg-secondary-fixed",
    textClass: "text-on-secondary-fixed",
  },
  processing: {
    icon: "autorenew",
    label: "Processing",
    bgClass: "bg-secondary-fixed",
    textClass: "text-on-secondary-fixed",
    spin: true,
  },
  partially_processed: {
    icon: "warning",
    label: "Partial",
    bgClass: "bg-error-container",
    textClass: "text-on-error-container",
  },
  failed: {
    icon: "error",
    label: "Failed",
    bgClass: "bg-error-container",
    textClass: "text-on-error-container",
  },
  needs_review: {
    icon: "visibility",
    label: "Needs Review",
    bgClass: "bg-secondary-fixed",
    textClass: "text-on-secondary-fixed",
  },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = statusConfig[status] || statusConfig.imported;
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 font-code-sm text-[11px] px-2 py-0.5 rounded font-medium",
        cfg.bgClass,
        cfg.textClass
      )}
    >
      <span
        className={clsx(
          "material-symbols-outlined text-[14px]",
          cfg.spin && "animate-spin"
        )}
      >
        {cfg.icon}
      </span>
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
  const [filter, setFilter] = useState<FilterStatus>("all");

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

  const filteredDocs = documents?.filter((doc) => {
    if (filter === "all") return true;
    if (filter === "indexed") return doc.processing_status === "indexed";
    if (filter === "processing")
      return ["processing", "queued", "imported"].includes(doc.processing_status);
    if (filter === "failed")
      return ["failed", "partially_processed", "needs_review"].includes(
        doc.processing_status
      );
    return true;
  });

  const filterTabs: { key: FilterStatus; label: string }[] = [
    { key: "all", label: "All" },
    { key: "indexed", label: "Indexed" },
    { key: "processing", label: "Processing" },
    { key: "failed", label: "Failed" },
  ];

  return (
    <div className="px-space-lg py-space-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-space-lg">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
            Documents
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-0.5">
            Upload and manage case documents for analysis.
          </p>
        </div>
        <label className="flex items-center gap-space-xs bg-primary text-on-primary px-space-md py-1.5 rounded font-label-md text-label-md hover:bg-primary-container transition-colors shadow-micro cursor-pointer">
          <span className="material-symbols-outlined text-[16px]">upload_file</span>
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

      {/* Drag-drop zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={clsx(
          "rounded-lg p-space-lg flex flex-col items-center justify-center text-center cursor-pointer transition-colors border-2 border-dashed mb-space-lg",
          dragOver
            ? "border-primary bg-primary-fixed"
            : "bg-surface-container-low border-surface-variant hover:bg-surface-container"
        )}
      >
        <span className="material-symbols-outlined text-[32px] text-on-surface-variant mb-space-sm">
          upload_file
        </span>
        <p className="font-body-md text-body-md text-on-surface-variant">
          Drag and drop PDF or DOCX files here
        </p>
        <p className="font-label-sm text-label-sm text-outline mt-1">
          Files are processed entirely on your local machine
        </p>
      </div>

      {/* Upload progress */}
      {upload.isPending && (
        <div className="flex items-center gap-space-sm mb-space-md p-space-md rounded-lg bg-primary-fixed">
          <span className="material-symbols-outlined text-[18px] text-primary animate-spin">
            autorenew
          </span>
          <span className="font-body-sm text-body-sm text-primary">
            Uploading and processing...
          </span>
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex items-center gap-1 bg-surface-container-low p-1 rounded-lg mb-space-lg self-start inline-flex">
        {filterTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={clsx(
              "px-space-md py-1 rounded font-label-md text-label-md transition-colors",
              filter === tab.key
                ? "bg-surface-container-lowest text-primary shadow-micro font-semibold"
                : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container"
            )}
          >
            {tab.label}
            {tab.key !== "all" && documents && (
              <span className="ml-1 font-code-sm text-code-sm">
                (
                {
                  documents.filter((d) => {
                    if (tab.key === "indexed") return d.processing_status === "indexed";
                    if (tab.key === "processing")
                      return ["processing", "queued", "imported"].includes(
                        d.processing_status
                      );
                    if (tab.key === "failed")
                      return ["failed", "partially_processed", "needs_review"].includes(
                        d.processing_status
                      );
                    return false;
                  }).length
                }
                )
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Document list */}
      {isLoading ? (
        <div className="flex items-center justify-center py-space-xl text-on-surface-variant">
          <span className="material-symbols-outlined text-[24px] animate-spin mr-space-sm">
            autorenew
          </span>
          <span className="font-body-md text-body-md">Loading documents...</span>
        </div>
      ) : !filteredDocs?.length ? (
        <div className="flex flex-col items-center justify-center py-space-xl text-center">
          <span className="material-symbols-outlined text-[48px] text-outline mb-space-md">
            description
          </span>
          <p className="font-body-md text-body-md text-on-surface-variant">
            {filter === "all"
              ? "No documents yet. Upload PDF or DOCX files to begin analysis."
              : `No ${filter} documents found.`}
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-1">
          {/* Table header */}
          <div className="flex items-center gap-space-md px-space-md py-space-sm text-on-surface-variant">
            <div className="w-6" />
            <span className="flex-1 font-label-sm text-label-sm uppercase tracking-wider font-semibold">
              Document
            </span>
            <span className="w-20 text-right font-label-sm text-label-sm uppercase tracking-wider font-semibold">
              Pages
            </span>
            <span className="w-20 text-right font-label-sm text-label-sm uppercase tracking-wider font-semibold">
              Size
            </span>
            <span className="w-24 text-right font-label-sm text-label-sm uppercase tracking-wider font-semibold">
              Status
            </span>
          </div>

          {filteredDocs.map((doc) => (
            <div
              key={doc.id}
              className={clsx(
                "flex items-center gap-space-md px-space-md py-space-sm rounded-lg transition-colors cursor-pointer",
                selectedDoc?.id === doc.id
                  ? "bg-primary-fixed border border-primary"
                  : "bg-surface-container-lowest hover:bg-surface-container-low border border-transparent"
              )}
              onClick={() =>
                setSelectedDoc(selectedDoc?.id === doc.id ? null : doc)
              }
            >
              <span className="material-symbols-outlined text-[20px] text-primary w-6 text-center">
                description
              </span>
              <div className="flex-1 min-w-0">
                <span className="font-title text-[13px] leading-tight text-on-surface truncate block">
                  {doc.original_name}
                </span>
                <span className="font-code-sm text-[10px] text-on-surface-variant mt-0.5 block">
                  {format(new Date(doc.imported_at), "dd MMM yyyy HH:mm")}
                  {doc.is_scanned && (
                    <span className="ml-2 text-on-surface-variant">&middot; OCR Scanned</span>
                  )}
                </span>
              </div>
              <span className="w-20 text-right font-code-sm text-code-sm text-on-surface-variant">
                {doc.page_count ?? "—"}
              </span>
              <span className="w-20 text-right font-code-sm text-code-sm text-on-surface-variant">
                {formatSize(doc.size_bytes)}
              </span>
              <div className="w-24 flex justify-end">
                <StatusBadge status={doc.processing_status} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Selected document detail panel */}
      {selectedDoc && (
        <div className="bg-surface-container-lowest rounded-xl shadow-micro p-space-lg mt-space-lg border border-surface-variant">
          <div className="flex items-center justify-between mb-space-md">
            <h3 className="font-headline-sm text-headline-sm text-on-surface">
              {selectedDoc.original_name}
            </h3>
            <button
              onClick={() => setSelectedDoc(null)}
              className="p-1 rounded hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors"
            >
              <span className="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          <div className="grid grid-cols-2 gap-space-sm">
            <div className="flex flex-col gap-0.5">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                SHA-256
              </span>
              <span className="font-code-sm text-code-sm text-on-surface">
                {selectedDoc.sha256.substring(0, 16)}...
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                MIME Type
              </span>
              <span className="font-code-sm text-code-sm text-on-surface">
                {selectedDoc.mime_type}
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                Parser Version
              </span>
              <span className="font-code-sm text-code-sm text-on-surface">
                {selectedDoc.parser_version || "N/A"}
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                OCR Version
              </span>
              <span className="font-code-sm text-code-sm text-on-surface">
                {selectedDoc.ocr_version || "N/A"}
              </span>
            </div>
          </div>

          {selectedDoc.extraction_warnings && (
            <div className="mt-space-md p-space-sm rounded-lg bg-error-container flex items-start gap-space-sm">
              <span className="material-symbols-outlined text-[18px] text-on-error-container mt-0.5">
                warning
              </span>
              <p className="font-body-sm text-body-sm text-on-error-container">
                {selectedDoc.extraction_warnings}
              </p>
            </div>
          )}

          <div className="flex gap-space-sm mt-space-md">
            <button
              onClick={() => refetch()}
              className="flex items-center gap-space-xs h-8 px-space-sm bg-surface-container-low hover:bg-surface-container text-on-surface rounded font-label-sm text-label-sm transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">refresh</span>
              Reprocess
            </button>
            <button
              onClick={async () => {
                if (confirm("Delete this document and all associated data?")) {
                  await deleteDoc.mutateAsync(selectedDoc.id);
                  setSelectedDoc(null);
                }
              }}
              className="flex items-center gap-space-xs h-8 px-space-sm bg-error-container hover:bg-error text-on-error-container hover:text-on-error rounded font-label-sm text-label-sm transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">delete</span>
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
