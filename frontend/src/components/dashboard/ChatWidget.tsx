/**
 * FILE: src/components/dashboard/ChatWidget.tsx
 *
 * Gyan (ज्ञान) — Dashboard Chat Widget
 * Uses useChatEngine hook for shared logic.
 * Adds: ✅ Voice input (Web Speech API) | ✅ Navigate action confirmation
 *
 * All copy and the language list come from `i18n/chatLanguages`, shared with
 * HomeChatWidget so the two widgets stay identical in behaviour.
 *
 * Archit Shukla | SIH 2026
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  X, Send, Bot, ChevronDown, ChevronRight, Mic, MicOff, Navigation,
  Target, GraduationCap, TrendingUp, ClipboardCheck, Lightbulb, AudioLines, Landmark, Paperclip,
} from 'lucide-react';
import type { SkillGapEntry, CourseRecommendation } from '../../types/domain';
import type { ChatLanguage, NavigateAction } from '../../services/chatApi';
import type { ChatMessage } from '../../services/chatApi';
import { useChatEngine } from '../../hooks/useChatEngine';
import { useTheme } from '../../hooks/useTheme';
import { GyanBot, GyanHero } from '../chat/GyanAvatar';
import LanguageMenu from '../chat/LanguageMenu';
import { AshokaChakra } from '../gov/GovUI';
import { chatCopy, languageOption, type ChatCopy } from '../../i18n/chatLanguages';
import { setPendingStudioUpload, type StudioMode } from '../../services/pendingStudioUpload';

// A document is already attached in the chat — read the reply as a mode pick
// instead of sending it to the (offline, document-blind) chat backend.
const QUIZ_INTENT_RE = /\b(quiz|test|assess|question|mcq|exam)\b/i;
const LEARN_INTENT_RE = /\b(learn|study|understand|explain|summar|notes?|teach)\b/i;
const STUDIO_ACCEPT = '.pdf,.docx,.pptx,.txt';

// ─── Capability cards — each sends a real prompt to the engine ───────────────
// `label` / `ask` are keys into the per-language copy table, so a new language
// needs no change here.
const CAPABILITIES = [
  { id: 'gaps',     icon: Target,         label: 'gaps',     ask: 'gaps',        tile: 'bg-accent-rose-soft',   ink: 'text-accent-rose' },
  { id: 'courses',  icon: GraduationCap,  label: 'courses',  ask: 'firstCourse', tile: 'bg-accent-green-soft',  ink: 'text-accent-green' },
  { id: 'progress', icon: TrendingUp,     label: 'progress', ask: 'progress',    tile: 'bg-accent-blue-soft',   ink: 'text-accent-blue' },
  { id: 'assess',   icon: ClipboardCheck, label: 'assess',   ask: 'assessment',  tile: 'bg-accent-purple-soft', ink: 'text-accent-purple' },
] as const;

const SUGGESTION_KEYS = ['gaps', 'firstCourse', 'gdp', 'usePlatform'] as const;

// ─── Props ────────────────────────────────────────────────────────────────────
interface ChatWidgetProps {
  officialId: string;
  fullName?: string;
  govId?: string;
  jobRole?: string;
  department?: string;
  skillGaps: SkillGapEntry[];
  recommendations: CourseRecommendation[];
  onNavigate?: (action: NavigateAction) => void;
}

// ─── Markdown renderer (bold only) ───────────────────────────────────────────
function renderMarkdown(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part.split('\n').map((line, j, arr) => (
      <React.Fragment key={`${i}-${j}`}>
        {line}
        {j < arr.length - 1 && <br />}
      </React.Fragment>
    ));
  });
}

// ─── Typing indicator ─────────────────────────────────────────────────────────
const TypingIndicator: React.FC = () => (
  <div className="mb-3 flex animate-bubble-in items-end gap-2">
    <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-slate-200/80">
      <GyanBot size={22} />
    </span>
    <div className="rounded-2xl rounded-bl-md border border-slate-200/70 bg-white px-4 py-3 shadow-sm">
      <div className="flex h-4 items-center gap-1">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className="h-1.5 w-1.5 animate-bounce rounded-full bg-gov-sky/70"
            style={{ animationDelay: `${i * 0.18}s`, animationDuration: '0.9s' }}
          />
        ))}
      </div>
    </div>
  </div>
);

// ─── Message bubble ───────────────────────────────────────────────────────────
const MessageBubble: React.FC<{ msg: ChatMessage }> = ({ msg }) => {
  const isUser = msg.role === 'user';
  const time = msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  if (isUser) {
    return (
      <div className="mb-3 flex animate-bubble-in justify-end">
        <div className="max-w-[78%]">
          <div className="rounded-2xl rounded-br-md bg-gradient-to-br from-gov-ink via-gov-navy to-gov-blue px-4 py-2.5 text-[13px] leading-relaxed text-white shadow-[0_6px_18px_-8px_rgba(11,42,85,0.75)]">
            {msg.content}
          </div>
          <p className="mr-1.5 mt-1 text-right text-[10px] tabular-nums text-slate-400">{time}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-3 flex animate-bubble-in items-end gap-2">
      <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-slate-200/80">
        <GyanBot size={22} />
      </span>
      <div className="max-w-[82%]">
        <div className="rounded-2xl rounded-bl-md border border-slate-200/70 bg-white px-4 py-2.5 text-[13px] leading-relaxed text-slate-800 shadow-[0_4px_16px_-10px_rgba(10,26,51,0.5)]">
          {renderMarkdown(msg.content)}
        </div>
        <p className="ml-1.5 mt-1 text-[10px] tabular-nums text-slate-400">{time}</p>
      </div>
    </div>
  );
};

// ─── Nav Confirmation Banner ──────────────────────────────────────────────────
const NavConfirmBanner: React.FC<{
  action: NavigateAction;
  copy: ChatCopy;
  onConfirm: () => void;
  onCancel: () => void;
}> = ({ action, copy, onConfirm, onCancel }) => (
  <div className="animate-bubble-in mx-3.5 mb-3 flex flex-col gap-2 rounded-2xl border border-gov-sky/25 bg-gradient-to-br from-[#eef4ff] to-white p-3 shadow-sm">
    <p className="flex items-center gap-1.5 text-[12px] font-semibold text-gov-navy">
      <Navigation size={12} className="text-gov-blue" />
      {copy.navConfirmDash(action.label)}
    </p>
    <div className="flex gap-2">
      <button
        onClick={onConfirm}
        className="flex-1 rounded-xl bg-gradient-to-br from-gov-navy to-gov-blue py-1.5 text-[11px] font-bold text-white shadow-sm transition-all hover:shadow-md active:scale-[0.98]"
      >
        {copy.yes}
      </button>
      <button
        onClick={onCancel}
        className="rounded-xl px-3 py-1.5 text-[11px] font-semibold text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
      >
        {copy.no}
      </button>
    </div>
  </div>
);

// ─── Voice Button ─────────────────────────────────────────────────────────────
const VoiceButton: React.FC<{
  lang: ChatLanguage;
  onResult: (text: string) => void;
}> = ({ lang, onResult }) => {
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const SpeechRecognitionAPI =
    (window as { SpeechRecognition?: typeof SpeechRecognition; webkitSpeechRecognition?: typeof SpeechRecognition }).SpeechRecognition ||
    (window as { SpeechRecognition?: typeof SpeechRecognition; webkitSpeechRecognition?: typeof SpeechRecognition }).webkitSpeechRecognition;

  if (!SpeechRecognitionAPI) return null; // hide on unsupported browsers

  const toggleListening = () => {
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const rec = new SpeechRecognitionAPI();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = languageOption(lang).speech;
    rec.onresult = (e: SpeechRecognitionEvent) => {
      const transcript = e.results[0][0].transcript;
      onResult(transcript);
      setListening(false);
    };
    rec.onerror = () => setListening(false);
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    rec.start();
    setListening(true);
  };

  return (
    <button
      onClick={toggleListening}
      title={listening ? 'Stop listening' : 'Voice input'}
      aria-label={listening ? 'Stop voice input' : 'Start voice input'}
      className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full transition-all
        ${listening
          ? 'animate-pulse bg-red-500 text-white shadow-lg shadow-red-200'
          : 'text-slate-400 hover:bg-white hover:text-gov-navy hover:shadow-sm'
        }`}
    >
      {listening ? <MicOff size={16} /> : <Mic size={16} />}
    </button>
  );
};

// ─── Main Widget ──────────────────────────────────────────────────────────────
const ChatWidget: React.FC<ChatWidgetProps> = ({
  officialId,
  fullName,
  govId,
  jobRole   = 'Statistical Official',
  department = 'MoSPI',
  skillGaps,
  recommendations,
  onNavigate,
}) => {
  const [isOpen, setIsOpen]         = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [lang, setLang]             = useState<ChatLanguage>('en');
  const [hasUnread, setHasUnread]   = useState(true);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const inputRef                    = useRef<HTMLTextAreaElement>(null);
  const attachInputRef              = useRef<HTMLInputElement>(null);
  const chatPanelRef                = useRef<HTMLDivElement>(null);

  const { theme, toggleTheme } = useTheme();
  const copy = chatCopy(lang);

  const { messages, isTyping, pendingNav, handleSend, confirmNav, cancelNav, messagesEndRef } =
    useChatEngine({
      officialId, fullName, govId, jobRole, department,
      skillGaps, recommendations,
      context: 'dashboard',
      lang,
      onNavigate,
      onThemeToggle: (target) => {
        // 'toggle' always flips; 'dark'/'light' only act if not already that theme
        if (target === 'toggle') { toggleTheme(); }
        else if (target === 'dark'  && theme !== 'dark')  { toggleTheme(); }
        else if (target === 'light' && theme !== 'light') { toggleTheme(); }
      },
      // "switch to Hindi" has to move the widget itself, otherwise the header
      // pill and the suggestion chips keep saying EN while replies come back Hindi.
      onLanguageChange: (target) => setLang(target),
    });

  const activeGapsCount = skillGaps.filter(g => g.gap > 0).length;

  // ── Document hand-off to the Assessment Studio (quiz / Learning Mode) ──────
  // Gyan stays offline (no API key), so it never reads the file itself — it
  // only carries it to the Studio, which already has GEMINI_API_KEY wired up.
  const handleAttach = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) setPendingFile(f);
    e.target.value = '';
  };

  const startStudio = useCallback((mode: StudioMode) => {
    if (!pendingFile) return;
    setPendingStudioUpload(pendingFile, mode);
    setPendingFile(null);
    onNavigate?.({
      type: 'redirect',
      target: '/assessment',
      label: mode === 'quiz' ? 'Assessment Studio' : 'Assessment Studio — Learning Mode',
    });
  }, [pendingFile, onNavigate]);

  const sendWithAttachment = useCallback((text: string) => {
    if (pendingFile) {
      if (QUIZ_INTENT_RE.test(text)) { startStudio('quiz'); return; }
      if (LEARN_INTENT_RE.test(text)) { startStudio('learn'); return; }
    }
    handleSend(text);
  }, [pendingFile, startStudio, handleSend]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300);
      setHasUnread(false);
    }
  }, [isOpen]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendWithAttachment(inputValue);
      setInputValue('');
    }
  };

  const onVoiceResult = useCallback((text: string) => {
    setInputValue(text);
    // Auto-send after brief delay so user can see what was recognized
    setTimeout(() => {
      sendWithAttachment(text);
      setInputValue('');
    }, 800);
  }, [sendWithAttachment]);

  const canSend = Boolean(inputValue.trim()) && !isTyping;

  return (
    <>
      {/* ── Chat Panel ────────────────────────────────────────────────────── */}
      <div
        ref={chatPanelRef}
        role="dialog"
        aria-label="Gyan AI assistant"
        className={`fixed bottom-24 right-4 z-50 flex max-h-[min(660px,calc(100vh-8rem))] w-[calc(100vw-2rem)] max-w-[400px] flex-col
          overflow-hidden rounded-[28px] border border-white/60 bg-white ring-1 ring-slate-900/[0.06]
          transition-all duration-300 ease-out sm:right-6
          ${isOpen
            ? 'pointer-events-auto translate-y-0 scale-100 opacity-100'
            : 'pointer-events-none translate-y-4 scale-95 opacity-0'
          }`}
        style={{ boxShadow: '0 32px 80px -16px rgba(10,26,51,0.42), 0 8px 24px -12px rgba(10,26,51,0.22)' }}
      >
        {/* Header */}
        <div className="relative flex flex-shrink-0 items-center gap-3 overflow-hidden bg-gradient-to-br from-gov-ink via-gov-navy to-gov-blue px-4 pb-4 pt-3.5">
          <div className="pointer-events-none absolute -right-6 -top-10 text-white/[0.07]">
            <AshokaChakra size={140} />
          </div>
          {/* soft top sheen */}
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-white/25" />

          <div className="relative flex-shrink-0">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/25 bg-white/15 shadow-inner backdrop-blur-sm">
              <GyanBot size={30} />
            </span>
            <span className="absolute -bottom-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full border-2 border-gov-ink bg-emerald-400">
              <span className="h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
            </span>
          </div>

          <div className="relative min-w-0 flex-1">
            <p className="text-[15px] font-bold leading-tight text-white">Gyan (ज्ञान)</p>
            <p className="mt-0.5 truncate text-[11px] font-medium text-sky-300">
              MoSPI AI Assistant • {copy.tagline}
            </p>
          </div>

          <LanguageMenu value={lang} onChange={setLang} chatPanelRef={chatPanelRef} />

          {/* Minimize */}
          <button
            onClick={() => setIsOpen(false)}
            aria-label="Minimise assistant"
            className="relative flex-shrink-0 rounded-full p-1 text-white/70 transition-colors hover:bg-white/10 hover:text-white"
          >
            <ChevronDown size={18} />
          </button>

          {/* Tricolour rule — the GoI cue that ties the widget to the portal */}
          <span className="pointer-events-none absolute inset-x-0 bottom-0 h-[3px] bg-gradient-to-r from-gov-saffron via-white/80 to-gov-green" />
        </div>

        {/* Messages area */}
        <div className="custom-scrollbar min-h-0 flex-1 overflow-y-auto scroll-smooth bg-gradient-to-b from-[#f5f9ff] via-[#fbfdff] to-white px-4 py-4">
          {messages.length === 0 && (
            <div className="flex animate-fade-in flex-col items-center">
              <GyanHero className="mb-1" />

              <p className="text-center text-[21px] font-bold text-gov-ink">{copy.greeting}</p>
              <p className="mb-5 mt-1 text-center text-[12.5px] leading-relaxed text-slate-500">
                {copy.dashSubtitle(activeGapsCount)}
              </p>

              {/* Capability cards — each sends a real prompt */}
              <div className="mb-5 grid w-full grid-cols-2 gap-2.5 sm:grid-cols-4">
                {CAPABILITIES.map(({ id, icon: Icon, label, ask, tile, ink }) => (
                  <button
                    key={id}
                    onClick={() => handleSend(copy.ask[ask])}
                    className="group flex flex-col items-center gap-2 rounded-2xl border border-slate-200/80 bg-white px-2 py-3 text-center
                      transition-all duration-200 hover:-translate-y-0.5 hover:border-gov-blue/30 hover:shadow-[0_10px_24px_-14px_rgba(10,26,51,0.6)]"
                  >
                    <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${tile} transition-transform duration-200 group-hover:scale-105`}>
                      <Icon size={18} className={ink} aria-hidden="true" />
                    </span>
                    <span className="text-[10.5px] font-semibold leading-tight text-slate-700">{copy.label[label]}</span>
                  </button>
                ))}
              </div>

              <div className="mb-3 flex w-full items-center gap-3">
                <span className="h-px flex-1 bg-gradient-to-r from-transparent to-slate-200" />
                <span className="text-[11.5px] font-medium text-slate-400">{copy.tryAsking}</span>
                <span className="h-px flex-1 bg-gradient-to-l from-transparent to-slate-200" />
              </div>

              <div className="flex w-full flex-col gap-2">
                {SUGGESTION_KEYS.map(key => (
                  <button
                    key={key}
                    onClick={() => handleSend(copy.ask[key])}
                    className="group relative flex items-center gap-3 overflow-hidden rounded-2xl border border-slate-200/80 bg-[#f4f8ff] px-3.5 py-2.5 text-left
                      transition-all duration-200 hover:border-gov-blue/35 hover:bg-white hover:shadow-sm"
                  >
                    <span className="absolute inset-y-0 left-0 w-[3px] origin-top scale-y-0 bg-gov-saffron transition-transform duration-200 group-hover:scale-y-100" />
                    <span className="flex-1 text-[12.5px] font-medium text-slate-700">{copy.ask[key]}</span>
                    <ChevronRight size={15} className="flex-shrink-0 text-slate-300 transition-all group-hover:translate-x-0.5 group-hover:text-gov-navy" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map(msg => <MessageBubble key={msg.id} msg={msg} />)}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Attached-document banner — attach → pick quiz or Learning Mode → Assessment Studio */}
        {pendingFile && (
          <div className="animate-bubble-in mx-3.5 mb-3 flex flex-col gap-2 rounded-2xl border border-gov-sky/25 bg-gradient-to-br from-[#eef4ff] to-white p-3 shadow-sm">
            <div className="flex items-center gap-2">
              <Paperclip size={13} className="flex-shrink-0 text-gov-blue" />
              <span className="min-w-0 flex-1 truncate text-[12px] font-semibold text-gov-navy">{pendingFile.name}</span>
              <button
                onClick={() => setPendingFile(null)}
                aria-label="Remove attached document"
                className="rounded-md p-0.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
              >
                <X size={13} />
              </button>
            </div>
            <p className="text-[11px] text-slate-500">What should I do with this document?</p>
            <div className="flex gap-2">
              <button
                onClick={() => startStudio('quiz')}
                className="flex-1 rounded-xl bg-gradient-to-br from-gov-navy to-gov-blue py-1.5 text-[11px] font-bold text-white shadow-sm transition-all hover:shadow-md active:scale-[0.98]"
              >
                📝 Generate a quiz
              </button>
              <button
                onClick={() => startStudio('learn')}
                className="flex-1 rounded-xl border border-gov-blue/30 bg-white py-1.5 text-[11px] font-bold text-gov-navy shadow-sm transition-all hover:shadow-md active:scale-[0.98]"
              >
                📖 Help me study this
              </button>
            </div>
          </div>
        )}

        {/* Navigation Confirmation Banner */}
        {pendingNav && (
          <NavConfirmBanner
            action={pendingNav.action}
            copy={copy}
            onConfirm={confirmNav}
            onCancel={cancelNav}
          />
        )}

        {/* Input bar */}
        <div className="relative flex-shrink-0 overflow-hidden border-t border-slate-100 bg-white px-3.5 pb-3 pt-3">
          <div className="pointer-events-none absolute -bottom-3 right-4 text-slate-900/[0.04]">
            <Landmark size={64} strokeWidth={1} />
          </div>

          <input
            ref={attachInputRef}
            type="file"
            className="hidden"
            accept={STUDIO_ACCEPT}
            aria-label="Attach a document for a quiz or Learning Mode"
            onChange={handleAttach}
          />

          <div className="relative flex items-end gap-1.5 rounded-[22px] border border-slate-200 bg-slate-50/80 py-1.5 pl-4 pr-1.5
            transition-all duration-200 focus-within:border-gov-blue/40 focus-within:bg-white focus-within:shadow-[0_0_0_4px_rgba(47,111,191,0.10)]">
            <button
              onClick={() => attachInputRef.current?.click()}
              title="Attach a document (quiz or Learning Mode)"
              aria-label="Attach a document"
              className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-slate-400 transition-all hover:bg-white hover:text-gov-navy hover:shadow-sm"
            >
              <Paperclip size={16} />
            </button>
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={copy.placeholderDash}
              rows={1}
              disabled={isTyping}
              aria-label="Message Gyan"
              // focus-visible:ring-0 opts out of the global saffron a11y ring —
              // the pill's own focus-within treatment already shows focus here.
              className="max-h-24 flex-1 resize-none self-center overflow-y-auto bg-transparent py-1.5 text-[13px] leading-relaxed text-slate-800
                placeholder-slate-400 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 disabled:opacity-50"
              style={{ minHeight: '24px' }}
            />
            <VoiceButton lang={lang} onResult={onVoiceResult} />
            <button
              onClick={() => { sendWithAttachment(inputValue); setInputValue(''); }}
              disabled={!canSend}
              aria-label="Send message"
              className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-white transition-all duration-200
                ${canSend
                  ? 'bg-gradient-to-br from-gov-navy to-gov-blue shadow-[0_6px_16px_-6px_rgba(11,42,85,0.8)] hover:scale-105 active:scale-95'
                  : 'cursor-not-allowed bg-slate-300 shadow-none'
                }`}
            >
              <Send size={15} className={canSend ? 'translate-x-[1px]' : ''} />
            </button>
          </div>

          <p className="relative mt-2 flex items-center justify-center gap-2.5 text-[10.5px] text-slate-400">
            <span className="flex items-center gap-1">
              <Lightbulb size={11} className="text-gov-saffron" aria-hidden="true" />
              {copy.hintNewline}
            </span>
            <span className="h-3 w-px bg-slate-200" />
            <span className="flex items-center gap-1">
              <AudioLines size={11} className="text-accent-blue" aria-hidden="true" />
              {copy.hintMic}
            </span>
          </p>
        </div>
      </div>

      {/* ── Floating Bubble ────────────────────────────────────────────────── */}
      <button
        id="chat-widget-bubble"
        onClick={() => setIsOpen(v => !v)}
        className={`fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full
          bg-gradient-to-br from-gov-ink to-gov-blue text-white
          shadow-[0_8px_32px_-8px_rgba(43,76,126,0.6)] transition-all duration-200
          hover:scale-110 hover:shadow-[0_12px_40px_-8px_rgba(43,76,126,0.8)] active:scale-95`}
        title={copy.bubbleTitle}
        aria-label="Open AI chat assistant"
      >
        {isOpen ? (
          <X size={20} />
        ) : (
          <>
            <span className="absolute inset-0 animate-ping rounded-full bg-gov-sky/25" style={{ animationDuration: '3s' }} />
            <Bot size={22} className="relative" />
            {hasUnread && (
              <span className="absolute -right-1 -top-1 h-4 w-4 animate-pulse rounded-full border-2 border-white bg-emerald-400" />
            )}
          </>
        )}
      </button>
    </>
  );
};

export default ChatWidget;
