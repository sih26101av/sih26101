/**
 * FILE: src/services/mediaQuizApi.ts
 *
 * Client for the video / audio / YouTube → quiz pipeline
 * (backend: routers/media_quiz.py, mounted at /api/v1/rag/media).
 *
 * The response keeps the document-quiz shape (`quiz_id`, `questions`, …) so the
 * Assessment Studio's quiz + grade flow is reused unchanged; the extra `media`
 * report (route, probe, evidence, validator, fact-check) feeds MediaAnalysisCard.
 */

import { API_BASE_URL } from '../config';

const MEDIA_BASE_URL = `${API_BASE_URL}/api/v1/rag/media`;

export const MEDIA_VIDEO_EXTS = [".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".mpeg", ".mpg", ".3gp"];
export const MEDIA_AUDIO_EXTS = [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".opus", ".flac", ".wma"];
export const MEDIA_ACCEPT = [...MEDIA_VIDEO_EXTS, ...MEDIA_AUDIO_EXTS].join(",");

export type MediaContentType =
  | "narrated_slides"
  | "talking_head"
  | "silent_screen_demo"
  | "silent_slides"
  | "reject";

export interface MediaQuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  evidence: string[];
  kind: "chunk" | "synthesis";
  answer_type: string;
  t_start: number | null;
  t_end: number | null;
  review: { status?: "ok" | "flagged" | "no_reference" | "unchecked"; note?: string; reference_id?: string };
}

export interface MediaEvidence {
  id: string;
  t_start: number;
  t_end: number;
  source: "asr" | "ocr" | "vlm";
  text: string;
  confidence: number;
  lang: string;
}

export interface MediaReport {
  content_type: MediaContentType;
  vlm_backend: string;
  probe: {
    duration: number;
    speech_ratio: number;
    text_density: number;
    screen_activity: number;
    scene_changes: number;
    keyframes: number;
    tools: string[];
  };
  evidence?: { extracted: Record<string, number>; kept: Record<string, number>; dropped: Record<string, number>; min_confidence: number };
  relevance?: { competency_id?: string; competency_name?: string; chunks_kept?: number; off_topic?: boolean };
  generation?: { raw_candidates: number; accepted: number; rejected_total: number; rejected: Record<string, number> };
  fact_check?: { checked: number; flagged: number; ok: number; no_reference: number };
  timings?: Record<string, number>;
  /** Where the material came from, e.g. "speech from YouTube auto captions (hi)".
   *  A deployed server is often refused YouTube's media URLs and builds the quiz
   *  from captions alone, so say so rather than silently dropping on-screen text. */
  source_notes?: string[];
}

export interface MediaQuizResponse {
  status: string;
  message: string;
  quiz_id: string;
  filename: string;
  file_type: string;
  competency_id: string | null;
  skill_name: string;
  questions: MediaQuizQuestion[];
  metadata: { duration_s: number; source: "upload" | "youtube"; chunk_count: number };
  media: MediaReport;
  evidence: MediaEvidence[];
}

export function isMediaFile(file: File): boolean {
  const name = file.name.toLowerCase();
  const ext = name.slice(name.lastIndexOf("."));
  return (
    MEDIA_VIDEO_EXTS.includes(ext) ||
    MEDIA_AUDIO_EXTS.includes(ext) ||
    file.type.startsWith("video/") ||
    file.type.startsWith("audio/")
  );
}

export function isYoutubeUrl(url: string): boolean {
  try {
    const host = new URL(url.trim()).hostname.toLowerCase();
    return ["youtu.be", "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"].includes(host);
  } catch {
    return false;
  }
}

async function readError(res: Response): Promise<Error> {
  try {
    const body = await res.json();
    const d = body?.detail;
    // 422 "not learnable" carries {message, media}; other errors a plain string.
    const msg = typeof d === "string" ? d : d?.message ?? JSON.stringify(d ?? body);
    return new Error(msg || `Request failed (${res.status})`);
  } catch {
    return new Error(`Request failed (${res.status})`);
  }
}

export async function generateMediaQuiz(
  file: File,
  difficulty: string,
  targetLang?: string,
): Promise<MediaQuizResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("difficulty", difficulty);
  if (targetLang) form.append("target_lang", targetLang);
  const res = await fetch(`${MEDIA_BASE_URL}/upload`, { method: "POST", body: form });
  if (!res.ok) throw await readError(res);
  return res.json();
}

export async function generateYoutubeQuiz(
  url: string,
  difficulty: string,
  targetLang?: string,
): Promise<MediaQuizResponse> {
  const res = await fetch(`${MEDIA_BASE_URL}/youtube`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: url.trim(), difficulty, target_lang: targetLang || null }),
  });
  if (!res.ok) throw await readError(res);
  return res.json();
}

export function formatTimestamp(seconds: number | null | undefined): string {
  if (seconds == null) return "";
  const s = Math.max(0, Math.floor(seconds));
  const mm = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
  const ss = String(s % 60).padStart(2, "0");
  return s >= 3600 ? `${Math.floor(s / 3600)}:${mm}:${ss}` : `${mm}:${ss}`;
}
