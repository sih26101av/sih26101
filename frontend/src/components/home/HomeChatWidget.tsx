/**
 * FILE: src/components/home/HomeChatWidget.tsx
 *
 * Gyan (ज्ञान) — Public Homepage Chat Widget
 * Variant of ChatWidget for the landing page.
 * - No personal profile data (anonymous visitor)
 * - Knows all homepage sections and can scroll/navigate to them
 * - Also supports voice input
 * - Inherits all chat engine logic via useChatEngine
 *
 * Archit Shukla | SIH 2026
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  X, Send, Bot, Languages, ChevronDown, ChevronRight, Mic, MicOff, Navigation,
  BookOpen, GraduationCap, BarChart3, FileText, Search, User, Landmark, Lightbulb, AudioLines,
} from 'lucide-react';
import type { NavigateAction } from '../../services/chatApi';
import type { ChatMessage } from '../../services/chatApi';
import { useChatEngine } from '../../hooks/useChatEngine';
import { useTheme } from '../../hooks/useTheme';
import { GyanBot, GyanHero } from '../chat/GyanAvatar';
import { AshokaChakra } from '../gov/GovUI';

// ─── Props ───────────────────────────────────────────────────────────────────
interface HomeChatWidgetProps {
  onScrollToSection: (sectionId: string) => void;
  onOpenLogin: () => void;
  onLanguageChange?: (lang: 'en' | 'hi') => void;
}

// ─── Capability cards — each one sends a real prompt to the engine ───────────
const CAPABILITIES = [
  {
    id: 'guidance', icon: BookOpen,
    label: { en: 'Platform Guidance', hi: 'प्लेटफ़ॉर्म मार्गदर्शन' },
    prompt: { en: 'What is this platform?', hi: 'यह platform क्या है?' },
    tile: 'bg-accent-blue-soft', ink: 'text-accent-blue',
  },
  {
    id: 'courses', icon: GraduationCap,
    label: { en: 'Course Recommendations', hi: 'पाठ्यक्रम अनुशंसाएँ' },
    prompt: { en: 'How do course recommendations work?', hi: 'Course recommendations कैसे काम करती हैं?' },
    tile: 'bg-accent-green-soft', ink: 'text-accent-green',
  },
  {
    id: 'insights', icon: BarChart3,
    label: { en: 'Competency Insights', hi: 'दक्षता अंतर्दृष्टि' },
    prompt: { en: 'How does skill gap analysis work?', hi: 'Skill gap analysis कैसे होता है?' },
    tile: 'bg-accent-orange-soft', ink: 'text-accent-orange',
  },
  {
    id: 'quick', icon: FileText,
    label: { en: 'Quick Information', hi: 'त्वरित जानकारी' },
    prompt: { en: 'Tell me about MoSPI', hi: 'MoSPI के बारे में बताओ' },
    tile: 'bg-accent-purple-soft', ink: 'text-accent-purple',
  },
] as const;

// ─── Homepage-specific suggestions ───────────────────────────────────────────
const SUGGESTIONS_EN = [
  { icon: Search, text: 'What is this platform?' },
  { icon: BookOpen, text: 'Show me the Features section' },
  { icon: User, text: 'How do I login?' },
  { icon: Landmark, text: 'Tell me about MoSPI' },
];
const SUGGESTIONS_HI = [
  { icon: Search, text: 'यह platform क्या है?' },
  { icon: BookOpen, text: 'Features section दिखाओ' },
  { icon: User, text: 'Login कैसे करूँ?' },
  { icon: Landmark, text: 'MoSPI के बारे में बताओ' },
];

// ─── Markdown renderer ────────────────────────────────────────────────────────
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
  <div className="mb-3 flex items-end gap-2">
    <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-slate-200">
      <GyanBot size={22} />
    </span>
    <div className="rounded-2xl rounded-bl-sm border border-slate-100 bg-white px-4 py-3 shadow-sm">
      <div className="flex h-4 items-center gap-1">
        {[0, 1, 2].map(i => (
          <span key={i} className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400"
            style={{ animationDelay: `${i * 0.18}s`, animationDuration: '0.9s' }} />
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
      <div className="mb-3 flex justify-end">
        <div className="max-w-[78%]">
          <div className="rounded-2xl rounded-br-sm bg-gradient-to-br from-gov-ink to-gov-blue px-4 py-2.5 text-[13px] leading-relaxed text-white shadow-md">
            {msg.content}
          </div>
          <p className="mr-1 mt-1 text-right text-[10px] text-slate-400">{time}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-3 flex items-end gap-2">
      <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-white shadow-sm ring-1 ring-slate-200">
        <GyanBot size={22} />
      </span>
      <div className="max-w-[82%]">
        <div className="rounded-2xl rounded-bl-sm border border-slate-100 bg-white px-4 py-2.5 text-[13px] leading-relaxed text-slate-800 shadow-sm">
          {renderMarkdown(msg.content)}
        </div>
        <p className="ml-1 mt-1 text-[10px] text-slate-400">{time}</p>
      </div>
    </div>
  );
};

// ─── Nav Confirmation Banner ──────────────────────────────────────────────────
const NavConfirmBanner: React.FC<{
  action: NavigateAction;
  lang: 'en' | 'hi';
  onConfirm: () => void;
  onCancel: () => void;
}> = ({ action, lang, onConfirm, onCancel }) => (
  <div className="mx-4 mb-3 flex flex-col gap-2 rounded-xl border border-blue-200 bg-blue-50 p-3">
    <p className="flex items-center gap-1.5 text-[12px] font-medium text-blue-800">
      <Navigation size={12} />
      {lang === 'hi'
        ? `क्या मैं आपको "${action.label}" पर ले जाऊं?`
        : `Scroll to the ${action.label}?`}
    </p>
    <div className="flex gap-2">
      <button onClick={onConfirm}
        className="flex-1 rounded-lg bg-gov-navy py-1.5 text-[11px] font-bold text-white transition-colors hover:bg-gov-blue">
        {lang === 'hi' ? 'हाँ ✈️' : 'Yes, take me there ✈️'}
      </button>
      <button onClick={onCancel}
        className="rounded-lg px-3 py-1.5 text-[11px] font-medium text-slate-500 transition-colors hover:bg-slate-100">
        {lang === 'hi' ? 'नहीं' : 'No'}
      </button>
    </div>
  </div>
);

// ─── Voice Button ─────────────────────────────────────────────────────────────
const VoiceButton: React.FC<{ lang: 'en' | 'hi'; onResult: (t: string) => void }> = ({ lang, onResult }) => {
  const [listening, setListening] = useState(false);
  const recRef = useRef<SpeechRecognition | null>(null);

  const SRAPI =
    (window as { SpeechRecognition?: typeof SpeechRecognition; webkitSpeechRecognition?: typeof SpeechRecognition }).SpeechRecognition ||
    (window as { SpeechRecognition?: typeof SpeechRecognition; webkitSpeechRecognition?: typeof SpeechRecognition }).webkitSpeechRecognition;

  if (!SRAPI) return null;

  const toggle = () => {
    if (listening) { recRef.current?.stop(); setListening(false); return; }
    const rec = new SRAPI();
    rec.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    rec.onresult = (e: SpeechRecognitionEvent) => { onResult(e.results[0][0].transcript); setListening(false); };
    rec.onerror = () => setListening(false);
    rec.onend   = () => setListening(false);
    recRef.current = rec;
    rec.start();
    setListening(true);
  };

  return (
    <button
      onClick={toggle}
      aria-label={listening ? 'Stop voice input' : 'Start voice input'}
      title={listening ? 'Stop' : 'Voice input'}
      className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full transition-all
        ${listening ? 'animate-pulse bg-red-500 text-white shadow-lg shadow-red-200' : 'text-slate-400 hover:bg-slate-100 hover:text-gov-navy'}`}
    >
      {listening ? <MicOff size={16} /> : <Mic size={16} />}
    </button>
  );
};

// ─── Main HomeChatWidget ───────────────────────────────────────────────────────
const HomeChatWidget: React.FC<HomeChatWidgetProps> = ({ onScrollToSection, onOpenLogin, onLanguageChange }) => {
  const [isOpen, setIsOpen]         = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [lang, setLang]             = useState<'en' | 'hi'>('en');
  const [hasUnread, setHasUnread]   = useState(true);
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const inputRef                    = useRef<HTMLTextAreaElement>(null);

  // Navigation handler: route scroll/modal actions from the bot
  const handleNavigate = useCallback((action: NavigateAction) => {
    if (action.type === 'scroll') {
      const sectionId = action.target.replace('#', '');
      onScrollToSection(sectionId);
    } else if (action.type === 'modal' && action.target === 'login') {
      onOpenLogin();
      setIsOpen(false);
    }
  }, [onScrollToSection, onOpenLogin]);

  const { theme, toggleTheme } = useTheme();

  const { messages, isTyping, pendingNav, handleSend, confirmNav, cancelNav, messagesEndRef } =
    useChatEngine({
      officialId: 'anonymous',
      context: 'home',
      lang,
      onNavigate: handleNavigate,
      onThemeToggle: (target) => {
        if (target === 'toggle') { toggleTheme(); }
        else if (target === 'dark'  && theme !== 'dark')  { toggleTheme(); }
        else if (target === 'light' && theme !== 'light') { toggleTheme(); }
      },
      onLanguageChange,
    });

  const suggestions = lang === 'hi' ? SUGGESTIONS_HI : SUGGESTIONS_EN;

  useEffect(() => {
    if (isOpen) { setTimeout(() => inputRef.current?.focus(), 300); setHasUnread(false); }
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
      handleSend(inputValue);
      setInputValue('');
    }
  };

  const onVoiceResult = useCallback((text: string) => {
    setInputValue(text);
    setTimeout(() => { handleSend(text); setInputValue(''); }, 800);
  }, [handleSend]);

  return (
    <>
      {/* ── Chat Panel ────────────────────────────────────────────────── */}
      <div
        role="dialog"
        aria-label="Gyan AI assistant"
        className={`fixed bottom-24 right-4 z-50 flex max-h-[min(660px,calc(100vh-8rem))] w-[calc(100vw-2rem)] max-w-[400px] flex-col
          overflow-hidden rounded-[28px] border border-slate-200/80 bg-white
          transition-all duration-300 ease-out sm:right-6
          ${isOpen ? 'pointer-events-auto translate-y-0 scale-100 opacity-100' : 'pointer-events-none translate-y-4 scale-95 opacity-0'}`}
        style={{ boxShadow: '0 28px 70px -14px rgba(10,26,51,0.35)' }}
      >
        {/* ── Header ───────────────────────────────────────────────────── */}
        <div className="relative flex flex-shrink-0 items-center gap-3 overflow-hidden bg-gradient-to-r from-gov-ink via-gov-navy to-gov-blue px-4 py-3.5">
          <div className="pointer-events-none absolute -right-6 -top-10 text-white/[0.07]">
            <AshokaChakra size={140} />
          </div>

          <div className="relative flex-shrink-0">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/25 bg-white/15">
              <GyanBot size={30} />
            </span>
            <span className="absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 rounded-full border-2 border-gov-ink bg-emerald-400" />
          </div>

          <div className="relative min-w-0 flex-1">
            <p className="text-[15px] font-bold leading-tight text-white">Gyan (ज्ञान)</p>
            <p className="mt-0.5 truncate text-[11px] font-medium text-sky-300">
              MoSPI AI Assistant • {lang === 'hi' ? 'कुछ भी पूछें' : 'Ask me anything'}
            </p>
          </div>

          {/* Language selector */}
          <div className="relative flex-shrink-0">
            <button
              onClick={() => setLangMenuOpen(o => !o)}
              aria-haspopup="menu"
              aria-expanded={langMenuOpen}
              aria-label="Change assistant language"
              className="flex items-center gap-1.5 rounded-xl border border-white/25 bg-white/10 px-2.5 py-1.5 text-[11.5px] font-bold text-white transition-colors hover:bg-white/20"
            >
              <Languages size={13} />
              {lang === 'en' ? 'EN' : 'HI'}
              <ChevronDown size={13} className={`transition-transform ${langMenuOpen ? 'rotate-180' : ''}`} />
            </button>

            {langMenuOpen && (
              <>
                <div className="fixed inset-0 z-0" onClick={() => setLangMenuOpen(false)} aria-hidden="true" />
                <div role="menu" className="animate-scale-in absolute right-0 z-10 mt-1.5 w-28 overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-xl">
                  {(['en', 'hi'] as const).map(l => (
                    <button
                      key={l}
                      role="menuitem"
                      onClick={() => { setLang(l); setLangMenuOpen(false); }}
                      className={`block w-full px-3.5 py-2 text-left text-[12.5px] font-medium transition-colors hover:bg-slate-50 ${
                        lang === l ? 'text-gov-navy' : 'text-slate-600'
                      }`}
                    >
                      {l === 'en' ? 'English' : 'हिंदी'}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          <button
            onClick={() => setIsOpen(false)}
            aria-label="Minimise assistant"
            className="relative flex-shrink-0 rounded-full p-1 text-white/70 transition-colors hover:bg-white/10 hover:text-white"
          >
            <ChevronDown size={18} />
          </button>
        </div>

        {/* ── Body ─────────────────────────────────────────────────────── */}
        <div className="min-h-0 flex-1 overflow-y-auto scroll-smooth bg-gradient-to-b from-[#f7faff] to-white px-4 py-4 custom-scrollbar">
          {messages.length === 0 && (
            <div className="flex flex-col items-center">
              <GyanHero className="mb-1" />

              <p className="text-center text-[21px] font-bold text-gov-ink">
                {lang === 'hi' ? 'नमस्ते! मैं ज्ञान हूँ 🙏' : "Hello! I'm Gyan 👋"}
              </p>
              <p className="mb-5 mt-1 text-center text-[12.5px] leading-relaxed text-slate-500">
                {lang === 'hi'
                  ? 'KarmaSkill के लिए आपका AI सहायक'
                  : 'Your AI assistant for KarmaSkill'}
              </p>

              {/* Capability cards — each sends a real prompt */}
              <div className="mb-5 grid w-full grid-cols-2 gap-2.5 sm:grid-cols-4">
                {CAPABILITIES.map(({ id, icon: Icon, label, prompt, tile, ink }) => (
                  <button
                    key={id}
                    onClick={() => handleSend(prompt[lang])}
                    className="flex flex-col items-center gap-2 rounded-xl border border-slate-200 bg-white px-2 py-3 text-center transition-all duration-200 hover:-translate-y-0.5 hover:border-gov-blue/30 hover:shadow-md"
                  >
                    <span className={`flex h-9 w-9 items-center justify-center rounded-lg ${tile}`}>
                      <Icon size={18} className={ink} aria-hidden="true" />
                    </span>
                    <span className="text-[10.5px] font-semibold leading-tight text-slate-700">{label[lang]}</span>
                  </button>
                ))}
              </div>

              {/* Divider */}
              <div className="mb-3 flex w-full items-center gap-3">
                <span className="h-px flex-1 bg-slate-200" />
                <span className="text-[11.5px] font-medium text-slate-400">
                  {lang === 'hi' ? 'यह पूछकर देखें' : 'Try asking'}
                </span>
                <span className="h-px flex-1 bg-slate-200" />
              </div>

              <div className="flex w-full flex-col gap-2">
                {suggestions.map(({ icon: Icon, text }, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(text)}
                    className="group flex items-center gap-3 rounded-xl border border-slate-200/80 bg-[#f4f8ff] px-3.5 py-2.5 text-left transition-all duration-200 hover:border-gov-blue/35 hover:bg-white hover:shadow-sm"
                  >
                    <Icon size={15} className="flex-shrink-0 text-accent-blue" aria-hidden="true" />
                    <span className="flex-1 text-[12.5px] font-medium text-slate-700">{text}</span>
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

        {/* Navigation Confirmation */}
        {pendingNav && (
          <NavConfirmBanner action={pendingNav.action} lang={lang} onConfirm={confirmNav} onCancel={cancelNav} />
        )}

        {/* ── Input bar ────────────────────────────────────────────────── */}
        <div className="relative flex-shrink-0 overflow-hidden border-t border-slate-100 bg-white px-3.5 pb-3 pt-3">
          <div className="pointer-events-none absolute -bottom-3 right-4 text-slate-900/[0.04]">
            <Landmark size={64} strokeWidth={1} />
          </div>

          <div className="relative flex items-end gap-1.5 rounded-full border border-slate-200 bg-slate-50 py-1.5 pl-4 pr-1.5 transition-all focus-within:border-gov-blue/40 focus-within:bg-white focus-within:ring-2 focus-within:ring-gov-sky/15">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={lang === 'hi' ? 'MoSPI, features, login के बारे में पूछें…' : 'Ask about MoSPI, features, login…'}
              rows={1}
              disabled={isTyping}
              aria-label="Message Gyan"
              className="max-h-24 flex-1 resize-none self-center overflow-y-auto bg-transparent py-1.5 text-[13px] leading-relaxed text-slate-800 placeholder-slate-400 focus:outline-none disabled:opacity-50"
              style={{ minHeight: '24px' }}
            />
            <VoiceButton lang={lang} onResult={onVoiceResult} />
            <button
              onClick={() => { handleSend(inputValue); setInputValue(''); }}
              disabled={!inputValue.trim() || isTyping}
              aria-label="Send message"
              className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-gov-navy to-gov-blue text-white shadow-md transition-all hover:shadow-lg active:scale-95 disabled:opacity-40"
            >
              <Send size={15} />
            </button>
          </div>

          <p className="relative mt-2 flex items-center justify-center gap-2.5 text-[10.5px] text-slate-400">
            <span className="flex items-center gap-1">
              <Lightbulb size={11} className="text-gov-saffron" aria-hidden="true" />
              {lang === 'hi' ? 'नई line के लिए Shift + Enter' : 'Shift + Enter for new line'}
            </span>
            <span className="h-3 w-px bg-slate-200" />
            <span className="flex items-center gap-1">
              <AudioLines size={11} className="text-accent-blue" aria-hidden="true" />
              {lang === 'hi' ? 'बोलने के लिए mic दबाएँ' : 'Click mic to speak'}
            </span>
          </p>
        </div>
      </div>

      {/* ── Floating Bubble ───────────────────────────────────────────── */}
      <button
        id="home-chat-widget-bubble"
        onClick={() => setIsOpen(v => !v)}
        className={`fixed bottom-20 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full
          bg-gradient-to-br from-gov-ink to-gov-blue text-white
          shadow-[0_8px_32px_-8px_rgba(11,42,85,0.6)] transition-all duration-200
          hover:scale-110 hover:shadow-[0_12px_40px_-8px_rgba(11,42,85,0.8)] active:scale-95`}
        title={lang === 'hi' ? 'Gyan AI से बात करें' : 'Chat with Gyan AI'}
        aria-label="Open AI chat assistant"
      >
        {isOpen ? <X size={20} /> : (
          <>
            <Bot size={22} />
            {hasUnread && <span className="absolute -right-1 -top-1 h-4 w-4 animate-pulse rounded-full border-2 border-white bg-emerald-400" />}
          </>
        )}
      </button>
    </>
  );
};

export default HomeChatWidget;
