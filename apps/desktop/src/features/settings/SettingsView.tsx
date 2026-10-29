import { useHealth, useModelStatus } from "@/hooks/useApi";
import { Settings, Cpu, HardDrive, Shield, CheckCircle2, XCircle } from "lucide-react";

function StatusDot({ ok }: { ok: boolean }) {
  return ok ? (
    <CheckCircle2 size={14} className="text-[var(--color-success)]" />
  ) : (
    <XCircle size={14} className="text-[var(--color-danger)]" />
  );
}

export default function SettingsView() {
  const { data: health } = useHealth();
  const { data: model } = useModelStatus();

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-xl font-bold mb-6">Settings</h1>

      <div className="space-y-4">
        <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
          <div className="flex items-center gap-2 mb-4">
            <Settings size={16} className="text-[var(--color-accent)]" />
            <h2 className="text-sm font-semibold">System Status</h2>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="flex items-center gap-2">
              <StatusDot ok={health?.status === "ok"} />
              <span className="text-sm">Backend Service</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusDot ok={health?.db_connected || false} />
              <span className="text-sm">Database</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusDot ok={health?.llm_available || false} />
              <span className="text-sm">Language Model</span>
            </div>
            <div className="flex items-center gap-2">
              <StatusDot ok={health?.embedding_available || false} />
              <span className="text-sm">Embedding Model</span>
            </div>
          </div>

          {health && (
            <div className="mt-3 text-xs text-[var(--color-text-muted)]">
              Version: {health.version} · Uptime: {Math.round(health.uptime_seconds)}s
            </div>
          )}
        </div>

        <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
          <div className="flex items-center gap-2 mb-4">
            <Cpu size={16} className="text-[var(--color-accent)]" />
            <h2 className="text-sm font-semibold">Model Information</h2>
          </div>

          {model ? (
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-[var(--color-text-muted)]">LLM: </span>
                <span className={model.llm_loaded ? "text-[var(--color-success)]" : "text-[var(--color-danger)]"}>
                  {model.llm_loaded ? "Loaded" : "Not loaded"}
                </span>
              </div>
              <div>
                <span className="text-[var(--color-text-muted)]">Embeddings: </span>
                <span className={model.embedding_loaded ? "text-[var(--color-success)]" : "text-[var(--color-danger)]"}>
                  {model.embedding_loaded ? "Loaded" : "Not loaded"}
                </span>
              </div>
              {model.llm_model_name && (
                <div>
                  <span className="text-[var(--color-text-muted)]">LLM Model: </span>
                  {model.llm_model_name}
                </div>
              )}
              {model.embedding_model_name && (
                <div>
                  <span className="text-[var(--color-text-muted)]">Embedding Model: </span>
                  {model.embedding_model_name}
                </div>
              )}
              {model.llm_context_length && (
                <div>
                  <span className="text-[var(--color-text-muted)]">Context: </span>
                  {model.llm_context_length} tokens
                </div>
              )}
              {model.memory_usage_mb && (
                <div>
                  <span className="text-[var(--color-text-muted)]">Memory: </span>
                  {model.memory_usage_mb.toFixed(0)} MB
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-[var(--color-text-muted)]">Loading model info...</p>
          )}
        </div>

        <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
          <div className="flex items-center gap-2 mb-4">
            <Shield size={16} className="text-[var(--color-success)]" />
            <h2 className="text-sm font-semibold">Privacy & Security</h2>
          </div>

          <div className="space-y-2 text-sm text-[var(--color-text-secondary)]">
            <p>All processing runs locally on this device.</p>
            <p>No case data, documents, or AI outputs are sent to external services.</p>
            <p>The local API is bound to 127.0.0.1 and requires session authentication.</p>
            <p>Document originals are preserved with SHA-256 integrity hashes.</p>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
          <div className="flex items-center gap-2 mb-4">
            <HardDrive size={16} className="text-[var(--color-accent)]" />
            <h2 className="text-sm font-semibold">Storage</h2>
          </div>
          {health?.data_dir && (
            <p className="text-sm text-[var(--color-text-secondary)] mb-2">
              Data directory: <code className="text-xs bg-[var(--color-bg-tertiary)] px-1.5 py-0.5 rounded">{health.data_dir}</code>
            </p>
          )}
          <p className="text-sm text-[var(--color-text-muted)]">
            Data is stored locally in the application data directory.
            Use the backup feature to create encrypted copies.
          </p>
        </div>
      </div>
    </div>
  );
}
