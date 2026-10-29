import { useState } from 'react';
import { Link, Outlet, useParams, useLocation } from 'react-router-dom';
import {
  Scale,
  FolderOpen,
  FileText,
  Search,
  Clock,
  GitCompare,
  CheckSquare,
  Download,
  Settings,
  Shield,
  ChevronRight,
  Menu,
  X,
  Home,
} from 'lucide-react';
import clsx from 'clsx';

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
}

export default function Layout() {
  const { matterId } = useParams();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const matterNav: NavItem[] = matterId
    ? [
        { label: 'Overview', path: `/matters/${matterId}`, icon: <Home size={18} /> },
        { label: 'Documents', path: `/matters/${matterId}/documents`, icon: <FileText size={18} /> },
        { label: 'Search & Ask', path: `/matters/${matterId}/search`, icon: <Search size={18} /> },
        { label: 'Chronology', path: `/matters/${matterId}/chronology`, icon: <Clock size={18} /> },
        { label: 'Compare', path: `/matters/${matterId}/compare`, icon: <GitCompare size={18} /> },
        { label: 'Findings', path: `/matters/${matterId}/findings`, icon: <CheckSquare size={18} /> },
        { label: 'Export', path: `/matters/${matterId}/export`, icon: <Download size={18} /> },
      ]
    : [];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      <aside
        className={clsx(
          'flex flex-col border-r border-zinc-800 bg-zinc-900 transition-all duration-200',
          sidebarOpen ? 'w-64' : 'w-16'
        )}
      >
        <div className="flex items-center justify-between px-4 py-4 border-b border-zinc-800">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <Scale size={24} className="text-amber-500" />
              <span className="text-lg font-semibold tracking-tight">CounselOS</span>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 rounded-md hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
          >
            {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto py-3">
          <div className="px-3 mb-2">
            <Link
              to="/"
              className={clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive('/')
                  ? 'bg-zinc-800 text-zinc-100'
                  : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200'
              )}
            >
              <FolderOpen size={18} />
              {sidebarOpen && <span>All Matters</span>}
            </Link>
          </div>

          {matterId && matterNav.length > 0 && (
            <>
              {sidebarOpen && (
                <div className="px-6 py-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
                  Current Matter
                </div>
              )}
              <div className="px-3 space-y-0.5">
                {matterNav.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={clsx(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                      isActive(item.path)
                        ? 'bg-amber-500/10 text-amber-400 font-medium'
                        : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200'
                    )}
                  >
                    {item.icon}
                    {sidebarOpen && <span>{item.label}</span>}
                  </Link>
                ))}
              </div>
            </>
          )}
        </nav>

        <div className="border-t border-zinc-800">
          <div className="px-3 py-2">
            <Link
              to="/settings"
              className={clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive('/settings')
                  ? 'bg-zinc-800 text-zinc-100'
                  : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200'
              )}
            >
              <Settings size={18} />
              {sidebarOpen && <span>Settings</span>}
            </Link>
          </div>
          {sidebarOpen && (
            <div className="px-4 py-3 flex items-center gap-2 text-xs text-zinc-500">
              <Shield size={14} className="text-emerald-500" />
              <span>All processing is local</span>
            </div>
          )}
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
