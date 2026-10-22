import { useQuery } from "@tanstack/react-query";
import { Activity, ArrowUpRight, CheckCircle2, Clock3, FileText, RefreshCw } from "lucide-react";
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
import { loadClaims } from "../components/resources";

const chartColors: Record<string, string> = {
  SUBMITTED: "#7192c7",
  PENDING: "#e9aa51",
  UNDER_REVIEW: "#678fe1",
  IN_PROGRESS: "#678fe1",
  APPROVED: "#34a987",
  REJECTED: "#df7376",
  CLOSED: "#788ca2",
  SETTLED: "#34a987",
};

function labelForStatus(value: unknown): string {
  return String(value ?? "UNKNOWN").replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (char) => char.toUpperCase());
}

export function Dashboard() {
  const { user } = useAuth();
  const query = useQuery({
    queryKey: ["dashboard-claims"],
    queryFn: loadClaims,
  });
  const claims = query.data ?? [];
  const counts = claims.reduce<Record<string, number>>((totals, claim) => {
    const status = String(claim.status ?? "UNKNOWN").toUpperCase();
    totals[status] = (totals[status] ?? 0) + 1;
    return totals;
  }, {});
  const chartData = Object.entries(counts).map(([name, value]) => ({ name, value }));
  const pending = claims.filter((claim) =>
    ["PENDING", "SUBMITTED"].includes(String(claim.status).toUpperCase()),
  ).length;
  const inProgress = claims.filter((claim) =>
    ["UNDER_REVIEW", "IN_PROGRESS", "INSPECTION"].includes(
      String(claim.status).toUpperCase(),
    ),
  ).length;
  const complete = claims.filter((claim) =>
    ["APPROVED", "REJECTED", "SETTLED", "CLOSED"].includes(
      String(claim.status).toUpperCase(),
    ),
  ).length;
  const greeting = user?.role === "CUSTOMER" ? "Your claims, at a glance" : "Good morning";

  return (
    <div className="page-stack">
      <section className="welcome-row">
        <div>
          <div className="eyebrow">CLAIMS OVERVIEW</div>
          <h1>{greeting}{user?.role !== "CUSTOMER" && user ? `, ${user.email.split("@")[0]}` : ""}.</h1>
          <p className="page-subtitle">
            {user?.role === "CUSTOMER"
              ? "A clear view of your submitted claims and their progress."
              : "Here’s where your claims portfolio stands today."}
          </p>
        </div>
        <Link className="button button-secondary" to="/claims">
          View claims <ArrowUpRight size={16} />
        </Link>
      </section>

      {query.isLoading ? (
        <div className="metric-grid">
          {[0, 1, 2, 3].map((item) => <div className="metric-card skeleton" key={item} />)}
        </div>
      ) : query.isError ? (
        <div className="notice notice-error" role="alert">
          <span>{readableError(query.error)}</span>
          <button className="text-button" onClick={() => void query.refetch()}><RefreshCw size={15} /> Retry</button>
        </div>
      ) : (
        <>
          <section className="metric-grid" aria-label="Claim metrics">
            <Metric label="Total claims" value={claims.length} icon={FileText} accent="navy" note="Visible in your workspace" />
            <Metric label="Awaiting review" value={pending} icon={Clock3} accent="amber" note="Submitted or pending" />
            <Metric label="In progress" value={inProgress} icon={Activity} accent="blue" note="Under active review" />
            <Metric label="Resolved" value={complete} icon={CheckCircle2} accent="green" note="Approved, rejected or closed" />
          </section>
          <section className="dashboard-grid">
            <article className="panel chart-panel">
              <div className="panel-heading">
                <div><h2>Claims by status</h2><p>Distribution based on records you can access</p></div>
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
                <div><h2>Recent claims</h2><p>Latest records available to your role</p></div>
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
            <div><strong>Keep the lifecycle moving</strong><span>Open a claim to review its current status and the next action available to your role.</span></div>
            <Link to="/claims">Go to claims <ArrowUpRight size={15} /></Link>
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
  icon: typeof FileText;
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
