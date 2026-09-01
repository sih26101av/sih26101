/**
 * FILE: src/components/dashboard/ChatWidget.tsx
 *
 * Gyan (ज्ञान) — Multilingual AI Learning Assistant
 * Floating chat bubble widget for the MoSPI Skill Intelligence Platform.
 *
 * Archit Shukla | SIH 2026
 *
 * Features:
 *  - Animated floating bubble (bottom-right, fixed)
 *  - Slide-up chat panel with glassmorphism styling
 *  - Personalized suggestion chips (context-aware)
 *  - Auto-scroll to latest message
 *  - Typing indicator (3-dot animation)
 *  - EN/HI language toggle
 *  - Renders markdown bold via simple parser
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { X, Send, Bot, Languages, ChevronDown } from 'lucide-react';
import type { SkillGapEntry, CourseRecommendation } from '../../types/domain';
import { sendChatMessage, type ChatMessage } from '../../services/chatApi';

// ─── Props ────────────────────────────────────────────────────────────────────
interface ChatWidgetProps {
  officialId: string;
  fullName?: string;
  govId?: string;
  jobRole?: string;
  department?: string;
  skillGaps: SkillGapEntry[];
  recommendations: CourseRecommendation[];
}

// ─── Suggestion chips (bilingual) ──────────────────────────────────────────────
const SUGGESTIONS_EN = [
  'What are my skill gaps?',
  'Which course should I take first?',
  'Explain GDP calculation',
  'How do I use this platform?',
];
const SUGGESTIONS_HI = [
  'मेरे skill gaps क्या हैं?',
  'मुझे पहले कौन सा course लेना चाहिए?',
  'GDP कैसे calculate होती है?',
  'यह platform कैसे use करूँ?',
];

// ─── Tiny markdown renderer (bold only) ──────────────────────────────────────
function renderMarkdown(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    // Preserve newlines
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
    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#2b4c7e] to-[#1e3a5f] flex items-center justify-center flex-shrink-0 shadow-sm">
      <Bot size={14} className="text-white" />
    </div>
    <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm border border-slate-100">
      <div className="flex gap-1 items-center h-4">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"
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
      <div className="flex justify-end mb-3">
        <div className="max-w-[78%]">
          <div className="bg-gradient-to-br from-[#2b4c7e] to-[#1a3660] text-white px-4 py-2.5 rounded-2xl rounded-br-sm text-[13px] leading-relaxed shadow-md">
            {msg.content}
          </div>
          <p className="text-[10px] text-slate-400 text-right mt-1 mr-1">{time}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-end gap-2 mb-3">
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#2b4c7e] to-[#1e3a5f] flex items-center justify-center flex-shrink-0 shadow-sm">
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

// ─── Main Widget ──────────────────────────────────────────────────────────────
const ChatWidget: React.FC<ChatWidgetProps> = ({
  officialId,
  fullName,
  govId,
  jobRole   = 'Statistical Official',
  department = 'MoSPI',
  skillGaps,
  recommendations,
}) => {
  const [isOpen, setIsOpen]         = useState(false);
  const [messages, setMessages]     = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping]     = useState(false);
  const [lang, setLang]             = useState<'en' | 'hi'>('en');
  const [hasUnread, setHasUnread]   = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef       = useRef<HTMLTextAreaElement>(null);

  const suggestions = lang === 'hi' ? SUGGESTIONS_HI : SUGGESTIONS_EN;

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300);
      setHasUnread(false);
    }
  }, [isOpen]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  // Send a message
  const handleSend = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isTyping) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: trimmed,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    try {
      const { reply, detectedLanguage } = await sendChatMessage(
        officialId,
        trimmed,
        messages,
        jobRole,
        department,
        skillGaps,
        recommendations,
        fullName,
        govId,
      );

      // Simulate realistic typing delay (600ms–1.2s)
      await new Promise(resolve => setTimeout(resolve, 600 + Math.random() * 600));

      const botMsg: ChatMessage = {
        id: `msg-${Date.now()}-bot`,
        role: 'model',
        content: reply,
        timestamp: new Date(),
        detectedLanguage,
      };
      setMessages(prev => [...prev, botMsg]);
    } catch {
      const errMsg: ChatMessage = {
        id: `msg-err-${Date.now()}`,
        role: 'model',
        content: lang === 'hi'
          ? 'Maafi chahta hoon, abhi kuch technical problem aa gayi. Thodi der baad dobara try karein. 🙏'
          : 'Sorry, I encountered a technical issue. Please try again in a moment. 🙏',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setIsTyping(false);
    }
  }, [isTyping, messages, officialId, fullName, govId, jobRole, department, skillGaps, recommendations, lang]);

  // Handle Enter key (Shift+Enter = newline)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(inputValue);
    }
  };

  const activeGapsCount = skillGaps.filter(g => g.gap > 0).length;

  return (
    <>
      {/* ── Chat Panel ────────────────────────────────────────────────────── */}
      <div
        className={`fixed bottom-24 right-6 z-50 w-[370px] max-h-[580px] flex flex-col
          bg-[#f8fafc] rounded-3xl shadow-2xl border border-slate-200/80
          transition-all duration-300 ease-out origin-bottom-right
          ${isOpen
            ? 'opacity-100 scale-100 translate-y-0 pointer-events-auto'
            : 'opacity-0 scale-95 translate-y-4 pointer-events-none'
          }`}
        style={{ boxShadow: '0 24px 60px -12px rgba(0,0,0,0.18), 0 8px 20px -8px rgba(43,76,126,0.12)' }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 px-4 py-3.5 bg-gradient-to-r from-[#1a2f52] to-[#2b4c7e] rounded-t-3xl flex-shrink-0">
          <div className="relative">
            <div className="w-9 h-9 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center border border-white/30">
              <Bot size={18} className="text-white" />
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#1a2f52]" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white font-bold text-[13px] leading-none">Gyan (ज्ञान)</p>
            <p className="text-blue-200 text-[10px] mt-0.5">MoSPI AI Training Assistant · Online</p>
          </div>

          {/* Language Toggle */}
          <button
            onClick={() => setLang(l => l === 'en' ? 'hi' : 'en')}
            title="Switch language"
            className="flex items-center gap-1 bg-white/15 hover:bg-white/25 border border-white/20 rounded-full px-2.5 py-1 text-white text-[10px] font-bold transition-colors"
          >
            <Languages size={10} />
            {lang === 'en' ? 'EN' : 'HI'}
          </button>

          {/* Minimize */}
          <button
            onClick={() => setIsOpen(false)}
            className="text-white/70 hover:text-white hover:bg-white/10 rounded-full p-1 transition-colors"
          >
            <ChevronDown size={16} />
          </button>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto px-4 py-3 scroll-smooth min-h-0">
          {/* Empty state: suggestion chips */}
          {messages.length === 0 && (
            <div className="flex flex-col items-center pt-2 pb-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#2b4c7e] to-[#1e3a5f] flex items-center justify-center shadow-md mb-3">
                <Bot size={22} className="text-white" />
              </div>
              <p className="text-slate-700 font-bold text-[13px] text-center">
                {lang === 'hi' ? 'Namaste! Main Gyan hoon 🙏' : 'Hello! I\'m Gyan 👋'}
              </p>
              <p className="text-slate-500 text-[11px] text-center mt-1 mb-4 leading-relaxed">
                {lang === 'hi'
                  ? `Aapke paas ${activeGapsCount} active skill gap${activeGapsCount !== 1 ? 's' : ''} hain. Main aapki madad karunga!`
                  : `You have ${activeGapsCount} active skill gap${activeGapsCount !== 1 ? 's' : ''}. Ask me anything!`
                }
              </p>

              {/* Suggestion chips */}
              <div className="flex flex-col gap-2 w-full">
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(s)}
                    className="text-left px-3 py-2 rounded-xl bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-300 text-[12px] text-slate-700 font-medium transition-all shadow-sm hover:shadow-md active:scale-[0.98]"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message list */}
          {messages.map(msg => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}

          {/* Typing indicator */}
          {isTyping && <TypingIndicator />}

          <div ref={messagesEndRef} />
        </div>

        {/* Input bar */}
        <div className="flex-shrink-0 bg-white border-t border-slate-100 rounded-b-3xl px-3 py-3">
          <div className="flex items-end gap-2 bg-slate-50 rounded-2xl border border-slate-200 px-3 py-2 focus-within:ring-2 focus-within:ring-[#2b4c7e]/20 focus-within:border-[#2b4c7e]/40 transition-all">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={lang === 'hi' ? 'Kuch bhi poochiye...' : 'Ask anything about your training...'}
              rows={1}
              disabled={isTyping}
              className="flex-1 bg-transparent text-[13px] text-slate-800 placeholder-slate-400 resize-none focus:outline-none max-h-24 overflow-y-auto leading-relaxed disabled:opacity-50"
              style={{ minHeight: '24px' }}
            />
            <button
              onClick={() => handleSend(inputValue)}
              disabled={!inputValue.trim() || isTyping}
              className="flex-shrink-0 w-8 h-8 rounded-xl bg-gradient-to-br from-[#2b4c7e] to-[#1a3660] text-white flex items-center justify-center shadow-md hover:shadow-lg hover:from-[#3a5d91] transition-all disabled:opacity-40 disabled:cursor-not-allowed active:scale-95"
            >
              <Send size={13} />
            </button>
          </div>
          <p className="text-[10px] text-slate-400 text-center mt-1.5">
            {lang === 'hi' ? 'Shift+Enter नई line के लिए' : 'Shift+Enter for new line'}
          </p>
        </div>
      </div>

      {/* ── Floating Bubble ────────────────────────────────────────────────── */}
      <button
        id="chat-widget-bubble"
        onClick={() => setIsOpen(v => !v)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full
          bg-gradient-to-br from-[#2b4c7e] to-[#1a3660]
          text-white shadow-[0_8px_32px_-8px_rgba(43,76,126,0.6)]
          hover:shadow-[0_12px_40px_-8px_rgba(43,76,126,0.8)]
          hover:scale-110 active:scale-95
          transition-all duration-200 flex items-center justify-center
          ${isOpen ? 'rotate-0' : ''}`}
        title={lang === 'hi' ? 'Gyan AI से बात करें' : 'Chat with Gyan AI'}
        aria-label="Open AI chat assistant"
      >
        {isOpen ? (
          <X size={20} />
        ) : (
          <>
            <Bot size={22} />
            {/* Unread notification dot */}
            {hasUnread && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-emerald-400 border-2 border-white animate-pulse" />
            )}
          </>
        )}
      </button>
    </>
  );
};

export default ChatWidget;
