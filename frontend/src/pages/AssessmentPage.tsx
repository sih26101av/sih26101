/**
 * FILE: src/pages/AssessmentPage.tsx
 *
 * Assessment Studio at /assessment: upload a document → RAG generates an MCQ
 * assessment → grade it → evidence is written back to the competency baseline.
 *
 * Sections: new_quiz · history · settings, inside the shared AppShell.
 *
 * History and the "last assessment" card read the learner's real achievement
 * record (`fetchAchievements`), replacing the hardcoded sample rows the page
 * previously displayed.
 */

import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowRight, Bot, CheckCircle, FilePlus, File, FileText, History,
  LayoutDashboard, Link as LinkIcon, Mic, Settings, Timer, Video, X, XCircle,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { fetchAchievements } from "../services/api";
import type { Achievement } from "../types/domain";

import AppShell, { type ShellNavGroup } from "../components/shell/AppShell";
import PageHeader from "../components/shell/PageHeader";
import { MediaAnalysisCard, MediaAnswerReview, YoutubeLinkInput } from "../components/assessment/MediaQuizExtras";
import { MEDIA_ACCEPT, generateMediaQuiz, generateYoutubeQuiz, isMediaFile, isYoutubeUrl } from "../services/mediaQuizApi";
import SectionCard from "../components/shell/SectionCard";

type StudioTab = "new_quiz" | "history" | "settings";
type Difficulty = "Easy" | "Medium" | "Hard";

const DIFFICULTIES: Difficulty[] = ["Easy", "Medium", "Hard"];

const formatDate = (iso: string): string => {
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
  const [answers, setAnswers] = useState<number[]>([]);
  const [scoreInfo, setScoreInfo] = useState<any>(null);

  const [activeTab, setActiveTab] = useState<StudioTab>("new_quiz");
  const [selectedFormat, setSelectedFormat] = useState("pdf");
  const [difficulty, setDifficulty] = useState<Difficulty>("Medium");
  const [searchTerm, setSearchTerm] = useState("");
  const [youtubeUrl, setYoutubeUrl] = useState("");

  // ── Real assessment history ────────────────────────────────────────────────
  const [history, setHistory] = useState<Achievement[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const all = await fetchAchievements(userId);
      setHistory(
        all
          .filter((a) => a.category === "RAG Quiz")
          .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()),
      );
    } catch (err) {
      console.error("[AssessmentPage] history", err);
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }, [userId]);

  useEffect(() => { loadHistory(); }, [loadHistory]);

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

  const handleGenerate = async () => {
    // Video / audio / YouTube go to the media pipeline (services/mediaQuizApi.ts).
    const useYoutube = selectedFormat === "text" && youtubeUrl.trim() !== "";
    if (useYoutube && !isYoutubeUrl(youtubeUrl)) { setErrorMsg("Please paste a valid YouTube link."); return; }
    if (!file && !useYoutube) { setErrorMsg("Please upload a document to proceed."); return; }
    const isMedia = useYoutube || (file !== null && isMediaFile(file));
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
          : await generateMediaQuiz(file as File, difficulty);
        setQuizData(data);
        setAnswers(new Array(data.questions.length).fill(-1));
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
      formData.append("file", file as File);
      formData.append("user_id", userId);
      formData.append("difficulty", difficulty);

      const res = await fetch("http://localhost:8000/api/v1/rag/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Failed to generate assessment");
      }

      const data = await res.json();
      setQuizData(data);
      setAnswers(new Array(data.questions.length).fill(-1));
      setStatus("quiz");
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || "An error occurred");
      setStatus("idle");
    }
  };

  const handleOptionSelect = (qIndex: number, optionIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[qIndex] = optionIndex;
    setAnswers(newAnswers);
  };

  const handleSubmitQuiz = async () => {
    if (answers.includes(-1)) {
      setErrorMsg("Please answer all questions before submitting.");
      return;
    }
    setErrorMsg("");
    setStatus("grading");

    try {
      const res = await fetch("http://localhost:8000/api/v1/rag/grade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, quiz_id: quizData.quiz_id, answers }),
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Failed to grade assessment");
      }

      const data = await res.json();
      setScoreInfo(data);
      setStatus("result");
      loadHistory(); // a pass writes a new achievement — refresh the record
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
    { id: "word", label: "Upload Word Doc", icon: File },
    { id: "text", label: "Paste Text/URL", icon: LinkIcon },
  ];

  const navGroups: ShellNavGroup[] = [
    {
      items: [
        { id: "dashboard", label: "Back to Dashboard", icon: LayoutDashboard },
        { id: "new_quiz", label: "New Assessment", icon: FilePlus },
        { id: "history", label: "History", icon: History, badge: history.length || undefined },
        { id: "settings", label: "Settings", icon: Settings },
      ],
    },
  ];

  const META: Record<StudioTab, { title: string; subtitle: string }> = {
    new_quiz: { title: "Assessment Studio", subtitle: "Generate a competency-tagged assessment from any NSO training document." },
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

                <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
                  <button type="button" onClick={handleGenerate} className="gov-btn-primary !px-6 !py-3">
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
                          stroke={lastAttempt.score >= 70 ? "#10b981" : "#e11d48"}
                          strokeWidth="12" fill="none" strokeLinecap="round"
                          strokeDasharray="251.2"
                          strokeDashoffset={251.2 * (1 - Math.min(100, lastAttempt.score) / 100)}
                        />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-[26px] font-bold text-gov-ink dark:text-white">{lastAttempt.score}%</span>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                          {lastAttempt.score >= 70 ? "Passed" : "Not passed"}
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
                      <div className="flex gap-2">
                        <dt className="w-20 flex-shrink-0 text-[13px] font-semibold text-gov-ink dark:text-white">Outcome</dt>
                        <dd className="flex items-center gap-1.5 text-[13px] text-slate-600 dark:text-slate-400">
                          {lastAttempt.score >= 70 ? (
                            <><CheckCircle className="h-4 w-4 text-accent-green" aria-hidden="true" /> Evidence logged to your competency baseline</>
                          ) : (
                            <><XCircle className="h-4 w-4 text-accent-rose" aria-hidden="true" /> 70% required to log verified evidence</>
                          )}
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

          {(activeTab === "new_quiz" || activeTab === "history") && (
            <SectionCard
              title="Assessment History"
              subtitle={`${filteredHistory.length} assessment${filteredHistory.length === 1 ? "" : "s"} on record`}
              padded={false}
            >
              <div className="overflow-x-auto">
                <table className="gov-table min-w-[620px]">
                  <thead>
                    <tr>
                      <th scope="col">Date</th>
                      <th scope="col">Assessment Source</th>
                      <th scope="col">Score</th>
                      <th scope="col">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historyLoading ? (
                      Array.from({ length: 3 }, (_, i) => (
                        <tr key={i} className="animate-pulse">
                          {Array.from({ length: 4 }, (_, j) => (
                            <td key={j} className="px-4 py-4"><div className="h-4 w-full rounded bg-slate-100 dark:bg-slate-700" /></td>
                          ))}
                        </tr>
                      ))
                    ) : filteredHistory.length > 0 ? (
                      filteredHistory.map((row) => (
                        <tr key={row.id}>
                          <td className="whitespace-nowrap text-slate-500 dark:text-slate-400">{formatDate(row.date)}</td>
                          <td className="font-medium text-gov-ink dark:text-white">{row.title}</td>
                          <td className="font-semibold tabular-nums">{row.score}%</td>
                          <td>
                            <span className={`chip ${
                              row.score >= 70
                                ? "bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300"
                                : "bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300"
                            }`}>
                              {row.score >= 70 ? "Passed" : "Not passed"}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4} className="py-12 text-center text-slate-400">
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
                <p className="rounded-xl border border-gov-line bg-gov-paper px-4 py-3 text-[12px] leading-relaxed text-slate-500 dark:border-slate-700/60 dark:bg-slate-800/50 dark:text-slate-400">
                  A score of 70% or higher writes verified evidence against the competencies detected in
                  your document and syncs the result to your iGOT Karmayogi record.
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
                {quizData.questions.length} questions · {difficulty} difficulty
              </p>
            </div>
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
            {quizData.questions.map((q: any, i: number) => (
              <fieldset key={i} className="panel p-6 md:p-7">
                <legend className="mb-5 text-[16.5px] font-semibold text-gov-ink dark:text-slate-100">
                  <span className="mr-3 text-slate-400">{i + 1}.</span>
                  {q.question}
                </legend>
                <div className="space-y-3">
                  {q.options.map((opt: string, optIdx: number) => {
                    const isSelected = answers[i] === optIdx;
                    return (
                      <label
                        key={optIdx}
                        className={`flex cursor-pointer items-center gap-4 rounded-xl border-2 p-4 transition-all ${
                          isSelected
                            ? "border-gov-navy bg-accent-blue-soft dark:border-sky-500 dark:bg-sky-900/20"
                            : "border-gov-line hover:border-gov-blue/40 dark:border-slate-700 dark:hover:border-slate-600"
                        }`}
                      >
                        <input
                          type="radio"
                          name={`q-${i}`}
                          className="sr-only"
                          checked={isSelected}
                          onChange={() => handleOptionSelect(i, optIdx)}
                        />
                        <span className={`flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border-2 ${isSelected ? "border-gov-navy dark:border-sky-400" : "border-slate-300 dark:border-slate-600"}`}>
                          {isSelected && <span className="h-2.5 w-2.5 rounded-full bg-gov-navy dark:bg-sky-400" />}
                        </span>
                        <span className={`font-medium ${isSelected ? "text-gov-navy dark:text-sky-100" : "text-slate-700 dark:text-slate-300"}`}>
                          {opt}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </fieldset>
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
                ? "Your competency profile has been updated on iGOT."
                : "You need 70% or more to pass. Review and try again."}
            </p>
            {scoreInfo.message && (
              <p className="mb-8 px-4 text-xs leading-relaxed text-slate-400 dark:text-slate-500">{scoreInfo.message}</p>
            )}

            <div className="mb-8 grid grid-cols-2 gap-4">
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
          {quizData?.media && (
            <MediaAnswerReview questions={quizData.questions} evidence={quizData.evidence ?? []} answers={answers} />
          )}
        </div>
      )}
    </AppShell>
  );
};

export default AssessmentPage;
