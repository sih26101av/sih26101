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
import { X, Send, Bot, Languages, ChevronDown, Mic, MicOff, Navigation } from 'lucide-react';
import type { NavigateAction } from '../../services/chatApi';
import type { ChatMessage } from '../../services/chatApi';
import { useChatEngine } from '../../hooks/useChatEngine';

// ─── Props ───────────────────────────────────────────────────────────────────
interface HomeChatWidgetProps {
  onScrollToSection: (sectionId: string) => void;
  onOpenLogin: () => void;
}

// ─── Homepage-specific suggestions ───────────────────────────────────────────
const SUGGESTIONS_EN = [
  'What is this platform?',
  'Show me the Features section',
  'How do I login?',
  'Tell me about MoSPI',
];
const SUGGESTIONS_HI = [
  'यह platform क्या है?',
  'Features section दिखाओ',
  'Login कैसे करूँ?',
  'MoSPI के बारे में बताओ',
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
  <div className="flex items-end gap-2 mb-3">
    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#1f2d4d] to-[#2b4c7e] flex items-center justify-center flex-shrink-0 shadow-sm">
      <Bot size={14} className="text-white" />
    </div>
    <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm border border-slate-100">
      <div className="flex gap-1 items-center h-4">
        {[0, 1, 2].map(i => (
          <span key={i} className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"
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
      <div className="flex justify-end mb-3">
        <div className="max-w-[78%]">
          <div className="bg-gradient-to-br from-[#1f2d4d] to-[#2b4c7e] text-white px-4 py-2.5 rounded-2xl rounded-br-sm text-[13px] leading-relaxed shadow-md">
            {msg.content}
          </div>
          <p className="text-[10px] text-slate-400 text-right mt-1 mr-1">{time}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-end gap-2 mb-3">
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#1f2d4d] to-[#2b4c7e] flex items-center justify-center flex-shrink-0 shadow-sm">
        <Bot size={14} className="text-white" />
      </div>
      <div className="max-w-[82%]">
        <div className="bg-white text-slate-800 px-4 py-2.5 rounded-2xl rounded-bl-sm text-[13px] leading-relaxed shadow-sm border border-slate-100">
          {renderMarkdown(msg.content)}
        </div>
        <p className="text-[10px] text-slate-400 mt-1 ml-1">{time}</p>
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
  <div className="mx-4 mb-3 p-3 rounded-xl bg-blue-50 border border-blue-200 flex flex-col gap-2">
    <p className="text-[12px] text-blue-800 font-medium flex items-center gap-1.5">
      <Navigation size={12} />
      {lang === 'hi'
        ? `क्या मैं आपको "${action.label}" पर ले जाऊं?`
        : `Scroll to the ${action.label}?`}
    </p>
    <div className="flex gap-2">
      <button onClick={onConfirm}
        className="flex-1 py-1.5 bg-[#1f2d4d] text-white text-[11px] font-bold rounded-lg hover:bg-[#2b4c7e] transition-colors">
        {lang === 'hi' ? 'हाँ ✈️' : 'Yes, take me there ✈️'}
      </button>
      <button onClick={onCancel}
        className="px-3 py-1.5 text-slate-500 text-[11px] font-medium rounded-lg hover:bg-slate-100 transition-colors">
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
    <button onClick={toggle} title={listening ? 'Stop' : 'Voice input'}
      className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center transition-all
        ${listening ? 'bg-red-500 text-white animate-pulse shadow-lg shadow-red-200' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'}`}>
      {listening ? <MicOff size={13} /> : <Mic size={13} />}
    </button>
  );
};

// ─── Main HomeChatWidget ───────────────────────────────────────────────────────
const HomeChatWidget: React.FC<HomeChatWidgetProps> = ({ onScrollToSection, onOpenLogin }) => {
  const [isOpen, setIsOpen]         = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [lang, setLang]             = useState<'en' | 'hi'>('en');
  const [hasUnread, setHasUnread]   = useState(true);
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

  const { messages, isTyping, pendingNav, handleSend, confirmNav, cancelNav, messagesEndRef } =
    useChatEngine({
      officialId: 'anonymous',
      context: 'home',
      lang,
      onNavigate: handleNavigate,
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
        className={`fixed bottom-24 right-6 z-50 w-[370px] max-h-[560px] flex flex-col
          bg-[#f8fafc] rounded-3xl shadow-2xl border border-slate-200/80
          transition-all duration-300 ease-out origin-bottom-right
          ${isOpen ? 'opacity-100 scale-100 translate-y-0 pointer-events-auto' : 'opacity-0 scale-95 translate-y-4 pointer-events-none'}`}
        style={{ boxShadow: '0 24px 60px -12px rgba(0,0,0,0.18)' }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 px-4 py-3.5 bg-gradient-to-r from-[#111827] to-[#1f2d4d] rounded-t-3xl flex-shrink-0">
          <div className="relative">
            <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center border border-white/30">
              <Bot size={18} className="text-white" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#111827]" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white font-bold text-[13px] leading-none">Gyan (ज्ञान)</p>
            <p className="text-blue-300 text-[10px] mt-0.5">MoSPI AI Assistant · Ask me anything</p>
          </div>
          <button onClick={() => setLang(l => l === 'en' ? 'hi' : 'en')}
            className="flex items-center gap-1 bg-white/15 hover:bg-white/25 border border-white/20 rounded-full px-2.5 py-1 text-white text-[10px] font-bold transition-colors">
            <Languages size={10} />{lang === 'en' ? 'EN' : 'HI'}
          </button>
          <button onClick={() => setIsOpen(false)}
            className="text-white/70 hover:text-white hover:bg-white/10 rounded-full p-1 transition-colors">
            <ChevronDown size={16} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-3 scroll-smooth min-h-0">
          {messages.length === 0 && (
            <div className="flex flex-col items-center pt-2 pb-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#1f2d4d] to-[#2b4c7e] flex items-center justify-center shadow-md mb-3">
                <Bot size={22} className="text-white" />
              </div>
              <p className="text-slate-700 font-bold text-[13px] text-center">
                {lang === 'hi' ? 'Namaste! Main Gyan hoon 🙏' : "Hello! I'm Gyan 👋"}
              </p>
              <p className="text-slate-500 text-[11px] text-center mt-1 mb-4 leading-relaxed">
                {lang === 'hi'
                  ? 'MoSPI Skill Intelligence Platform ke baare mein poochiye!'
                  : 'Ask me anything about MoSPI Skill Intelligence Platform!'}
              </p>
              <div className="flex flex-col gap-2 w-full">
                {suggestions.map((s, i) => (
                  <button key={i} onClick={() => { handleSend(s); }}
                    className="text-left px-3 py-2 rounded-xl bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-300 text-[12px] text-slate-700 font-medium transition-all shadow-sm hover:shadow-md active:scale-[0.98]">
                    {s}
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

        {/* Input bar */}
        <div className="flex-shrink-0 bg-white border-t border-slate-100 rounded-b-3xl px-3 py-3">
          <div className="flex items-end gap-2 bg-slate-50 rounded-2xl border border-slate-200 px-3 py-2 focus-within:ring-2 focus-within:ring-[#1f2d4d]/20 transition-all">
            <textarea ref={inputRef} value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={lang === 'hi' ? 'Kuch bhi poochiye...' : 'Ask about MoSPI, features, login...'}
              rows={1} disabled={isTyping}
              className="flex-1 bg-transparent text-[13px] text-slate-800 placeholder-slate-400 resize-none focus:outline-none max-h-24 overflow-y-auto leading-relaxed disabled:opacity-50"
              style={{ minHeight: '24px' }}
            />
            <VoiceButton lang={lang} onResult={onVoiceResult} />
            <button onClick={() => { handleSend(inputValue); setInputValue(''); }}
              disabled={!inputValue.trim() || isTyping}
              className="flex-shrink-0 w-8 h-8 rounded-xl bg-gradient-to-br from-[#1f2d4d] to-[#2b4c7e] text-white flex items-center justify-center shadow-md hover:shadow-lg transition-all disabled:opacity-40 active:scale-95">
              <Send size={13} />
            </button>
          </div>
          <p className="text-[10px] text-slate-400 text-center mt-1.5">
            {lang === 'hi' ? 'Shift+Enter नई line | 🎤 बोलकर पूछें' : 'Shift+Enter for new line | 🎤 speak to ask'}
          </p>
        </div>
      </div>

      {/* ── Floating Bubble ───────────────────────────────────────────── */}
      <button
        id="home-chat-widget-bubble"
        onClick={() => setIsOpen(v => !v)}
        className={`fixed bottom-20 right-6 z-50 w-14 h-14 rounded-full
          bg-gradient-to-br from-[#1f2d4d] to-[#2b4c7e]
          text-white shadow-[0_8px_32px_-8px_rgba(31,45,77,0.6)]
          hover:shadow-[0_12px_40px_-8px_rgba(31,45,77,0.8)]
          hover:scale-110 active:scale-95
          transition-all duration-200 flex items-center justify-center`}
        title={lang === 'hi' ? 'Gyan AI से बात करें' : 'Chat with Gyan AI'}
        aria-label="Open AI chat assistant"
      >
        {isOpen ? <X size={20} /> : (
          <>
            <Bot size={22} />
            {hasUnread && <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-emerald-400 border-2 border-white animate-pulse" />}
          </>
        )}
      </button>
    </>
  );
};

export default HomeChatWidget;
