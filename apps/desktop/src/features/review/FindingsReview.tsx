import { useState } from "react";
import { useParams } from "react-router-dom";
import { useFindings, useReviewFinding } from "@/hooks/useApi";
import { clsx } from "clsx";
import { format } from "date-fns";
import type { Finding } from "@/types";

const reviewStatuses = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "accepted", label: "Accepted" },
  { value: "rejected", label: "Rejected" },
  { value: "needs_evidence", label: "Needs Evidence" },
  { value: "ambiguous", label: "Ambiguous" },
  { value: "corrected", label: "Corrected" },
  { value: "irrelevant", label: "Irrelevant" },
];

const statusColors: Record<string, string> = {
  pending: "bg-secondary-fixed text-on-secondary-fixed",
  accepted: "bg-tertiary-fixed text-on-tertiary-fixed",
  rejected: "bg-error-container text-on-error-container",
  needs_evidence: "bg-primary-fixed text-on-primary-fixed",
  ambiguous: "bg-secondary-fixed text-on-secondary-fixed",
  corrected: "bg-tertiary-fixed text-on-tertiary-fixed",
  irrelevant: "bg-surface-container-high text-on-surface-variant",
};

const typeColors: Record<string, string> = {
  contradiction: "bg-error-container text-on-error-container",
  consistency: "bg-tertiary-fixed text-on-tertiary-fixed",
  claim: "bg-primary-fixed text-on-primary-fixed",
  entity: "bg-secondary-fixed text-on-secondary-fixed",
  timeline: "bg-secondary-fixed text-on-secondary-fixed",
};

function FindingCard({ finding, matterId }: { finding: Finding; matterId: string }) {
  const [showReview, setShowReview] = useState(false);
  const [note, setNote] = useState(finding.reviewer_note || "");
  const reviewMutation = useReviewFinding(matterId);

  const handleReview = async (status: string) => {
    await reviewMutation.mutateAsync({
      findingId: finding.id,
      data: { review_status: status, reviewer_note: note || undefined },
    });
    setShowReview(false);
  };

  const typeBadge = typeColors[finding.finding_type] || "bg-surface-container-high text-on-surface-variant";
  const statusBadge = statusColors[finding.review_status] || "bg-surface-container-high text-on-surface-variant";

  return (
    <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
      <div className="flex items-start justify-between mb-space-md">
        <div className="flex items-center gap-space-sm">
          <span className={clsx("font-code-sm text-[11px] px-2 py-0.5 rounded font-medium capitalize", typeBadge)}>
            {finding.finding_type.replace(/_/g, " ")}
          </span>
          <span className={clsx("font-code-sm text-[11px] px-2 py-0.5 rounded font-medium capitalize", statusBadge)}>
            {finding.review_status}
          </span>
        </div>
        <span className="font-code-sm text-code-sm text-on-surface-variant">
          {format(new Date(finding.created_at), "dd MMM yyyy HH:mm")}
        </span>
      </div>

      <h3 className="font-title text-[14px] text-on-surface mb-space-sm">{finding.summary}</h3>

      {finding.explanation && (
        <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed mb-space-md">
          {finding.explanation}
        </p>
      )}

      {finding.reviewer_note && (
        <div className="p-space-sm rounded-lg bg-surface-container-low mb-space-md">
          <div className="flex items-center gap-space-xs font-label-sm text-label-sm text-on-surface-variant mb-1">
            <span className="material-symbols-outlined text-[12px]">comment</span>
            Reviewer Note
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant">{finding.reviewer_note}</p>
        </div>
      )}

      <button
        onClick={() => setShowReview(!showReview)}
        className="font-label-md text-label-md text-primary hover:text-primary-container transition-colors"
      >
        {showReview ? "Cancel" : "Review"}
      </button>

      {showReview && (
        <div className="mt-space-md pt-space-md border-t border-surface-variant">
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Optional reviewer note..."
            rows={2}
            className="w-full bg-surface-container-lowest border border-surface-variant rounded px-space-md py-1.5 text-on-surface font-body-sm text-body-sm outline-none focus:border-primary mb-space-md resize-none"
          />
          <div className="flex flex-wrap gap-space-sm">
            {[
              { value: "accepted", label: "Accept", icon: "check_circle", colors: "bg-tertiary-fixed text-on-tertiary-fixed" },
              { value: "rejected", label: "Reject", icon: "cancel", colors: "bg-error-container text-on-error-container" },
              { value: "needs_evidence", label: "Needs Evidence", icon: "help", colors: "bg-primary-fixed text-on-primary-fixed" },
              { value: "ambiguous", label: "Ambiguous", icon: "help", colors: "bg-secondary-fixed text-on-secondary-fixed" },
              { value: "corrected", label: "Corrected", icon: "check_circle", colors: "bg-tertiary-fixed text-on-tertiary-fixed" },
              { value: "irrelevant", label: "Irrelevant", icon: "cancel", colors: "bg-surface-container-high text-on-surface-variant" },
            ].map(({ value, label, icon, colors }) => (
              <button
                key={value}
                onClick={() => handleReview(value)}
                disabled={reviewMutation.isPending}
                className={clsx(
                  "flex items-center gap-space-xs font-code-sm text-[11px] px-2.5 py-1 rounded font-medium cursor-pointer hover:opacity-80 transition-opacity",
                  colors
                )}
              >
                <span className="material-symbols-outlined text-[14px]">{icon}</span>
                {label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function FindingsReview() {
  const { matterId } = useParams();
  const [statusFilter, setStatusFilter] = useState("all");
  const { data: findings, isLoading } = useFindings(
    matterId,
    statusFilter === "all" ? undefined : statusFilter
  );

  const pendingCount = findings?.filter((f) => f.review_status === "pending").length || 0;

  return (
    <div className="px-space-lg py-space-xl max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-space-lg">
        <div className="flex items-center gap-space-md">
          <h1 className="font-headline-sm text-headline-sm text-on-surface">Findings Review</h1>
          {pendingCount > 0 && (
            <span className="font-code-sm text-[11px] px-2 py-0.5 rounded font-medium bg-secondary-fixed text-on-secondary-fixed">
              {pendingCount} pending
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-space-sm mb-space-lg">
        <span className="material-symbols-outlined text-[16px] text-on-surface-variant">filter_list</span>
        <div className="bg-surface-container-low p-1 rounded-lg flex items-center gap-0.5 overflow-x-auto">
          {reviewStatuses.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => setStatusFilter(value)}
              className={clsx(
                "px-space-md py-1 rounded font-label-md text-label-md whitespace-nowrap transition-all",
                statusFilter === value
                  ? "bg-surface-container-lowest text-primary shadow-micro font-semibold"
                  : "text-on-surface-variant hover:text-on-surface"
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16 text-on-surface-variant">
          <span className="material-symbols-outlined text-[20px] animate-spin mr-space-sm">autorenew</span>
          <span className="font-body-sm text-body-sm">Loading findings...</span>
        </div>
      ) : !findings?.length ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <span className="material-symbols-outlined text-[40px] text-outline mb-space-md">notification_important</span>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-md">
            {statusFilter === "all"
              ? "No findings yet. Run a comparison or extraction to generate findings."
              : `No findings with status "${statusFilter}".`}
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-space-md">
          {findings.map((finding) => (
            <FindingCard key={finding.id} finding={finding} matterId={matterId!} />
          ))}
        </div>
      )}
    </div>
  );
}
