/**
 * FILE: src/pages/AssessmentPage.tsx
 *
 * Assessment Studio at /assessment: upload a document → RAG generates an MCQ
 * assessment → grade it → evidence is written back to the competency baseline.
 *
 * Sections: new_quiz · history · settings, inside the shared AppShell.
 *
 * Document quizzes: the learner picks the question count (3–20), the objective
 * types (MCQ, True/False, multi-select, fill-in-the-blank, numeric) and the
 * language (English, Hindi, bilingual); questions render through
 * components/assessment/QuizQuestionInput.tsx.
 *
 * Grading goes through the authenticated `gradeQuiz` (JWT → learner id). Every
 * first attempt moves the learner's practice ability on the linked role
 * competency with a difficulty-aware step, and the result screen shows the
 * skill-gap impact, an answer review and next-step recommendations
 * (components/assessment/QuizSkillImpact.tsx). History and the "last
 * assessment" card read the learner's graded attempts (`fetchQuizAttempts`).
 */

import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight, Bot, BookOpen, CheckCircle, FilePlus, File, FileText, History,
  LayoutDashboard, Link as LinkIcon, Mic, Settings, Timer, Video, X, XCircle,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { fetchQuizAttempts, gradeQuiz } from "../services/api";
import type { DocQuizQuestion, QuizAnswer, QuizAttemptRecord, QuizGradeResult, QuizQuestionType } from "../services/api";

import AppShell, { type ShellNavGroup } from "../components/shell/AppShell";
import PageHeader from "../components/shell/PageHeader";
import { MediaAnalysisCard, MediaAnswerReview, YoutubeLinkInput } from "../components/assessment/MediaQuizExtras";
import { MEDIA_ACCEPT, generateMediaQuiz, generateYoutubeQuiz, isMediaFile, isYoutubeUrl } from "../services/mediaQuizApi";
import SectionCard from "../components/shell/SectionCard";
import { DifficultyChip, QuizQuestionReview, QuizRecommendations, SkillImpactCard } from "../components/assessment/QuizSkillImpact";
import QuizQuestionInput, { TYPE_LABEL, emptyAnswer, isAnswered, type QuizLang } from "../components/assessment/QuizQuestionInput";
import LearningChat from "../components/assessment/LearningChat";
import { startLearningSession, type LearningStartResponse } from "../services/learningApi";
import { consumePendingStudioUpload } from "../services/pendingStudioUpload";

type StudioTab = "new_quiz" | "history" | "settings" | "learning";
type Difficulty = "Easy" | "Medium" | "Hard";

/** Cosmetic only — which upload-format chip to highlight for a file Gyan hands off. */
const guessUploadFormat = (f: File): string => {
  if (isMediaFile(f)) {
    return /\.(mp3|wav|m4a|aac|ogg|oga|opus|flac|wma)$/i.test(f.name) ? "audio" : "video";
  }
  return /\.docx?$/i.test(f.name) ? "word" : "pdf";
};

const DIFFICULTIES: Difficulty[] = ["Easy", "Medium", "Hard"];
const QUESTION_TYPES: QuizQuestionType[] = ["mcq", "true_false", "multi_select", "fill_blank", "numeric"];
const QUESTION_COUNTS = [3, 5, 8, 10, 15, 20];
const LANGUAGES: { id: QuizLang; label: string }[] = [
  { id: "en", label: "English" },
  { id: "hi", label: "हिंदी" },
  { id: "bi", label: "Bilingual" },
];

/** FastAPI errors: `detail` is a string, or {message, …} for generation failures. */
const errorText = (body: any, fallback: string): string =>
  typeof body?.detail === "string" ? body.detail : body?.detail?.message ?? fallback;

const formatDate = (iso: string | null): string => {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
};

const AssessmentPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const userId = user?.username ?? "usr_720465595";

  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "quiz" | "grading" | "result">("idle");
  const [loadingText, setLoadingText] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const [quizData, setQuizData] = useState<any>(null);
  const [answers, setAnswers] = useState<QuizAnswer[]>([]);
  const [scoreInfo, setScoreInfo] = useState<QuizGradeResult | null>(null);

  // ── Learning Mode: NotebookLM-style study chat over the same upload ───────
  const [learningSession, setLearningSession] = useState<LearningStartResponse | null>(null);
  const [learningLoading, setLearningLoading] = useState(false);
  const [learningError, setLearningError] = useState("");

  const [activeTab, setActiveTab] = useState<StudioTab>("new_quiz");
  const [selectedFormat, setSelectedFormat] = useState("pdf");
  const [difficulty, setDifficulty] = useState<Difficulty>("Medium");
  const [searchTerm, setSearchTerm] = useState("");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);
  const [questionTypes, setQuestionTypes] = useState<QuizQuestionType[]>(QUESTION_TYPES);
  const [quizLanguage, setQuizLanguage] = useState<QuizLang>("en");
  const [displayLang, setDisplayLang] = useState<QuizLang>("en");

  const toggleType = (t: QuizQuestionType) =>
    setQuestionTypes((cur) => (cur.includes(t) ? (cur.length > 1 ? cur.filter((x) => x !== t) : cur) : [...cur, t]));

  // ── Real assessment history ────────────────────────────────────────────────
  const [history, setHistory] = useState<QuizAttemptRecord[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      setHistory(await fetchQuizAttempts());
    } catch (err) {
      console.error("[AssessmentPage] history", err);
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory, userId]);

  const filteredHistory = history.filter((item) =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase()),
  );
  const lastAttempt = history[0] ?? null;

  // ── Handlers (unchanged API contracts) ─────────────────────────────────────
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) { setFile(f); setErrorMsg(""); }
  };

  const triggerFileInput = () => inputRef.current?.click();

  const handleGenerate = async (fileOverride?: File) => {
    const activeFile = fileOverride ?? file;
    // Video / audio / YouTube go to the media pipeline (services/mediaQuizApi.ts).
    const useYoutube = selectedFormat === "text" && youtubeUrl.trim() !== "";
    if (useYoutube && !isYoutubeUrl(youtubeUrl)) { setErrorMsg("Please paste a valid YouTube link."); return; }
    if (!activeFile && !useYoutube) { setErrorMsg("Please upload a document to proceed."); return; }
    const isMedia = useYoutube || (activeFile !== null && isMediaFile(activeFile));
    setErrorMsg("");
    setStatus("loading");
    if (isMedia) {
      setLoadingText(useYoutube ? "Downloading video..." : "Probing speech, on-screen text and activity...");
      setTimeout(() => setLoadingText("Extracting evidence (speech, slides, screen)..."), 6000);
      setTimeout(() => setLoadingText("Reading slides and speech — long videos take 2–5 minutes..."), 30000);
      setTimeout(() => setLoadingText("Generating evidence-cited questions..."), 120000);
      try {
        const data = useYoutube
          ? await generateYoutubeQuiz(youtubeUrl, difficulty)
          : await generateMediaQuiz(activeFile as File, difficulty);
        setQuizData(data);
        setAnswers(data.questions.map((q: DocQuizQuestion) => emptyAnswer(q)));
        setDisplayLang("en");
        setStatus("quiz");
      } catch (err: any) {
        console.error(err);
        setErrorMsg(err.message || "An error occurred");
        setStatus("idle");
      }
      return;
    }
    setLoadingText("Extracting knowledge base...");

    setTimeout(() => setLoadingText("Generating Q&A pairs..."), 2000);
    setTimeout(() => setLoadingText("Finalizing assessment..."), 4000);

    try {
      const formData = new FormData();
      formData.append("file", activeFile as File);
      formData.append("user_id", userId);
      formData.append("difficulty", difficulty);
      formData.append("num_questions", String(numQuestions));
      formData.append("question_types", questionTypes.join(","));
      formData.append("language", quizLanguage);

      const res = await fetch("http://localhost:8000/api/v1/rag/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(errorText(error, "Failed to generate assessment"));
      }

      const data = await res.json();
      setQuizData(data);
      setAnswers(data.questions.map((q: DocQuizQuestion) => emptyAnswer(q)));
      setDisplayLang(data.language === "hi" ? "hi" : data.language === "bi" ? "bi" : "en");
      setStatus("quiz");
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "An error occurred");
      setStatus("idle");
    }
  };

  const startLearning = useCallback(async (f: File) => {
    setLearningLoading(true);
    setLearningError("");
    try {
      setLearningSession(await startLearningSession(f));
    } catch (err: any) {
      console.error(err);
      setLearningError(err.message || "Could not start a study session from this document.");
    } finally {
      setLearningLoading(false);
    }
  }, []);

  // Gyan hands off an already-uploaded document here (see services/pendingStudioUpload.ts) —
  // the learner asked for a quiz or to study it, so pick up right where they left the chat.
  useEffect(() => {
    const pending = consumePendingStudioUpload();
    if (!pending) return;
    if (pending.mode === "learn") {
      setActiveTab("learning");
      void startLearning(pending.file);
    } else {
      setFile(pending.file);
      setSelectedFormat(guessUploadFormat(pending.file));
      setErrorMsg("");
      void handleGenerate(pending.file);
    }
    // Runs once, on mount — consumePendingStudioUpload() clears the hand-off after reading it.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setAnswer = (qIndex: number, value: QuizAnswer) => {
    setAnswers((cur) => cur.map((a, i) => (i === qIndex ? value : a)));
  };

  const handleSubmitQuiz = async () => {
    if (quizData.questions.some((q: DocQuizQuestion, i: number) => !isAnswered(q, answers[i]))) {
      setErrorMsg("Please answer all questions before submitting.");
      return;
    }
    setErrorMsg("");
    setStatus("grading");

    try {
      // Authenticated: the backend takes the learner id from the JWT.
      const data = await gradeQuiz(quizData.quiz_id, answers);
      setScoreInfo(data);
      setStatus("result");
      loadHistory(); // every first attempt is recorded — refresh the history
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "An error occurred during grading");
      setStatus("quiz");
    }
  };

  const reset = () => {
    setFile(null);
    setQuizData(null);
    setAnswers([]);
    setScoreInfo(null);
    setStatus("idle");
    setErrorMsg("");
    setYoutubeUrl("");
    if (inputRef.current) inputRef.current.value = "";
  };

  const uploadOptions = [
    { id: "video", label: "Upload Video", icon: Video },
    { id: "audio", label: "Upload Audio", icon: Mic },
    { id: "pdf", label: "Upload PDF", icon: FileText },
    { id: "word", label: "Upload Word Doc (.docx)", icon: File },
    { id: "text", label: "Paste Text/URL", icon: LinkIcon },
  ];

  const navGroups: ShellNavGroup[] = [
    {
      items: [
        { id: "dashboard", label: "Back to Dashboard", icon: LayoutDashboard },
        { id: "new_quiz", label: "New Assessment", icon: FilePlus },
        { id: "learning", label: "Learning Mode", icon: BookOpen },
        { id: "history", label: "History", icon: History, badge: history.length || undefined },
        { id: "settings", label: "Settings", icon: Settings },
      ],
    },
  ];

  const META: Record<StudioTab, { title: string; subtitle: string }> = {
    new_quiz: { title: "Assessment Studio", subtitle: "Generate a competency-tagged assessment from any NSO training document." },
    learning: { title: "Learning Mode", subtitle: "Study any uploaded document in a grounded chat — NotebookLM-style, with source citations." },
    history:  { title: "Assessment History", subtitle: "Every RAG assessment on your verified achievement record." },
    settings: { title: "Studio Settings", subtitle: "Preferences for assessment generation." },
  };

  return (
    <AppShell
      groups={navGroups}
      activeId={activeTab}
      onNavigate={(id) => {
        if (id === "dashboard") navigate("/dashboard-redirect");
        else setActiveTab(id as StudioTab);
      }}
      userName={user?.username}
      userRole="Official"
      searchValue={searchTerm}
      onSearchChange={(v) => { setSearchTerm(v); if (v) setActiveTab("history"); }}
      searchPlaceholder="Search assessment history…"
    >
      <PageHeader
        title={META[activeTab].title}
        subtitle={META[activeTab].subtitle}
        breadcrumb={["Home", "Learner", "Assessment Studio"]}
      />

      {/* ── Idle: studio surfaces ──────────────────────────────────────────── */}
      {status === "idle" && (
        <div className="animate-fade-up space-y-5">
          {activeTab === "new_quiz" && (
            <>
              <SectionCard
                title="Generate New Assessment"
                subtitle="Supported: PDF, DOCX, PPTX, TXT, video (MP4, MKV, WEBM, MOV), audio (MP3, WAV, M4A) and YouTube links"
              >
                <input
                  ref={inputRef}
                  type="file"
                  className="hidden"
                  accept={`.pdf,.txt,.docx,.pptx,${MEDIA_ACCEPT}`}
                  aria-label="Choose a document to generate an assessment from"
                  onChange={handleFileChange}
                />

                <div className="mb-5 grid grid-cols-2 gap-3.5 md:grid-cols-5">
                  {uploadOptions.map(({ id, label, icon: Icon }) => {
                    const isSelected = selectedFormat === id;
                    return (
                      <button
                        key={id}
                        type="button"
                        aria-pressed={isSelected}
                        onClick={() => { setSelectedFormat(id); if (id !== "text") triggerFileInput(); }}
                        className={`flex flex-col items-center justify-center gap-2 rounded-xl border p-5 text-center transition-all duration-300 hover:-translate-y-0.5 ${
                          isSelected
                            ? "border-gov-blue bg-accent-blue-soft shadow-gov dark:border-sky-500 dark:bg-sky-500/10"
                            : "border-gov-line hover:border-gov-blue/40 hover:shadow-gov dark:border-slate-700"
                        }`}
                      >
                        <Icon className={`h-7 w-7 ${isSelected ? "text-accent-blue dark:text-sky-300" : "text-slate-400"}`} aria-hidden="true" />
                        <span className={`text-[12.5px] font-semibold ${isSelected ? "text-gov-navy dark:text-sky-300" : "text-slate-600 dark:text-slate-300"}`}>
                          {label}
                        </span>
                      </button>
                    );
                  })}
                </div>

                {selectedFormat === "text" && <YoutubeLinkInput value={youtubeUrl} onChange={setYoutubeUrl} />}

                {file && (
                  <div className="mb-5 flex items-center justify-between rounded-xl border border-accent-blue/25 bg-accent-blue-soft px-4 py-3 text-accent-blue dark:border-sky-800/50 dark:bg-sky-900/20 dark:text-sky-300">
                    <span className="flex min-w-0 items-center gap-2">
                      <FileText className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                      <span className="truncate font-medium">{file.name}</span>
                    </span>
                    <button
                      type="button"
                      onClick={() => setFile(null)}
                      className="rounded-md p-1 hover:bg-white/60 dark:hover:bg-sky-800/50"
                      aria-label={`Remove ${file.name}`}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                )}

                {errorMsg && (
                  <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-accent-rose dark:border-red-800/50 dark:bg-red-900/20 dark:text-red-400">
                    {errorMsg}
                  </div>
                )}

                {/* Document quizzes only (media quizzes keep their own pipeline) */}
                <div className="mb-5 grid gap-4 rounded-xl border border-gov-line bg-gov-paper p-4 lg:grid-cols-[auto_1fr_auto] dark:border-slate-700/60 dark:bg-slate-800/40">
                  <label className="flex items-center gap-2.5 text-[12.5px] font-medium text-slate-500 dark:text-slate-400">
                    Questions
                    <select
                      value={numQuestions}
                      onChange={(e) => setNumQuestions(Number(e.target.value))}
                      className="rounded-lg border border-gov-line bg-white px-2 py-1.5 text-[13px] font-semibold text-gov-ink dark:border-slate-600 dark:bg-slate-900 dark:text-white"
                    >
                      {QUESTION_COUNTS.map((n) => <option key={n} value={n}>{n}</option>)}
                    </select>
                  </label>
                  <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label="Question types">
                    <span className="mr-1 text-[12.5px] font-medium text-slate-500 dark:text-slate-400">Types</span>
                    {QUESTION_TYPES.map((t) => (
                      <button key={t} type="button" aria-pressed={questionTypes.includes(t)} onClick={() => toggleType(t)} className="chip-filter">
                        {TYPE_LABEL[t]}
                      </button>
                    ))}
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label="Quiz language">
                    <span className="mr-1 text-[12.5px] font-medium text-slate-500 dark:text-slate-400">Language</span>
                    {LANGUAGES.map((l) => (
                      <button key={l.id} type="button" aria-pressed={quizLanguage === l.id} onClick={() => setQuizLanguage(l.id)} className="chip-filter">
                        {l.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
                  <button type="button" onClick={() => handleGenerate()} className="gov-btn-primary !px-6 !py-3">
                    <Bot size={16} /> Generate Assessment
                  </button>

                  {/* Difficulty is sent to /api/v1/rag/upload */}
                  <div className="flex items-center gap-2.5">
                    <span className="text-[12.5px] font-medium text-slate-500 dark:text-slate-400">Difficulty</span>
                    <div role="group" aria-label="Assessment difficulty" className="flex gap-1.5">
                      {DIFFICULTIES.map((d) => (
                        <button
                          key={d}
                          type="button"
                          aria-pressed={difficulty === d}
                          onClick={() => setDifficulty(d)}
                          className="chip-filter"
                        >
                          {d}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </SectionCard>

              {/* Last assessment — real achievement, or an honest empty state */}
              <SectionCard title="Your Last Assessment" subtitle="From your verified achievement record">
                {historyLoading ? (
                  <div className="skeleton h-28" />
                ) : lastAttempt ? (
                  <div className="flex flex-col items-center gap-7 md:flex-row">
                    <div className="relative h-32 w-32 flex-shrink-0">
                      <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100" aria-hidden="true">
                        <circle cx="50" cy="50" r="40" stroke="currentColor" strokeWidth="12" fill="none" className="text-slate-100 dark:text-slate-700" />
                        <circle
                          cx="50" cy="50" r="40"
                          stroke={lastAttempt.passed ? "#10b981" : "#e11d48"}
                          strokeWidth="12" fill="none" strokeLinecap="round"
                          strokeDasharray="251.2"
                          strokeDashoffset={251.2 * (1 - Math.min(100, lastAttempt.score) / 100)}
                        />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-[26px] font-bold text-gov-ink dark:text-white">{Math.round(lastAttempt.score)}%</span>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                          {lastAttempt.passed ? "Passed" : "Not passed"}
                        </span>
                      </div>
                    </div>

                    <dl className="flex-1 space-y-2.5">
                      <div className="flex gap-2">
                        <dt className="w-20 flex-shrink-0 text-[13px] font-semibold text-gov-ink dark:text-white">Source</dt>
                        <dd className="text-[13px] text-slate-600 dark:text-slate-400">{lastAttempt.title}</dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="w-20 flex-shrink-0 text-[13px] font-semibold text-gov-ink dark:text-white">Date</dt>
                        <dd className="text-[13px] text-slate-600 dark:text-slate-400">{formatDate(lastAttempt.date)}</dd>
                      </div>
                      {lastAttempt.competencyName && (
                        <div className="flex gap-2">
                          <dt className="w-20 flex-shrink-0 text-[13px] font-semibold text-gov-ink dark:text-white">Skill</dt>
                          <dd className="flex items-center gap-2 text-[13px] text-slate-600 dark:text-slate-400">
                            {lastAttempt.competencyName}
                            {lastAttempt.difficulty && <DifficultyChip difficulty={lastAttempt.difficulty} />}
                          </dd>
                        </div>
                      )}
                      <div className="flex gap-2">
                        <dt className="w-20 flex-shrink-0 text-[13px] font-semibold text-gov-ink dark:text-white">Outcome</dt>
                        <dd className="flex items-center gap-1.5 text-[13px] text-slate-600 dark:text-slate-400">
                          {lastAttempt.passed
                            ? <CheckCircle className="h-4 w-4 text-accent-green" aria-hidden="true" />
                            : <XCircle className="h-4 w-4 text-accent-rose" aria-hidden="true" />}
                          {lastAttempt.abilityBefore != null && lastAttempt.abilityAfter != null
                            ? `Practice ability ${lastAttempt.abilityBefore.toFixed(2)} → ${lastAttempt.abilityAfter.toFixed(2)}`
                            : lastAttempt.passed ? "Passed" : "70% needed to pass"}
                        </dd>
                      </div>
                    </dl>
                  </div>
                ) : (
                  <p className="py-8 text-center text-[13px] text-slate-400">
                    No assessments yet — upload a document above to generate your first one.
                  </p>
                )}
              </SectionCard>
            </>
          )}

          {activeTab === "learning" && (
            <LearningChat
              session={learningSession}
              loading={learningLoading}
              error={learningError}
              onUpload={(f) => { void startLearning(f); }}
              onReset={() => { setLearningSession(null); setLearningError(""); }}
            />
          )}

          {(activeTab === "new_quiz" || activeTab === "history") && (
            <SectionCard
              title="Assessment History"
              subtitle={`${filteredHistory.length} assessment${filteredHistory.length === 1 ? "" : "s"} on record`}
              padded={false}
            >
              <div className="overflow-x-auto">
                <table className="gov-table min-w-[760px]">
                  <thead>
                    <tr>
                      <th scope="col">Date</th>
                      <th scope="col">Assessment Source</th>
                      <th scope="col">Skill</th>
                      <th scope="col">Difficulty</th>
                      <th scope="col">Score</th>
                      <th scope="col">Ability</th>
                      <th scope="col">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historyLoading ? (
                      Array.from({ length: 3 }, (_, i) => (
                        <tr key={i} className="animate-pulse">
                          {Array.from({ length: 7 }, (_, j) => (
                            <td key={j} className="px-4 py-4"><div className="h-4 w-full rounded bg-slate-100 dark:bg-slate-700" /></td>
                          ))}
                        </tr>
                      ))
                    ) : filteredHistory.length > 0 ? (
                      filteredHistory.map((row) => (
                        <tr key={row.id}>
                          <td className="whitespace-nowrap text-slate-500 dark:text-slate-400">{formatDate(row.date)}</td>
                          <td className="font-medium text-gov-ink dark:text-white">{row.title}</td>
                          <td className="text-slate-600 dark:text-slate-300">{row.competencyName ?? "—"}</td>
                          <td>{row.difficulty ? <DifficultyChip difficulty={row.difficulty} /> : "—"}</td>
                          <td className="font-semibold tabular-nums">
                            {Math.round(row.score)}%
                            {row.weightedScore != null && (
                              <span className="ml-1 text-[11.5px] font-normal text-slate-400">({Math.round(row.weightedScore)}% wtd)</span>
                            )}
                          </td>
                          <td className="tabular-nums">
                            {row.abilityBefore != null && row.abilityAfter != null ? (
                              <span className={row.abilityAfter >= row.abilityBefore ? "text-accent-green" : "text-accent-rose"}>
                                {row.abilityAfter >= row.abilityBefore ? "+" : ""}{(row.abilityAfter - row.abilityBefore).toFixed(2)}
                              </span>
                            ) : "—"}
                          </td>
                          <td>
                            <span className={`chip ${
                              row.passed
                                ? "bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300"
                                : "bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300"
                            }`}>
                              {row.passed ? "Passed" : "Not passed"}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={7} className="py-12 text-center text-slate-400">
                          {searchTerm
                            ? `No assessments match “${searchTerm}”.`
                            : "No assessments on record yet."}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </SectionCard>
          )}

          {activeTab === "settings" && (
            <SectionCard title="Generation Preferences" subtitle="Applied to the next assessment you generate">
              <div className="space-y-5">
                <fieldset>
                  <legend className="mb-2.5 text-[13px] font-semibold text-gov-ink dark:text-white">Default difficulty</legend>
                  <div className="flex flex-wrap gap-2">
                    {DIFFICULTIES.map((d) => (
                      <button key={d} type="button" aria-pressed={difficulty === d} onClick={() => setDifficulty(d)} className="chip-filter">
                        {d}
                      </button>
                    ))}
                  </div>
                </fieldset>
                <fieldset>
                  <legend className="mb-2.5 text-[13px] font-semibold text-gov-ink dark:text-white">Default question types (documents)</legend>
                  <div className="flex flex-wrap gap-2">
                    {QUESTION_TYPES.map((t) => (
                      <button key={t} type="button" aria-pressed={questionTypes.includes(t)} onClick={() => toggleType(t)} className="chip-filter">
                        {TYPE_LABEL[t]}
                      </button>
                    ))}
                  </div>
                </fieldset>
                <p className="rounded-xl border border-gov-line bg-gov-paper px-4 py-3 text-[12px] leading-relaxed text-slate-500 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-400">
                  Every question cites the passage it was written from, and a question's difficulty is
                  re-estimated from how learners actually answer it once enough responses exist.
                  Every first attempt updates your practice ability on the role competency the quiz matches:
                  missing an easy question costs more than missing a hard one, and solving a hard question
                  earns more. That ability feeds your skill-gap score. 70% or higher also passes the quiz,
                  earns Karma Points and syncs to your iGOT Karmayogi record.
                </p>
              </div>
            </SectionCard>
          )}
        </div>
      )}

      {/* ── Loading / grading ──────────────────────────────────────────────── */}
      {(status === "loading" || status === "grading") && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm dark:bg-slate-900/85" role="status" aria-live="polite">
          <div className="flex flex-col items-center gap-6">
            <div className="relative h-16 w-16">
              <div className="absolute inset-0 rounded-full border-4 border-accent-blue-soft dark:border-sky-900/50" />
              <div className="absolute inset-0 animate-spin rounded-full border-4 border-gov-navy border-t-transparent dark:border-sky-400 dark:border-t-transparent" />
              <Bot className="absolute inset-0 m-auto h-6 w-6 text-gov-navy dark:text-sky-400" aria-hidden="true" />
            </div>
            <div className="text-center">
              <h3 className="mb-1 text-lg font-semibold text-gov-ink dark:text-white">AI agent working</h3>
              <p className="animate-pulse text-sm font-medium text-gov-blue dark:text-sky-400">{loadingText}</p>
            </div>
          </div>
        </div>
      )}

      {/* ── Quiz ───────────────────────────────────────────────────────────── */}
      {status === "quiz" && quizData && (
        <div className="mx-auto max-w-4xl animate-fade-up pb-24">
          <div className="mb-7 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="mb-1 text-2xl font-bold text-gov-ink dark:text-white">Assessment ready</h2>
              <p className="text-[13px] font-medium text-slate-500 dark:text-slate-400">
                {quizData.questions.length} questions · {quizData.difficulty ?? difficulty} difficulty
              </p>
            </div>
            {quizData.language && quizData.language !== "en" && (
              <div className="flex items-center gap-1.5" role="group" aria-label="Display language">
                {LANGUAGES.map((l) => (
                  <button key={l.id} type="button" aria-pressed={displayLang === l.id} onClick={() => setDisplayLang(l.id)} className="chip-filter">
                    {l.label}
                  </button>
                ))}
              </div>
            )}
            <span className="flex items-center gap-2 rounded-lg bg-accent-blue-soft px-4 py-2 font-semibold text-accent-blue dark:bg-sky-900/30 dark:text-sky-300">
              <Timer size={18} aria-hidden="true" /> 20:00
            </span>
          </div>

          {quizData.media && <MediaAnalysisCard report={quizData.media} skillName={quizData.skill_name} />}

          {errorMsg && (
            <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-accent-rose dark:border-red-800/50 dark:bg-red-900/20 dark:text-red-400">
              {errorMsg}
            </div>
          )}

          <div className="space-y-5">
            {quizData.questions.map((q: DocQuizQuestion, i: number) => (
              <QuizQuestionInput
                key={i}
                q={q}
                index={i}
                answer={answers[i]}
                onChange={(a) => setAnswer(i, a)}
                lang={displayLang}
              />
            ))}
          </div>

          <div className="fixed bottom-0 left-0 right-0 z-10 flex justify-center border-t border-gov-line bg-white/85 p-4 backdrop-blur-md md:p-5 dark:border-slate-800 dark:bg-slate-900/85">
            <button onClick={handleSubmitQuiz} className="gov-btn-primary !px-12 !py-3.5 !text-[14px]">
              Submit Assessment <ArrowRight size={18} />
            </button>
          </div>
        </div>
      )}

      {/* ── Result ─────────────────────────────────────────────────────────── */}
      {status === "result" && scoreInfo && (
        <div className="mx-auto max-w-2xl animate-fade-up">
          <div className="panel p-8 text-center shadow-gov-lg md:p-12">
            <span className={`mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-full ${scoreInfo.passed ? "bg-accent-green-soft dark:bg-emerald-900/30" : "bg-accent-rose-soft dark:bg-red-900/30"}`}>
              {scoreInfo.passed
                ? <CheckCircle className="h-12 w-12 text-accent-green" aria-hidden="true" />
                : <XCircle className="h-12 w-12 text-accent-rose" aria-hidden="true" />}
            </span>

            <h2 className="mb-2 text-3xl font-bold text-gov-ink dark:text-white">
              {scoreInfo.passed ? "Assessment passed" : "Assessment complete"}
            </h2>
            <p className="mb-2 font-medium text-slate-500 dark:text-slate-400">
              {scoreInfo.passed
                ? "Your skill-gap evidence has been updated and synced to iGOT."
                : "You need 70% or more to pass — your attempt still counts toward your skill level."}
            </p>
            {scoreInfo.message && (
              <p className="mb-8 px-4 text-xs leading-relaxed text-slate-400 dark:text-slate-500">{scoreInfo.message}</p>
            )}

            <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-gov-line bg-gov-paper p-6 dark:border-slate-700 dark:bg-slate-900/50">
                <p className="mb-1 text-[11.5px] font-semibold uppercase tracking-wider text-slate-400">Score</p>
                <p className={`text-4xl font-bold ${scoreInfo.passed ? "text-accent-green" : "text-accent-rose"}`}>
                  {scoreInfo.score}%
                </p>
              </div>
              <div className="rounded-2xl border border-gov-line bg-gov-paper p-6 dark:border-slate-700 dark:bg-slate-900/50">
                <p className="mb-1 text-[11.5px] font-semibold uppercase tracking-wider text-slate-400">Correct</p>
                <p className="text-4xl font-bold text-gov-ink dark:text-white">
                  {scoreInfo.correct_count}
                  <span className="text-xl text-slate-400">/{scoreInfo.total_questions}</span>
                </p>
              </div>
              {scoreInfo.weighted_score != null && (
                <div className="col-span-2 rounded-2xl border border-gov-line bg-gov-paper p-6 md:col-span-1 dark:border-slate-700 dark:bg-slate-900/50">
                  <p className="mb-1 text-[11.5px] font-semibold uppercase tracking-wider text-slate-400">Difficulty-weighted</p>
                  <p className="text-4xl font-bold text-gov-ink dark:text-white">{Math.round(scoreInfo.weighted_score)}%</p>
                </div>
              )}
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <button onClick={reset} className="gov-btn-outline flex-1 !py-3.5">
                Generate another
              </button>
              <button onClick={() => navigate("/dashboard-redirect")} className="gov-btn-primary flex-1 !py-3.5">
                Return to Dashboard <ArrowRight size={16} />
              </button>
            </div>
          </div>
          <SkillImpactCard result={scoreInfo} />
          <QuizRecommendations
            result={scoreInfo}
            onRetry={(d) => { setDifficulty(d); reset(); setActiveTab("new_quiz"); }}
          />
          {quizData?.media ? (
            <MediaAnswerReview questions={quizData.questions} evidence={quizData.evidence ?? []} answers={answers as number[]} />
          ) : scoreInfo.questionReview && scoreInfo.questionReview.length > 0 ? (
            <QuizQuestionReview rows={scoreInfo.questionReview} />
          ) : null}
        </div>
      )}
    </AppShell>
  );
};

export default AssessmentPage;
