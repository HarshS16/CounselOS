import { useState } from "react";
import { useParams } from "react-router-dom";
import { GitCompare, Loader2, CheckCircle2, FileText } from "lucide-react";
import { useDocuments, useCompareDocuments, useExtractClaims } from "@/hooks/useApi";
import type { DiscrepancyResult } from "@/types";

const findingTypeColors: Record<string, string> = {
  contradiction: "var(--color-danger)",
  date_discrepancy: "var(--color-danger)",
  amount_discrepancy: "var(--color-danger)",
  attribution_difference: "var(--color-warning)",
  omission: "var(--color-warning)",
  ambiguity: "var(--color-warning)",
  corroboration: "var(--color-success)",
  other: "var(--color-text-muted)",
};

function FindingCard({ finding }: { finding: DiscrepancyResult }) {
  const [expanded, setExpanded] = useState(false);
  const color = findingTypeColors[finding.finding_type] || "var(--color-text-muted)";

  return (
    <div className="p-4 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
      <div className="flex items-center gap-2 mb-2">
        <span
          className="text-xs px-2 py-0.5 rounded font-medium capitalize"
          style={{ color, backgroundColor: `color-mix(in srgb, ${color} 12%, transparent)` }}
        >
          {finding.finding_type.replace(/_/g, " ")}
        </span>
        <span className="text-xs px-2 py-0.5 rounded capitalize text-[var(--color-text-muted)]">
          {finding.review_status}
        </span>
      </div>

      <p className="text-sm font-medium mb-2">{finding.summary}</p>

      <button
        onClick={() => setExpanded(!expanded)}
        className="text-xs text-[var(--color-accent)] hover:underline"
      >
        {expanded ? "Hide details" : "Show details"}
      </button>

      {expanded && (
        <div className="mt-3 space-y-3">
          {finding.explanation && (
            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              {finding.explanation}
            </p>
          )}

          <div className="grid grid-cols-2 gap-3">
            {finding.claim_a && (
              <div className="p-3 rounded-lg bg-[var(--color-bg-tertiary)]">
                <div className="text-xs font-medium text-[var(--color-text-muted)] mb-1">
                  Claim A
                </div>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  {finding.claim_a.claim_text}
                </p>
              </div>
            )}
            {finding.claim_b && (
              <div className="p-3 rounded-lg bg-[var(--color-bg-tertiary)]">
                <div className="text-xs font-medium text-[var(--color-text-muted)] mb-1">
                  Claim B
                </div>
                <p className="text-xs text-[var(--color-text-secondary)]">
                  {finding.claim_b.claim_text}
                </p>
              </div>
            )}
          </div>

          {finding.uncertainty && (
            <p className="text-xs text-[var(--color-warning)] italic">
              Uncertainty: {finding.uncertainty}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function ComparisonView() {
  const { matterId } = useParams();
  const { data: documents } = useDocuments(matterId);
  const [docA, setDocA] = useState("");
  const [docB, setDocB] = useState("");

  const compareMutation = useCompareDocuments(matterId!);
  const extractMutation = useExtractClaims(matterId!);

  const handleCompare = () => {
    if (docA && docB && docA !== docB) {
      compareMutation.mutate({ documentAId: docA, documentBId: docB });
    }
  };

  const handleExtractFirst = () => {
    const ids = [docA, docB].filter(Boolean);
    extractMutation.mutate(ids.length ? ids : undefined);
  };

  const indexedDocs = documents?.filter((d) => d.processing_status === "indexed") || [];

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-xl font-bold mb-6">Compare Documents</h1>

      <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)] mb-6">
        <p className="text-xs text-[var(--color-text-muted)] mb-4">
          Select two documents to compare their claims and identify potential discrepancies.
          Claims must be extracted first.
        </p>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1.5">
              Document A
            </label>
            <select
              value={docA}
              onChange={(e) => setDocA(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] text-sm focus:outline-none focus:border-[var(--color-accent)]"
            >
              <option value="">Select document...</option>
              {indexedDocs.map((d) => (
                <option key={d.id} value={d.id}>{d.original_name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1.5">
              Document B
            </label>
            <select
              value={docB}
              onChange={(e) => setDocB(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] text-sm focus:outline-none focus:border-[var(--color-accent)]"
            >
              <option value="">Select document...</option>
              {indexedDocs.map((d) => (
                <option key={d.id} value={d.id}>{d.original_name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleExtractFirst}
            disabled={extractMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-bg-tertiary)] text-sm hover:bg-[var(--color-bg-hover)] transition-colors"
          >
            {extractMutation.isPending ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <FileText size={14} />
            )}
            Extract Claims First
          </button>
          <button
            onClick={handleCompare}
            disabled={!docA || !docB || docA === docB || compareMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-accent)] text-white text-sm font-medium hover:bg-[var(--color-accent-hover)] disabled:opacity-50 transition-colors"
          >
            {compareMutation.isPending ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <GitCompare size={14} />
            )}
            Compare
          </button>
        </div>
      </div>

      {compareMutation.data && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-sm font-semibold">
              {compareMutation.data.discrepancies.length} Findings
              <span className="text-xs font-normal text-[var(--color-text-muted)] ml-2">
                ({compareMutation.data.total_claims_compared} claims compared)
              </span>
            </h2>
          </div>

          {compareMutation.data.discrepancies.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle2 size={32} className="mx-auto mb-2 text-[var(--color-success)]" />
              <p className="text-sm text-[var(--color-text-muted)]">
                No discrepancies found between these documents.
              </p>
            </div>
          ) : (
            compareMutation.data.discrepancies.map((f, i) => (
              <FindingCard key={i} finding={f} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
