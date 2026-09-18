/**
 * FILE: src/components/chat/LanguageMenu.tsx
 *
 * The language control in Gyan's header — one component for both widgets, so
 * the dashboard and the landing page can never offer different languages.
 * The list comes from `i18n/chatLanguages`, which mirrors the backend's reply
 * template catalogue.
 *
 * Archit Shukla | SIH 2026
 */

import React, { useEffect, useRef, useState } from 'react';
import { Check, ChevronDown, Languages } from 'lucide-react';
import type { ChatLanguage } from '../../services/chatApi';
import { CHAT_LANGUAGES, chatCopy, languageOption } from '../../i18n/chatLanguages';

interface LanguageMenuProps {
  value: ChatLanguage;
  onChange: (lang: ChatLanguage) => void;
}

const LanguageMenu: React.FC<LanguageMenuProps> = ({ value, onChange }) => {
  const [open, setOpen] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const active = languageOption(value);
  const copy = chatCopy(value);

  // Esc closes the menu — it sits inside a dialog, so a stray open menu would
  // otherwise swallow the next click.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);

  // Bring the current language into view when the list opens.
  useEffect(() => {
    if (!open) return;
    listRef.current?.querySelector('[data-active="true"]')
      ?.scrollIntoView({ block: 'nearest' });
  }, [open]);

  return (
    <div className="relative flex-shrink-0">
      <button
        onClick={() => setOpen(o => !o)}
        aria-haspopup="menu"
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

      {open && (
        <>
          <div className="fixed inset-0 z-0" onClick={() => setOpen(false)} aria-hidden="true" />
          <div
            role="menu"
            ref={listRef}
            className="animate-scale-in custom-scrollbar absolute right-0 z-10 mt-2 max-h-[248px] w-[188px]
              overflow-y-auto rounded-2xl border border-slate-200/90 bg-white/95 p-1.5 backdrop-blur-xl"
            style={{ boxShadow: '0 18px 44px -12px rgba(10,26,51,0.38)' }}
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
                  onClick={() => { onChange(opt.code); setOpen(false); }}
                  className={`flex w-full items-center gap-2 rounded-xl px-2.5 py-1.5 text-left transition-colors
                    ${isActive ? 'bg-gov-blue/10' : 'hover:bg-slate-100'}`}
                >
                  <span className={`flex h-6 w-8 flex-shrink-0 items-center justify-center rounded-md text-[9.5px] font-bold tracking-wide
                    ${isActive ? 'bg-gov-navy text-white' : 'bg-slate-100 text-slate-500'}`}>
                    {opt.pill}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className={`block truncate text-[12.5px] font-semibold leading-tight
                      ${isActive ? 'text-gov-navy' : 'text-slate-700'}`}>
                      {opt.native}
                    </span>
                    <span className="block truncate text-[10px] leading-tight text-slate-400">{opt.english}</span>
                  </span>
                  {isActive && <Check size={13} className="flex-shrink-0 text-gov-blue" />}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageMenu;
