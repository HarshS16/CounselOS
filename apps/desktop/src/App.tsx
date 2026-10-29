import { Routes, Route, NavLink, useParams, useNavigate } from "react-router-dom";
import { clsx } from "clsx";
import {
  Scale,
  FolderOpen,
  FileText,
  Search,
  Clock,
  GitCompare,
  AlertTriangle,
  Download,
  Settings,
  Plus,
  ChevronLeft,
  Shield,
} from "lucide-react";
import { useMatters, useMatter } from "@/hooks/useApi";
import MatterList from "@/features/matters/MatterList";
import MatterOverview from "@/features/matters/MatterOverview";
import DocumentList from "@/features/documents/DocumentList";
import SearchView from "@/features/search/SearchView";
import ChronologyView from "@/features/chronology/ChronologyView";
import ComparisonView from "@/features/comparison/ComparisonView";
import FindingsReview from "@/features/review/FindingsReview";
import ExportView from "@/features/export/ExportView";
import SettingsView from "@/features/settings/SettingsView";

function MatterSidebar() {
  const { matterId } = useParams();
  const { data: matter } = useMatter(matterId);
  const navigate = useNavigate();

  if (!matterId) return null;

  const links = [
    { to: `/matters/${matterId}`, icon: FolderOpen, label: "Overview", end: true },
    { to: `/matters/${matterId}/documents`, icon: FileText, label: "Documents" },
    { to: `/matters/${matterId}/search`, icon: Search, label: "Search & Ask" },
    { to: `/matters/${matterId}/chronology`, icon: Clock, label: "Chronology" },
    { to: `/matters/${matterId}/compare`, icon: GitCompare, label: "Compare" },
    { to: `/matters/${matterId}/findings`, icon: AlertTriangle, label: "Findings" },
    { to: `/matters/${matterId}/export`, icon: Download, label: "Export" },
  ];

  return (
    <div className="flex flex-col gap-0.5">
      <button
        onClick={() => navigate("/")}
        className="flex items-center gap-2 px-3 py-1.5 text-xs rounded
          text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]
          hover:bg-[var(--color-bg-hover)] transition-colors mb-1"
      >
        <ChevronLeft size={14} />
        All Matters
      </button>

      <div className="px-3 py-2 mb-2">
        <h3 className="text-sm font-semibold text-[var(--color-text-primary)] truncate">
          {matter?.title || "Loading..."}
        </h3>
        {matter?.reference && (
          <p className="text-xs text-[var(--color-text-muted)] truncate mt-0.5">
            {matter.reference}
          </p>
        )}
      </div>

      {links.map(({ to, icon: Icon, label, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            clsx(
              "flex items-center gap-2.5 px-3 py-2 text-sm rounded-md transition-colors",
              isActive
                ? "bg-[var(--color-bg-elevated)] text-[var(--color-accent)]"
                : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)] hover:text-[var(--color-text-primary)]"
            )
          }
        >
          <Icon size={16} />
          {label}
        </NavLink>
      ))}
    </div>
  );
}

function Sidebar() {
  const { matterId } = useParams();
  const { data: matters } = useMatters();
  const navigate = useNavigate();

  return (
    <aside className="w-60 flex-shrink-0 h-full flex flex-col bg-[var(--color-bg-secondary)] border-r border-[var(--color-border-primary)]">
      <div className="flex items-center gap-2 px-4 py-4 border-b border-[var(--color-border-primary)]">
        <Scale size={20} className="text-[var(--color-accent)]" />
        <span className="text-base font-bold tracking-tight">CounselOS</span>
      </div>

      <div className="flex items-center gap-1 px-3 py-2">
        <Shield size={12} className="text-[var(--color-success)]" />
        <span className="text-[10px] text-[var(--color-success)] font-medium tracking-wide uppercase">
          Local · Offline
        </span>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 py-2">
        {matterId ? (
          <MatterSidebar />
        ) : (
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center justify-between px-3 py-1.5 mb-1">
              <span className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">
                Matters
              </span>
              <button
                onClick={() => navigate("/?new=1")}
                className="p-0.5 rounded hover:bg-[var(--color-bg-hover)] text-[var(--color-text-muted)] hover:text-[var(--color-accent)] transition-colors"
                title="New Matter"
              >
                <Plus size={14} />
              </button>
            </div>

            {matters?.map((m) => (
              <NavLink
                key={m.id}
                to={`/matters/${m.id}`}
                className={({ isActive }) =>
                  clsx(
                    "flex flex-col px-3 py-2 rounded-md transition-colors",
                    isActive
                      ? "bg-[var(--color-bg-elevated)] text-[var(--color-text-primary)]"
                      : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)]"
                  )
                }
              >
                <span className="text-sm truncate">{m.title}</span>
                {m.reference && (
                  <span className="text-xs text-[var(--color-text-muted)] truncate">
                    {m.reference}
                  </span>
                )}
              </NavLink>
            ))}

            {(!matters || matters.length === 0) && (
              <p className="px-3 py-4 text-xs text-[var(--color-text-muted)] text-center">
                No matters yet. Create one to begin.
              </p>
            )}
          </div>
        )}
      </nav>

      <div className="px-2 py-2 border-t border-[var(--color-border-primary)]">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            clsx(
              "flex items-center gap-2.5 px-3 py-2 text-sm rounded-md transition-colors",
              isActive
                ? "bg-[var(--color-bg-elevated)] text-[var(--color-accent)]"
                : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-hover)]"
            )
          }
        >
          <Settings size={16} />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}

function MatterLayout() {
  return (
    <Routes>
      <Route index element={<MatterOverview />} />
      <Route path="documents" element={<DocumentList />} />
      <Route path="search" element={<SearchView />} />
      <Route path="chronology" element={<ChronologyView />} />
      <Route path="compare" element={<ComparisonView />} />
      <Route path="findings" element={<FindingsReview />} />
      <Route path="export" element={<ExportView />} />
    </Routes>
  );
}

export default function App() {
  return (
    <div className="flex h-full">
      <Routes>
        <Route
          path="*"
          element={
            <>
              <Sidebar />
              <main className="flex-1 overflow-y-auto bg-[var(--color-bg-primary)]">
                <Routes>
                  <Route index element={<MatterList />} />
                  <Route path="matters/:matterId/*" element={<MatterLayout />} />
                  <Route path="settings" element={<SettingsView />} />
                </Routes>
              </main>
            </>
          }
        />
      </Routes>
    </div>
  );
}
