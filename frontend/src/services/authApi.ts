/**
 * FILE: src/services/authApi.ts
 *
 * Dedicated module for all /auth/* calls to My App Backend (port 8000).
 *
 * Design notes
 * ────────────
 * • All requests use credentials: 'include' so the browser sends/receives
 *   the httpOnly refresh_token cookie automatically.
 * • Access tokens are NOT handled here — callers (AuthContext) manage them
 *   in React state.
 * • Errors are thrown as plain Error objects with human-readable messages
 *   parsed from the FastAPI detail field.
 */

const AUTH_BASE = 'http://localhost:8000';

// ── Response shapes ────────────────────────────────────────────────────────────

export interface LoginResponse {
  access_token: string;
  token_type: string;
  must_change_password: boolean;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
}

export interface UserAuthOut {
  id: number;
  username: string;
  role: string;
  must_change_password: boolean;
}

// ── Helper: extract FastAPI detail from error responses ────────────────────────
async function extractError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return body?.detail ?? `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
}

// ── POST /auth/login ───────────────────────────────────────────────────────────
/**
 * Exchange username + password for an access token.
 * The server also sets an httpOnly refresh_token cookie automatically.
 *
 * Uses application/x-www-form-urlencoded because FastAPI's OAuth2PasswordRequestForm
 * expects form data, not JSON.
 */
export async function login(username: string, password: string): Promise<LoginResponse> {
  const body = new URLSearchParams({ username, password });

  const res = await fetch(`${AUTH_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
    credentials: 'include', // sends/receives cookies
  });

  if (!res.ok) {
    const msg = await extractError(res);
    throw new Error(msg);
  }

  return res.json() as Promise<LoginResponse>;
}

// ── POST /auth/refresh ─────────────────────────────────────────────────────────
/**
 * Use the httpOnly refresh_token cookie to obtain a new access token.
 * The browser sends the cookie automatically thanks to credentials: 'include'.
 */
export async function refresh(): Promise<RefreshResponse> {
  const res = await fetch(`${AUTH_BASE}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  });

  if (!res.ok) {
    const msg = await extractError(res);
    throw new Error(msg);
  }

  return res.json() as Promise<RefreshResponse>;
}

// ── POST /auth/logout ──────────────────────────────────────────────────────────
/**
 * Invalidate the server-side refresh token and clear the cookie.
 * Requires a valid access token in the Authorization header.
 */
export async function logout(accessToken: string): Promise<void> {
  await fetch(`${AUTH_BASE}/auth/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${accessToken}` },
    credentials: 'include',
  });
  // Swallow errors — we always clear local state regardless of server response
}

// ── POST /auth/change-password ─────────────────────────────────────────────────
export async function changePassword(
  accessToken: string,
  currentPassword: string,
  newPassword: string,
): Promise<void> {
  const res = await fetch(`${AUTH_BASE}/auth/change-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    credentials: 'include',
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });

  if (!res.ok) {
    const msg = await extractError(res);
    throw new Error(msg);
  }
}

// ── GET /auth/me ───────────────────────────────────────────────────────────────
/**
 * Re-hydrate user info from the server.
 * Used after a successful token refresh to sync AuthContext.
 */
export async function getMe(accessToken: string): Promise<UserAuthOut> {
  const res = await fetch(`${AUTH_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    credentials: 'include',
  });

  if (!res.ok) {
    const msg = await extractError(res);
    throw new Error(msg);
  }

  return res.json() as Promise<UserAuthOut>;
}
