/**
 * FILE: src/components/chat/LanguageMenu.tsx
 *
 * The language control in Gyan's header — one component for both widgets, so
 * the dashboard and the landing page can never offer different languages.
 * The list comes from `i18n/chatLanguages`, which mirrors the backend's reply
 * template catalogue.
 *
 * When `chatPanelRef` is provided the picker renders as a full-panel overlay
 * inside the chat widget (via React.createPortal into the panel element).
 * When omitted it falls back to the standard small dropdown.
 *
 * Archit Shukla | SIH 2026
 */

import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Check, ChevronDown, Languages, X } from 'lucide-react';
import type { ChatLanguage } from '../../services/chatApi';
import { CHAT_LANGUAGES, chatCopy, languageOption } from '../../i18n/chatLanguages';

interface LanguageMenuProps {
  value: ChatLanguage;
  onChange: (lang: ChatLanguage) => void;
  /**
   * Pass the chat panel's root HTMLElement (the fixed widget div) to enable
   * full-panel overlay mode. The picker will be portaled into that element
   * so it fills the panel exactly, respecting its border-radius & overflow.
   */
  chatPanelRef?: React.RefObject<HTMLElement | null>;
}

const LanguageMenu: React.FC<LanguageMenuProps> = ({ value, onChange, chatPanelRef }) => {
  const [open, setOpen] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const active  = languageOption(value);
  const copy    = chatCopy(value);

  const usePanelMode = chatPanelRef != null;

  // Esc closes
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);

  // Scroll selected language into view
  useEffect(() => {
    if (!open) return;
    setTimeout(() => {
      listRef.current?.querySelector('[data-active="true"]')
        ?.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }, 50);
  }, [open]);

  const handleSelect = (code: ChatLanguage) => {
    onChange(code);
    setOpen(false);
  };

  // ── Full-panel overlay (portaled into chat widget) ───────────────────────
  const panelOverlay = (
    <div
      className="absolute inset-0 z-50 flex flex-col animate-fade-in"
      style={{
        borderRadius: 'inherit',
        background: 'rgba(255,255,255,0.97)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
      }}
      aria-modal="true"
      role="dialog"
      aria-label={copy.languageLabel}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gov-blue/10">
            <Languages size={16} className="text-gov-blue" />
          </div>
          <div>
            <p className="text-[14px] font-bold text-slate-800">{copy.languageLabel}</p>
            <p className="text-[10px] text-slate-400">Choose your preferred language</p>
          </div>
        </div>
        <button
          onClick={() => setOpen(false)}
          className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 transition-colors text-slate-500 hover:text-slate-700"
          aria-label="Close"
        >
          <X size={15} />
        </button>
      </div>

      {/* Language list */}
      <div
        ref={listRef}
        className="flex-1 overflow-y-auto px-3 py-3 space-y-1.5"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#cbd5e1 transparent' }}
      >
        {CHAT_LANGUAGES.map(opt => {
          const isActive = opt.code === value;
          return (
            <button
              key={opt.code}
              role="menuitemradio"
              aria-checked={isActive}
              data-active={isActive}
              onClick={() => handleSelect(opt.code)}
              className={`flex w-full items-center gap-3.5 rounded-2xl px-4 py-3.5 text-left transition-all duration-150
                ${isActive
                  ? 'bg-gov-blue/10 ring-2 ring-gov-blue/25'
                  : 'hover:bg-slate-50 active:bg-slate-100'
                }`}
            >
              {/* Pill */}
              <span className={`flex h-11 w-14 flex-shrink-0 items-center justify-center rounded-xl text-[11px] font-bold tracking-widest
                ${isActive ? 'bg-gov-navy text-white shadow-md shadow-gov-navy/20' : 'bg-slate-100 text-slate-500'}`}>
                {opt.pill}
              </span>

              {/* Names */}
              <span className="flex-1 min-w-0">
                <span
                  className={`block text-[15px] font-semibold leading-snug
                    ${isActive ? 'text-gov-navy' : 'text-slate-800'}`}
                  lang={opt.code === 'hi_latn' ? 'hi' : opt.code}
                >
                  {opt.native}
                </span>
                <span className={`block text-[11px] mt-0.5 ${isActive ? 'text-gov-blue/70' : 'text-slate-400'}`}>
                  {opt.english}
                </span>
              </span>

              {/* Check */}
              {isActive ? (
                <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gov-blue shadow-md shadow-gov-blue/30">
                  <Check size={14} className="text-white" strokeWidth={3} />
                </span>
              ) : (
                <span className="h-7 w-7 flex-shrink-0 rounded-full border-2 border-slate-200" />
              )}
            </button>
          );
        })}
      </div>

      {/* Footer hint */}
      <div className="px-5 py-3 border-t border-slate-100 text-center flex-shrink-0">
        <p className="text-[10px] text-slate-400 leading-relaxed">
          Gyan will reply in your chosen language
        </p>
      </div>
    </div>
  );

  // ── Small dropdown fallback (no panel container) ─────────────────────────
  const dropdown = open && !usePanelMode && (
    <>
      <div className="fixed inset-0 z-0" onClick={() => setOpen(false)} aria-hidden="true" />
      <div
        role="menu"
        ref={listRef}
        className="animate-scale-in absolute right-0 z-10 mt-2 max-h-[300px] w-[220px]
          overflow-y-auto rounded-2xl border border-slate-200/90 bg-white/95 p-1.5 backdrop-blur-xl"
        style={{
          boxShadow: '0 18px 44px -12px rgba(10,26,51,0.38)',
          scrollbarWidth: 'thin',
          scrollbarColor: '#cbd5e1 transparent',
        }}
      >
        <p className="px-2.5 pb-1.5 pt-1 text-[9.5px] font-bold uppercase tracking-[0.12em] text-slate-400">
          {copy.languageLabel}
        </p>
        {CHAT_LANGUAGES.map(opt => {
          const isActive = opt.code === value;
          return (
            <button
              key={opt.code}
              role="menuitemradio"
              aria-checked={isActive}
              data-active={isActive}
              onClick={() => handleSelect(opt.code)}
              className={`flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left transition-colors
                ${isActive ? 'bg-gov-blue/10' : 'hover:bg-slate-100'}`}
            >
              <span className={`flex h-7 w-9 flex-shrink-0 items-center justify-center rounded-md text-[9.5px] font-bold tracking-wide
                ${isActive ? 'bg-gov-navy text-white' : 'bg-slate-100 text-slate-500'}`}>
                {opt.pill}
              </span>
              <span className="min-w-0 flex-1">
                <span className={`block text-[13px] font-semibold leading-snug ${isActive ? 'text-gov-navy' : 'text-slate-700'}`}
                  lang={opt.code === 'hi_latn' ? 'hi' : opt.code}>
                  {opt.native}
                </span>
                <span className="block text-[10.5px] leading-tight text-slate-400">{opt.english}</span>
              </span>
              {isActive && <Check size={13} className="flex-shrink-0 text-gov-blue" />}
            </button>
          );
        })}
      </div>
    </>
  );

  return (
    <>
      {/* Trigger button — always shown in the header */}
      <div className="relative flex-shrink-0">
        <button
          onClick={() => setOpen(o => !o)}
          aria-haspopup="dialog"
          aria-expanded={open}
          aria-label={`${copy.languageLabel} — ${active.english}`}
          title={copy.languageLabel}
          className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1.5 text-[11.5px] font-bold text-white
            backdrop-blur-sm transition-all duration-200
            ${open
              ? 'border-white/50 bg-white/25 shadow-inner'
              : 'border-white/25 bg-white/10 hover:border-white/40 hover:bg-white/20'
            }`}
        >
          <Languages size={13} className="opacity-90" />
          <span className="tracking-wide">{active.pill}</span>
          <ChevronDown size={12} className={`opacity-80 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
        </button>

        {dropdown}
      </div>

      {/* Portal the full-panel overlay into the chat widget div */}
      {usePanelMode && open && chatPanelRef.current &&
        createPortal(panelOverlay, chatPanelRef.current)
      }
    </>
  );
};

export default LanguageMenu;
