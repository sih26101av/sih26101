/**
 * FILE: src/components/assessment/LearningChat.tsx
 *
 * Learning Mode — the Assessment Studio's NotebookLM-style study companion.
 * Same document upload as the quiz pipeline (services/learningApi.ts →
 * routers/learning_mode.py), but instead of generating questions it opens a
 * grounded Q&A chat over the document: every answer is retrieved from the
 * learner's own source and can cite the passage it came from.
 */

import React, { useEffect, useRef, useState } from "react";
import { Bot, FileText, Quote, Send, Sparkles, Upload, User } from "lucide-react";
import type { LearningChatTurn, LearningCitation, LearningStartResponse } from "../../services/learningApi";
import { sendLearningMessage } from "../../services/learningApi";
import SectionCard from "../shell/SectionCard";

interface ChatEntry {
  role: "user" | "model";
  content: string;
  citations?: LearningCitation[];
}

interface LearningChatProps {
  session: LearningStartResponse | null;
  loading: boolean;
  error: string;
  onUpload: (file: File) => void;
  onReset: () => void;
}

const LEARNING_ACCEPT = ".pdf,.docx,.pptx,.txt";

const LearningChat: React.FC<LearningChatProps> = ({ session, loading, error, onUpload, onReset }) => {
  const [entries, setEntries] = useState<ChatEntry[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!loading) return;
    setElapsed(0);
    const id = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [loading]);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setEntries(session ? [{ role: "model", content: session.summary }] : []);
    setSendError("");
  }, [session?.material_id]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries, sending]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) onUpload(f);
    e.target.value = "";
  };

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || !session || sending) return;
    const history: LearningChatTurn[] = entries.map((e) => ({ role: e.role, content: e.content }));
    setEntries((cur) => [...cur, { role: "user", content: trimmed }]);
    setInput("");
    setSendError("");
    setSending(true);
    try {
      const res = await sendLearningMessage(session.material_id, trimmed, history);
      setEntries((cur) => [...cur, { role: "model", content: res.reply, citations: res.citations }]);
    } catch (err: any) {
      setSendError(err.message || "Could not get a study answer.");
    } finally {
      setSending(false);
    }
  };

  // ── No active session: the upload zone ──────────────────────────────────
  if (!session) {
    return (
      <SectionCard
        title="Learning Mode"
        subtitle="Upload a document and study it in a grounded chat — every answer cites the passage it came from"
      >
        <input
          ref={fileRef}
          type="file"
          className="hidden"
          accept={LEARNING_ACCEPT}
          aria-label="Choose a document to study"
          onChange={handleFileChange}
        />
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={loading}
          className="flex w-full flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-gov-line p-10 text-center transition-all hover:border-gov-blue/40 hover:bg-accent-blue-soft/40 disabled:opacity-60 dark:border-slate-700 dark:hover:bg-sky-500/5"
        >
          {loading ? (
            <>
              <span className="h-8 w-8 animate-spin rounded-full border-4 border-accent-blue-soft border-t-gov-navy dark:border-sky-900/50 dark:border-t-sky-400" />
              <span className="text-[13px] font-medium text-slate-500 dark:text-slate-400">Reading your document and preparing the study session…</span>
              <span className="text-[11.5px] tabular-nums text-slate-400">
                {elapsed}s — usually under 30 s{elapsed > 45 ? "; the first upload after a restart is slower" : ""}
              </span>
            </>
          ) : (
            <>
              <Upload className="h-8 w-8 text-accent-blue dark:text-sky-400" aria-hidden="true" />
              <span className="text-[13px] font-semibold text-gov-ink dark:text-white">Upload a document to start studying</span>
              <span className="text-[12px] text-slate-400">PDF, DOCX, PPTX or TXT</span>
            </>
          )}
        </button>
        {error && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-accent-rose dark:border-red-800/50 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}
      </SectionCard>
    );
  }

  // ── Active session: the study chat ──────────────────────────────────────
  return (
    <SectionCard
      title="Learning Mode"
      subtitle={session.filename}
      action={
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg px-2.5 py-1.5 text-[12px] font-semibold text-slate-500 transition-colors hover:bg-gov-paper hover:text-gov-ink dark:text-slate-400 dark:hover:bg-slate-800"
        >
          Study a different document
        </button>
      }
      padded={false}
    >
      <div className="flex flex-col gap-4 border-t border-gov-line px-5 py-5 dark:border-slate-700/60">
        {session.topics.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {session.topics.map((t) => (
              <span key={t} className="chip bg-accent-blue-soft text-accent-blue dark:bg-sky-900/30 dark:text-sky-300">{t}</span>
            ))}
          </div>
        )}

        <div className="custom-scrollbar max-h-[420px] min-h-[220px] overflow-y-auto rounded-xl border border-gov-line bg-gov-paper px-4 py-4 dark:border-slate-700/60 dark:bg-slate-800/40">
          {entries.map((e, i) => (
            <div key={i} className={`mb-3.5 flex items-start gap-2.5 ${e.role === "user" ? "flex-row-reverse text-right" : ""}`}>
              <span className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full ${e.role === "user" ? "bg-gov-navy text-white" : "bg-accent-blue-soft text-accent-blue dark:bg-sky-900/40 dark:text-sky-300"}`}>
                {e.role === "user" ? <User size={14} /> : <Bot size={14} />}
              </span>
              <div className={`min-w-0 max-w-[85%] rounded-2xl px-3.5 py-2.5 text-[13px] leading-relaxed ${
                e.role === "user"
                  ? "bg-gov-navy text-white"
                  : "border border-gov-line bg-white text-gov-ink dark:border-slate-700 dark:bg-slate-900 dark:text-white"
              }`}>
                <p className="whitespace-pre-wrap">{e.content}</p>
                {e.citations && e.citations.length > 0 && (
                  <div className="mt-2 space-y-1.5 border-t border-dashed border-gov-line pt-2 text-left dark:border-slate-700">
                    {e.citations.map((c, j) => (
                      <p key={j} className="flex items-start gap-1.5 text-[11px] text-slate-500 dark:text-slate-400">
                        <Quote size={11} className="mt-0.5 flex-shrink-0" aria-hidden="true" />
                        <span><span className="font-semibold text-slate-600 dark:text-slate-300">{c.locator}:</span> “{c.quote}”</span>
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex items-center gap-2.5 text-[12px] text-slate-400">
              <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-accent-blue-soft text-accent-blue dark:bg-sky-900/40 dark:text-sky-300">
                <Bot size={14} />
              </span>
              Reading the document…
            </div>
          )}
          <div ref={endRef} />
        </div>

        {session.suggested_questions.length > 0 && entries.length <= 1 && (
          <div className="flex flex-wrap gap-2">
            {session.suggested_questions.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => send(q)}
                className="flex items-center gap-1.5 rounded-full border border-gov-line bg-white px-3 py-1.5 text-[11.5px] font-medium text-slate-600 transition-colors hover:border-gov-blue/40 hover:text-gov-navy dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
              >
                <Sparkles size={11} className="text-gov-saffron" aria-hidden="true" /> {q}
              </button>
            ))}
          </div>
        )}

        {sendError && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-2.5 text-[12.5px] font-medium text-accent-rose dark:border-red-800/50 dark:bg-red-900/20 dark:text-red-400">
            {sendError}
          </div>
        )}

        <div className="flex items-end gap-2 rounded-2xl border border-gov-line bg-white p-2 dark:border-slate-700 dark:bg-slate-900">
          <FileText size={16} className="mb-2 ml-1 flex-shrink-0 text-slate-300" aria-hidden="true" />
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); }
            }}
            placeholder="Ask a question about this document…"
            rows={1}
            disabled={sending}
            aria-label="Ask Learning Mode a question"
            className="max-h-28 flex-1 resize-none self-center overflow-y-auto bg-transparent py-1.5 text-[13px] leading-relaxed text-gov-ink placeholder-slate-400 focus:outline-none disabled:opacity-50 dark:text-white"
          />
          <button
            type="button"
            onClick={() => send(input)}
            disabled={!input.trim() || sending}
            aria-label="Send"
            className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-white transition-all ${
              input.trim() && !sending
                ? "bg-gradient-to-br from-gov-navy to-gov-blue hover:scale-105 active:scale-95"
                : "cursor-not-allowed bg-slate-300"
            }`}
          >
            <Send size={15} />
          </button>
        </div>
      </div>
    </SectionCard>
  );
};

export default LearningChat;
