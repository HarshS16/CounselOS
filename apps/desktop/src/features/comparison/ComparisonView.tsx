import { useState } from "react";
import { useParams } from "react-router-dom";
import { useDocuments, useCompareDocuments, useExtractClaims } from "@/hooks/useApi";
import type { DiscrepancyResult } from "@/types";

const findingTypeConfig: Record<string, { badgeClass: string; borderClass: string }> = {
  contradiction: {
    badgeClass: "bg-error-container text-on-error-container",
    borderClass: "border-l-error",
  },
  date_discrepancy: {
    badgeClass: "bg-error-container text-on-error-container",
    borderClass: "border-l-error",
  },
  amount_discrepancy: {
    badgeClass: "bg-error-container text-on-error-container",
    borderClass: "border-l-error",
  },
  attribution_difference: {
    badgeClass: "bg-secondary-fixed text-on-secondary-fixed",
    borderClass: "border-l-secondary",
  },
  omission: {
    badgeClass: "bg-secondary-fixed text-on-secondary-fixed",
    borderClass: "border-l-secondary",
  },
  ambiguity: {
    badgeClass: "bg-secondary-fixed text-on-secondary-fixed",
    borderClass: "border-l-secondary",
  },
  corroboration: {
    badgeClass: "bg-tertiary-fixed text-on-tertiary-fixed",
    borderClass: "border-l-tertiary",
  },
  other: {
    badgeClass: "bg-surface-container-high text-on-surface-variant",
    borderClass: "border-l-outline",
  },
};

function FindingCard({ finding }: { finding: DiscrepancyResult }) {
  const [expanded, setExpanded] = useState(false);
  const config = findingTypeConfig[finding.finding_type] || findingTypeConfig.other;

  return (
    <div className={`bg-surface-container-lowest rounded-xl shadow-micro border border-surface-variant border-l-[3px] ${config.borderClass}`}>
      <div className="p-space-lg">
        {/* Type + status badges */}
        <div className="flex items-center gap-space-sm mb-space-sm">
          <span className={`font-code-sm text-[11px] px-2 py-0.5 rounded font-medium capitalize ${config.badgeClass}`}>
            {finding.finding_type.replace(/_/g, " ")}
          </span>
          <span className="font-code-sm text-[11px] px-2 py-0.5 rounded font-medium capitalize bg-surface-container-high text-on-surface-variant">
            {finding.review_status}
          </span>
        </div>

        {/* Summary */}
        <p className="font-body-md text-body-md text-on-surface font-medium mb-space-sm">
          {finding.summary}
        </p>

        {/* Expand toggle */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="inline-flex items-center gap-1 font-label-md text-label-md text-primary hover:text-primary-container transition-colors"
        >
          <span className="material-symbols-outlined text-[14px]">
            {expanded ? "expand_more" : "chevron_right"}
          </span>
          {expanded ? "Hide details" : "Show details"}
        </button>

        {expanded && (
          <div className="mt-space-md space-y-space-md">
            {/* Explanation */}
            {finding.explanation && (
              <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
                {finding.explanation}
              </p>
            )}

            {/* Side-by-side claims */}
            {(finding.claim_a || finding.claim_b) && (
              <div className="flex gap-space-sm items-stretch">
                {finding.claim_a && (
                  <div className="flex-1 p-space-md rounded-lg bg-surface-container border border-surface-variant">
                    <div className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
                      Claim A
                    </div>
                    <p className="font-body-sm text-body-sm text-on-surface">
                      {finding.claim_a.claim_text}
                    </p>
                    {finding.claim_a.sources && finding.claim_a.sources.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-space-sm">
                        {finding.claim_a.sources.map((src, i) => (
                          <span key={i} className="font-code-sm text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface-variant">
                            {src.document_name} · p.{src.page_start}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {finding.claim_a && finding.claim_b && (
                  <div className="flex items-center px-space-xs">
                    <span className="font-label-sm text-label-sm text-outline font-semibold">vs</span>
                  </div>
                )}

                {finding.claim_b && (
                  <div className="flex-1 p-space-md rounded-lg bg-surface-container border border-surface-variant">
                    <div className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
                      Claim B
                    </div>
                    <p className="font-body-sm text-body-sm text-on-surface">
                      {finding.claim_b.claim_text}
                    </p>
                    {finding.claim_b.sources && finding.claim_b.sources.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-space-sm">
                        {finding.claim_b.sources.map((src, i) => (
                          <span key={i} className="font-code-sm text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface-variant">
                            {src.document_name} · p.{src.page_start}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Uncertainty note */}
            {finding.uncertainty && (
              <div className="flex items-start gap-space-xs p-space-sm rounded bg-secondary-fixed">
                <span className="material-symbols-outlined text-[16px] text-on-secondary-fixed mt-0.5">help</span>
                <p className="font-body-sm text-body-sm text-on-secondary-fixed">
                  <span className="font-semibold">Uncertainty:</span> {finding.uncertainty}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
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
    <div className="px-space-lg py-space-xl">
      {/* Header */}
      <div className="mb-space-xl">
        <h1 className="font-headline-sm text-headline-sm text-on-surface">
          Compare Documents
        </h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
          Select two documents to compare their claims and identify discrepancies
        </p>
      </div>

      {/* Document selector card */}
      <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro border border-surface-variant mb-space-xl">
        <div className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-md">
          Document Selection
        </div>

        <div className="grid grid-cols-2 gap-space-lg mb-space-lg">
          <div>
            <label className="block font-label-md text-label-md text-on-surface-variant mb-space-xs">
              Document A
            </label>
            <select
              value={docA}
              onChange={(e) => setDocA(e.target.value)}
              className="w-full bg-surface-container-lowest border border-surface-variant rounded px-space-md py-1.5 text-on-surface font-body-sm text-body-sm outline-none focus:border-primary"
            >
              <option value="">Select document...</option>
              {indexedDocs.map((d) => (
                <option key={d.id} value={d.id}>{d.original_name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block font-label-md text-label-md text-on-surface-variant mb-space-xs">
              Document B
            </label>
            <select
              value={docB}
              onChange={(e) => setDocB(e.target.value)}
              className="w-full bg-surface-container-lowest border border-surface-variant rounded px-space-md py-1.5 text-on-surface font-body-sm text-body-sm outline-none focus:border-primary"
            >
              <option value="">Select document...</option>
              {indexedDocs.map((d) => (
                <option key={d.id} value={d.id}>{d.original_name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex gap-space-sm">
          <button
            onClick={handleExtractFirst}
            disabled={extractMutation.isPending}
            className="inline-flex items-center gap-space-xs bg-surface-container-low px-space-md py-1.5 rounded border border-surface-variant text-on-surface hover:bg-surface-container-high transition-colors font-label-md text-label-md"
          >
            {extractMutation.isPending ? (
              <span className="material-symbols-outlined text-[16px] animate-spin">autorenew</span>
            ) : (
              <span className="material-symbols-outlined text-[16px]">description</span>
            )}
            Extract Claims
          </button>
          <button
            onClick={handleCompare}
            disabled={!docA || !docB || docA === docB || compareMutation.isPending}
            className="inline-flex items-center gap-space-xs bg-primary text-on-primary px-space-md py-1.5 rounded font-label-md text-label-md hover:bg-primary-container transition-colors shadow-micro disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {compareMutation.isPending ? (
              <span className="material-symbols-outlined text-[16px] animate-spin">autorenew</span>
            ) : (
              <span className="material-symbols-outlined text-[16px]">compare_arrows</span>
            )}
            Compare
          </button>
        </div>
      </div>

      {/* Results */}
      {compareMutation.data && (
        <div>
          <div className="flex items-center gap-space-sm mb-space-lg">
            <h2 className="font-title text-title text-on-surface">
              {compareMutation.data.discrepancies.length} Findings
            </h2>
            <span className="font-code-sm text-code-sm text-on-surface-variant">
              ({compareMutation.data.total_claims_compared} claims compared)
            </span>
          </div>

          {compareMutation.data.discrepancies.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <span className="material-symbols-outlined text-[48px] text-tertiary mb-space-md">verified</span>
              <p className="font-body-md text-body-md text-on-surface-variant text-center">
                No discrepancies found between these documents.
              </p>
            </div>
          ) : (
            <div className="space-y-space-md">
              {compareMutation.data.discrepancies.map((f, i) => (
                <FindingCard key={i} finding={f} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
