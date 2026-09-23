/**
 * FILE: src/components/chat/ChatPrimitives.tsx
 *
 * The pieces every Gyan widget draws the same way: bubbles, the typing dots,
 * the navigation confirmation banner and the Web Speech mic button.
 *
 * Lifted out of `dashboard/ChatWidget.tsx` when the admin console got its own
 * widget — three copies of a message bubble is two too many. The styling is
 * unchanged and deliberately light-on-white in every widget: the panel is its
 * own surface floating over the page, so Gyan looks the same on the landing
 * page, the learner dashboard and the (dark-capable) admin console.
 *
 * Archit Shukla | SIH 2026
 */

import React, { useRef, useState } from 'react';
import { Mic, MicOff, Navigation } from 'lucide-react';
import type { ChatLanguage, ChatMessage, NavigateAction } from '../../services/chatApi';
import { GyanBot } from './GyanAvatar';
import { languageOption, type ChatCopy } from '../../i18n/chatLanguages';

// ─── Markdown renderer (bold only) ───────────────────────────────────────────
export function renderMarkdown(text: string): React.ReactNode[] {
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
export const TypingIndicator: React.FC = () => (
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
export const MessageBubble: React.FC<{ msg: ChatMessage }> = ({ msg }) => {
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

// ─── Nav confirmation banner ──────────────────────────────────────────────────
export const NavConfirmBanner: React.FC<{
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

// ─── Voice button ─────────────────────────────────────────────────────────────
export const VoiceButton: React.FC<{
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
