import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  CarFront,
  CheckCircle2,
  CircleDollarSign,
  ClipboardCheck,
  ClipboardList,
  Clock3,
  CreditCard,
  FileCheck2,
  FileText,
  RefreshCw,
  ShieldCheck,
  Users,
  type LucideIcon,
} from "lucide-react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Link } from "react-router-dom";
import { readableError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { loadResource } from "../components/resources";
import type { RecordData, Role } from "../types";

const chartColors: Record<string, string> = {
  SUBMITTED: "#a99bc8",
  PENDING: "#ad855d",
  UNDER_REVIEW: "#81759e",
  IN_PROGRESS: "#81759e",
  APPROVED: "#668a78",
  REJECTED: "#b46d72",
  CLOSED: "#94918e",
  SETTLED: "#668a78",
};

interface DashboardMetric {
  label: string;
  resource: string;
  icon: LucideIcon;
  accent: string;
  note: string;
  statuses?: string[];
}

interface DashboardAction {
  label: string;
  description: string;
  path: string;
  icon: LucideIcon;
}

interface DashboardProfile {
  eyebrow: string;
  title: string;
  description: string;
  queueTitle: string;
  resources: string[];
  metrics: DashboardMetric[];
  actions: DashboardAction[];
}

const dashboardProfiles: Record<Role, DashboardProfile> = {
  CUSTOMER: {
    eyebrow: "CUSTOMER HOME",
    title: "Your insurance, in one place",
    description: "Review your coverage, report accidents, submit claims, and follow each claim through settlement and payment.",
    queueTitle: "Your recent claims",
    resources: ["claims", "vehicles", "policies", "accidents", "settlements", "payments"],
    metrics: [
      { label: "Your claims", resource: "claims", icon: FileText, accent: "navy", note: "All submitted claims" },
      { label: "Registered vehicles", resource: "vehicles", icon: CarFront, accent: "blue", note: "Your vehicles" },
      { label: "Policies", resource: "policies", icon: ShieldCheck, accent: "green", note: "Your coverage records" },
      { label: "Accident reports", resource: "accidents", icon: AlertTriangle, accent: "amber", note: "Your reported accidents" },
    ],
    actions: [
      { label: "Review policies", description: "Check your coverage details", path: "/policies", icon: ShieldCheck },
      { label: "Report an accident", description: "Record a new incident", path: "/accidents", icon: AlertTriangle },
      { label: "Submit a claim", description: "Start a claim for an accident", path: "/claims", icon: FileText },
      { label: "Track settlement and payment", description: "View financial progress", path: "/settlements", icon: CircleDollarSign },
    ],
  },
  AGENT: {
    eyebrow: "AGENT WORKSPACE",
    title: "Customer service workspace",
    description: "Help customers with onboarding, vehicle and policy records, accident reports, and claim submissions.",
    queueTitle: "Claims needing attention",
    resources: ["claims", "customers", "vehicles", "policies", "accidents"],
    metrics: [
      { label: "Customers", resource: "customers", icon: Users, accent: "navy", note: "Customer profiles" },
      { label: "Vehicles", resource: "vehicles", icon: CarFront, accent: "blue", note: "Registered vehicles" },
      { label: "Policies", resource: "policies", icon: ShieldCheck, accent: "green", note: "Coverage records" },
      { label: "Claims to assist", resource: "claims", icon: Clock3, accent: "amber", note: "Submitted or pending", statuses: ["SUBMITTED", "PENDING"] },
    ],
    actions: [
      { label: "Register a customer", description: "Create a customer profile", path: "/customers", icon: Users },
      { label: "Register a vehicle", description: "Add or update vehicle details", path: "/vehicles", icon: CarFront },
      { label: "Manage policies", description: "Create or update coverage", path: "/policies", icon: ShieldCheck },
      { label: "Assist with an accident", description: "Record an accident report", path: "/accidents", icon: AlertTriangle },
      { label: "Help submit a claim", description: "Create a customer claim", path: "/claims", icon: FileText },
    ],
  },
  CLAIMS_OFFICER: {
    eyebrow: "CLAIMS OPERATIONS",
    title: "Claims review queue",
    description: "Verify policy eligibility, move claims through review, and coordinate inspections and damage assessments.",
    queueTitle: "Claims awaiting your review",
    resources: ["claims", "inspections", "assessments"],
    metrics: [
      { label: "Claims to review", resource: "claims", icon: Clock3, accent: "amber", note: "Submitted, pending, or under review", statuses: ["SUBMITTED", "PENDING", "UNDER_REVIEW"] },
      { label: "Inspections", resource: "inspections", icon: ClipboardCheck, accent: "blue", note: "Scheduled and recorded" },
      { label: "Damage assessments", resource: "assessments", icon: ClipboardList, accent: "navy", note: "Assessment records" },
    ],
    actions: [
      { label: "Review claims", description: "Verify eligibility and decide claims", path: "/claims", icon: FileText },
      { label: "Schedule inspections", description: "Assign a surveyor to a claim", path: "/inspections", icon: ClipboardCheck },
      { label: "Review assessments", description: "Approve damage assessment costs", path: "/assessments", icon: ClipboardList },
      { label: "View surveyors", description: "Check the surveyor roster", path: "/surveyors", icon: Users },
    ],
  },
  SURVEYOR: {
    eyebrow: "SURVEYOR WORKSPACE",
    title: "Your assigned inspections",
    description: "Inspect assigned vehicles, record damage details, estimate repair costs, and submit assessments.",
    queueTitle: "Claims connected to your assignments",
    resources: ["claims", "inspections", "assessments"],
    metrics: [
      { label: "Assigned inspections", resource: "inspections", icon: ClipboardCheck, accent: "blue", note: "Your inspection assignments" },
      { label: "Assigned claims", resource: "claims", icon: FileText, accent: "navy", note: "Claims linked to your work" },
      { label: "Damage assessments", resource: "assessments", icon: ClipboardList, accent: "amber", note: "Assessment records" },
    ],
    actions: [
      { label: "Open inspections", description: "Record inspection findings", path: "/inspections", icon: ClipboardCheck },
      { label: "Submit damage assessment", description: "Estimate repair costs by component", path: "/assessments", icon: ClipboardList },
      { label: "View assigned claims", description: "Review claim information", path: "/claims", icon: FileText },
    ],
  },
  FINANCE: {
    eyebrow: "FINANCE WORKSPACE",
    title: "Settlement and payment operations",
    description: "Prepare approved settlements, process payments, and monitor financial status across claims.",
    queueTitle: "Claims ready for financial processing",
    resources: ["claims", "settlements", "payments"],
    metrics: [
      { label: "Approved claims", resource: "claims", icon: CheckCircle2, accent: "green", note: "Ready for settlement", statuses: ["APPROVED"] },
      { label: "Settlements", resource: "settlements", icon: CircleDollarSign, accent: "blue", note: "Settlement records" },
      { label: "Payments", resource: "payments", icon: CreditCard, accent: "amber", note: "Payment records" },
    ],
    actions: [
      { label: "Prepare settlements", description: "Create or update approved amounts", path: "/settlements", icon: CircleDollarSign },
      { label: "Process payments", description: "Create and update payment status", path: "/payments", icon: CreditCard },
      { label: "Review approved claims", description: "Check claims ready for settlement", path: "/claims", icon: FileCheck2 },
      { label: "Financial reports", description: "Monitor settlement and payment totals", path: "/reports", icon: BarChart3 },
    ],
  },
  ADMIN: {
    eyebrow: "ADMINISTRATION",
    title: "System administration",
    description: "Provision user access and oversee the operational records available to your administrator role.",
    queueTitle: "Recent claims across the system",
    resources: ["claims", "users", "inspections", "policies", "surveyors"],
    metrics: [
      { label: "System users", resource: "users", icon: Users, accent: "navy", note: "Provisioned accounts" },
      { label: "Claims", resource: "claims", icon: FileText, accent: "blue", note: "System claim records" },
      { label: "Inspections", resource: "inspections", icon: ClipboardCheck, accent: "amber", note: "Inspection records" },
      { label: "Policies", resource: "policies", icon: ShieldCheck, accent: "green", note: "Coverage records" },
      { label: "Surveyors", resource: "surveyors", icon: Users, accent: "blue", note: "Surveyor profiles" },
    ],
    actions: [
      { label: "Manage user access", description: "View users and provision accounts", path: "/users", icon: Users },
      { label: "Add a surveyor profile", description: "Create a profile before assigning login access", path: "/surveyors", icon: ClipboardCheck },
      { label: "Review customers", description: "View customer profiles", path: "/customers", icon: FileCheck2 },
      { label: "Review claims", description: "Inspect claim workflow records", path: "/claims", icon: FileText },
      { label: "View reports", description: "Monitor financial operations", path: "/reports", icon: BarChart3 },
    ],
  },
  MANAGER: {
    eyebrow: "MANAGEMENT OVERVIEW",
    title: "Operations and performance",
    description: "Monitor claim progress, inspection activity, and financial workflow status across the operation.",
    queueTitle: "Latest claims in the workflow",
    resources: ["claims", "inspections", "assessments", "settlements", "payments"],
    metrics: [
      { label: "Claims in progress", resource: "claims", icon: Activity, accent: "blue", note: "Submitted or actively reviewed", statuses: ["SUBMITTED", "PENDING", "UNDER_REVIEW", "IN_PROGRESS"] },
      { label: "Inspections", resource: "inspections", icon: ClipboardCheck, accent: "amber", note: "Inspection workload" },
      { label: "Settlements", resource: "settlements", icon: CircleDollarSign, accent: "green", note: "Settlement records" },
      { label: "Payments", resource: "payments", icon: CreditCard, accent: "navy", note: "Payment records" },
    ],
    actions: [
      { label: "Operational reports", description: "Review settlement and payment summaries", path: "/reports", icon: BarChart3 },
      { label: "Monitor claims", description: "Track claim workflow progress", path: "/claims", icon: FileText },
      { label: "Monitor inspections", description: "Review inspection workload", path: "/inspections", icon: ClipboardCheck },
      { label: "Review assessments", description: "Track damage assessment activity", path: "/assessments", icon: ClipboardList },
      { label: "Financial workflow", description: "View settlements and payment status", path: "/settlements", icon: CircleDollarSign },
    ],
  },
};

function labelForStatus(value: unknown): string {
  return String(value ?? "UNKNOWN").replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase());
}

function statusOf(record: RecordData): string {
  return String(record.status ?? "UNKNOWN").toUpperCase();
}

export function Dashboard() {
  const { user } = useAuth();
  const profile = dashboardProfiles[user?.role ?? "CUSTOMER"];
  const query = useQuery({
    queryKey: ["role-dashboard", user?.id, user?.role],
    queryFn: async (): Promise<Record<string, RecordData[]>> => {
      const data: Record<string, RecordData[]> = {};
      await Promise.all(profile.resources.map(async (resource) => {
        data[resource] = await loadResource(resource);
      }));
      return data;
    },
    enabled: Boolean(user),
  });
  const data = query.data ?? {};
  const claims = data.claims ?? [];
  const counts = claims.reduce<Record<string, number>>((totals, claim) => {
    const status = statusOf(claim);
    totals[status] = (totals[status] ?? 0) + 1;
    return totals;
  }, {});
  const chartData = Object.entries(counts).map(([name, value]) => ({ name, value }));

  return (
    <div className="page-stack">
      <section className="welcome-row">
        <div>
          <div className="eyebrow">{profile.eyebrow}</div>
          <h1>{profile.title}{user?.role !== "CUSTOMER" && user ? `, ${user.email.split("@")[0]}` : ""}.</h1>
          <p className="page-subtitle">{profile.description}</p>
        </div>
        <Link className="button button-secondary" to={profile.actions[0].path}>
          {profile.actions[0].label} <ArrowUpRight size={16} />
        </Link>
      </section>

      {query.isLoading ? (
        <div className="metric-grid">
          {profile.metrics.map((metric) => <div className="metric-card skeleton" key={metric.label} />)}
        </div>
      ) : query.isError ? (
        <div className="notice notice-error" role="alert">
          <span>{readableError(query.error)}</span>
          <button className="text-button" onClick={() => void query.refetch()}><RefreshCw size={15} /> Retry</button>
        </div>
      ) : (
        <>
          <section className="metric-grid" aria-label={`${profile.eyebrow} metrics`}>
            {profile.metrics.map((metric) => {
              const records = data[metric.resource] ?? [];
              const value = metric.statuses
                ? records.filter((record) => metric.statuses?.includes(statusOf(record))).length
                : records.length;
              return (
                <Metric
                  key={metric.label}
                  label={metric.label}
                  value={value}
                  icon={metric.icon}
                  accent={metric.accent}
                  note={metric.note}
                />
              );
            })}
          </section>

          <section className="panel role-actions-panel">
            <div className="panel-heading">
              <div><h2>Quick actions</h2><p>Tasks available to your role</p></div>
              <span className="panel-icon"><Activity size={17} /></span>
            </div>
            <div className="role-actions-grid">
              {profile.actions.map(({ label, description, path, icon: Icon }) => (
                <Link className="role-action-link" to={path} key={label}>
                  <span className="role-action-icon"><Icon size={17} /></span>
                  <span className="role-action-copy"><strong>{label}</strong><span>{description}</span></span>
                  <ArrowUpRight className="role-action-arrow" size={15} />
                </Link>
              ))}
            </div>
          </section>

          <section className="dashboard-grid">
            <article className="panel chart-panel">
              <div className="panel-heading">
                <div><h2>Claims by status</h2><p>Distribution based on records available to your role</p></div>
                <span className="panel-icon"><Activity size={17} /></span>
              </div>
              {chartData.length ? (
                <>
                  <div className="chart-wrap">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={67} outerRadius={94} paddingAngle={3} stroke="none">
                          {chartData.map((entry) => <Cell key={entry.name} fill={chartColors[entry.name] ?? "#9baabd"} />)}
                        </Pie>
                        <Tooltip formatter={(value) => [value, "Claims"]} labelFormatter={labelForStatus} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="chart-total"><strong>{claims.length}</strong><span>claims</span></div>
                  </div>
                  <div className="chart-legend">
                    {chartData.map((entry) => (
                      <div className="legend-item" key={entry.name}>
                        <span className="legend-dot" style={{ background: chartColors[entry.name] ?? "#9baabd" }} />
                        <span>{labelForStatus(entry.name)}</span><strong>{entry.value}</strong>
                      </div>
                    ))}
                  </div>
                </>
              ) : <EmptyState title="No claims yet" description="Claim status insights will appear when records are available." />}
            </article>
            <article className="panel recent-panel">
              <div className="panel-heading">
                <div><h2>{profile.queueTitle}</h2><p>Latest records available to your role</p></div>
                <Link className="icon-link" to="/claims" aria-label="See all claims"><ArrowUpRight size={17} /></Link>
              </div>
              {claims.length ? (
                <div className="recent-list">
                  {[...claims].slice(-5).reverse().map((claim, index) => (
                    <div className="recent-row" key={String(claim.id ?? index)}>
                      <div className="recent-symbol"><FileText size={17} /></div>
                      <div className="recent-info">
                        <strong>{String(claim.claim_number ?? `Claim #${claim.id ?? "—"}`)}</strong>
                        <span>{String(claim.claim_type ?? "Insurance claim")} · {formatDate(claim.created_at)}</span>
                      </div>
                      <StatusBadge status={claim.status} />
                    </div>
                  ))}
                </div>
              ) : <EmptyState title="Nothing to show" description="New claims will appear here." />}
            </article>
          </section>
          <div className="workflow-note">
            <div className="workflow-mark"><Activity size={19} /></div>
            <div><strong>Role-specific workflow</strong><span>{profile.description}</span></div>
            <Link to={profile.actions[0].path}>Continue <ArrowUpRight size={15} /></Link>
          </div>
        </>
      )}
    </div>
  );
}

function Metric({
  label,
  value,
  icon: Icon,
  accent,
  note,
}: {
  label: string;
  value: number;
  icon: LucideIcon;
  accent: string;
  note: string;
}) {
  return (
    <article className="metric-card">
      <div className={`metric-icon metric-${accent}`}><Icon size={19} /></div>
      <span className="metric-label">{label}</span>
      <strong className="metric-value">{value}</strong>
      <span className="metric-note">{note}</span>
    </article>
  );
}

export function StatusBadge({ status }: { status: unknown }) {
  const normalized = String(status ?? "UNKNOWN").toLowerCase().replaceAll("_", "-");
  return <span className={`status-badge status-${normalized}`}>{labelForStatus(status)}</span>;
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return <div className="empty-state"><div className="empty-icon"><FileText size={20} /></div><strong>{title}</strong><span>{description}</span></div>;
}

export function formatDate(value: unknown): string {
  if (!value) return "Date not recorded";
  const date = new Date(String(value));
  return Number.isNaN(date.getTime())
    ? String(value)
    : new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(date);
}
