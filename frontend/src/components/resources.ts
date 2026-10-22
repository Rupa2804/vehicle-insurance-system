import { api } from "../api/client";
import type { RecordData, Role } from "../types";

export interface Field {
  name: string;
  label: string;
  type?: "text" | "number" | "date" | "email" | "password" | "select";
  required?: boolean;
  minLength?: number;
  options?: string[];
  secret?: boolean;
}

export interface ResourceDefinition {
  title: string;
  singular: string;
  description: string;
  endpoint: string;
  createRoles?: Role[];
  createFields?: Field[];
  updateRoles?: Role[];
  updateFields?: Field[];
  updateMethod?: "PATCH" | "PUT";
  updateEndpoint?: (record: RecordData) => string;
  allowDeleteRoles?: Role[];
  deleteEndpoint?: (record: RecordData) => string;
}

export const resources: Record<string, ResourceDefinition> = {
  customers: {
    title: "Customers",
    singular: "customer",
    description: "Customer profiles and contact information.",
    endpoint: "/customers/",
    createRoles: ["AGENT", "ADMIN"],
    createFields: [
      { name: "name", label: "Full name", required: true },
      { name: "email", label: "Email", type: "email", required: true },
      { name: "phone", label: "Phone", required: true },
      { name: "address", label: "Address", required: true },
    ],
    updateRoles: ["CUSTOMER", "AGENT", "ADMIN"],
    updateFields: [
      { name: "name", label: "Full name" },
      { name: "email", label: "Email", type: "email" },
      { name: "phone", label: "Phone" },
      { name: "address", label: "Address" },
      { name: "status", label: "Status" },
    ],
    updateEndpoint: (record) => `/customers/${record.id}`,
  },
  vehicles: {
    title: "Vehicles",
    singular: "vehicle",
    description: "Registered vehicles and customer ownership.",
    endpoint: "/vehicles/",
    createRoles: ["CUSTOMER", "AGENT", "ADMIN"],
    createFields: [
      { name: "customer_id", label: "Customer ID", type: "number" },
      { name: "registration_number", label: "Registration number", required: true },
      { name: "vin", label: "VIN", required: true },
      { name: "make", label: "Make", required: true },
      { name: "model", label: "Model", required: true },
      { name: "manufacture_year", label: "Year", type: "number", required: true },
      { name: "vehicle_type", label: "Vehicle type", required: true },
    ],
    updateRoles: ["AGENT", "ADMIN"],
    updateFields: [
      { name: "registration_number", label: "Registration number" },
      { name: "make", label: "Make" },
      { name: "model", label: "Model" },
      { name: "status", label: "Status" },
    ],
    updateEndpoint: (record) => `/vehicles/${record.id}`,
  },
  policies: {
    title: "Policies",
    singular: "policy",
    description: "Coverage terms, policy periods, and premiums.",
    endpoint: "/policies/",
    createRoles: ["AGENT", "ADMIN"],
    createFields: [
      { name: "customer_id", label: "Customer ID", type: "number", required: true },
      { name: "vehicle_id", label: "Vehicle ID", type: "number", required: true },
      { name: "policy_number", label: "Policy number", required: true },
      { name: "policy_type", label: "Policy type", required: true },
      { name: "start_date", label: "Start date", type: "date", required: true },
      { name: "end_date", label: "End date", type: "date", required: true },
      { name: "premium", label: "Premium", type: "number", required: true },
      { name: "coverage_limit", label: "Coverage limit", type: "number", required: true },
      { name: "deductible", label: "Deductible", type: "number", required: true },
    ],
    updateRoles: ["AGENT", "ADMIN"],
    updateFields: [
      { name: "premium", label: "Premium", type: "number" },
      { name: "coverage_limit", label: "Coverage limit", type: "number" },
      { name: "deductible", label: "Deductible", type: "number" },
      { name: "status", label: "Status" },
    ],
    updateEndpoint: (record) => `/policies/${record.id}`,
  },
  accidents: {
    title: "Accidents",
    singular: "accident",
    description: "Accident reports connected to insured vehicles.",
    endpoint: "/accidents/",
    createRoles: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "ADMIN"],
    createFields: [
      { name: "vehicle_id", label: "Vehicle ID", type: "number", required: true },
      { name: "customer_id", label: "Customer ID", type: "number", required: true },
      { name: "accident_date", label: "Accident date", type: "date", required: true },
      { name: "location", label: "Location", required: true },
      { name: "accident_type", label: "Accident type", required: true },
      { name: "description", label: "Description" },
    ],
    updateRoles: ["AGENT", "CLAIMS_OFFICER", "ADMIN"],
    updateFields: [
      { name: "location", label: "Location" },
      { name: "accident_type", label: "Accident type" },
      { name: "description", label: "Description" },
    ],
    updateEndpoint: (record) => `/accidents/${record.id}`,
    allowDeleteRoles: ["CLAIMS_OFFICER", "ADMIN"],
    deleteEndpoint: (record) => `/accidents/${record.id}`,
  },
  claims: {
    title: "Claims",
    singular: "claim",
    description: "Claim submissions, status, and linked accident records.",
    endpoint: "/claims/",
    createRoles: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "ADMIN"],
    createFields: [
      { name: "policy_id", label: "Policy ID", type: "number", required: true },
      { name: "vehicle_id", label: "Vehicle ID", type: "number", required: true },
      { name: "accident_id", label: "Accident ID", type: "number", required: true },
      { name: "claim_type", label: "Claim type", required: true },
      { name: "claimed_amount", label: "Claimed amount", type: "number", required: true },
      {
        name: "priority",
        label: "Priority",
        type: "select",
        options: ["LOW", "MEDIUM", "HIGH"],
        required: true,
      },
      { name: "description", label: "Description" },
    ],
    updateRoles: ["CLAIMS_OFFICER", "ADMIN"],
    updateFields: [
      { name: "claim_type", label: "Claim type" },
      { name: "claimed_amount", label: "Claimed amount", type: "number" },
      { name: "priority", label: "Priority" },
      { name: "description", label: "Description" },
    ],
    updateEndpoint: (record) => `/claims/${record.id}`,
    allowDeleteRoles: ["CLAIMS_OFFICER", "ADMIN"],
    deleteEndpoint: (record) => `/claims/${record.id}`,
  },
  surveyors: {
    title: "Surveyors",
    singular: "surveyor",
    description: "Surveyor roster and current availability.",
    endpoint: "/surveyors/",
    createRoles: ["CLAIMS_OFFICER", "ADMIN"],
    createFields: [
      { name: "name", label: "Name", required: true },
      { name: "email", label: "Email", type: "email", required: true },
      { name: "phone", label: "Phone" },
      { name: "region", label: "Region" },
      { name: "specialization", label: "Specialization" },
    ],
  },
  inspections: {
    title: "Inspections",
    singular: "inspection",
    description: "Field inspections and surveyor assignments.",
    endpoint: "/inspections/",
    createRoles: ["CLAIMS_OFFICER", "ADMIN"],
    createFields: [
      { name: "claim_id", label: "Claim ID", type: "number", required: true },
      { name: "surveyor_id", label: "Surveyor ID", type: "number", required: true },
      { name: "inspection_date", label: "Scheduled at", type: "text", required: true },
      { name: "vehicle_condition", label: "Vehicle condition" },
      { name: "damage_summary", label: "Damage summary" },
      { name: "remarks", label: "Remarks" },
    ],
    updateRoles: ["CLAIMS_OFFICER", "SURVEYOR", "ADMIN"],
    updateFields: [
      { name: "inspection_date", label: "Scheduled at", type: "text" },
      { name: "vehicle_condition", label: "Vehicle condition" },
      { name: "damage_summary", label: "Damage summary" },
      { name: "estimated_cost", label: "Estimated cost", type: "number" },
      { name: "remarks", label: "Remarks" },
    ],
    updateEndpoint: (record) => `/inspections/${record.id}`,
    allowDeleteRoles: ["CLAIMS_OFFICER", "ADMIN"],
    deleteEndpoint: (record) => `/inspections/${record.id}`,
  },
  assessments: {
    title: "Damage assessments",
    singular: "assessment",
    description: "Assessed vehicle components and approved repair costs.",
    endpoint: "/damage-assessments/",
    createRoles: ["CLAIMS_OFFICER", "SURVEYOR", "ADMIN"],
    createFields: [
      { name: "claim_id", label: "Claim ID", type: "number", required: true },
      { name: "component", label: "Component", required: true },
      { name: "damage_type", label: "Damage type", required: true },
      { name: "severity", label: "Severity", required: true },
      { name: "estimated_cost", label: "Estimated cost", type: "number", required: true },
      { name: "remarks", label: "Remarks" },
    ],
    updateRoles: ["CLAIMS_OFFICER", "SURVEYOR", "ADMIN"],
    updateFields: [
      { name: "component", label: "Component" },
      { name: "damage_type", label: "Damage type" },
      { name: "severity", label: "Severity" },
      { name: "estimated_cost", label: "Estimated cost", type: "number" },
      { name: "remarks", label: "Remarks" },
    ],
    updateEndpoint: (record) => `/damage-assessments/${record.id}`,
    allowDeleteRoles: ["CLAIMS_OFFICER", "ADMIN"],
    deleteEndpoint: (record) => `/damage-assessments/${record.id}`,
  },
  settlements: {
    title: "Settlements",
    singular: "settlement",
    description: "Financial settlement figures returned by the claims API.",
    endpoint: "/settlements/",
    createRoles: ["FINANCE", "ADMIN"],
    createFields: [
      { name: "claim_id", label: "Claim ID", type: "number", required: true },
      { name: "estimated_amount", label: "Estimated amount", type: "number", required: true },
      { name: "approved_amount", label: "Approved amount", type: "number", required: true },
      { name: "deductible", label: "Deductible", type: "number", required: true },
      { name: "coverage_limit", label: "Coverage limit", type: "number", required: true },
      { name: "final_amount", label: "Final amount (server recalculates)", type: "number", required: true },
    ],
    updateRoles: ["FINANCE", "ADMIN"],
    updateFields: [
      { name: "claim_id", label: "Claim ID", type: "number", required: true },
      { name: "estimated_amount", label: "Estimated amount", type: "number", required: true },
      { name: "approved_amount", label: "Approved amount", type: "number", required: true },
      { name: "deductible", label: "Deductible", type: "number", required: true },
      { name: "coverage_limit", label: "Coverage limit", type: "number", required: true },
      { name: "final_amount", label: "Final amount (server recalculates)", type: "number", required: true },
      { name: "status", label: "Status", required: true },
    ],
    updateEndpoint: (record) => `/settlements/${record.id}`,
    updateMethod: "PUT",
  },
  payments: {
    title: "Payments",
    singular: "payment",
    description: "Payment records and processing state.",
    endpoint: "/payments/",
    createRoles: ["FINANCE", "ADMIN"],
    createFields: [
      { name: "settlement_id", label: "Settlement ID", type: "number", required: true },
      { name: "amount", label: "Amount", type: "number", required: true },
      { name: "payment_method", label: "Payment method", required: true },
      { name: "transaction_reference", label: "Transaction reference", required: true },
    ],
  },
  users: {
    title: "User access",
    singular: "account",
    description: "Provision team access. Public self-registration is disabled.",
    endpoint: "/auth/users",
    createRoles: ["ADMIN"],
    createFields: [
      { name: "email", label: "Email", type: "email", required: true },
      { name: "password", label: "Temporary password (at least 12 characters)", type: "password", required: true, minLength: 12 },
      {
        name: "role",
        label: "Role",
        type: "select",
        options: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "SURVEYOR", "FINANCE", "MANAGER", "ADMIN"],
        required: true,
      },
      { name: "customer_id", label: "Customer ID (customer accounts only)", type: "number" },
      { name: "surveyor_id", label: "Surveyor ID (surveyor accounts only)", type: "number" },
    ],
  },
};

export async function loadResource(key: string): Promise<RecordData[]> {
  const paginatedResources = new Set(["claims", "surveyors", "inspections", "assessments"]);
  if (paginatedResources.has(key)) {
    return loadAllPages(resources[key].endpoint);
  }
  if (key === "settlements" || key === "payments") {
    const claims = await loadClaims();
    const settlements = (
      await Promise.all(
        claims.map(async (claim) => {
          try {
            const { data } = await api.get<RecordData[] | RecordData>(
              `/settlements/claim/${claim.id}`,
            );
            return Array.isArray(data) ? data : [data];
          } catch (error) {
            if (isNotFound(error)) return [];
            throw error;
          }
        }),
      )
    ).flat();
    if (key === "settlements") return settlements;
    return (
      await Promise.all(
        settlements.map(async (settlement) => {
          const { data } = await api.get<RecordData[]>(
            `/payments/settlement/${settlement.id}`,
          );
          return data;
        }),
      )
    ).flat();
  }
  if (key === "users") {
    const { data } = await api.get<RecordData[]>("/auth/users");
    return data;
  }
  const { data } = await api.get<RecordData[]>(resources[key].endpoint);
  return data;
}

export function loadClaims(): Promise<RecordData[]> {
  return loadAllPages("/claims/");
}

async function loadAllPages(endpoint: string): Promise<RecordData[]> {
  const records: RecordData[] = [];
  const limit = 100;
  for (let skip = 0; ; skip += limit) {
    const { data } = await api.get<RecordData[]>(endpoint, {
      params: { skip, limit },
    });
    records.push(...data);
    if (data.length < limit) return records;
  }
}

function isNotFound(error: unknown): boolean {
  return typeof error === "object" && error !== null && "response" in error
    && typeof error.response === "object" && error.response !== null
    && "status" in error.response && error.response.status === 404;
}
