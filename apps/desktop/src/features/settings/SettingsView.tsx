import { useHealth, useModelStatus } from "@/hooks/useApi";
import { useTheme } from "@/App";

export default function SettingsView() {
  const { data: health } = useHealth();
  const { data: model } = useModelStatus();
  const { theme, toggle } = useTheme();

  return (
    <div className="px-space-lg py-space-xl max-w-4xl mx-auto">
      <h1 className="font-headline-sm text-headline-sm text-on-surface mb-space-lg">Settings</h1>

      <div className="flex flex-col gap-space-lg">
        {/* Appearance */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
          <div className="flex items-center gap-space-sm mb-space-md">
            <span className="material-symbols-outlined text-[18px] text-primary">
              {theme === "light" ? "light_mode" : "dark_mode"}
            </span>
            <h2 className="font-title text-[14px] text-on-surface">Appearance</h2>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-body-sm text-body-sm text-on-surface">Theme</p>
              <p className="font-label-sm text-label-sm text-on-surface-variant mt-0.5">
                Switch between light and dark mode
              </p>
            </div>
            <button
              onClick={toggle}
              className="flex items-center gap-space-xs bg-surface-container-low px-space-md py-1.5 rounded border border-surface-variant text-on-surface hover:bg-surface-container-high transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">
                {theme === "light" ? "dark_mode" : "light_mode"}
              </span>
              <span className="font-label-md text-label-md">
                {theme === "light" ? "Dark Mode" : "Light Mode"}
              </span>
            </button>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
          <div className="flex items-center gap-space-sm mb-space-md">
            <span className="material-symbols-outlined text-[18px] text-primary">settings</span>
            <h2 className="font-title text-[14px] text-on-surface">System Status</h2>
          </div>

          <div className="grid grid-cols-2 gap-space-sm">
            {[
              { label: "Backend Service", ok: health?.status === "ok" },
              { label: "Database", ok: health?.db_connected || false },
              { label: "Language Model", ok: health?.llm_available || false },
              { label: "Embedding Model", ok: health?.embedding_available || false },
            ].map(({ label, ok }) => (
              <div key={label} className="p-space-sm rounded-lg bg-surface-container-low flex items-center gap-space-sm">
                <span className={`w-2 h-2 rounded-full ${ok ? "bg-tertiary" : "bg-error"}`} />
                <span className="font-body-sm text-body-sm text-on-surface">{label}</span>
                <span className={`ml-auto font-code-sm text-code-sm ${ok ? "text-tertiary" : "text-error"}`}>
                  {ok ? "Online" : "Offline"}
                </span>
              </div>
            ))}
          </div>

          {health && (
            <div className="mt-space-md pt-space-sm border-t border-surface-variant flex items-center gap-space-lg font-code-sm text-code-sm text-on-surface-variant">
              <span>Version: {health.version}</span>
              <span>Uptime: {Math.round(health.uptime_seconds)}s</span>
            </div>
          )}
        </div>

        {/* Model Information */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
          <div className="flex items-center gap-space-sm mb-space-md">
            <span className="material-symbols-outlined text-[18px] text-primary">memory</span>
            <h2 className="font-title text-[14px] text-on-surface">Model Information</h2>
          </div>

          {model ? (
            <div className="grid grid-cols-2 gap-space-sm">
              <div className="p-space-sm rounded-lg bg-surface-container-low flex flex-col gap-1">
                <span className="font-label-sm text-label-sm text-on-surface-variant">LLM Status</span>
                <span className={`font-body-sm text-body-sm ${model.llm_loaded ? "text-tertiary" : "text-error"}`}>
                  {model.llm_loaded ? "Loaded" : "Not loaded"}
                </span>
              </div>
              <div className="p-space-sm rounded-lg bg-surface-container-low flex flex-col gap-1">
                <span className="font-label-sm text-label-sm text-on-surface-variant">Embeddings</span>
                <span className={`font-body-sm text-body-sm ${model.embedding_loaded ? "text-tertiary" : "text-error"}`}>
                  {model.embedding_loaded ? "Loaded" : "Not loaded"}
                </span>
              </div>
              {model.llm_model_name && (
                <div className="p-space-sm rounded-lg bg-surface-container-low flex flex-col gap-1">
                  <span className="font-label-sm text-label-sm text-on-surface-variant">LLM Model</span>
                  <span className="font-code-sm text-code-sm text-on-surface">{model.llm_model_name}</span>
                </div>
              )}
              {model.embedding_model_name && (
                <div className="p-space-sm rounded-lg bg-surface-container-low flex flex-col gap-1">
                  <span className="font-label-sm text-label-sm text-on-surface-variant">Embedding Model</span>
                  <span className="font-code-sm text-code-sm text-on-surface">{model.embedding_model_name}</span>
                </div>
              )}
              {model.llm_context_length && (
                <div className="p-space-sm rounded-lg bg-surface-container-low flex flex-col gap-1">
                  <span className="font-label-sm text-label-sm text-on-surface-variant">Context Length</span>
                  <span className="font-code-md text-code-md text-on-surface">{model.llm_context_length.toLocaleString()} tokens</span>
                </div>
              )}
              {model.memory_usage_mb && (
                <div className="p-space-sm rounded-lg bg-surface-container-low flex flex-col gap-1">
                  <span className="font-label-sm text-label-sm text-on-surface-variant">Memory Usage</span>
                  <span className="font-code-md text-code-md text-on-surface">{model.memory_usage_mb.toFixed(0)} MB</span>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-space-sm text-on-surface-variant py-space-md">
              <span className="material-symbols-outlined text-[16px] animate-spin">autorenew</span>
              <span className="font-body-sm text-body-sm">Loading model info...</span>
            </div>
          )}
        </div>

        {/* Privacy & Security */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
          <div className="flex items-center gap-space-sm mb-space-md">
            <span className="material-symbols-outlined text-[18px] text-tertiary">shield</span>
            <h2 className="font-title text-[14px] text-on-surface">Privacy & Security</h2>
          </div>

          <div className="flex flex-col gap-space-sm">
            {[
              { icon: "lock", text: "All processing runs locally on this device." },
              { icon: "cloud_off", text: "No case data, documents, or AI outputs are sent to external services." },
              { icon: "vpn_lock", text: "The local API is bound to 127.0.0.1 and requires session authentication." },
              { icon: "verified_user", text: "Document originals are preserved with SHA-256 integrity hashes." },
            ].map(({ icon, text }) => (
              <div key={icon} className="flex items-start gap-space-sm p-space-sm rounded-lg bg-surface-container-low">
                <span className="material-symbols-outlined text-[16px] text-tertiary mt-0.5">{icon}</span>
                <span className="font-body-sm text-body-sm text-on-surface-variant">{text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Storage */}
        <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-micro">
          <div className="flex items-center gap-space-sm mb-space-md">
            <span className="material-symbols-outlined text-[18px] text-primary">hard_drive</span>
            <h2 className="font-title text-[14px] text-on-surface">Storage</h2>
          </div>

          {health?.data_dir && (
            <div className="p-space-sm rounded-lg bg-surface-container-low mb-space-md">
              <span className="font-label-sm text-label-sm text-on-surface-variant block mb-1">Data Directory</span>
              <code className="font-code-md text-code-md text-on-surface">{health.data_dir}</code>
            </div>
          )}
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            Data is stored locally in the application data directory.
            Use the backup feature to create encrypted copies.
          </p>
        </div>
      </div>
    </div>
  );
}
