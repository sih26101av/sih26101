/**
 * FILE: src/context/AuthContext.tsx
 *
 * PATTERN: Context + Provider
 * ─────────────────────────────────────────────────────────────────────────────
 * Full JWT + RBAC auth context.
 *
 * Security model
 * ──────────────
 * • Access token is stored ONLY in React state (never localStorage / sessionStorage).
 *   It is cleared automatically when the tab closes.
 * • Refresh token lives in an httpOnly, SameSite=Strict cookie managed entirely
 *   by the browser. JS code can never read or write it.
 * • On startup the context attempts a silent /auth/refresh so a page reload
 *   doesn't log the user out (as long as the refresh cookie is still valid).
 *
 * Public API exposed via useAuth()
 * ─────────────────────────────────
 *   user               – current AuthUser or null
 *   accessToken        – current JWT string or null (use for Authorization headers)
 *   mustChangePassword – true if the user must set a new password before proceeding
 *   isLoading          – true during the initial silent refresh attempt
 *   login(u, p)        – async; calls /auth/login
 *   logout()           – async; calls /auth/logout, clears state
 *   refreshToken()     – async; calls /auth/refresh, returns new token string
 *   setMustChangePassword(v) – called by ChangePasswordPage after success
 * ─────────────────────────────────────────────────────────────────────────────
 */

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';
import * as authApi from '../services/authApi';
import type { UserRole } from '../patterns/DashboardFactory';

// ── Domain types ───────────────────────────────────────────────────────────────

export interface AuthUser {
  /** The usr_XXXXXXXXX userId from iGOT — also the login username */
  username: string;
  /** Mapped from auth DB role ("learner" | "admin") to DashboardFactory's UserRole */
  role: UserRole;
}

interface AuthContextType {
  user: AuthUser | null;
  accessToken: string | null;
  mustChangePassword: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<string>;
  setMustChangePassword: (v: boolean) => void;
}

// ── Role mapping ────────────────────────────────────────────────────────────────
function mapRole(serverRole: string): UserRole {
  if (serverRole === 'admin') return 'admin';
  return 'official'; // "learner" maps to the existing "official" DashboardFactory key
}

// ── Context ────────────────────────────────────────────────────────────────────
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ── Provider ───────────────────────────────────────────────────────────────────
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [mustChangePassword, setMustChangePasswordState] = useState(false);
  const [isLoading, setIsLoading] = useState(true); // true during silent-refresh on mount

  // Track whether a refresh is already in-flight to prevent double calls
  const refreshingRef = useRef(false);

  // ── Silent refresh on mount ─────────────────────────────────────────────────
  // If the user still has a valid refresh cookie from a previous session,
  // exchange it for a new access token without showing a login screen.
  useEffect(() => {
    let cancelled = false;

    const silentRefresh = async () => {
      try {
        const { access_token } = await authApi.refresh();
        if (cancelled) return;

        // Got a new token — fetch user info to rebuild state
        const me = await authApi.getMe(access_token);
        if (cancelled) return;

        setAccessToken(access_token);
        setUser({ username: me.username, role: mapRole(me.role) });
        setMustChangePasswordState(me.must_change_password);
      } catch {
        // No valid refresh cookie — stay logged out (that's fine)
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    silentRefresh();
    return () => { cancelled = true; };
  }, []);

  // ── login ───────────────────────────────────────────────────────────────────
  const login = useCallback(async (username: string, password: string) => {
    const data = await authApi.login(username, password);
    // Fetch /auth/me to get role (not embedded in TokenResponse by design)
    const me = await authApi.getMe(data.access_token);

    setAccessToken(data.access_token);
    setUser({ username: me.username, role: mapRole(me.role) });
    setMustChangePasswordState(data.must_change_password);
  }, []);

  // ── logout ──────────────────────────────────────────────────────────────────
  const logout = useCallback(async () => {
    if (accessToken) {
      await authApi.logout(accessToken);
    }
    setUser(null);
    setAccessToken(null);
    setMustChangePasswordState(false);
  }, [accessToken]);

  // ── refreshToken ────────────────────────────────────────────────────────────
  // Returns the new token string so callers (API interceptor) can retry.
  const refreshToken = useCallback(async (): Promise<string> => {
    if (refreshingRef.current) {
      // Wait for the ongoing refresh to settle instead of double-calling
      return new Promise((resolve, reject) => {
        const interval = setInterval(() => {
          if (!refreshingRef.current) {
            clearInterval(interval);
            if (accessToken) resolve(accessToken);
            else reject(new Error('Refresh failed'));
          }
        }, 100);
      });
    }

    refreshingRef.current = true;
    try {
      const { access_token } = await authApi.refresh();
      setAccessToken(access_token);
      return access_token;
    } finally {
      refreshingRef.current = false;
    }
  }, [accessToken]);

  // ── setMustChangePassword (called by ChangePasswordPage on success) ──────────
  const setMustChangePassword = useCallback((v: boolean) => {
    setMustChangePasswordState(v);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        mustChangePassword,
        isLoading,
        login,
        logout,
        refreshToken,
        setMustChangePassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// ── Hook ───────────────────────────────────────────────────────────────────────
export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
