export type Role =
  | "CUSTOMER"
  | "AGENT"
  | "CLAIMS_OFFICER"
  | "SURVEYOR"
  | "FINANCE"
  | "ADMIN"
  | "MANAGER";

export interface User {
  id: number;
  email: string;
  role: Role;
  customer_id: number | null;
  surveyor_id: number | null;
  is_active: boolean;
  created_at: string;
}

export interface CustomerRegistration {
  name: string;
  email: string;
  password: string;
  phone: string;
  address: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: User;
}

export type RecordData = Record<string, unknown>;
