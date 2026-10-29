import { useState } from "react";
import { useParams } from "react-router-dom";
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  HelpCircle,
  MessageSquare,
  Filter,
} from "lucide-react";
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
  pending: "var(--color-warning)",
  accepted: "var(--color-success)",
  rejected: "var(--color-danger)",
  needs_evidence: "var(--color-info)",
  ambiguous: "var(--color-warning)",
  corrected: "var(--color-accent)",
  irrelevant: "var(--color-text-muted)",
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

  const color = statusColors[finding.review_status] || "var(--color-text-muted)";

  return (
    <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className="text-xs px-2 py-0.5 rounded font-medium capitalize"
            style={{ color, backgroundColor: `color-mix(in srgb, ${color} 12%, transparent)` }}
          >
            {finding.finding_type.replace(/_/g, " ")}
          </span>
          <span
            className="text-xs px-2 py-0.5 rounded capitalize"
            style={{ color, backgroundColor: `color-mix(in srgb, ${color} 8%, transparent)` }}
          >
            {finding.review_status}
          </span>
        </div>
        <span className="text-xs text-[var(--color-text-muted)]">
          {format(new Date(finding.created_at), "dd MMM yyyy HH:mm")}
        </span>
      </div>

      <h3 className="text-sm font-medium mb-2">{finding.summary}</h3>

      {finding.explanation && (
        <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-3">
          {finding.explanation}
        </p>
      )}

      {finding.reviewer_note && (
        <div className="p-2 rounded-lg bg-[var(--color-bg-tertiary)] mb-3">
          <div className="flex items-center gap-1 text-xs text-[var(--color-text-muted)] mb-1">
            <MessageSquare size={10} />
            Reviewer Note
          </div>
          <p className="text-xs text-[var(--color-text-secondary)]">{finding.reviewer_note}</p>
        </div>
      )}

      <div className="flex items-center gap-2">
        <button
          onClick={() => setShowReview(!showReview)}
          className="text-xs text-[var(--color-accent)] hover:underline"
        >
          {showReview ? "Cancel" : "Review"}
        </button>
      </div>

      {showReview && (
        <div className="mt-3 pt-3 border-t border-[var(--color-border-primary)]">
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Optional reviewer note..."
            rows={2}
            className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] text-xs mb-2 focus:outline-none focus:border-[var(--color-accent)]"
          />
          <div className="flex flex-wrap gap-2">
            {[
              { value: "accepted", label: "Accept", icon: CheckCircle2, color: "var(--color-success)" },
              { value: "rejected", label: "Reject", icon: XCircle, color: "var(--color-danger)" },
              { value: "needs_evidence", label: "Needs Evidence", icon: HelpCircle, color: "var(--color-info)" },
              { value: "ambiguous", label: "Ambiguous", icon: HelpCircle, color: "var(--color-warning)" },
              { value: "corrected", label: "Corrected", icon: CheckCircle2, color: "var(--color-accent)" },
              { value: "irrelevant", label: "Irrelevant", icon: XCircle, color: "var(--color-text-muted)" },
            ].map(({ value, label, icon: Icon, color: c }) => (
              <button
                key={value}
                onClick={() => handleReview(value)}
                disabled={reviewMutation.isPending}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded text-xs transition-colors hover:opacity-80"
                style={{ color: c, backgroundColor: `color-mix(in srgb, ${c} 10%, transparent)` }}
              >
                <Icon size={12} />
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
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold">Findings Review</h1>
          {pendingCount > 0 && (
            <p className="text-xs text-[var(--color-warning)] mt-1">
              {pendingCount} findings pending review
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
        <Filter size={14} className="text-[var(--color-text-muted)] flex-shrink-0" />
        {reviewStatuses.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => setStatusFilter(value)}
            className={clsx(
              "px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors",
              statusFilter === value
                ? "bg-[var(--color-accent)] text-white"
                : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)]"
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="text-center text-[var(--color-text-muted)] py-8">Loading...</div>
      ) : !findings?.length ? (
        <div className="text-center py-16">
          <AlertTriangle size={40} className="mx-auto mb-3 text-[var(--color-text-muted)] opacity-50" />
          <p className="text-sm text-[var(--color-text-muted)]">
            {statusFilter === "all"
              ? "No findings yet. Run a comparison or extraction to generate findings."
              : `No findings with status "${statusFilter}".`}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {findings.map((finding) => (
            <FindingCard key={finding.id} finding={finding} matterId={matterId!} />
          ))}
        </div>
      )}
    </div>
  );
}
