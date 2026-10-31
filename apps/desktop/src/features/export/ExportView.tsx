import { useState } from "react";
import { useParams } from "react-router-dom";
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
    <div className="px-space-lg py-space-xl max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-space-lg">
        <h1 className="font-headline-sm text-headline-sm text-on-surface">Export Report</h1>
        <button
          onClick={handleExport}
          disabled={createExport.isPending}
          className="flex items-center gap-space-xs bg-primary text-on-primary px-space-md py-1.5 rounded font-label-md text-label-md hover:bg-primary-container transition-colors shadow-micro disabled:opacity-50"
        >
          {createExport.isPending ? (
            <span className="material-symbols-outlined text-[16px] animate-spin">autorenew</span>
          ) : (
            <span className="material-symbols-outlined text-[16px]">download</span>
          )}
          Export Chronology DOCX
        </button>
      </div>

      {exported && createExport.data && (
        <div className="flex items-center gap-space-sm bg-tertiary-fixed/20 border border-tertiary-fixed-dim rounded-lg px-space-md py-space-sm mb-space-lg">
          <span className="material-symbols-outlined text-[16px] text-tertiary">check_circle</span>
          <span className="font-body-sm text-body-sm text-tertiary">
            Report saved: {createExport.data.file_name}
          </span>
        </div>
      )}

      <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro mb-space-lg">
        <h2 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-md">
          Report Options
        </h2>

        <div className="flex flex-col gap-space-md mb-space-lg">
          {[
            { label: "Include Chronology", desc: "Timeline of events with dates and sources", checked: includeChronology, set: setIncludeChronology },
            { label: "Include Findings", desc: "AI-generated findings and contradictions", checked: includeFindings, set: setIncludeFindings },
            { label: "Include Source References", desc: "Page numbers and document citations", checked: includeSources, set: setIncludeSources },
          ].map(({ label, desc, checked, set }) => (
            <label key={label} className="flex items-start gap-space-md cursor-pointer group">
              <input
                type="checkbox"
                checked={checked}
                onChange={(e) => set(e.target.checked)}
                className="w-4 h-4 mt-0.5 rounded border-surface-variant accent-primary cursor-pointer"
              />
              <div>
                <span className="font-body-sm text-body-sm text-on-surface group-hover:text-primary transition-colors">{label}</span>
                <p className="font-label-sm text-label-sm text-on-surface-variant mt-0.5">{desc}</p>
              </div>
            </label>
          ))}
        </div>

        <div className="bg-error-container/20 border-l-[3px] border-error p-space-md rounded-r-lg">
          <div className="flex items-start gap-space-sm">
            <span className="material-symbols-outlined text-[16px] text-error mt-0.5">warning</span>
            <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
              The exported report will contain AI-generated analysis that requires professional legal review.
              All AI-generated content is clearly labelled. Source citations indicate where text was found,
              not whether the underlying statements are true.
            </p>
          </div>
        </div>
      </div>

      {exports && exports.length > 0 && (
        <div>
          <h2 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-md">
            Previous Exports
          </h2>
          <div className="flex flex-col gap-space-sm">
            {exports.map((exp, i) => (
              <div key={i} className="bg-surface-container-lowest p-space-md rounded-xl shadow-micro flex items-center gap-space-md">
                <div className="w-9 h-9 rounded-lg bg-surface-container flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-[18px] text-primary">description</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-body-sm text-body-sm text-on-surface truncate">{exp.file_name}</p>
                  <p className="font-code-sm text-code-sm text-on-surface-variant">
                    {format(new Date(exp.export_timestamp), "dd MMM yyyy HH:mm")}
                    {" · "}{exp.finding_count} findings, {exp.event_count} events
                  </p>
                </div>
                <span className="font-code-sm text-[11px] px-2 py-0.5 rounded font-medium bg-surface-container-high text-on-surface-variant uppercase">
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
