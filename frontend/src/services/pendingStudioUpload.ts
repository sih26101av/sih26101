/**
 * FILE: src/services/pendingStudioUpload.ts
 *
 * Hand-off from Gyan's chat widget to the Assessment Studio: when the learner
 * attaches a document in the chat and asks for a quiz or to study it, Gyan
 * stores the File here and navigates to /assessment, so the learner never has
 * to upload it a second time (see docs/features/rag-quiz-generator.md).
 *
 * A File object can't survive sessionStorage or react-router `state` cleanly
 * across a lazy-loaded route remount, so this is a plain module singleton —
 * it lives only for the current tab's JS runtime, which is exactly the
 * hand-off's lifetime (set right before navigate(), consumed on the next
 * page's mount).
 */

export type StudioMode = "quiz" | "learn";

export interface PendingStudioUpload {
  file: File;
  mode: StudioMode;
}

let pending: PendingStudioUpload | null = null;

export function setPendingStudioUpload(file: File, mode: StudioMode): void {
  pending = { file, mode };
}

/** Reads and clears the pending upload — call once, on the Assessment Studio's mount. */
export function consumePendingStudioUpload(): PendingStudioUpload | null {
  const cur = pending;
  pending = null;
  return cur;
}
