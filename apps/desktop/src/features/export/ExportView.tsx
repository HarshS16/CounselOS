import { useState } from "react";
import { useParams } from "react-router-dom";
import { Download, FileText, Loader2, CheckCircle2 } from "lucide-react";
import { useCreateExport, useExports } from "@/hooks/useApi";
import { format } from "date-fns";

export default function ExportView() {
  const { matterId } = useParams();
  const [includeChronology, setIncludeChronology] = useState(true);
  const [includeFindings, setIncludeFindings] = useState(true);
  const [includeSources, setIncludeSources] = useState(true);
  const [exported, setExported] = useState(false);

  const createExport = useCreateExport(matterId!);
  const { data: exports } = useExports(matterId);

  const handleExport = async () => {
    setExported(false);
    await createExport.mutateAsync({
      include_chronology: includeChronology,
      include_findings: includeFindings,
      include_sources: includeSources,
      format: "docx",
    });
    setExported(true);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-xl font-bold mb-6">Export Report</h1>

      <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)] mb-6">
        <h2 className="text-sm font-semibold mb-4">Report Options</h2>

        <div className="space-y-3 mb-5">
          {[
            { label: "Include Chronology", checked: includeChronology, set: setIncludeChronology },
            { label: "Include Findings", checked: includeFindings, set: setIncludeFindings },
            { label: "Include Source References", checked: includeSources, set: setIncludeSources },
          ].map(({ label, checked, set }) => (
            <label key={label} className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={checked}
                onChange={(e) => set(e.target.checked)}
                className="w-4 h-4 rounded border-[var(--color-border-primary)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]"
              />
              <span className="text-sm">{label}</span>
            </label>
          ))}
        </div>

        <div className="p-3 rounded-lg bg-[color-mix(in_srgb,var(--color-warning)_8%,transparent)] mb-4">
          <p className="text-xs text-[var(--color-warning)] leading-relaxed">
            The exported report will contain AI-generated analysis that requires professional legal review.
            All AI-generated content is clearly labelled. Source citations indicate where text was found,
            not whether the underlying statements are true.
          </p>
        </div>

        <button
          onClick={handleExport}
          disabled={createExport.isPending}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[var(--color-accent)] text-white text-sm font-medium hover:bg-[var(--color-accent-hover)] disabled:opacity-50 transition-colors"
        >
          {createExport.isPending ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Download size={16} />
          )}
          Generate & Export Report
        </button>

        {exported && createExport.data && (
          <div className="flex items-center gap-2 mt-3 text-sm text-[var(--color-success)]">
            <CheckCircle2 size={16} />
            Report saved: {createExport.data.file_name}
          </div>
        )}
      </div>

      {exports && exports.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-3">Previous Exports</h2>
          <div className="space-y-2">
            {exports.map((exp, i) => (
              <div
                key={i}
                className="flex items-center gap-3 p-3 rounded-lg bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]"
              >
                <FileText size={16} className="text-[var(--color-accent)]" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate">{exp.file_name}</p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    {format(new Date(exp.export_timestamp), "dd MMM yyyy HH:mm")}
                    {" · "}{exp.finding_count} findings, {exp.event_count} events
                  </p>
                </div>
                <span className="text-xs text-[var(--color-text-muted)] uppercase">
                  {exp.format}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
