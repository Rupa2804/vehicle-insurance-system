import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeftRight,
  BarChart3,
  CarFront,
  ClipboardCheck,
  ClipboardList,
  CreditCard,
  FileCheck2,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  ShieldCheck,
  Users,
  X,
  type LucideIcon,
} from "lucide-react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import type { Role } from "../types";

interface NavigationItem {
  label: string;
  path: string;
  icon: LucideIcon;
  roles: Role[];
}

const allRoles: Role[] = [
  "CUSTOMER",
  "AGENT",
  "CLAIMS_OFFICER",
  "SURVEYOR",
  "FINANCE",
  "ADMIN",
  "MANAGER",
];

const navigation: NavigationItem[] = [
  { label: "Overview", path: "/", icon: LayoutDashboard, roles: allRoles },
  {
    label: "Customers",
    path: "/customers",
    icon: Users,
    roles: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  },
  {
    label: "Vehicles",
    path: "/vehicles",
    icon: CarFront,
    roles: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  },
  {
    label: "Policies",
    path: "/policies",
    icon: ShieldCheck,
    roles: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  },
  {
    label: "Accidents",
    path: "/accidents",
    icon: AlertTriangle,
    roles: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  },
  {
    label: "Claims",
    path: "/claims",
    icon: FileText,
    roles: allRoles,
  },
  {
    label: "Surveyors",
    path: "/surveyors",
    icon: Users,
    roles: ["CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  },
  {
    label: "Inspections",
    path: "/inspections",
    icon: ClipboardCheck,
    roles: ["CUSTOMER", "CLAIMS_OFFICER", "SURVEYOR", "MANAGER", "ADMIN"],
  },
  {
    label: "Assessments",
    path: "/assessments",
    icon: ClipboardList,
    roles: ["CUSTOMER", "CLAIMS_OFFICER", "SURVEYOR", "MANAGER", "ADMIN"],
  },
  {
    label: "Settlements",
    path: "/settlements",
    icon: ArrowLeftRight,
    roles: ["CUSTOMER", "FINANCE", "MANAGER", "ADMIN"],
  },
  {
    label: "Payments",
    path: "/payments",
    icon: CreditCard,
    roles: ["CUSTOMER", "FINANCE", "MANAGER", "ADMIN"],
  },
  {
    label: "Reports",
    path: "/reports",
    icon: BarChart3,
    roles: ["FINANCE", "MANAGER", "ADMIN"],
  },
  { label: "User access", path: "/users", icon: FileCheck2, roles: ["ADMIN"] },
];

function roleName(role: Role): string {
  return role.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase());
}

export function Shell() {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const activePage =
    navigation.find((item) => item.path === location.pathname)?.label ?? "Overview";
  const visibleNavigation = navigation.filter((item) => user && item.roles.includes(user.role));

  function signOut() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <button
        className="mobile-menu-button"
        type="button"
        aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
        onClick={() => setMobileOpen((open) => !open)}
      >
        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
      {mobileOpen && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setMobileOpen(false)} />}
      <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><ShieldCheck size={21} strokeWidth={2.1} /></div>
          <div>
            <div className="brand-name">claimcare-portal</div>
            <div className="brand-caption">CLAIMS MANAGEMENT</div>
          </div>
        </div>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="navigation" aria-label="Main navigation">
          {visibleNavigation.map(({ icon: Icon, ...item }) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/"}
              className={({ isActive }) => `nav-item ${isActive ? "nav-item-active" : ""}`}
              onClick={() => setMobileOpen(false)}
            >
              <Icon size={18} strokeWidth={1.9} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-support">
            <div className="support-icon"><Activity size={17} /></div>
            <div><strong>Claims, in sync.</strong><span>One clear view of every next step.</span></div>
          </div>
          <div className="sidebar-user">
            <div className="avatar">{user?.email.slice(0, 1).toUpperCase()}</div>
            <div className="sidebar-user-info">
              <strong>{user?.email}</strong>
              <span>{user ? roleName(user.role) : "Signed out"}</span>
            </div>
          </div>
        </div>
      </aside>
      <div className="main-column">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><span className="breadcrumb-divider">/</span><strong>{activePage}</strong></div>
          <div className="topbar-right">
            <span className="secure-label"><span className="secure-dot" /> Secure workspace</span>
            <div className="topbar-avatar">{user?.email.slice(0, 1).toUpperCase()}</div>
            <button className="button button-secondary sign-out" type="button" onClick={signOut}>
              <LogOut size={16} />
              <span>Log out</span>
            </button>
          </div>
        </header>
        <main className="page-content"><Outlet /></main>
        <footer className="footer">
          <span>claimcare-portal · Insurance operations</span>
          <span>Role-aware access · Data from your claims system</span>
        </footer>
      </div>
    </div>
  );
}
