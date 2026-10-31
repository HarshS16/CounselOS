import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
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
    <div className="px-space-lg py-space-xl">
      {/* Page header */}
      <div className="flex items-center justify-between mb-space-xl">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface">Matters</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-space-xs">
            Manage your case matters and documents
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-space-xs bg-primary text-on-primary px-space-md py-1.5 rounded font-label-md text-label-md hover:bg-primary-container transition-colors shadow-micro"
        >
          <span className="material-symbols-outlined text-[16px]">add</span>
          New Matter
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro mb-space-xl border border-surface-variant">
          <h2 className="font-headline-sm text-headline-sm text-on-surface mb-space-lg">
            Create New Matter
          </h2>
          <div className="grid grid-cols-2 gap-space-md">
            <div className="col-span-2">
              <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
                Matter Title *
              </label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Singh v. Sharma — Contract Dispute"
                className="w-full bg-surface-container-lowest border border-surface-variant rounded px-space-md py-1.5 text-on-surface font-body-sm text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
                Reference
              </label>
              <input
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="Internal reference number"
                className="w-full bg-surface-container-lowest border border-surface-variant rounded px-space-md py-1.5 text-on-surface font-body-sm text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
                Jurisdiction
              </label>
              <input
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value)}
                placeholder="e.g. Delhi High Court"
                className="w-full bg-surface-container-lowest border border-surface-variant rounded px-space-md py-1.5 text-on-surface font-body-sm text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold mb-space-xs">
                Matter Type
              </label>
              <select
                value={matterType}
                onChange={(e) => setMatterType(e.target.value)}
                className="w-full bg-surface-container-lowest border border-surface-variant rounded px-space-md py-1.5 text-on-surface font-body-sm text-body-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
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
          <div className="flex gap-space-sm mt-space-lg">
            <button
              onClick={handleCreate}
              disabled={!title.trim() || createMatter.isPending}
              className="flex items-center gap-space-xs bg-primary text-on-primary px-space-md py-1.5 rounded font-label-md text-label-md hover:bg-primary-container transition-colors shadow-micro disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMatter.isPending ? "Creating..." : "Create Matter"}
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="bg-surface-container-low px-space-md py-1.5 rounded border border-surface-variant text-on-surface-variant font-label-md text-label-md hover:bg-surface-container-high transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Matter list */}
      {isLoading ? (
        <div className="text-center text-on-surface-variant font-body-md text-body-md py-space-xl">
          Loading matters...
        </div>
      ) : !matters?.length ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="w-16 h-16 rounded-xl bg-surface-container flex items-center justify-center mb-space-lg">
            <span className="material-symbols-outlined text-[32px] text-on-surface-variant">folder_open</span>
          </div>
          <h3 className="font-headline-sm text-headline-sm text-on-surface mb-space-xs">
            No matters yet
          </h3>
          <p className="font-body-sm text-body-sm text-on-surface-variant max-w-sm">
            Create a matter to start analyzing case documents
          </p>
        </div>
      ) : (
        <div className="bg-surface-container-lowest rounded-xl shadow-micro border border-surface-variant overflow-hidden">
          {/* Table header */}
          <div className="grid grid-cols-[1fr_150px_160px_100px_100px] gap-space-md px-space-lg py-space-sm border-b border-surface-variant bg-surface-container-low">
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
              Matter
            </span>
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
              Reference
            </span>
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
              Jurisdiction
            </span>
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
              Type
            </span>
            <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold text-right">
              Created
            </span>
          </div>

          {/* Rows */}
          {matters.map((m) => (
            <button
              key={m.id}
              onClick={() => navigate(`/matters/${m.id}`)}
              className="grid grid-cols-[1fr_150px_160px_100px_100px] gap-space-md px-space-lg py-space-sm border-b border-surface-variant last:border-b-0 hover:bg-surface-container transition-colors text-left w-full items-center"
            >
              <div className="flex items-center gap-space-sm min-w-0">
                <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-[16px] text-on-primary-container">
                    {m.status === "archived" ? "inventory_2" : "gavel"}
                  </span>
                </div>
                <span className="font-body-sm text-body-sm text-on-surface font-medium truncate">
                  {m.title}
                </span>
              </div>
              <span className="font-code-sm text-code-sm text-on-surface-variant truncate">
                {m.reference || "—"}
              </span>
              <span className="font-body-sm text-body-sm text-on-surface-variant truncate">
                {m.jurisdiction || "—"}
              </span>
              <span className="font-code-sm text-code-sm text-on-surface-variant capitalize">
                {m.matter_type || "—"}
              </span>
              <span className="font-code-sm text-code-sm text-on-surface-variant text-right">
                {format(new Date(m.created_at), "dd MMM yy")}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
