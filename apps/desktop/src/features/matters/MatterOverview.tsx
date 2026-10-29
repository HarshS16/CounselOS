import { useParams, useNavigate } from "react-router-dom";
import { FileText, Search, Clock, GitCompare, AlertTriangle, Download } from "lucide-react";
import { useMatter, useDocuments, useFindings, useChronology } from "@/hooks/useApi";
import { format } from "date-fns";

export default function MatterOverview() {
  const { matterId } = useParams();
  const navigate = useNavigate();
  const { data: matter, isLoading } = useMatter(matterId);
  const { data: documents } = useDocuments(matterId);
  const { data: findings } = useFindings(matterId);
  const { data: events } = useChronology(matterId);

  if (isLoading) {
    return <div className="p-8 text-[var(--color-text-muted)]">Loading...</div>;
  }

  if (!matter) {
    return <div className="p-8 text-[var(--color-danger)]">Matter not found</div>;
  }

  const pendingFindings = findings?.filter((f) => f.review_status === "pending").length || 0;
  const processedDocs = documents?.filter((d) => d.processing_status === "indexed").length || 0;
  const failedDocs = documents?.filter((d) => d.processing_status === "failed").length || 0;

  const cards = [
    {
      label: "Documents",
      value: documents?.length || 0,
      sub: failedDocs > 0 ? `${failedDocs} failed` : `${processedDocs} indexed`,
      icon: FileText,
      path: "documents",
      color: "var(--color-info)",
    },
    {
      label: "Search & Ask",
      value: "Query",
      sub: "Search case documents",
      icon: Search,
      path: "search",
      color: "var(--color-accent)",
    },
    {
      label: "Chronology",
      value: events?.total_events || 0,
      sub: "Timeline events",
      icon: Clock,
      path: "chronology",
      color: "var(--color-warning)",
    },
    {
      label: "Findings",
      value: findings?.length || 0,
      sub: pendingFindings > 0 ? `${pendingFindings} pending review` : "All reviewed",
      icon: AlertTriangle,
      path: "findings",
      color: "var(--color-danger)",
    },
  ];

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">{matter.title}</h1>
        <div className="flex items-center gap-4 mt-2 text-sm text-[var(--color-text-muted)]">
          {matter.reference && <span>Ref: {matter.reference}</span>}
          {matter.jurisdiction && <span>{matter.jurisdiction}</span>}
          {matter.matter_type && (
            <span className="capitalize">{matter.matter_type}</span>
          )}
          <span>Created {format(new Date(matter.created_at), "dd MMM yyyy")}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8">
        {cards.map(({ label, value, sub, icon: Icon, path, color }) => (
          <button
            key={label}
            onClick={() => navigate(path)}
            className="flex items-start gap-4 p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)] hover:border-[var(--color-border-secondary)] transition-colors text-left"
          >
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: `color-mix(in srgb, ${color} 15%, transparent)` }}
            >
              <Icon size={20} style={{ color }} />
            </div>
            <div>
              <div className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">
                {label}
              </div>
              <div className="text-xl font-bold mt-0.5">{value}</div>
              <div className="text-xs text-[var(--color-text-muted)] mt-0.5">{sub}</div>
            </div>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => navigate("compare")}
          className="flex items-center gap-3 p-4 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)] hover:border-[var(--color-border-secondary)] transition-colors text-left"
        >
          <GitCompare size={18} className="text-[var(--color-accent)]" />
          <div>
            <div className="text-sm font-medium">Compare Documents</div>
            <div className="text-xs text-[var(--color-text-muted)]">
              Cross-document discrepancy analysis
            </div>
          </div>
        </button>
        <button
          onClick={() => navigate("export")}
          className="flex items-center gap-3 p-4 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)] hover:border-[var(--color-border-secondary)] transition-colors text-left"
        >
          <Download size={18} className="text-[var(--color-accent)]" />
          <div>
            <div className="text-sm font-medium">Export Report</div>
            <div className="text-xs text-[var(--color-text-muted)]">
              Generate evidence report (DOCX)
            </div>
          </div>
        </button>
      </div>

      {matter.notes && (
        <div className="mt-8 p-4 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
          <h3 className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
            Notes
          </h3>
          <p className="text-sm text-[var(--color-text-secondary)] whitespace-pre-wrap">
            {matter.notes}
          </p>
        </div>
      )}
    </div>
  );
}
