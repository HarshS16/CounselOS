import { useState } from "react";
import { useParams } from "react-router-dom";
import { useChronology, useBuildChronology, useUpdateEvent } from "@/hooks/useApi";
import type { TimelineEvent } from "@/types";

const precisionLabel: Record<string, string> = {
  exact: "EXACT DATE",
  approximate: "APPROX DATE",
  range: "DATE RANGE",
  inferred: "INFERRED DATE",
  unknown: "UNKNOWN",
};

const precisionBadgeClass: Record<string, string> = {
  exact: "bg-tertiary-fixed text-on-tertiary-fixed",
  approximate: "bg-secondary-fixed text-on-secondary-fixed",
  range: "bg-secondary-fixed text-on-secondary-fixed",
  inferred: "bg-error-container text-on-error-container",
  unknown: "bg-surface-container-high text-on-surface-variant",
};

const statusDotColor: Record<string, string> = {
  accepted: "bg-tertiary",
  rejected: "bg-error",
  pending: "bg-outline",
  needs_evidence: "bg-secondary",
  ambiguous: "bg-outline",
};

const statusBadgeClass: Record<string, string> = {
  accepted: "bg-tertiary-fixed text-on-tertiary-fixed",
  rejected: "bg-error-container text-on-error-container",
  pending: "bg-surface-container-high text-on-surface-variant",
  needs_evidence: "bg-secondary-fixed text-on-secondary-fixed",
  ambiguous: "bg-surface-container-high text-on-surface-variant",
};

function EventCard({ event, matterId }: { event: TimelineEvent; matterId: string }) {
  const [editing, setEditing] = useState(false);
  const [desc, setDesc] = useState(event.description);
  const updateEvent = useUpdateEvent(matterId);

  const handleReview = async (status: string) => {
    await updateEvent.mutateAsync({
      eventId: event.id,
      data: { review_status: status },
    });
  };

  const handleSave = async () => {
    await updateEvent.mutateAsync({
      eventId: event.id,
      data: { review_status: event.review_status, description: desc },
    });
    setEditing(false);
  };

  const precision = event.date_precision || "unknown";
  const status = event.review_status || "pending";

  return (
    <div className="flex gap-space-lg">
      {/* Left: date column */}
      <div className="w-32 shrink-0 pt-1 text-right">
        <div className="font-code-md text-code-md font-bold text-on-surface">
          {event.event_date || "No date"}
        </div>
        <div className="mt-1">
          <span className={`font-code-sm text-[10px] px-1.5 py-0.5 rounded uppercase tracking-wider font-semibold ${precisionBadgeClass[precision] || precisionBadgeClass.unknown}`}>
            {precisionLabel[precision] || "UNKNOWN"}
          </span>
        </div>
      </div>

      {/* Center: dot + line */}
      <div className="flex flex-col items-center pt-1.5">
        <div className={`w-3 h-3 rounded-full border-2 border-surface-container-lowest ${statusDotColor[status] || statusDotColor.pending}`} />
        <div className="w-px flex-1 bg-outline-variant mt-1" />
      </div>

      {/* Right: event card */}
      <div className="flex-1 pb-space-xl">
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro border border-surface-variant">
          {/* Badges row */}
          <div className="flex items-center gap-space-sm mb-space-sm">
            <span className={`font-code-sm text-[11px] px-2 py-0.5 rounded font-medium capitalize ${statusBadgeClass[status] || statusBadgeClass.pending}`}>
              {status.replace(/_/g, " ")}
            </span>
          </div>

          {/* Description */}
          {editing ? (
            <div className="flex gap-space-sm mt-space-sm">
              <textarea
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
                rows={3}
                className="flex-1 bg-surface-container-lowest border border-surface-variant rounded px-space-md py-1.5 text-on-surface font-body-sm text-body-sm outline-none focus:border-primary resize-none"
              />
              <div className="flex flex-col gap-space-xs">
                <button
                  onClick={handleSave}
                  className="bg-primary text-on-primary px-space-md py-1.5 rounded font-label-md text-label-md hover:bg-primary-container transition-colors shadow-micro"
                >
                  Save
                </button>
                <button
                  onClick={() => { setEditing(false); setDesc(event.description); }}
                  className="bg-surface-container-low px-space-md py-1.5 rounded border border-surface-variant text-on-surface hover:bg-surface-container-high transition-colors font-label-md text-label-md"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <p className="font-body-md text-body-md text-on-surface leading-relaxed">
              {event.description}
            </p>
          )}

          {/* Source badges */}
          {event.sources && event.sources.length > 0 && (
            <div className="flex flex-wrap gap-space-xs mt-space-md">
              {event.sources.map((src, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 font-code-sm text-[11px] px-2 py-0.5 rounded bg-surface-container text-on-surface-variant border border-surface-variant"
                >
                  <span className="material-symbols-outlined text-[12px]">description</span>
                  {src.document_name}
                  {src.page_start && (
                    <span className="text-outline">· p.{src.page_start}{src.page_end && src.page_end !== src.page_start ? `-${src.page_end}` : ""}</span>
                  )}
                </span>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-space-sm mt-space-md pt-space-sm border-t border-surface-variant">
            <button
              onClick={() => handleReview("accepted")}
              disabled={updateEvent.isPending}
              className="inline-flex items-center gap-1 px-space-md py-1 rounded font-label-md text-label-md text-tertiary hover:bg-tertiary-fixed transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">check_circle</span>
              Accept
            </button>
            <button
              onClick={() => handleReview("rejected")}
              disabled={updateEvent.isPending}
              className="inline-flex items-center gap-1 px-space-md py-1 rounded font-label-md text-label-md text-error hover:bg-error-container transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">cancel</span>
              Reject
            </button>
            <button
              onClick={() => handleReview("needs_evidence")}
              disabled={updateEvent.isPending}
              className="inline-flex items-center gap-1 px-space-md py-1 rounded font-label-md text-label-md text-secondary hover:bg-secondary-fixed transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">help</span>
              Needs Evidence
            </button>
            <div className="flex-1" />
            <button
              onClick={() => setEditing(true)}
              className="inline-flex items-center gap-1 px-space-sm py-1 rounded font-label-md text-label-md text-on-surface-variant hover:bg-surface-container-high transition-colors"
            >
              <span className="material-symbols-outlined text-[14px]">edit</span>
              Edit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

type FilterTab = "all" | "accepted" | "pending" | "ambiguous";

export default function ChronologyView() {
  const { matterId } = useParams();
  const { data: chronology, isLoading } = useChronology(matterId);
  const buildChronology = useBuildChronology(matterId!);
  const [filter, setFilter] = useState<FilterTab>("all");

  const events = chronology?.events || [];

  const counts = {
    all: events.length,
    accepted: events.filter((e) => e.review_status === "accepted").length,
    pending: events.filter((e) => e.review_status === "pending").length,
    ambiguous: events.filter((e) => e.review_status === "ambiguous" || e.review_status === "needs_evidence").length,
  };

  const filtered = filter === "all"
    ? events
    : filter === "ambiguous"
      ? events.filter((e) => e.review_status === "ambiguous" || e.review_status === "needs_evidence")
      : events.filter((e) => e.review_status === filter);

  const acceptedRatio = events.length > 0
    ? Math.round((counts.accepted / events.length) * 100)
    : 0;

  const tabs: { key: FilterTab; label: string }[] = [
    { key: "all", label: `All (${counts.all})` },
    { key: "accepted", label: `Accepted (${counts.accepted})` },
    { key: "pending", label: `Pending Review (${counts.pending})` },
    { key: "ambiguous", label: `Ambiguous (${counts.ambiguous})` },
  ];

  return (
    <div className="px-space-lg py-space-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-space-xl">
        <div>
          <h1 className="font-headline-sm text-headline-sm text-on-surface">
            Case Chronology
          </h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
            Timeline of events extracted from case documents
          </p>
        </div>
        <div className="flex items-center gap-space-sm">
          <button
            onClick={() => buildChronology.mutate()}
            disabled={buildChronology.isPending}
            className="inline-flex items-center gap-space-xs bg-primary text-on-primary px-space-md py-1.5 rounded font-label-md text-label-md hover:bg-primary-container transition-colors shadow-micro"
          >
            {buildChronology.isPending ? (
              <span className="material-symbols-outlined text-[16px] animate-spin">autorenew</span>
            ) : (
              <span className="material-symbols-outlined text-[16px]">play_arrow</span>
            )}
            {events.length > 0 ? "Re-Build Chronology" : "Build Chronology"}
          </button>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-1 p-1 bg-surface-container rounded-lg mb-space-lg w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-space-md py-1.5 rounded font-label-md text-label-md transition-colors ${
              filter === tab.key
                ? "bg-surface-container-lowest text-on-surface shadow-micro font-semibold"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Stat cards */}
      {events.length > 0 && (
        <div className="grid grid-cols-4 gap-space-md mb-space-xl">
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
            <div className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
              Total Event Nodes
            </div>
            <div className="font-headline-sm text-headline-sm text-on-surface">{events.length}</div>
          </div>
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
            <div className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
              Admitted Evidentiary Ratio
            </div>
            <div className="font-headline-sm text-headline-sm text-on-surface">{acceptedRatio}%</div>
            <div className="w-full h-1.5 bg-surface-container-high rounded-full mt-space-sm overflow-hidden">
              <div className="h-full bg-tertiary rounded-full transition-all" style={{ width: `${acceptedRatio}%` }} />
            </div>
          </div>
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
            <div className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
              Pending Review
            </div>
            <div className="font-headline-sm text-headline-sm text-on-surface">{counts.pending}</div>
          </div>
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
            <div className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
              Ambiguous Events
            </div>
            <div className="font-headline-sm text-headline-sm text-on-surface">{counts.ambiguous}</div>
          </div>
        </div>
      )}

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-space-xl">
          <span className="material-symbols-outlined text-[24px] text-on-surface-variant animate-spin">autorenew</span>
          <span className="ml-space-sm font-body-sm text-body-sm text-on-surface-variant">Loading chronology...</span>
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <span className="material-symbols-outlined text-[48px] text-outline-variant mb-space-md">schedule</span>
          <p className="font-body-md text-body-md text-on-surface-variant text-center max-w-md">
            {events.length === 0
              ? "No chronology events yet. Extract claims from documents first, then build the chronology timeline."
              : "No events match the selected filter."}
          </p>
        </div>
      ) : (
        <div className="ml-2">
          {filtered.map((event) => (
            <EventCard key={event.id} event={event} matterId={matterId!} />
          ))}
        </div>
      )}
    </div>
  );
}
