import { useState } from "react";
import { useParams } from "react-router-dom";
import {
  Clock,
  Play,
  Loader2,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Edit3,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { useChronology, useBuildChronology, useUpdateEvent } from "@/hooks/useApi";
import type { TimelineEvent } from "@/types";

const precisionLabel: Record<string, string> = {
  exact: "Exact",
  approximate: "Approx.",
  range: "Range",
  inferred: "Inferred",
  unknown: "Unknown",
};

const statusActions = [
  { value: "accepted", label: "Accept", icon: CheckCircle2, color: "var(--color-success)" },
  { value: "rejected", label: "Reject", icon: XCircle, color: "var(--color-danger)" },
  { value: "needs_evidence", label: "Needs Evidence", icon: HelpCircle, color: "var(--color-warning)" },
  { value: "ambiguous", label: "Ambiguous", icon: HelpCircle, color: "var(--color-warning)" },
];

function EventRow({ event, matterId }: { event: TimelineEvent; matterId: string }) {
  const [expanded, setExpanded] = useState(false);
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

  const statusColor =
    event.review_status === "accepted" ? "var(--color-success)" :
    event.review_status === "rejected" ? "var(--color-danger)" :
    "var(--color-warning)";

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div
          className="w-3 h-3 rounded-full border-2 mt-1.5"
          style={{ borderColor: statusColor }}
        />
        <div className="w-px flex-1 bg-[var(--color-border-primary)]" />
      </div>

      <div className="flex-1 pb-6">
        <div className="flex items-center gap-3 mb-1">
          <span className="text-xs font-mono font-medium" style={{ color: statusColor }}>
            {event.event_date || "Date unknown"}
          </span>
          <span className="text-xs text-[var(--color-text-muted)]">
            ({precisionLabel[event.date_precision || "unknown"]})
          </span>
          <span
            className="text-xs px-1.5 py-0.5 rounded capitalize"
            style={{
              color: statusColor,
              backgroundColor: `color-mix(in srgb, ${statusColor} 10%, transparent)`,
            }}
          >
            {event.review_status}
          </span>
        </div>

        {editing ? (
          <div className="flex gap-2 mt-1">
            <textarea
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              rows={2}
              className="flex-1 px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] text-sm focus:outline-none focus:border-[var(--color-accent)]"
            />
            <div className="flex flex-col gap-1">
              <button onClick={handleSave} className="px-3 py-1 rounded bg-[var(--color-accent)] text-white text-xs">Save</button>
              <button onClick={() => setEditing(false)} className="px-3 py-1 rounded bg-[var(--color-bg-tertiary)] text-xs">Cancel</button>
            </div>
          </div>
        ) : (
          <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
            {event.description}
          </p>
        )}

        <div className="flex items-center gap-2 mt-2">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] flex items-center gap-1"
          >
            {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            Actions
          </button>
          <button
            onClick={() => setEditing(true)}
            className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-accent)] flex items-center gap-1"
          >
            <Edit3 size={10} /> Edit
          </button>
        </div>

        {expanded && (
          <div className="flex gap-2 mt-2">
            {statusActions.map(({ value, label, icon: Icon, color }) => (
              <button
                key={value}
                onClick={() => handleReview(value)}
                disabled={updateEvent.isPending}
                className="flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors hover:opacity-80"
                style={{
                  color,
                  backgroundColor: `color-mix(in srgb, ${color} 10%, transparent)`,
                }}
              >
                <Icon size={10} />
                {label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChronologyView() {
  const { matterId } = useParams();
  const { data: chronology, isLoading } = useChronology(matterId);
  const buildChronology = useBuildChronology(matterId!);
  const events = chronology?.events;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold">Chronology</h1>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">
            Timeline of events extracted from case documents
            {chronology && ` · ${chronology.total_events} events`}
          </p>
        </div>
        <button
          onClick={() => buildChronology.mutate()}
          disabled={buildChronology.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-accent)] text-white text-sm font-medium hover:bg-[var(--color-accent-hover)] disabled:opacity-50 transition-colors"
        >
          {buildChronology.isPending ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Play size={16} />
          )}
          Build Chronology
        </button>
      </div>

      {isLoading ? (
        <div className="text-center text-[var(--color-text-muted)] py-8">Loading...</div>
      ) : !events?.length ? (
        <div className="text-center py-16">
          <Clock size={40} className="mx-auto mb-3 text-[var(--color-text-muted)] opacity-50" />
          <p className="text-sm text-[var(--color-text-muted)]">
            No chronology events yet. Extract claims first, then build the chronology.
          </p>
        </div>
      ) : (
        <div className="pl-2">
          {events.map((event) => (
            <EventRow key={event.id} event={event} matterId={matterId!} />
          ))}
        </div>
      )}
    </div>
  );
}
