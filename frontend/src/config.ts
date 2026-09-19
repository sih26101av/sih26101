/// <reference types="vite/client" />
/**
 * FILE: src/config.ts
 *
 * Backend origin for every API call. Set VITE_API_BASE_URL at build time
 * (Vercel → Project Settings → Environment Variables); local dev falls back
 * to the FastAPI server on port 8000.
 */

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');
