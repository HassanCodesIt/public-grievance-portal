import { useEffect, useRef, useState, type ReactNode } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router";
import {
  AlertCircle,
  BarChart3,
  Bell,
  Building2,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  ClipboardList,
  Clock3,
  FileText,
  Gauge,
  Home,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  Search,
  ShieldCheck,
  Star,
  UserRound,
  X,
} from "lucide-react";
import type { Priority, Role, Status, HistoryEntry } from "./api";

export const disclaimer =
  "Recruitment prototype. Not affiliated with or endorsed by the Government of Kerala or the Chief Minister's Office. All data is fictional.";

export function Logo({ light = false }: { light?: boolean }) {
  return (
    <Link to="/" className="logo" aria-label="Janasevanam Public Grievance Redressal Portal home">
      <span className={light ? "logo-mark light" : "logo-mark"}>
        <MessageSquare size={20} />
      </span>
      <span>
        <strong lang="ml">ജനസേവനം</strong>
        <small>Janasevanam</small>
      </span>
    </Link>
  );
}

export function StatusBadge({ status }: { status: Status }) {
  return (
    <span className={`badge status-${status.toLowerCase().replace(/ /g, "-")}`}>
      <span className="badge-dot" />
      {status}
    </span>
  );
}
export function PriorityChip({ priority }: { priority: Priority }) {
  return <span className={`badge priority-${priority.toLowerCase()}`}>{priority}</span>;
}
export function AssignmentChip({ value }: { value: string }) {
  return <span className="badge assignment">{value}</span>;
}

const publicLinks = [
  ["/", "Home"],
  ["/about", "About"],
  ["/how-it-works", "How it works"],
  ["/departments", "Departments"],
  ["/faq", "FAQ"],
  ["/contact", "Contact"],
];
const roleHome = (role: Role | null) =>
  role === "cmo_admin" ? "/cmo" : role === "officer" ? "/officer" : "/citizen";

export function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [userOpen, setUserOpen] = useState(false);
  const role = localStorage.getItem("role") as Role | null;
  const name = localStorage.getItem("name") || "Demo user";
  const portal =
    location.pathname.startsWith("/citizen") ||
    location.pathname.startsWith("/cmo") ||
    location.pathname.startsWith("/officer");

  useEffect(() => {
    const section = location.pathname.startsWith("/citizen/submit")
      ? "Submit Grievance"
      : location.pathname.startsWith("/citizen/grievances/")
        ? "Grievance Detail"
        : location.pathname === "/citizen"
          ? "Citizen Dashboard"
          : location.pathname.startsWith("/cmo/grievances/")
            ? "CMO Grievance Detail"
            : location.pathname === "/cmo"
              ? "CMO Dashboard"
              : location.pathname.startsWith("/officer/grievances/")
                ? "Officer Grievance Detail"
                : location.pathname === "/officer"
                  ? "Officer Dashboard"
                  : (
                      {
                        "/": "Home",
                        "/about": "About",
                        "/how-it-works": "How It Works",
                        "/departments": "Departments",
                        "/contact": "Contact",
                        "/faq": "FAQ",
                        "/track": "Track Grievance",
                        "/login": "Log In",
                        "/register": "Register",
                      } as Record<string, string>
                    )[location.pathname] || "Public Grievance Redressal Portal";
    document.title = `${section} | ജനസേവനം · Janasevanam`;
  }, [location.pathname]);

  const logout = () => {
    localStorage.removeItem("role");
    localStorage.removeItem("name");
    navigate("/login");
    setUserOpen(false);
  };
  return (
    <div className="app">
      <div className="prototype-banner">{disclaimer}</div>
      <header className="topbar">
        <div className="topbar-inner">
          <Logo />
          <nav className="desktop-nav" aria-label="Primary navigation">
            {!portal &&
              publicLinks.map(([to, label]) => (
                <NavLink key={to} to={to} className={({ isActive }) => (isActive ? "active" : "")}>
                  {label}
                </NavLink>
              ))}
          </nav>
          <div className="header-actions">
            {role ? (
              <>
                <button className="icon-btn" aria-label="Notifications">
                  <Bell size={20} />
                </button>
                <div className="user-menu">
                  <button
                    className="user-trigger"
                    onClick={() => setUserOpen(!userOpen)}
                    aria-expanded={userOpen}
                  >
                    <span className="avatar">{name[0]}</span>
                    <span className="user-copy">
                      <strong>{name}</strong>
                      <small>
                        {role === "cmo_admin"
                          ? "CMO Admin"
                          : role === "officer"
                            ? "Officer"
                            : "Citizen"}
                      </small>
                    </span>
                    <ChevronDown size={16} />
                  </button>
                  {userOpen && (
                    <div className="menu-popover">
                      <Link to={roleHome(role)} onClick={() => setUserOpen(false)}>
                        <LayoutDashboard size={16} /> Dashboard
                      </Link>
                      <button onClick={logout}>
                        <LogOut size={16} /> Log out
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link className="text-link" to="/login">
                  Log in
                </Link>
                <Link className="btn small" to="/register">
                  Register
                </Link>
              </>
            )}
            <button
              className="icon-btn mobile-menu-btn"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Toggle navigation"
            >
              <Menu size={22} />
            </button>
          </div>
        </div>
        {menuOpen && (
          <div className="mobile-nav">
            {(portal && role ? portalNav(role) : publicLinks).map(([to, label]) => (
              <Link key={to} to={to} onClick={() => setMenuOpen(false)}>
                {label}
              </Link>
            ))}
          </div>
        )}
      </header>
      <div className={portal ? "portal-layout" : ""}>
        {portal && role && <Sidebar role={role} />}
        <main className={portal ? "portal-main" : "public-main"}>
          <Outlet />
        </main>
      </div>
      <Footer compact={portal} />
    </div>
  );
}

function portalNav(role: Role): string[][] {
  if (role === "cmo_admin")
    return [
      ["/cmo", "Overview"],
      ["/cmo/grievances/1", "Review grievance"],
    ];
  if (role === "officer")
    return [
      ["/officer", "Assigned grievances"],
      ["/officer/grievances/3", "Action report"],
    ];
  return [
    ["/citizen", "My dashboard"],
    ["/citizen/submit", "Submit grievance"],
    ["/track", "Track grievance"],
  ];
}
function Sidebar({ role }: { role: Role }) {
  const icons = [LayoutDashboard, ClipboardList, Search];
  return (
    <aside className="sidebar">
      <div className="sidebar-label">
        {role === "cmo_admin"
          ? "CMO workspace"
          : role === "officer"
            ? "Officer workspace"
            : "Citizen portal"}
      </div>
      <nav>
        {portalNav(role).map(([to, label], index) => {
          const Icon = icons[index] || FileText;
          return (
            <NavLink
              key={to}
              to={to}
              end={to.split("/").length === 2}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              <Icon size={19} />
              {label}
            </NavLink>
          );
        })}
      </nav>
      <div className="sidebar-help">
        <CircleHelp size={20} />
        <div>
          <strong>Need help?</strong>
          <span>View FAQs or contact the support team.</span>
        </div>
      </div>
    </aside>
  );
}

export function Footer({ compact = false }: { compact?: boolean }) {
  return (
    <footer className={compact ? "footer compact" : "footer"}>
      {!compact && (
        <div className="footer-main">
          <div>
            <Logo light />
            <p>Janasevanam is a clear, accessible way to raise and track civic service concerns.</p>
          </div>
          <div>
            <strong>Quick links</strong>
            <Link to="/how-it-works">How it works</Link>
            <Link to="/departments">Departments</Link>
            <Link to="/faq">Frequently asked questions</Link>
          </div>
          <div>
            <strong>Fictional contact</strong>
            <span>1800 123 4567</span>
            <span>support@janasevanam.example.test</span>
            <span>Monday–Friday, 9:00–17:00</span>
          </div>
        </div>
      )}
      <div className="footer-bottom">{disclaimer}</div>
    </footer>
  );
}

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}
export function Button({
  children,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "amber" | "danger" | "ghost";
}) {
  return (
    <button className={`btn ${variant}`} {...props}>
      {children}
    </button>
  );
}
export function Field({
  label,
  error,
  hint,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small className="hint">{hint}</small>}
      {error && (
        <small className="field-error">
          <AlertCircle size={14} />
          {error}
        </small>
      )}
    </label>
  );
}
export function SelectField({
  label,
  value,
  onChange,
  options,
  placeholder = "Select an option",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: readonly string[];
  placeholder?: string;
}) {
  return (
    <Field label={label}>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option}>{option}</option>
        ))}
      </select>
    </Field>
  );
}
export function CountCard({
  label,
  value,
  icon: Icon,
  tone = "teal",
  detail,
}: {
  label: string;
  value: string | number;
  icon: typeof Gauge;
  tone?: string;
  detail?: string;
}) {
  return (
    <article className={`count-card ${tone}`}>
      <div className="count-icon">
        <Icon size={22} />
      </div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        {detail && <small>{detail}</small>}
      </div>
    </article>
  );
}
export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`card ${className}`}>{children}</section>;
}

export function HistoryTimeline({
  history,
  publicOnly = false,
}: {
  history: HistoryEntry[];
  publicOnly?: boolean;
}) {
  const items = publicOnly ? history.filter((item) => item.visibility === "Public") : history;
  return (
    <ol className="timeline">
      {[...items].reverse().map((item, index) => (
        <li key={`${item.timestamp}-${index}`}>
          <span className="timeline-marker">
            <Check size={12} />
          </span>
          <div>
            <div className="timeline-top">
              <strong>{item.toStatus}</strong>
              <time>
                {new Date(item.timestamp).toLocaleString("en-IN", {
                  dateStyle: "medium",
                  timeStyle: "short",
                })}
              </time>
            </div>
            <p>{item.remark}</p>
            <small>
              {item.actorName} · {item.actorRole}{" "}
              {!publicOnly && (
                <span className={`visibility ${item.visibility.toLowerCase()}`}>
                  {item.visibility}
                </span>
              )}
            </small>
          </div>
        </li>
      ))}
    </ol>
  );
}
export function Accordion({ items }: { items: { question: string; answer: string }[] }) {
  const [open, setOpen] = useState(0);
  return (
    <div className="accordion">
      {items.map((item, index) => (
        <div className="accordion-item" key={item.question}>
          <button
            onClick={() => setOpen(open === index ? -1 : index)}
            aria-expanded={open === index}
          >
            <span>{item.question}</span>
            <ChevronDown className={open === index ? "rotate" : ""} size={20} />
          </button>
          {open === index && <div className="accordion-content">{item.answer}</div>}
        </div>
      ))}
    </div>
  );
}
export function Modal({
  title,
  children,
  onClose,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    ref.current?.focus();
  }, []);
  return (
    <div className="modal-backdrop" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabIndex={-1}
        ref={ref}
      >
        <div className="modal-head">
          <h2 id="modal-title">{title}</h2>
          <button className="icon-btn" onClick={onClose} aria-label="Close dialog">
            <X size={20} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
export function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 3500);
    return () => clearTimeout(timer);
  }, [onClose]);
  return (
    <div className="toast" role="status">
      <Check size={18} />
      {message}
      <button onClick={onClose} aria-label="Dismiss">
        <X size={16} />
      </button>
    </div>
  );
}
export function Skeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="skeleton-wrap" aria-label="Loading">
      {Array.from({ length: rows }).map((_, i) => (
        <div className="skeleton" key={i} />
      ))}
    </div>
  );
}
export function ErrorBanner({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="error-banner">
      <AlertCircle />
      <div>
        <strong>We couldn't load this information.</strong>
        <span>Please try again.</span>
      </div>
      <Button variant="secondary" onClick={onRetry}>
        Retry
      </Button>
    </div>
  );
}
export function EmptyState({
  title = "Nothing here yet",
  text = "New items will appear here when available.",
}: {
  title?: string;
  text?: string;
}) {
  return (
    <div className="empty-state">
      <ClipboardList size={32} />
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}
export function WakeBanner() {
  return (
    <div className="wake-banner">
      <span className="spinner" />
      The server is waking up. This can take up to a minute on the free host.
    </div>
  );
}
export function Pagination({
  page,
  totalPages,
  onChange,
}: {
  page: number;
  totalPages: number;
  onChange: (page: number) => void;
}) {
  return (
    <div className="pagination">
      <button aria-label="Previous page" disabled={page === 1} onClick={() => onChange(page - 1)}>
        <ChevronLeft size={18} />
      </button>
      {Array.from({ length: totalPages }, (_, i) => (
        <button className={page === i + 1 ? "active" : ""} onClick={() => onChange(i + 1)} key={i}>
          {i + 1}
        </button>
      ))}
      <button
        aria-label="Next page"
        disabled={page === totalPages}
        onClick={() => onChange(page + 1)}
      >
        <ChevronRight size={18} />
      </button>
    </div>
  );
}
export function StarRating({
  value,
  onChange,
}: {
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div className="stars" aria-label={`${value} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange(star)}
          aria-label={`${star} star${star > 1 ? "s" : ""}`}
        >
          <Star fill={star <= value ? "currentColor" : "none"} />
        </button>
      ))}
    </div>
  );
}

export const iconMap = {
  Home,
  Building2,
  ShieldCheck,
  BarChart3,
  Clock3,
  UserRound,
  FileText,
  Search,
};
