import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Plus, Briefcase, Archive } from "lucide-react";
import { useMatters, useCreateMatter } from "@/hooks/useApi";
import { format } from "date-fns";

export default function MatterList() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [showCreate, setShowCreate] = useState(searchParams.get("new") === "1");
  const [title, setTitle] = useState("");
  const [reference, setReference] = useState("");
  const [jurisdiction, setJurisdiction] = useState("");
  const [matterType, setMatterType] = useState("");

  const { data: matters, isLoading } = useMatters();
  const createMatter = useCreateMatter();

  const handleCreate = async () => {
    if (!title.trim()) return;
    const matter = await createMatter.mutateAsync({
      title: title.trim(),
      reference: reference.trim() || undefined,
      jurisdiction: jurisdiction.trim() || undefined,
      matter_type: matterType.trim() || undefined,
    });
    setShowCreate(false);
    setTitle("");
    setReference("");
    setJurisdiction("");
    setMatterType("");
    navigate(`/matters/${matter.id}`);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Matters</h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            Manage your case matters and documents
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-accent)] text-white text-sm font-medium hover:bg-[var(--color-accent-hover)] transition-colors"
        >
          <Plus size={16} />
          New Matter
        </button>
      </div>

      {showCreate && (
        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)] rounded-xl p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Create New Matter</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1.5">
                Matter Title *
              </label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Singh v. Sharma — Contract Dispute"
                className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] text-sm focus:outline-none focus:border-[var(--color-accent)] transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1.5">
                Reference
              </label>
              <input
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="Internal reference number"
                className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] text-sm focus:outline-none focus:border-[var(--color-accent)] transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1.5">
                Jurisdiction
              </label>
              <input
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value)}
                placeholder="e.g. Delhi High Court"
                className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] text-sm focus:outline-none focus:border-[var(--color-accent)] transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-muted)] mb-1.5">
                Matter Type
              </label>
              <select
                value={matterType}
                onChange={(e) => setMatterType(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] border border-[var(--color-border-primary)] text-sm focus:outline-none focus:border-[var(--color-accent)] transition-colors"
              >
                <option value="">Select type...</option>
                <option value="civil">Civil</option>
                <option value="criminal">Criminal</option>
                <option value="commercial">Commercial</option>
                <option value="family">Family</option>
                <option value="constitutional">Constitutional</option>
                <option value="taxation">Taxation</option>
                <option value="labour">Labour</option>
                <option value="arbitration">Arbitration</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div className="flex gap-3 mt-5">
            <button
              onClick={handleCreate}
              disabled={!title.trim() || createMatter.isPending}
              className="px-4 py-2 rounded-lg bg-[var(--color-accent)] text-white text-sm font-medium hover:bg-[var(--color-accent-hover)] disabled:opacity-50 transition-colors"
            >
              {createMatter.isPending ? "Creating..." : "Create Matter"}
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 rounded-lg bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] text-sm hover:bg-[var(--color-bg-hover)] transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="text-center text-[var(--color-text-muted)] py-12">Loading matters...</div>
      ) : !matters?.length ? (
        <div className="text-center py-16">
          <Briefcase size={48} className="mx-auto mb-4 text-[var(--color-text-muted)] opacity-50" />
          <h3 className="text-lg font-medium text-[var(--color-text-secondary)]">No matters yet</h3>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            Create a matter to start analyzing case documents
          </p>
        </div>
      ) : (
        <div className="grid gap-3">
          {matters.map((m) => (
            <button
              key={m.id}
              onClick={() => navigate(`/matters/${m.id}`)}
              className="flex items-center gap-4 p-4 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)] hover:border-[var(--color-border-secondary)] hover:bg-[var(--color-bg-tertiary)] transition-colors text-left w-full"
            >
              <div className="w-10 h-10 rounded-lg bg-[var(--color-bg-elevated)] flex items-center justify-center">
                {m.status === "archived" ? (
                  <Archive size={18} className="text-[var(--color-text-muted)]" />
                ) : (
                  <Briefcase size={18} className="text-[var(--color-accent)]" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium truncate">{m.title}</h3>
                <div className="flex items-center gap-3 mt-0.5">
                  {m.reference && (
                    <span className="text-xs text-[var(--color-text-muted)]">{m.reference}</span>
                  )}
                  {m.jurisdiction && (
                    <span className="text-xs text-[var(--color-text-muted)]">{m.jurisdiction}</span>
                  )}
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs text-[var(--color-text-muted)]">
                  {format(new Date(m.created_at), "dd MMM yyyy")}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
