import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { lazy, Suspense, useMemo } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from "react-router-dom";
import type { ReactNode } from "react";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { Shell } from "./components/Shell";
import type { Role } from "./types";

const Dashboard = lazy(() =>
  import("./pages/Dashboard").then((module) => ({ default: module.Dashboard })),
);
const Login = lazy(() =>
  import("./pages/Login").then((module) => ({ default: module.Login })),
);
const ReportsPage = lazy(() =>
  import("./pages/ReportsPage").then((module) => ({ default: module.ReportsPage })),
);
const ResourcePage = lazy(() =>
  import("./pages/ResourcePage").then((module) => ({ default: module.ResourcePage })),
);

const resourceRoles: Record<string, Role[]> = {
  customers: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  vehicles: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  policies: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  accidents: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  claims: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "SURVEYOR", "FINANCE", "MANAGER", "ADMIN"],
  surveyors: ["CLAIMS_OFFICER", "MANAGER", "ADMIN"],
  inspections: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "SURVEYOR", "MANAGER", "ADMIN"],
  assessments: ["CUSTOMER", "AGENT", "CLAIMS_OFFICER", "SURVEYOR", "FINANCE", "MANAGER", "ADMIN"],
  settlements: ["CUSTOMER", "CLAIMS_OFFICER", "FINANCE", "MANAGER", "ADMIN"],
  payments: ["CUSTOMER", "CLAIMS_OFFICER", "FINANCE", "MANAGER", "ADMIN"],
  users: ["ADMIN"],
};

function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) return <div className="app-loading"><div className="loading-mark" /><span>Preparing your workspace…</span></div>;
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}

function RoleRoute({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const { user } = useAuth();
  return user && roles.includes(user.role) ? children : <Navigate to="/" replace />;
}

function ApplicationRoutes() {
  const { user } = useAuth();
  const resourceRoutes = useMemo(
    () =>
      Object.entries(resourceRoles).map(([key, roles]) => (
        <Route
          key={key}
          path={`/${key}`}
          element={
            <RoleRoute roles={roles}>
              <Suspense fallback={<RouteLoading />}>
                <ResourcePage resourceKey={key} />
              </Suspense>
            </RoleRoute>
          }
        />
      )),
    [],
  );
  return (
    <Routes>
      <Route
        path="/login"
        element={
          user ? <Navigate to="/" replace /> : (
            <Suspense fallback={<RouteLoading />}><Login /></Suspense>
          )
        }
      />
      <Route element={<ProtectedRoute />}>
        <Route element={<Shell />}>
          <Route index element={<Suspense fallback={<RouteLoading />}><Dashboard /></Suspense>} />
          {resourceRoutes}
          <Route
            path="/reports"
            element={
              <RoleRoute roles={["CLAIMS_OFFICER", "FINANCE", "MANAGER", "ADMIN"]}>
                <Suspense fallback={<RouteLoading />}><ReportsPage /></Suspense>
              </RoleRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Route>
    </Routes>
  );
}

function RouteLoading() {
  return <div className="app-loading"><div className="loading-mark" /><span>Loading section…</span></div>;
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false, staleTime: 15_000 },
    mutations: { retry: 0 },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter><ApplicationRoutes /></BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}
