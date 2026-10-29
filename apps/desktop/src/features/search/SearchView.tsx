import { useState } from "react";
import { useParams } from "react-router-dom";
import { Search, MessageSquare, FileText, Loader2, Bot, AlertTriangle } from "lucide-react";
import { useSearch, useAsk } from "@/hooks/useApi";
import { clsx } from "clsx";
import type { QAResponse } from "@/types";

export default function SearchView() {
  const { matterId } = useParams();
  const [query, setQuery] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [mode, setMode] = useState<"search" | "ask">("search");
  const [qaResult, setQaResult] = useState<QAResponse | null>(null);

  const { data: searchResults, isLoading: searching } = useSearch(
    mode === "search" ? matterId : undefined,
    activeQuery
  );
  const askMutation = useAsk(matterId!);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    if (mode === "search") {
      setActiveQuery(query.trim());
    } else {
      setQaResult(null);
      const result = await askMutation.mutateAsync(query.trim());
      setQaResult(result);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-xl font-bold mb-6">Search & Ask</h1>

      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setMode("search")}
          className={clsx(
            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
            mode === "search"
              ? "bg-[var(--color-accent)] text-white"
              : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)]"
          )}
        >
          <Search size={16} />
          Search
        </button>
        <button
          onClick={() => setMode("ask")}
          className={clsx(
            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
            mode === "ask"
              ? "bg-[var(--color-accent)] text-white"
              : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)]"
          )}
        >
          <MessageSquare size={16} />
          Ask a Question
        </button>
      </div>

      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              mode === "search"
                ? "Search across case documents..."
                : "Ask a factual question about this case..."
            }
            className="flex-1 px-4 py-3 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)] text-sm focus:outline-none focus:border-[var(--color-accent)] transition-colors"
          />
          <button
            type="submit"
            disabled={!query.trim() || searching || askMutation.isPending}
            className="px-5 py-3 rounded-xl bg-[var(--color-accent)] text-white text-sm font-medium hover:bg-[var(--color-accent-hover)] disabled:opacity-50 transition-colors"
          >
            {searching || askMutation.isPending ? (
              <Loader2 size={16} className="animate-spin" />
            ) : mode === "search" ? (
              "Search"
            ) : (
              "Ask"
            )}
          </button>
        </div>
      </form>

      {mode === "search" && searchResults && (
        <div className="space-y-3">
          <p className="text-xs text-[var(--color-text-muted)]">
            {searchResults.total_results} results for "{searchResults.query}"
          </p>
          {searchResults.results.map((r, i) => (
            <div
              key={`${r.chunk_id}-${i}`}
              className="p-4 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]"
            >
              <div className="flex items-center gap-2 mb-2">
                <FileText size={14} className="text-[var(--color-accent)]" />
                <span className="text-xs font-medium text-[var(--color-accent)]">
                  {r.document_name}
                </span>
                <span className="text-xs text-[var(--color-text-muted)]">
                  Pages {r.page_start}–{r.page_end}
                </span>
                <span className="text-xs text-[var(--color-text-muted)] ml-auto">
                  {(r.score * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                {r.text}
              </p>
            </div>
          ))}
        </div>
      )}

      {mode === "ask" && qaResult && (
        <div className="space-y-4">
          <div className="p-5 rounded-xl bg-[var(--color-bg-secondary)] border border-[var(--color-border-primary)]">
            <div className="flex items-center gap-2 mb-3">
              <Bot size={16} className="text-[var(--color-accent)]" />
              <span className="text-xs font-medium text-[var(--color-accent)]">AI Answer</span>
              {qaResult.abstained && (
                <span className="text-xs px-2 py-0.5 rounded bg-[color-mix(in_srgb,var(--color-warning)_15%,transparent)] text-[var(--color-warning)]">
                  Insufficient Evidence
                </span>
              )}
              {qaResult.conflicts_detected && (
                <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded bg-[color-mix(in_srgb,var(--color-danger)_15%,transparent)] text-[var(--color-danger)]">
                  <AlertTriangle size={10} />
                  Conflicting Sources
                </span>
              )}
            </div>
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {qaResult.answer}
            </p>
          </div>

          {qaResult.citations.length > 0 && (
            <div>
              <h3 className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-2">
                Sources
              </h3>
              <div className="space-y-2">
                {qaResult.citations.map((c, i) => (
                  <div
                    key={i}
                    className={clsx(
                      "p-3 rounded-lg border text-xs",
                      c.is_valid
                        ? "bg-[var(--color-bg-secondary)] border-[var(--color-border-primary)]"
                        : "bg-[color-mix(in_srgb,var(--color-danger)_5%,transparent)] border-[var(--color-danger)]"
                    )}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <FileText size={12} className="text-[var(--color-accent)]" />
                      <span className="font-medium">{c.document_name}</span>
                      <span className="text-[var(--color-text-muted)]">Page {c.page_start}</span>
                      {!c.is_valid && (
                        <span className="text-[var(--color-danger)]">Citation not verified</span>
                      )}
                    </div>
                    {c.quote && (
                      <p className="text-[var(--color-text-secondary)] italic mt-1">
                        "{c.quote}"
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
