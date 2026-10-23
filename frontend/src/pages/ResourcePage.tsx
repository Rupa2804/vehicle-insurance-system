import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowDownWideNarrow,
  Check,
  ChevronLeft,
  ChevronRight,
  CirclePlus,
  LoaderCircle,
  Pencil,
  RefreshCw,
  Search,
  Trash2,
  X,
} from "lucide-react";
import { useMemo, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api, readableError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { EmptyState, formatDate, StatusBadge } from "./Dashboard";
import { loadResource, resources, type Field } from "../components/resources";
import type { RecordData } from "../types";

const pageSize = 10;

function titleCase(value: string): string {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function displayValue(key: string, value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (key.endsWith("_at") || key.endsWith("_date")) return formatDate(value);
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function toPayload(form: HTMLFormElement, fields: Field[]): Record<string, unknown> {
  const values = new FormData(form);
  const payload: Record<string, unknown> = {};
  for (const field of fields) {
    const raw = String(values.get(field.name) ?? "").trim();
    if (!raw) continue;
    payload[field.name] =
      field.type === "number" || field.name.endsWith("_id") ? Number(raw) : raw;
  }
  return payload;
}

export function ResourcePage({ resourceKey }: { resourceKey: string }) {
  const definition = resources[resourceKey];
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState("");
  const [sortAscending, setSortAscending] = useState(true);
  const [page, setPage] = useState(0);
  const [editing, setEditing] = useState<RecordData | null>(null);
  const [creating, setCreating] = useState(false);
  const [selectedUserRole, setSelectedUserRole] = useState("");
  const [selectedAccidentCustomerId, setSelectedAccidentCustomerId] = useState("");
  const [selectedAccidentVehicleId, setSelectedAccidentVehicleId] = useState("");
  const [accidentCustomerSearch, setAccidentCustomerSearch] = useState("");
  const [accidentVehicleSearch, setAccidentVehicleSearch] = useState("");
  const [notice, setNotice] = useState("");
  const [actionError, setActionError] = useState("");

  const listQuery = useQuery({
    queryKey: ["resource", resourceKey],
    queryFn: () => loadResource(resourceKey),
  });
  const surveyorsQuery = useQuery({
    queryKey: ["available-surveyors"],
    queryFn: () => loadResource("surveyors"),
    enabled: resourceKey === "users" && selectedUserRole === "SURVEYOR",
  });
  const accidentCustomersQuery = useQuery({
    queryKey: ["accident-customers"],
    queryFn: () => loadResource("customers"),
    enabled: resourceKey === "accidents" && creating && user?.role === "AGENT",
  });
  const accidentVehiclesQuery = useQuery({
    queryKey: ["accident-vehicles"],
    queryFn: () => loadResource("vehicles"),
    enabled:
      resourceKey === "accidents" &&
      creating &&
      (user?.role === "AGENT" || user?.role === "CUSTOMER"),
  });

  const createMutation = useMutation({
    mutationFn: async (payload: RecordData) => {
      const { data } = await api.post(definition.endpoint, payload);
      return data as RecordData;
    },
    onSuccess: async (_data, payload) => {
      setCreating(false);
      setNotice(
        resourceKey === "customers" && payload.initial_password
          ? "Customer profile and login created. Share the initial password securely."
          : `${definition.singular} created successfully.`,
      );
      await queryClient.invalidateQueries({ queryKey: ["resource"] });
    },
    onError: (error) => setActionError(readableError(error)),
  });

  const updateMutation = useMutation({
    mutationFn: async ({ endpoint, payload }: { endpoint: string; payload: RecordData }) => {
      const { data } = await api.request({
        url: endpoint,
        method: definition.updateMethod ?? "PATCH",
        data: payload,
      });
      return data as RecordData;
    },
    onSuccess: async () => {
      setEditing(null);
      setNotice("Changes saved successfully.");
      await queryClient.invalidateQueries({ queryKey: ["resource"] });
    },
    onError: (error) => setActionError(readableError(error)),
  });

  const deleteMutation = useMutation({
    mutationFn: async (endpoint: string) => api.delete(endpoint),
    onSuccess: async () => {
      setNotice("Record deleted.");
      await queryClient.invalidateQueries({ queryKey: ["resource"] });
    },
    onError: (error) => setActionError(readableError(error)),
  });

  const paymentMutation = useMutation({
    mutationFn: async ({ id, action }: { id: unknown; action: "process" | "fail" | "refund" }) => {
      const { data } = await api.post(`/payments/${id}/${action}`);
      return data as RecordData;
    },
    onSuccess: async () => {
      setNotice("Payment state updated.");
      await queryClient.invalidateQueries({ queryKey: ["resource"] });
    },
    onError: (error) => setActionError(readableError(error)),
  });

  const approvalMutation = useMutation({
    mutationFn: async ({ id, amount }: { id: unknown; amount: number }) => {
      const { data } = await api.post(`/damage-assessments/${id}/approve`, {
        approved_cost: amount,
      });
      return data as RecordData;
    },
    onSuccess: async () => {
      setNotice("Assessment approved.");
      await queryClient.invalidateQueries({ queryKey: ["resource"] });
    },
    onError: (error) => setActionError(readableError(error)),
  });

  const claimStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: unknown; status: "UNDER_REVIEW" | "APPROVED" | "REJECTED" }) => {
      const { data } = await api.patch(`/claims/${id}/status`, { status });
      return data as RecordData;
    },
    onSuccess: async () => {
      setNotice("Claim status updated.");
      await queryClient.invalidateQueries({ queryKey: ["resource"] });
    },
    onError: (error) => setActionError(readableError(error)),
  });

  const rows = listQuery.data ?? [];
  const filteredRows = useMemo(() => {
    const term = search.trim().toLowerCase();
    const matched = term
      ? rows.filter((row) => JSON.stringify(row).toLowerCase().includes(term))
      : [...rows];
    if (sortKey) {
      matched.sort((first, second) => {
        const a = String(first[sortKey] ?? "");
        const b = String(second[sortKey] ?? "");
        return (sortAscending ? 1 : -1) * a.localeCompare(b, undefined, { numeric: true });
      });
    }
    return matched;
  }, [rows, search, sortKey, sortAscending]);
  const pageCount = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  const visibleRows = filteredRows.slice(page * pageSize, (page + 1) * pageSize);
  const columns = rows.length
    ? Object.keys(rows[0]).filter((key) => key !== "description" && key !== "remarks").slice(0, 7)
    : [];

  const createFields =
    ["accidents", "vehicles"].includes(resourceKey) && user?.role === "CUSTOMER"
      ? (definition.createFields ?? []).filter((field) => field.name !== "customer_id")
      : definition.createFields ?? [];
  const updateFields =
    resourceKey === "customers"
      ? (definition.updateFields ?? []).filter(
        (field) =>
          (user?.role === "ADMIN" || field.name !== "status") &&
          ((user?.role === "AGENT" || user?.role === "ADMIN") ||
            field.name !== "initial_password"),
      )
      : definition.updateFields ?? [];
  const modalFields = (editing ? updateFields : createFields).filter((field) => {
    if (resourceKey !== "users") return true;
    if (field.name === "customer_id") return selectedUserRole === "CUSTOMER";
    if (field.name === "surveyor_id") return selectedUserRole === "SURVEYOR";
    return true;
  });
  const selectedCustomerVehicles = (accidentVehiclesQuery.data ?? []).filter(
    (vehicle) =>
      user?.role === "CUSTOMER" ||
      String(vehicle.customer_id) === selectedAccidentCustomerId,
  );
  const filteredAccidentCustomers = (accidentCustomersQuery.data ?? []).filter(
    (customer) =>
      String(customer.id) === selectedAccidentCustomerId ||
      `${customer.name ?? ""} ${customer.email ?? ""}`
        .toLowerCase()
        .includes(accidentCustomerSearch.trim().toLowerCase()),
  );
  const filteredAccidentVehicles = selectedCustomerVehicles.filter((vehicle) =>
    String(vehicle.id) === selectedAccidentVehicleId ||
    `${vehicle.registration_number ?? ""} ${vehicle.make ?? ""} ${vehicle.model ?? ""}`
      .toLowerCase()
      .includes(accidentVehicleSearch.trim().toLowerCase()),
  );
  const canCreate = user?.role === "ADMIN" || Boolean(user && definition.createRoles?.includes(user.role));
  const canUpdate = user?.role === "ADMIN" || Boolean(user && definition.updateRoles?.includes(user.role));
  const canDelete = user?.role === "ADMIN" || Boolean(user && definition.allowDeleteRoles?.includes(user.role));
  const canApprove = user?.role === "CLAIMS_OFFICER" || user?.role === "ADMIN";
  const canProcessPayments = user?.role === "FINANCE" || user?.role === "ADMIN";
  const canDecideClaims = canApprove && resourceKey === "claims";
  const canApproveAssessments = canApprove && resourceKey === "assessments";
  const hasActions =
    canUpdate ||
    canDelete ||
    canApproveAssessments ||
    canDecideClaims ||
    (canProcessPayments && resourceKey === "payments");

  function submitForm(event: FormEvent<HTMLFormElement>, fields: Field[]) {
    event.preventDefault();
    setNotice("");
    setActionError("");
    const payload = toPayload(event.currentTarget, fields);
    if (resourceKey === "accidents" && user?.role === "CUSTOMER") {
      payload.customer_id = user.customer_id;
    }
    if (resourceKey === "users" && payload.role !== "CUSTOMER") {
      delete payload.customer_id;
    }
    if (resourceKey === "users" && payload.role !== "SURVEYOR") {
      delete payload.surveyor_id;
    }
    if (editing && definition.updateEndpoint) {
      updateMutation.mutate({
        endpoint: definition.updateEndpoint(editing),
        payload,
      });
    } else {
      createMutation.mutate(payload);
    }
  }

  function requestDelete(row: RecordData) {
    const endpoint = definition.deleteEndpoint?.(row);
    if (!endpoint || !window.confirm(`Delete this ${definition.singular}? This cannot be undone.`)) return;
    setActionError("");
    deleteMutation.mutate(endpoint);
  }

  function requestApproval(row: RecordData) {
    const suggested = Number(row.estimated_cost ?? 0);
    const input = window.prompt("Approved cost", String(suggested));
    if (input === null) return;
    const amount = Number(input);
    if (!Number.isFinite(amount) || amount < 0) {
      setActionError("Enter a valid non-negative approved cost.");
      return;
    }
    approvalMutation.mutate({ id: row.id, amount });
  }

  function clearModal() {
    setCreating(false);
    setEditing(null);
    setSelectedAccidentCustomerId("");
    setSelectedAccidentVehicleId("");
    setAccidentCustomerSearch("");
    setAccidentVehicleSearch("");
    setActionError("");
  }

  if (!definition) return <div className="notice notice-error">This section is not available.</div>;

  return (
    <div className="page-stack">
      <section className="page-heading">
        <div>
          <div className="eyebrow">OPERATIONS</div>
          <h1>{definition.title}</h1>
          <p className="page-subtitle">{definition.description}</p>
        </div>
        {canCreate && (
          <button
            className="button button-primary"
            onClick={() => {
              setActionError("");
              setSelectedUserRole("");
              setSelectedAccidentCustomerId("");
              setSelectedAccidentVehicleId("");
              setAccidentCustomerSearch("");
              setAccidentVehicleSearch("");
              setCreating(true);
              setEditing(null);
            }}
          >
            <CirclePlus size={17} /> Add {definition.singular}
          </button>
        )}
      </section>

      {notice && <div className="notice notice-success"><Check size={17} />{notice}<button onClick={() => setNotice("")} aria-label="Dismiss"><X size={16} /></button></div>}
      {actionError && <div className="notice notice-error" role="alert"><span>{actionError}</span><button onClick={() => setActionError("")} aria-label="Dismiss"><X size={16} /></button></div>}

      <section className="panel table-panel">
        <div className="table-toolbar">
          <div>
            <h2>{definition.title} directory</h2>
            <p>{listQuery.data ? `${rows.length} record${rows.length === 1 ? "" : "s"} available` : "Live data from your claims workspace"}</p>
          </div>
          <div className="table-controls">
            <label className="search-field">
              <Search size={16} />
              <input
                aria-label={`Search ${definition.title.toLowerCase()}`}
                placeholder="Search records"
                value={search}
                onChange={(event) => {
                  setSearch(event.target.value);
                  setPage(0);
                }}
              />
            </label>
            <button
              className="icon-button refresh-button"
              title="Refresh"
              onClick={() => void listQuery.refetch()}
              disabled={listQuery.isFetching}
            >
              <RefreshCw size={16} className={listQuery.isFetching ? "spin" : ""} />
            </button>
          </div>
        </div>

        {listQuery.isLoading ? (
          <div className="table-loading"><LoaderCircle className="spin" size={24} /><span>Loading live records…</span></div>
        ) : listQuery.isError ? (
          <div className="table-error">
            <div className="empty-icon"><X size={20} /></div>
            <strong>Couldn’t load this section</strong>
            <span>{readableError(listQuery.error)}</span>
            <button className="button button-secondary" onClick={() => void listQuery.refetch()}><RefreshCw size={15} /> Try again</button>
          </div>
        ) : visibleRows.length ? (
          <>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    {columns.map((column) => (
                      <th key={column}>
                        <button
                          className="sort-button"
                          onClick={() => {
                            setSortAscending(sortKey === column ? !sortAscending : true);
                            setSortKey(column);
                          }}
                        >
                          {titleCase(column)}
                          {sortKey === column ? <ArrowDownWideNarrow size={13} /> : null}
                        </button>
                      </th>
                    ))}
                    {hasActions && <th>Actions</th>}
                  </tr>
                </thead>
                <tbody>
                  {visibleRows.map((row, index) => (
                    <tr key={String(row.id ?? row.email ?? index)}>
                      {columns.map((column) => (
                        <td key={column}>
                          {column === "status" || column === "availability_status"
                            ? <StatusBadge status={row[column]} />
                            : column === "email"
                              ? <span className="email-cell">{displayValue(column, row[column])}</span>
                              : <span className={column.endsWith("_amount") || column === "amount" ? "amount-cell" : ""}>{displayValue(column, row[column])}</span>}
                        </td>
                      ))}
                      {hasActions && (
                        <td><div className="row-actions">
                          {canUpdate && definition.updateEndpoint && (
                            <button className="icon-button row-action" title="Edit record" onClick={() => {
                              setActionError("");
                              setEditing(row);
                              setCreating(false);
                            }}><Pencil size={15} /></button>
                          )}
                          {canApproveAssessments && (
                            <button className="button button-table" onClick={() => requestApproval(row)}>Approve</button>
                          )}
                          {canDecideClaims && String(row.status).toUpperCase() === "SUBMITTED" && (
                            <button
                              className="button button-table"
                              disabled={claimStatusMutation.isPending}
                              onClick={() => claimStatusMutation.mutate({ id: row.id, status: "UNDER_REVIEW" })}
                            >
                              Start review
                            </button>
                          )}
                          {canDecideClaims && String(row.status).toUpperCase() === "UNDER_REVIEW" && (
                            <>
                              <button
                                className="button button-table"
                                disabled={claimStatusMutation.isPending}
                                onClick={() => claimStatusMutation.mutate({ id: row.id, status: "APPROVED" })}
                              >
                                Approve
                              </button>
                              <button
                                className="button button-table"
                                disabled={claimStatusMutation.isPending}
                                onClick={() => claimStatusMutation.mutate({ id: row.id, status: "REJECTED" })}
                              >
                                Reject
                              </button>
                            </>
                          )}
                          {canProcessPayments && resourceKey === "payments" && (
                            <>
                              {!["SUCCESS", "REFUNDED"].includes(String(row.status).toUpperCase()) && <button className="button button-table" onClick={() => paymentMutation.mutate({ id: row.id, action: "process" })}>Process</button>}
                              {!["SUCCESS", "REFUNDED"].includes(String(row.status).toUpperCase()) && <button className="icon-button row-action" title="Mark payment failed" onClick={() => paymentMutation.mutate({ id: row.id, action: "fail" })}><X size={15} /></button>}
                              {String(row.status).toUpperCase() === "SUCCESS" && <button className="icon-button row-action" title="Refund payment" onClick={() => paymentMutation.mutate({ id: row.id, action: "refund" })}><RefreshCw size={15} /></button>}
                            </>
                          )}
                          {canDelete && definition.deleteEndpoint && (
                            <button className="icon-button row-action row-action-danger" title="Delete record" onClick={() => requestDelete(row)}><Trash2 size={15} /></button>
                          )}
                        </div></td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="table-pagination">
              <span>Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, filteredRows.length)} of {filteredRows.length}</span>
              <div className="pagination-actions">
                <button className="icon-button" disabled={page === 0} onClick={() => setPage((current) => Math.max(0, current - 1))} aria-label="Previous page"><ChevronLeft size={17} /></button>
                <span>Page {page + 1} of {pageCount}</span>
                <button className="icon-button" disabled={page >= pageCount - 1} onClick={() => setPage((current) => Math.min(pageCount - 1, current + 1))} aria-label="Next page"><ChevronRight size={17} /></button>
              </div>
            </div>
          </>
        ) : (
          <EmptyState
            title={search ? "No matching records" : `No ${definition.title.toLowerCase()} yet`}
            description={search ? "Try another search term." : "Records will appear here when they are available to your role."}
          />
        )}
      </section>

      {(creating || editing) && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => {
          if (event.target === event.currentTarget) clearModal();
        }}>
          <section className="modal-card" role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <div className="modal-heading">
              <div><div className="eyebrow">{editing ? "UPDATE RECORD" : "NEW RECORD"}</div><h2 id="modal-title">{editing ? `Edit ${definition.singular}` : `Add ${definition.singular}`}</h2></div>
              <button className="icon-button" onClick={clearModal} aria-label="Close"><X size={18} /></button>
            </div>
            <form className="data-form" onSubmit={(event) => submitForm(event, modalFields)}>
              {modalFields.map((field) => {
                const isAccidentCustomer = resourceKey === "accidents" && field.name === "customer_id";
                const isAccidentVehicle = resourceKey === "accidents" && field.name === "vehicle_id";
                const isIdInput = field.type === "number" && field.name.endsWith("_id");
                const linkedRecordRequired =
                  resourceKey === "users" &&
                  ((selectedUserRole === "CUSTOMER" && field.name === "customer_id") ||
                    (selectedUserRole === "SURVEYOR" && field.name === "surveyor_id"));
                const required = Boolean(field.required || linkedRecordRequired);
                return (
                <label className="form-field" key={field.name}>
                  <span>{field.label}{required && <em> *</em>}</span>
                  {field.type === "select" ? (
                    <>
                      {isAccidentCustomer && (
                        <input
                          aria-label="Search customers"
                          placeholder="Search by name or email"
                          value={accidentCustomerSearch}
                          onChange={(event) => setAccidentCustomerSearch(event.target.value)}
                        />
                      )}
                      {isAccidentVehicle && (
                        <input
                          aria-label="Search vehicles"
                          placeholder="Search by registration, make, or model"
                          value={accidentVehicleSearch}
                          onChange={(event) => setAccidentVehicleSearch(event.target.value)}
                        />
                      )}
                      <select
                        name={field.name}
                        aria-label={
                          isAccidentCustomer
                            ? "Customer selection"
                            : isAccidentVehicle
                              ? "Vehicle selection"
                              : undefined
                        }
                        required={required}
                        value={
                          isAccidentCustomer
                            ? selectedAccidentCustomerId
                            : isAccidentVehicle
                              ? selectedAccidentVehicleId
                              : undefined
                        }
                        defaultValue={
                          isAccidentCustomer || isAccidentVehicle
                            ? undefined
                            : editing
                              ? String(editing[field.name] ?? "")
                              : ""
                        }
                        key={isAccidentVehicle ? selectedAccidentCustomerId : field.name}
                        onChange={
                          isAccidentCustomer
                            ? (event) => {
                              setSelectedAccidentCustomerId(event.target.value);
                              setSelectedAccidentVehicleId("");
                              setAccidentVehicleSearch("");
                            }
                            : isAccidentVehicle
                              ? (event) => setSelectedAccidentVehicleId(event.target.value)
                            : field.name === "role"
                              ? (event) => setSelectedUserRole(event.target.value)
                              : undefined
                        }
                        disabled={
                          (field.name === "surveyor_id" && surveyorsQuery.isLoading) ||
                          (isAccidentCustomer && accidentCustomersQuery.isLoading) ||
                          (isAccidentVehicle &&
                            (accidentVehiclesQuery.isLoading ||
                              (user?.role === "AGENT" && !selectedAccidentCustomerId)))
                        }
                      >
                        <option value="" disabled>
                          {isAccidentCustomer
                            ? "Select a customer"
                            : isAccidentVehicle
                              ? user?.role === "AGENT" && !selectedAccidentCustomerId
                                ? "Select a customer first"
                                : "Select a vehicle"
                              : "Select an option"}
                        </option>
                        {isAccidentCustomer
                          ? filteredAccidentCustomers.map((customer) => (
                            <option key={String(customer.id)} value={String(customer.id)}>
                              {String(customer.name)} — {String(customer.email)}
                            </option>
                          ))
                          : isAccidentVehicle
                            ? filteredAccidentVehicles.map((vehicle) => (
                              <option key={String(vehicle.id)} value={String(vehicle.id)}>
                                {String(vehicle.registration_number)} — {String(vehicle.make)} {String(vehicle.model)}
                              </option>
                            ))
                            : field.name === "surveyor_id"
                          ? (surveyorsQuery.data ?? []).map((surveyor) => (
                            <option key={String(surveyor.id)} value={String(surveyor.id)}>
                              {String(surveyor.name)} (ID {String(surveyor.id)})
                            </option>
                          ))
                          : field.options?.map((option) => <option key={option} value={option}>{titleCase(option)}</option>)}
                      </select>
                    </>
                  ) : (
                    <input
                      name={field.name}
                      type={isIdInput ? "text" : field.type ?? "text"}
                      required={required}
                      minLength={field.minLength}
                      maxLength={field.maxLength}
                      pattern={
                        isIdInput ? "[1-9][0-9]*" : field.pattern
                      }
                      inputMode={
                        isIdInput || field.type === "tel" ? "numeric" : undefined
                      }
                      step={field.type === "number" ? "any" : undefined}
                      defaultValue={editing ? String(editing[field.name] ?? "") : ""}
                      placeholder={field.placeholder ?? (field.type === "number" ? "0.00" : "")}
                      autoComplete={field.autoComplete}
                    />
                  )}
                </label>
                );
              })}
              {resourceKey === "customers" && !editing && (
                <p className="form-guidance">
                  This also creates the customer’s portal login. Share the initial password with them securely; they sign in using this email and the Customer role.
                </p>
              )}
              {resourceKey === "customers" &&
                editing &&
                (user?.role === "AGENT" || user?.role === "ADMIN") && (
                <p className="form-guidance">
                  Set an initial password only if this customer does not have a login yet. Existing login accounts cannot be overwritten here.
                </p>
              )}
              {resourceKey === "accidents" && accidentCustomersQuery.isError && (
                <div className="form-alert" role="alert">
                  Could not load customers: {readableError(accidentCustomersQuery.error)}
                </div>
              )}
              {resourceKey === "accidents" && accidentVehiclesQuery.isError && (
                <div className="form-alert" role="alert">
                  Could not load vehicles: {readableError(accidentVehiclesQuery.error)}
                </div>
              )}
              {resourceKey === "accidents" &&
                !accidentCustomersQuery.isLoading &&
                !accidentCustomersQuery.isError &&
                accidentCustomersQuery.data?.length === 0 && (
                  <div className="form-alert">
                    Add a customer profile before reporting an accident.
                  </div>
                )}
              {resourceKey === "accidents" &&
                !accidentVehiclesQuery.isLoading &&
                !accidentVehiclesQuery.isError &&
                selectedCustomerVehicles.length === 0 &&
                (user?.role === "CUSTOMER" || selectedAccidentCustomerId !== "") && (
                  <div className="form-alert">
                    No vehicles are registered under this customer yet. Add a vehicle before reporting the accident.
                  </div>
                )}
              {resourceKey === "accidents" &&
                selectedCustomerVehicles.length > 0 &&
                filteredAccidentVehicles.length === 0 && (
                  <div className="form-alert">
                    No vehicles match that search. Try a registration number, make, or model.
                  </div>
                )}
              {resourceKey === "users" &&
                selectedUserRole === "SURVEYOR" &&
                surveyorsQuery.isError && (
                  <div className="form-alert" role="alert">
                    Could not load surveyor profiles: {readableError(surveyorsQuery.error)}
                  </div>
                )}
              {resourceKey === "users" &&
                selectedUserRole === "SURVEYOR" &&
                !surveyorsQuery.isLoading &&
                !surveyorsQuery.isError &&
                surveyorsQuery.data?.length === 0 && (
                  <div className="form-alert">
                    Add a surveyor profile before provisioning its login account.{" "}
                    <Link to="/surveyors" onClick={clearModal}>Add surveyor profile</Link>
                  </div>
                )}
              {actionError && <div className="form-alert" role="alert">{actionError}</div>}
              <div className="form-actions">
                <button className="button button-secondary" type="button" onClick={clearModal}>Cancel</button>
                <button className="button button-primary" type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                  {(createMutation.isPending || updateMutation.isPending) && <LoaderCircle size={16} className="spin" />}
                  {editing ? "Save changes" : resourceKey === "customers" ? "Create customer" : "Create record"}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
