import { useQuery } from "@tanstack/react-query";
import { BarChart3, CircleDollarSign, RefreshCw } from "lucide-react";
import { api, readableError } from "../api/client";
import { EmptyState } from "./Dashboard";
import type { RecordData } from "../types";

interface ReportData {
  settlementSummary: RecordData;
  settlementStatus: RecordData[];
  paymentSummary: RecordData;
  paymentStatus: RecordData[];
}

export function ReportsPage() {
  const query = useQuery({
    queryKey: ["financial-reports"],
    queryFn: async (): Promise<ReportData> => {
      const [settlementSummary, settlementStatus, paymentSummary, paymentStatus] =
        await Promise.all([
          api.get<RecordData>("/reports/settlements/summary"),
          api.get<RecordData[]>("/reports/settlements/status"),
          api.get<RecordData>("/reports/payments/summary"),
          api.get<RecordData[]>("/reports/payments/status"),
        ]);
      return {
        settlementSummary: settlementSummary.data,
        settlementStatus: settlementStatus.data,
        paymentSummary: paymentSummary.data,
        paymentStatus: paymentStatus.data,
      };
    },
  });

  if (query.isLoading) {
    return <div className="page-stack"><div className="page-heading"><div><div className="eyebrow">INSIGHTS</div><h1>Reports</h1><p className="page-subtitle">Live settlement and payment summaries.</p></div></div><div className="report-skeleton" /></div>;
  }
  if (query.isError) {
    return (
      <div className="page-stack">
        <PageTitle />
        <div className="notice notice-error" role="alert">
          <span>{readableError(query.error)}</span>
          <button className="text-button" onClick={() => void query.refetch()}><RefreshCw size={15} /> Retry</button>
        </div>
      </div>
    );
  }
  const report = query.data;
  if (!report) return <EmptyState title="No report data" description="The reporting service returned no data." />;

  return (
    <div className="page-stack">
      <PageTitle />
      <section className="metric-grid report-metrics">
        <ReportMetric label="Settlements" value={report.settlementSummary.total_settlements} />
        <ReportMetric label="Estimated amount" value={report.settlementSummary.total_estimated_amount} />
        <ReportMetric label="Approved amount" value={report.settlementSummary.total_approved_amount} />
        <ReportMetric label="Payments" value={report.paymentSummary.total_payments} />
      </section>
      <section className="dashboard-grid">
        <StatusTable title="Settlement status" rows={report.settlementStatus} />
        <StatusTable title="Payment status" rows={report.paymentStatus} />
      </section>
      <div className="report-footnote">Figures are returned by the live reporting API and follow the data access granted to your role.</div>
    </div>
  );
}

function PageTitle() {
  return (
    <section className="page-heading">
      <div><div className="eyebrow">INSIGHTS</div><h1>Reports</h1><p className="page-subtitle">Live settlement and payment summaries.</p></div>
      <span className="panel-icon"><BarChart3 size={18} /></span>
    </section>
  );
}

function ReportMetric({
  label,
  value,
}: {
  label: string;
  value: unknown;
}) {
  const numericValue = Number(value ?? 0);
  const formatted = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(numericValue);
  return (
    <article className="metric-card">
      <div className="metric-icon metric-blue"><CircleDollarSign size={19} /></div>
      <span className="metric-label">{label}</span>
      <strong className="metric-value report-value">{formatted}</strong>
      <span className="metric-note">Current reported total</span>
    </article>
  );
}

function StatusTable({ title, rows }: { title: string; rows: RecordData[] }) {
  return (
    <article className="panel report-table-panel">
      <div className="panel-heading"><div><h2>{title}</h2><p>Breakdown by current status</p></div></div>
      {rows.length ? (
        <div className="table-scroll">
          <table>
            <thead><tr><th>Status</th><th>Count</th><th>Total amount</th></tr></thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={String(row.status ?? index)}>
                  <td><span className="report-status">{String(row.status ?? "Unknown").replaceAll("_", " ")}</span></td>
                  <td>{String(row.count ?? 0)}</td>
                  <td className="amount-cell">{new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(Number(row.total_amount ?? 0))}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : <EmptyState title="No status records" description="No transactions match this report yet." />}
    </article>
  );
}
