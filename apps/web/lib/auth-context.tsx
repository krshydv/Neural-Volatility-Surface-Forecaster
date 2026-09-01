"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api, UserRead } from "@/lib/api";

interface AuthContextValue {
  user: UserRead | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogleCode: (code: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = "volaris_access_token";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserRead | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = window.localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLoading(false);
      return;
    }
    api
      .me(stored)
      .then((u) => {
        setToken(stored);
        setUser(u);
      })
      .catch(() => {
        window.localStorage.removeItem(TOKEN_KEY);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await api.login(email, password);
    const currentUser = await api.me(tokens.access_token);
    window.localStorage.setItem(TOKEN_KEY, tokens.access_token);
    setToken(tokens.access_token);
    setUser(currentUser);
  }, []);

  const loginWithGoogleCode = useCallback(async (code: string) => {
    const tokens = await api.googleCallback(code);
    const currentUser = await api.me(tokens.access_token);
    window.localStorage.setItem(TOKEN_KEY, tokens.access_token);
    setToken(tokens.access_token);
    setUser(currentUser);
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      await api.register(email, password, fullName);
      await login(email, password);
    },
    [login]
  );

  const logout = useCallback(() => {
    window.localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, loginWithGoogleCode, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
