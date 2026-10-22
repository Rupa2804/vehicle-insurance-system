import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, TOKEN_KEY } from "../api/client";
import type { LoginResponse, User } from "../types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login(email: string, password: string): Promise<void>;
  logout(): void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    sessionStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  useEffect(() => {
    const expire = () => logout();
    window.addEventListener("session-expired", expire);
    const token = sessionStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      return () => window.removeEventListener("session-expired", expire);
    }
    api
      .get<User>("/auth/me")
      .then(({ data }) => setUser(data))
      .catch(logout)
      .finally(() => setLoading(false));
    return () => window.removeEventListener("session-expired", expire);
  }, [logout]);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await api.post<LoginResponse>("/auth/login", { email, password });
    sessionStorage.setItem(TOKEN_KEY, data.access_token);
    setUser(data.user);
  }, []);

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
