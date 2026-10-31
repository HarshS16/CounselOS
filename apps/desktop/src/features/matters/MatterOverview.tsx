import { useParams, useNavigate } from "react-router-dom";
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
    return (
      <div className="px-space-lg py-space-xl text-on-surface-variant font-body-md text-body-md">
        Loading...
      </div>
    );
  }

  if (!matter) {
    return (
      <div className="px-space-lg py-space-xl text-error font-body-md text-body-md">
        Matter not found
      </div>
    );
  }

  const pendingFindings = findings?.filter((f) => f.review_status === "pending").length || 0;
  const processedDocs = documents?.filter((d) => d.processing_status === "indexed").length || 0;
  const failedDocs = documents?.filter((d) => d.processing_status === "failed").length || 0;

  const stats = [
    {
      label: "Indexed Records",
      value: processedDocs,
      sub: failedDocs > 0 ? `${failedDocs} failed` : `${documents?.length || 0} total`,
      icon: "description",
      subClass: failedDocs > 0 ? "text-error" : "text-on-surface-variant",
    },
    {
      label: "Extracted Claims",
      value: findings?.length || 0,
      sub: pendingFindings > 0 ? `${pendingFindings} pending` : "All reviewed",
      icon: "fact_check",
      subClass: pendingFindings > 0 ? "text-secondary" : "text-tertiary",
    },
    {
      label: "Chronology Events",
      value: events?.total_events || 0,
      sub: "Timeline entries",
      icon: "timeline",
      subClass: "text-on-surface-variant",
    },
    {
      label: "Pending Findings",
      value: pendingFindings,
      sub: pendingFindings > 0 ? "Require review" : "Queue clear",
      icon: "pending_actions",
      subClass: pendingFindings > 0 ? "text-error" : "text-tertiary",
    },
  ];

  const workbenches = [
    {
      label: "Search & Ask",
      description: "Hybrid search and AI-powered QA over case documents",
      icon: "search",
      path: "search",
    },
    {
      label: "Compare Documents",
      description: "Cross-document discrepancy and claim analysis",
      icon: "compare",
      path: "compare",
    },
    {
      label: "Chronology",
      description: "Build and review timeline of events from evidence",
      icon: "timeline",
      path: "chronology",
    },
    {
      label: "Export Report",
      description: "Generate evidence report for court filing (DOCX)",
      icon: "download",
      path: "export",
    },
  ];

  return (
    <div className="px-space-lg py-space-xl">
      {/* Matter header */}
      <div className="mb-space-xl">
        <div className="flex items-center gap-space-sm mb-space-xs">
          {matter.jurisdiction && (
            <span className="font-code-sm text-code-sm text-on-surface-variant">
              {matter.jurisdiction}
            </span>
          )}
          {matter.jurisdiction && matter.matter_type && (
            <span className="text-outline">·</span>
          )}
          {matter.matter_type && (
            <span className="font-code-sm text-code-sm text-on-surface-variant capitalize">
              {matter.matter_type}
            </span>
          )}
        </div>
        <h1 className="font-headline-lg text-headline-lg text-on-surface">{matter.title}</h1>
        <div className="flex items-center gap-space-md mt-space-sm">
          {matter.reference && (
            <span className="font-code-sm text-code-sm bg-surface-container px-space-sm py-0.5 rounded text-on-surface-variant">
              {matter.reference}
            </span>
          )}
          <span className="font-code-sm text-code-sm text-on-surface-variant">
            Created {format(new Date(matter.created_at), "dd MMM yyyy")}
          </span>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-space-md mb-space-xl">
        {stats.map((s) => (
          <div
            key={s.label}
            className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro border border-surface-variant"
          >
            <div className="flex items-center justify-between mb-space-sm">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
                {s.label}
              </span>
              <span className="material-symbols-outlined text-[18px] text-on-surface-variant">
                {s.icon}
              </span>
            </div>
            <div className="font-headline-lg text-headline-lg text-on-surface">{s.value}</div>
            <div className={`font-code-sm text-code-sm mt-space-xs ${s.subClass}`}>{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Procedural Workbenches */}
      <div className="mb-space-xl">
        <h2 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-md">
          Procedural Workbenches
        </h2>
        <div className="grid grid-cols-4 gap-space-md">
          {workbenches.map((wb) => (
            <button
              key={wb.label}
              onClick={() => navigate(wb.path)}
              className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro border border-surface-variant hover:shadow-md hover:border-outline transition-all text-left group"
            >
              <div className="w-10 h-10 rounded-lg bg-primary-container flex items-center justify-center mb-space-md group-hover:bg-primary transition-colors">
                <span className="material-symbols-outlined text-[20px] text-on-primary-container group-hover:text-on-primary transition-colors">
                  {wb.icon}
                </span>
              </div>
              <div className="font-title text-title text-on-surface mb-space-xs">{wb.label}</div>
              <div className="font-body-sm text-body-sm text-on-surface-variant">
                {wb.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Notes */}
      {matter.notes && (
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro border border-surface-variant">
          <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-sm">
            Notes
          </h3>
          <p className="font-body-md text-body-md text-on-surface whitespace-pre-wrap">
            {matter.notes}
          </p>
        </div>
      )}
    </div>
  );
}
