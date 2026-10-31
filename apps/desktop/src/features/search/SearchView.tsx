import { useState } from "react";
import { useParams } from "react-router-dom";
import { useSearch, useAsk } from "@/hooks/useApi";
import { clsx } from "clsx";
import type { QAResponse } from "@/types";

type Mode = "ask" | "search";

export default function SearchView() {
  const { matterId } = useParams();
  const [query, setQuery] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [mode, setMode] = useState<Mode>("ask");
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

  const modeTabs: { key: Mode; icon: string; label: string }[] = [
    { key: "ask", icon: "smart_toy", label: "Ask AI" },
    { key: "search", icon: "manage_search", label: "Keyword Search" },
  ];

  return (
    <div className="px-space-lg py-space-xl">
      {/* Header & Mode Toggle */}
      <div className="flex flex-col gap-space-xs mb-space-lg">
        <div className="flex flex-wrap items-baseline justify-between gap-space-md">
          <div>
            <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tight">
              Search & Ask
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-0.5">
              Find facts or ask questions across case documents with verifiable citations.
            </p>
          </div>
          <div className="flex items-center gap-1 bg-surface-container-low p-1 rounded-lg">
            {modeTabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setMode(tab.key)}
                className={clsx(
                  "flex items-center gap-1.5 px-space-md py-1 rounded font-label-md text-label-md transition-all",
                  mode === tab.key
                    ? "bg-primary text-on-primary shadow-micro"
                    : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container"
                )}
              >
                <span className="material-symbols-outlined text-[16px]">
                  {tab.icon}
                </span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Query Box */}
      <div className="bg-surface-container-lowest rounded-xl shadow-micro p-space-md mb-space-lg">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <div className="absolute left-space-md flex items-center pointer-events-none text-outline">
            <span className="material-symbols-outlined text-[24px]">search</span>
          </div>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              mode === "search"
                ? "Search across case documents..."
                : "Ask a question across case record, witness depositions, or pleadings..."
            }
            className="w-full h-[52px] pl-12 pr-32 bg-surface-container-low rounded-lg text-on-surface font-body-lg text-body-lg placeholder:text-outline focus:outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary"
          />
          <div className="absolute right-2 flex items-center gap-1.5">
            {query && (
              <button
                type="button"
                onClick={() => setQuery("")}
                className="p-1.5 rounded hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            )}
            <button
              type="submit"
              disabled={!query.trim() || searching || askMutation.isPending}
              className="flex items-center gap-1.5 h-9 px-space-md bg-primary hover:bg-primary-container text-on-primary rounded font-label-md text-label-md shadow-micro transition-all disabled:opacity-50"
            >
              {searching || askMutation.isPending ? (
                <span className="material-symbols-outlined text-[16px] animate-spin">
                  autorenew
                </span>
              ) : (
                <>
                  <span>{mode === "search" ? "Search" : "Ask AI"}</span>
                  <span className="material-symbols-outlined text-[16px]">
                    arrow_forward
                  </span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Search Results */}
      {mode === "search" && searchResults && (
        <div className="flex flex-col gap-space-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-xs">
              <span className="font-title text-title text-on-surface font-semibold">
                Search Results
              </span>
              <span className="font-code-sm text-code-sm bg-surface-container px-2 py-0.5 rounded text-on-surface-variant font-semibold">
                {searchResults.total_results} Found
              </span>
            </div>
            <span className="font-body-sm text-body-sm text-on-surface-variant">
              Query: &ldquo;{searchResults.query}&rdquo;
            </span>
          </div>

          {searchResults.results.map((r, i) => (
            <div
              key={`${r.chunk_id}-${i}`}
              className="bg-surface-container-lowest rounded-xl p-space-md shadow-micro hover:shadow-overlay transition-all flex flex-col gap-space-xs group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-space-xs min-w-0">
                  <span className="material-symbols-outlined text-[20px] text-primary">
                    description
                  </span>
                  <div className="flex flex-col min-w-0">
                    <span className="font-title text-[13px] leading-tight text-on-surface font-semibold truncate group-hover:text-primary transition-colors">
                      {r.document_name}
                    </span>
                    <span className="font-code-sm text-[11px] text-on-surface-variant">
                      Pages {r.page_start}–{r.page_end}
                    </span>
                  </div>
                </div>
                <span className="font-code-sm text-code-sm px-1.5 py-0.5 bg-primary/10 text-primary rounded font-semibold shrink-0">
                  {(r.score * 100).toFixed(0)}% Match
                </span>
              </div>
              <div className="bg-surface-container-low rounded p-space-sm font-body-sm text-body-sm text-on-surface leading-normal mt-1">
                {r.text}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* AI Answer */}
      {mode === "ask" && qaResult && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
          {/* Left: AI Synthesis */}
          <div className="lg:col-span-7 flex flex-col gap-space-md">
            <div className="bg-surface-container-lowest rounded-xl shadow-micro p-space-lg flex flex-col gap-space-md relative overflow-hidden">
              <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-primary/5 pointer-events-none blur-2xl" />

              {/* Synthesis header */}
              <div className="flex flex-wrap items-center justify-between gap-space-xs pb-space-xs">
                <div className="flex items-center gap-space-sm">
                  <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse" />
                  <span className="font-label-md text-label-md uppercase tracking-wider text-primary font-semibold">
                    LOCAL LEGAL AI SYNTHESIS
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  {!qaResult.abstained && (
                    <span className="flex items-center gap-1 bg-surface-container px-space-sm py-0.5 rounded-full text-tertiary">
                      <span className="material-symbols-outlined text-[15px]">
                        verified_user
                      </span>
                      <span className="font-code-sm text-code-sm font-semibold">
                        Sourced from case documents
                      </span>
                    </span>
                  )}
                  {qaResult.abstained && (
                    <span className="flex items-center gap-1 bg-error-container px-space-sm py-0.5 rounded-full text-on-error-container">
                      <span className="material-symbols-outlined text-[15px]">
                        warning
                      </span>
                      <span className="font-code-sm text-code-sm font-semibold">
                        Insufficient Evidence
                      </span>
                    </span>
                  )}
                </div>
              </div>

              {/* Answer body */}
              <div className="font-body-md text-body-md text-on-surface leading-relaxed whitespace-pre-wrap">
                {qaResult.answer}
              </div>

              {/* Conflict callout */}
              {qaResult.conflicts_detected && qaResult.conflict_explanation && (
                <div className="bg-surface-container-high rounded-lg p-space-md flex items-start gap-space-sm shadow-micro">
                  <div className="p-1 rounded bg-error-container text-on-error-container flex items-center justify-center shrink-0 mt-0.5">
                    <span className="material-symbols-outlined text-[20px]">
                      warning
                    </span>
                  </div>
                  <div className="flex flex-col gap-0.5">
                    <span className="font-label-md text-label-md text-on-surface font-semibold">
                      Conflicting Sources Detected
                    </span>
                    <p className="font-body-sm text-body-sm text-on-surface-variant">
                      {qaResult.conflict_explanation}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Citations */}
          <div className="lg:col-span-5 flex flex-col gap-space-md">
            {qaResult.citations.length > 0 && (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-space-xs">
                    <span className="font-title text-title text-on-surface font-semibold">
                      Source Citations
                    </span>
                    <span className="font-code-sm text-code-sm bg-surface-container px-2 py-0.5 rounded text-on-surface-variant font-semibold">
                      {qaResult.citations.length} Found
                    </span>
                  </div>
                </div>

                {qaResult.citations.map((c, i) => (
                  <div
                    key={i}
                    className={clsx(
                      "bg-surface-container-lowest rounded-xl p-space-md shadow-micro flex flex-col gap-space-xs group",
                      !c.is_valid && "border-l-[3px] border-error"
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-space-xs min-w-0">
                        <span
                          className={clsx(
                            "material-symbols-outlined text-[18px]",
                            c.is_valid ? "text-primary" : "text-error"
                          )}
                        >
                          description
                        </span>
                        <span className="font-label-md text-label-md text-on-surface font-semibold">
                          {c.document_name}
                        </span>
                        <span className="font-code-sm text-code-sm bg-surface-container px-1.5 py-0.5 rounded text-on-surface-variant font-medium">
                          Page {c.page_start}
                          {c.page_end !== c.page_start && `–${c.page_end}`}
                        </span>
                      </div>
                      {!c.is_valid && (
                        <span className="font-code-sm text-code-sm bg-error-container text-on-error-container px-1.5 py-0.5 rounded font-semibold">
                          Unverified
                        </span>
                      )}
                    </div>
                    {c.quote && (
                      <div className="bg-surface-container-low rounded p-space-sm font-body-sm text-body-sm text-on-surface italic leading-normal mt-1">
                        &ldquo;{c.quote}&rdquo;
                      </div>
                    )}
                  </div>
                ))}
              </>
            )}
          </div>
        </div>
      )}

      {/* Empty states */}
      {mode === "search" && !searchResults && !searching && activeQuery === "" && (
        <div className="flex flex-col items-center justify-center py-space-xl text-center">
          <span className="material-symbols-outlined text-[48px] text-outline mb-space-md">
            manage_search
          </span>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Enter a keyword to search across all case documents.
          </p>
        </div>
      )}

      {mode === "ask" && !qaResult && !askMutation.isPending && (
        <div className="flex flex-col items-center justify-center py-space-xl text-center">
          <span className="material-symbols-outlined text-[48px] text-outline mb-space-md">
            smart_toy
          </span>
          <p className="font-body-md text-body-md text-on-surface-variant">
            Ask a factual question about this case. Answers are generated locally with verifiable citations.
          </p>
        </div>
      )}
    </div>
  );
}
