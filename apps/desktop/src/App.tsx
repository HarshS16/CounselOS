import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { Routes, Route, NavLink, useParams, useNavigate } from "react-router-dom";
import { clsx } from "clsx";
import { useMatters, useMatter, useFindings } from "@/hooks/useApi";
import MatterList from "@/features/matters/MatterList";
import MatterOverview from "@/features/matters/MatterOverview";
import DocumentList from "@/features/documents/DocumentList";
import SearchView from "@/features/search/SearchView";
import ChronologyView from "@/features/chronology/ChronologyView";
import ComparisonView from "@/features/comparison/ComparisonView";
import FindingsReview from "@/features/review/FindingsReview";
import ExportView from "@/features/export/ExportView";
import SettingsView from "@/features/settings/SettingsView";

type Theme = "light" | "dark";

const ThemeContext = createContext<{
  theme: Theme;
  toggle: () => void;
}>({ theme: "light", toggle: () => {} });

export function useTheme() {
  return useContext(ThemeContext);
}

function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      const saved = localStorage.getItem("counselos-theme") as Theme | null;
      return saved === "dark" ? "dark" : "light";
    } catch {
      return "light";
    }
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("counselos-theme", theme);
    } catch {}
  }, [theme]);

  const toggle = () => setTheme((t) => (t === "light" ? "dark" : "light"));

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}

function Icon({ name, className }: { name: string; className?: string }) {
  return (
    <span className={clsx("material-symbols-outlined", className)}>{name}</span>
  );
}

interface NavItemProps {
  to: string;
  icon?: string;
  label: string;
  badge?: string | number;
  badgeClass?: string;
  end?: boolean;
}

function NavItem({ to, icon, label, badge, badgeClass, end }: NavItemProps) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        clsx(
          "flex items-center justify-between px-space-sm py-1.5 rounded transition-colors",
          isActive
            ? "bg-primary-container text-on-primary-container font-semibold shadow-micro"
            : "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface"
        )
      }
    >
      <span className="font-body-sm text-body-sm flex items-center gap-space-sm">
        {icon && <Icon name={icon} className="text-[16px]" />}
        {label}
      </span>
      {badge !== undefined && badge !== 0 && (
        <span
          className={clsx(
            "font-code-sm text-code-sm px-1.5 py-0.5 rounded font-medium",
            badgeClass || "bg-surface-container-high text-on-surface-variant"
          )}
        >
          {badge}
        </span>
      )}
    </NavLink>
  );
}

function MatterSidebar() {
  const { matterId } = useParams();
  const { data: matter } = useMatter(matterId);
  const { data: findings } = useFindings(matterId);
  const navigate = useNavigate();

  if (!matterId) return null;

  const pendingCount = findings?.filter((f) => f.review_status === "pending").length || 0;
  const basePath = `/matters/${matterId}`;

  return (
    <>
      {/* Active matter selector */}
      <div className="px-space-md py-space-sm bg-surface-container border-t border-b border-surface-variant flex items-center justify-between cursor-pointer hover:bg-surface-container-high transition-colors"
        onClick={() => navigate("/")}
      >
        <div className="flex flex-col min-w-0 pr-space-xs">
          <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider font-semibold">
            Active Matter
          </span>
          <span className="font-title text-[13px] leading-tight text-on-surface truncate">
            {matter?.title || "Loading..."}
          </span>
          <span className="font-code-sm text-[10px] leading-none text-on-surface-variant truncate mt-0.5">
            {matter?.reference || ""}{matter?.jurisdiction ? ` · ${matter.jurisdiction}` : ""}
          </span>
        </div>
        <Icon name="unfold_more" className="text-[18px] text-on-surface-variant" />
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto px-space-sm py-space-md flex flex-col gap-space-lg">
        <nav className="flex flex-col gap-0.5">
          <div className="px-space-sm py-1 font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
            Input & Search
          </div>
          <NavItem to={basePath} label="Overview" end />
          <NavItem to={`${basePath}/documents`} label="Documents" />
          <NavItem to={`${basePath}/search`} label="Search & Ask" />
        </nav>

        <nav className="flex flex-col gap-0.5">
          <div className="px-space-sm py-1 font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
            Analysis
          </div>
          <NavItem to={`${basePath}/chronology`} label="Chronology" />
          <NavItem to={`${basePath}/compare`} label="Compare" />
          <NavItem
            to={`${basePath}/findings`}
            label="Findings"
            badge={pendingCount > 0 ? `${pendingCount} pending` : undefined}
            badgeClass="bg-secondary-fixed text-on-secondary-fixed text-[10px] font-semibold"
          />
        </nav>

        <nav className="flex flex-col gap-0.5">
          <div className="px-space-sm py-1 font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
            Case Work
          </div>
          <NavItem to={`${basePath}/export`} label="Export" />
        </nav>
      </div>
    </>
  );
}

function GlobalSidebar() {
  const { data: matters } = useMatters();
  const navigate = useNavigate();

  return (
    <>
      <div className="flex-1 overflow-y-auto px-space-sm py-space-md flex flex-col gap-space-lg">
        <nav className="flex flex-col gap-0.5">
          <div className="px-space-sm py-1 font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
            Navigation
          </div>
          <NavItem to="/" label="All Matters" icon="folder_open" end />
          <NavItem to="/settings" label="Settings" icon="settings" />
        </nav>

        <nav className="flex flex-col gap-0.5">
          <div className="flex items-center justify-between px-space-sm py-1">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              Recent Matters
            </span>
            <button
              onClick={() => navigate("/?new=1")}
              className="p-0.5 rounded hover:bg-surface-container text-on-surface-variant hover:text-on-surface transition-colors"
              title="New Matter"
            >
              <Icon name="add" className="text-[16px]" />
            </button>
          </div>
          {matters?.slice(0, 8).map((m) => (
            <NavLink
              key={m.id}
              to={`/matters/${m.id}`}
              className={({ isActive }) =>
                clsx(
                  "flex flex-col px-space-sm py-1.5 rounded transition-colors",
                  isActive
                    ? "bg-primary-container text-on-primary-container font-semibold shadow-micro"
                    : "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface"
                )
              }
            >
              <span className="font-body-sm text-body-sm truncate">{m.title}</span>
              {m.reference && (
                <span className="font-code-sm text-[10px] text-on-surface-variant truncate mt-0.5">
                  {m.reference}
                </span>
              )}
            </NavLink>
          ))}
          {(!matters || matters.length === 0) && (
            <p className="px-space-sm py-4 text-body-sm text-on-surface-variant text-center">
              No matters yet
            </p>
          )}
        </nav>
      </div>
    </>
  );
}

function Sidebar() {
  const { matterId } = useParams();
  const { theme, toggle } = useTheme();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-[260px] bg-surface-container-low z-50 flex flex-col justify-between shadow-micro">
      <div className="flex flex-col h-full overflow-hidden">
        {/* Logo */}
        <div className="p-space-lg flex flex-col gap-space-sm bg-surface-container-lowest">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-sm">
              <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center">
                <Icon name="balance" className="text-[18px] text-on-primary-container" />
              </div>
              <span className="font-headline-sm text-headline-sm text-on-surface tracking-tight">
                CounselOS
              </span>
            </div>
            <span className="font-code-sm text-code-sm bg-surface-container text-tertiary px-space-xs py-0.5 rounded font-semibold">
              v2.0
            </span>
          </div>
          <div className="flex items-center gap-space-xs px-space-sm py-1 bg-surface-container rounded-lg self-start">
            <span className="w-2 h-2 rounded-full bg-tertiary animate-pulse" />
            <span className="font-code-sm text-code-sm text-tertiary tracking-wider font-semibold">
              LOCAL · SECURE
            </span>
          </div>
        </div>

        {/* Context-dependent navigation */}
        {matterId ? <MatterSidebar /> : <GlobalSidebar />}

        {/* Bottom bar */}
        <div className="p-space-sm bg-surface-container-lowest border-t border-surface-variant flex flex-col gap-space-xs">
          <div className="flex items-center justify-between px-space-xs py-1 text-on-surface-variant">
            <button
              className="p-1 rounded hover:bg-surface-container hover:text-on-surface transition-colors"
              title="Quick Export"
            >
              <Icon name="download" className="text-[18px]" />
            </button>
            <NavLink
              to="/settings"
              className="p-1 rounded hover:bg-surface-container hover:text-on-surface transition-colors"
              title="Settings"
            >
              <Icon name="settings" className="text-[18px]" />
            </NavLink>
            <button
              onClick={toggle}
              className="p-1 rounded hover:bg-surface-container hover:text-on-surface transition-colors"
              title="Toggle Theme"
            >
              <Icon name={theme === "light" ? "light_mode" : "dark_mode"} className="text-[18px]" />
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}

function Header() {
  const navigate = useNavigate();

  return (
    <header className="fixed top-0 left-[260px] right-0 h-14 bg-surface-container-lowest z-40 flex items-center justify-between px-space-lg shadow-micro">
      <div className="flex items-center gap-space-md">
        <div className="flex items-center gap-space-xs text-on-surface-variant text-label-md">
          <Icon name="gavel" className="text-[16px]" />
          <span className="font-body-sm text-body-sm text-on-surface-variant">
            Tauri Desktop · Session Active
          </span>
        </div>
      </div>
      <div className="flex items-center gap-space-md">
        <button
          className="flex items-center justify-between gap-space-lg bg-surface-container-low px-space-md py-1.5 rounded border border-surface-variant text-on-surface-variant hover:text-on-surface hover:border-outline transition-colors w-72"
          type="button"
        >
          <div className="flex items-center gap-space-xs">
            <Icon name="search" className="text-[18px]" />
            <span className="font-body-sm text-body-sm truncate">Search matter facts...</span>
          </div>
          <kbd className="font-code-sm text-[10px] px-1.5 py-0.5 rounded bg-surface-container border border-surface-variant text-on-surface-variant">
            Ctrl+K
          </kbd>
        </button>
        <div className="flex items-center gap-1.5 bg-surface-container px-space-sm py-1 rounded text-tertiary font-code-sm text-code-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-tertiary" />
          <span>LOCAL ONLY</span>
        </div>
        <button
          onClick={() => navigate("/?new=1")}
          className="flex items-center gap-space-xs bg-primary text-on-primary px-space-md py-1.5 rounded font-label-md text-label-md hover:bg-primary-container transition-colors shadow-micro"
          type="button"
        >
          <Icon name="add" className="text-[16px]" />
          <span>New Matter</span>
        </button>
      </div>
    </header>
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
    <ThemeProvider>
      <div className="flex h-full">
        <Routes>
          <Route
            path="*"
            element={
              <>
                <Sidebar />
                <Header />
                <main className="pl-[260px] pt-14 flex-1 overflow-y-auto bg-background min-h-screen">
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
    </ThemeProvider>
  );
}
