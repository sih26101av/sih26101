/**
 * FILE: src/services/learningApi.ts
 *
 * Client for Learning Mode — a NotebookLM-style study chat built from the same
 * document upload the Assessment Studio uses for quizzes
 * (backend: routers/learning_mode.py, mounted at /api/v1/rag/learning).
 *
 * Unauthenticated, like the document/media quiz uploads: `material_id` is an
 * in-memory session key, not tied to a user.
 */

const LEARNING_BASE_URL = "http://localhost:8000/api/v1/rag/learning";

export interface LearningMetadata {
  filename: string;
  file_type: string;
  character_count: number;
  word_count: number;
  chunk_count: number;
  page_count?: number | null;
  slide_count?: number | null;
  line_count?: number | null;
  section_count?: number | null;
  ocr?: Record<string, unknown> | null;
}

export interface LearningStartResponse {
  status: string;
  material_id: string;
  filename: string;
  file_type: string;
  metadata: LearningMetadata;
  summary: string;
  topics: string[];
  suggested_questions: string[];
}

export interface LearningCitation {
  locator: string;
  quote: string;
}

export interface LearningChatTurn {
  role: "user" | "model";
  content: string;
}

export interface LearningChatResponse {
  status: string;
  material_id: string;
  reply: string;
  citations: LearningCitation[];
}

async function readError(res: Response): Promise<Error> {
  try {
    const body = await res.json();
    const d = body?.detail;
    const msg = typeof d === "string" ? d : d?.message ?? JSON.stringify(d ?? body);
    return new Error(msg || `Request failed (${res.status})`);
  } catch {
    return new Error(`Request failed (${res.status})`);
  }
}

// Backend bounds its own LLM calls (30 s overview, 60 s chat); these cover a
// server that accepts the connection but never answers (e.g. a hung --reload).
const START_TIMEOUT_MS = 120_000;
const CHAT_TIMEOUT_MS = 90_000;

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs: number): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } catch (err) {
    if (controller.signal.aborted) {
      throw new Error(
        `The server didn't respond within ${timeoutMs / 1000} s. Check the backend on port 8000 is running ` +
        "(restart uvicorn if it was auto-reloading) and try again.",
      );
    }
    throw new Error("Could not reach the backend on port 8000 — is it running?");
  } finally {
    clearTimeout(timer);
  }
}

export async function startLearningSession(file: File): Promise<LearningStartResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetchWithTimeout(`${LEARNING_BASE_URL}/start`, { method: "POST", body: form }, START_TIMEOUT_MS);
  if (!res.ok) throw await readError(res);
  return res.json();
}

export async function sendLearningMessage(
  materialId: string,
  message: string,
  history: LearningChatTurn[],
): Promise<LearningChatResponse> {
  const res = await fetchWithTimeout(`${LEARNING_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ material_id: materialId, message, history }),
  }, CHAT_TIMEOUT_MS);
  if (!res.ok) throw await readError(res);
  return res.json();
}
