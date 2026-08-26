/**
 * FILE: src/context/AuthContext.tsx
 *
 * Lightweight auth context that stores the currently logged-in user.
 * LoginPage writes here after the DashboardFactory resolves the role.
 * All dashboards read userId from here — no hardcoded IDs anywhere.
 *
 * When you implement real authentication, replace setUser() call
 * in LoginPage with the real token + user-fetch response.
 */

import React, { createContext, useContext, useState } from 'react';
import type { UserRole } from '../patterns/DashboardFactory';

export interface AuthUser {
  userId:   string;    // e.g. "usr_720465595" — must match mock server
  govId:    string;    // e.g. "EMP-6282"
  fullName: string;
  role:     UserRole;
}

interface AuthContextType {
  user:    AuthUser | null;
  setUser: (u: AuthUser | null) => void;
  logout:  () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
