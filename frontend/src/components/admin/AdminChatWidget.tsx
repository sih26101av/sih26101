/**
 * FILE: src/components/admin/AdminChatWidget.tsx
 *
 * Gyan (ज्ञान) on the admin console.
 *
 * Same assistant, same panel and the same nine languages as the learner widget
 * (`dashboard/ChatWidget.tsx`) — the chrome comes from `chat/ChatPrimitives`
 * and `i18n/chatLanguages`, so the three widgets can't drift apart. What
 * differs:
 *
 *  • Transport. It posts to `/api/v1/admin/console/chat` through `api.ts`
 *    (bearer token + 401 refresh) instead of the public `/api/v1/chat`, so the
 *    backend can read the roster, the KPIs and one official's record. There is
 *    deliberately **no** browser fallback engine: invented roster numbers
 *    would be worse than an error bubble.
 *  • Scope. The dashboard's filter bar rides along on every message, so "what
 *    is the compliance" answers about whatever the admin is looking at. Naming
 *    a department, office or service tier in the question overrides it.
 *  • Cards. Workforce / mandatory training / one official / what to train next,
 *    instead of the learner's gaps / courses / progress / assessments.
 *  • No document attach — the Assessment Studio hand-off is a learner flow.
 *
 * Actions come back in the same shape as everywhere else; `AdminDashboard`
 * turns a `tab` action into an `AdminTab` and a `redirect` into a route.
 *
 * Archit Shukla | SIH 2026
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  X, Send, Bot, ChevronDown, ChevronRight,
  Users, ClipboardCheck, UserSearch, Sparkles, Lightbulb, AudioLines, Landmark,
} from 'lucide-react';
import type { ChatLanguage, NavigateAction } from '../../services/chatApi';
import type { ChatTransport } from '../../hooks/useChatEngine';
import { useChatEngine } from '../../hooks/useChatEngine';
import { useTheme } from '../../hooks/useTheme';
import { sendAdminChatMessage, type AdminFilters } from '../../services/api';
import { GyanBot, GyanHero } from '../chat/GyanAvatar';
import { MessageBubble, NavConfirmBanner, TypingIndicator, VoiceButton } from '../chat/ChatPrimitives';
import LanguageMenu from '../chat/LanguageMenu';
import { AshokaChakra } from '../gov/GovUI';
import { chatCopy, adminChatCopy } from '../../i18n/chatLanguages';

// Each card sends a real prompt; `label` / `ask` are keys into the per-language
// admin copy table, so a new language needs no change here.
const CAPABILITIES = [
  { id: 'workforce',  icon: Users,          label: 'workforce',  ask: 'overview',  tile: 'bg-accent-blue-soft',   ink: 'text-accent-blue' },
  { id: 'compliance', icon: ClipboardCheck, label: 'compliance', ask: 'mandatory', tile: 'bg-accent-rose-soft',   ink: 'text-accent-rose' },
  { id: 'official',   icon: UserSearch,     label: 'official',   ask: 'official',  tile: 'bg-accent-green-soft',  ink: 'text-accent-green' },
  { id: 'insights',   icon: Sparkles,       label: 'insights',   ask: 'emerging',  tile: 'bg-accent-purple-soft', ink: 'text-accent-purple' },
] as const;

const SUGGESTION_KEYS = ['compliance', 'shortages', 'departments', 'health'] as const;

interface AdminChatWidgetProps {
  /** Shown to the backend as the asker; the reply never depends on it. */
  adminName?: string;
  /** The dashboard's current filter bar — the default scope for every answer. */
  filters?: AdminFilters;
  onNavigate?: (action: NavigateAction) => void;
}

const AdminChatWidget: React.FC<AdminChatWidgetProps> = ({ adminName, filters, onNavigate }) => {
  const [isOpen, setIsOpen]         = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [lang, setLang]             = useState<ChatLanguage>('en');
  const [hasUnread, setHasUnread]   = useState(true);
  const inputRef                    = useRef<HTMLTextAreaElement>(null);
  const chatPanelRef                = useRef<HTMLDivElement>(null);

  const { theme, toggleTheme } = useTheme();
  const copy = chatCopy(lang);          // shared chrome: hints, yes/no, errors
  const admin = adminChatCopy(lang);    // console-specific cards and prompts

  const transport = useCallback<ChatTransport>(async (message, history, language) => {
    const data = await sendAdminChatMessage({
      message,
      history: history.map(m => ({ role: m.role, content: m.content })),
      preferred_language: language,
      filters,
      full_name: adminName,
    });
    return {
      reply: data.reply,
      detectedLanguage: (data.detected_language as ChatLanguage) ?? 'en',
      navigateAction: data.navigate_action ?? undefined,
      navigateActions: data.navigate_actions ?? [],
    };
  }, [filters, adminName]);

  const { messages, isTyping, pendingNav, handleSend, confirmNav, cancelNav, messagesEndRef } =
    useChatEngine({
      officialId: adminName || 'admin',
      jobRole: 'System Administrator',
      department: 'MoSPI',
      context: 'dashboard',
      lang,
      transport,
      onNavigate,
      onThemeToggle: (target) => {
        if (target === 'toggle') { toggleTheme(); }
        else if (target === 'dark'  && theme !== 'dark')  { toggleTheme(); }
        else if (target === 'light' && theme !== 'light') { toggleTheme(); }
      },
      onLanguageChange: (target) => setLang(target),
    });

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

  const send = (text: string) => { handleSend(text); setInputValue(''); };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send(inputValue);
    }
  };

  const onVoiceResult = useCallback((text: string) => {
    setInputValue(text);
    // Brief delay so the admin can see what was recognised before it is sent.
    setTimeout(() => { handleSend(text); setInputValue(''); }, 800);
  }, [handleSend]);

  const canSend = Boolean(inputValue.trim()) && !isTyping;

  return (
    <>
      {/* ── Chat Panel ────────────────────────────────────────────────────── */}
      <div
        ref={chatPanelRef}
        role="dialog"
        aria-label="Gyan admin assistant"
        className={`fixed bottom-[4.75rem] right-2 z-50 flex max-h-[min(660px,calc(100dvh-6rem))] w-[calc(100vw-1rem)] sm:bottom-24 sm:max-h-[min(660px,calc(100dvh-8rem))] sm:w-[calc(100vw-3rem)] max-w-[400px] flex-col
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
              MoSPI AI Assistant • {admin.tagline}
            </p>
          </div>

          <LanguageMenu value={lang} onChange={setLang} chatPanelRef={chatPanelRef} />

          <button
            onClick={() => setIsOpen(false)}
            aria-label="Minimise assistant"
            className="relative flex-shrink-0 rounded-full p-1 text-white/70 transition-colors hover:bg-white/10 hover:text-white"
          >
            <ChevronDown size={18} />
          </button>

          <span className="pointer-events-none absolute inset-x-0 bottom-0 h-[3px] bg-gradient-to-r from-gov-saffron via-white/80 to-gov-green" />
        </div>

        {/* Messages area */}
        <div className="custom-scrollbar min-h-0 flex-1 overflow-y-auto scroll-smooth bg-gradient-to-b from-[#f5f9ff] via-[#fbfdff] to-white px-4 py-4">
          {messages.length === 0 && (
            <div className="flex animate-fade-in flex-col items-center">
              <GyanHero className="mb-1" />

              <p className="text-center text-[21px] font-bold text-gov-ink">{copy.greeting}</p>
              <p className="mb-5 mt-1 text-center text-[12.5px] leading-relaxed text-slate-500">
                {admin.subtitle}
              </p>

              <div className="mb-5 grid w-full grid-cols-2 gap-2 sm:grid-cols-4">
                {CAPABILITIES.map(({ id, icon: Icon, label, ask, tile, ink }) => (
                  <button
                    key={id}
                    onClick={() => handleSend(admin.ask[ask])}
                    className="group flex min-w-0 flex-col items-center gap-2 overflow-hidden rounded-2xl border border-slate-200/80 bg-white px-0.5 py-3 text-center
                      transition-all duration-200 hover:-translate-y-0.5 hover:border-gov-blue/30 hover:shadow-[0_10px_24px_-14px_rgba(10,26,51,0.6)]"
                  >
                    <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${tile} transition-transform duration-200 group-hover:scale-105`}>
                      <Icon size={18} className={ink} aria-hidden="true" />
                    </span>
                    <span className="w-full hyphens-auto break-words text-[9.5px] font-semibold leading-tight tracking-tight text-slate-700 [overflow-wrap:anywhere]">
                      {admin.label[label]}
                    </span>
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
                    onClick={() => handleSend(admin.ask[key])}
                    className="group relative flex items-center gap-3 overflow-hidden rounded-2xl border border-slate-200/80 bg-[#f4f8ff] px-3.5 py-2.5 text-left
                      transition-all duration-200 hover:border-gov-blue/35 hover:bg-white hover:shadow-sm"
                  >
                    <span className="absolute inset-y-0 left-0 w-[3px] origin-top scale-y-0 bg-gov-saffron transition-transform duration-200 group-hover:scale-y-100" />
                    <span className="flex-1 text-[12.5px] font-medium text-slate-700">{admin.ask[key]}</span>
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

        {/* Navigation confirmation */}
        {pendingNav && (
          <NavConfirmBanner action={pendingNav.action} copy={copy} onConfirm={confirmNav} onCancel={cancelNav} />
        )}

        {/* Input bar */}
        <div className="relative flex-shrink-0 overflow-hidden border-t border-slate-100 bg-white px-3.5 pb-3 pt-3">
          <div className="pointer-events-none absolute -bottom-3 right-4 text-slate-900/[0.04]">
            <Landmark size={64} strokeWidth={1} />
          </div>

          <div className="relative flex items-end gap-1.5 rounded-[22px] border border-slate-200 bg-slate-50/80 py-1.5 pl-4 pr-1.5
            transition-all duration-200 focus-within:border-gov-blue/40 focus-within:bg-white focus-within:shadow-[0_0_0_4px_rgba(47,111,191,0.10)]">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={admin.placeholder}
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
              onClick={() => send(inputValue)}
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
        id="admin-chat-widget-bubble"
        onClick={() => setIsOpen(v => !v)}
        className={`fixed bottom-4 right-4 z-50 flex h-12 w-12 items-center sm:bottom-6 sm:right-6 sm:h-14 sm:w-14 justify-center rounded-full
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

export default AdminChatWidget;
