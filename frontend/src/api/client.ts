import axios, { AxiosError } from "axios";

export const TOKEN_KEY = "vehicle-insurance-access-token";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: unknown }>) => {
    if (error.response?.status === 401 && sessionStorage.getItem(TOKEN_KEY)) {
      sessionStorage.removeItem(TOKEN_KEY);
      window.dispatchEvent(new Event("session-expired"));
    }
    return Promise.reject(error);
  },
);

export function readableError(error: unknown): string {
  if (!axios.isAxiosError(error)) return "Something went wrong. Please try again.";
  if (!error.response) {
    return `Cannot connect to the API at ${api.defaults.baseURL}. Start the FastAPI server and check VITE_API_BASE_URL.`;
  }
  const detail = error.response.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((issue) =>
        typeof issue === "object" && issue !== null && "msg" in issue
          ? String(issue.msg)
          : String(issue),
      )
      .join(" · ");
  }
  if (error.response.status === 403) return "Your role does not have access to this action.";
  if (error.response.status === 404) return "This record could not be found.";
  if (error.response.status === 409) return "This change conflicts with an existing record.";
  if (error.response.status >= 500) return "The server could not complete the request.";
  return `Request failed (${error.response.status}). Please check your entries.`;
}
