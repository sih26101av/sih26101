/**
 * FILE: src/context/AccessibilityContext.tsx
 *
 * GIGW 3.0 accessibility preferences, shared by every page of the portal.
 *
 * Guidelines for Indian Government Websites require a visible, persistent way to
 * (a) resize text, (b) switch to a high-contrast presentation and (c) switch the
 * site language. Those three controls live in the utility strip at the very top
 * of every page (`components/gov/GovUtilityBar.tsx`) and read their state here.
 *
 * How the preferences are applied
 * ───────────────────────────────
 *  - text size : `--gov-zoom` on <html>; `index.css` turns it into `zoom` on
 *                <body>. Most type in this app is authored in px, so scaling the
 *                root font-size alone would do nothing — zoom scales everything.
 *                Viewport-height utilities are divided back out in `index.css`.
 *  - contrast  : `.hc` class on <html>; `index.css` holds the override block.
 *  - language  : `lang` attribute on <html> (needed by screen readers and by the
 *                Devanagari font stack), plus the `lang` value consumers read.
 *
 * All three persist in localStorage so a return visit keeps the user's setting.
 */

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

export type SiteLang = 'en' | 'hi';

/** Zoom applied to <body> per step. Index 2 (100%) is the default. */
export const TEXT_STEPS = [0.9, 0.95, 1, 1.075, 1.15] as const;
const DEFAULT_STEP = 2;
const MIN_STEP = 0;
const MAX_STEP = TEXT_STEPS.length - 1;

const LS_TEXT = 'gov-text-step';
const LS_CONTRAST = 'gov-high-contrast';
const LS_LANG = 'gov-lang';

interface AccessibilityContextType {
  /** 0…4; 2 is the 100% baseline. */
  textStep: number;
  /** e.g. 115 — shown in the A‑/A/A+ control as a percentage. */
  textPercent: number;
  increaseText: () => void;
  decreaseText: () => void;
  resetText: () => void;
  canIncrease: boolean;
  canDecrease: boolean;

  highContrast: boolean;
  toggleHighContrast: () => void;

  lang: SiteLang;
  setLang: (lang: SiteLang) => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

function readStored<T>(key: string, parse: (raw: string) => T | null, fallback: T): T {
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = window.localStorage.getItem(key);
    if (raw === null) return fallback;
    const parsed = parse(raw);
    return parsed === null ? fallback : parsed;
  } catch {
    // Private mode / blocked storage — preferences just don't persist.
    return fallback;
  }
}

function persist(key: string, value: string) {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    /* ignore */
  }
}

export const AccessibilityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [textStep, setTextStep] = useState(() =>
    readStored(LS_TEXT, (raw) => {
      const n = Number(raw);
      return Number.isInteger(n) && n >= MIN_STEP && n <= MAX_STEP ? n : null;
    }, DEFAULT_STEP)
  );

  const [highContrast, setHighContrast] = useState(() =>
    readStored(LS_CONTRAST, (raw) => (raw === '1' ? true : raw === '0' ? false : null), false)
  );

  const [lang, setLangState] = useState<SiteLang>(() =>
    readStored<SiteLang>(LS_LANG, (raw) => (raw === 'hi' || raw === 'en' ? raw : null), 'en')
  );

  useEffect(() => {
    document.documentElement.style.setProperty('--gov-zoom', String(TEXT_STEPS[textStep]));
    persist(LS_TEXT, String(textStep));
  }, [textStep]);

  useEffect(() => {
    document.documentElement.classList.toggle('hc', highContrast);
    persist(LS_CONTRAST, highContrast ? '1' : '0');
  }, [highContrast]);

  useEffect(() => {
    document.documentElement.lang = lang;
    persist(LS_LANG, lang);
  }, [lang]);

  const setLang = useCallback((next: SiteLang) => setLangState(next), []);

  const value = useMemo<AccessibilityContextType>(() => ({
    textStep,
    textPercent: Math.round(TEXT_STEPS[textStep] * 100),
    increaseText: () => setTextStep((s) => Math.min(MAX_STEP, s + 1)),
    decreaseText: () => setTextStep((s) => Math.max(MIN_STEP, s - 1)),
    resetText: () => setTextStep(DEFAULT_STEP),
    canIncrease: textStep < MAX_STEP,
    canDecrease: textStep > MIN_STEP,
    highContrast,
    toggleHighContrast: () => setHighContrast((v) => !v),
    lang,
    setLang,
  }), [textStep, highContrast, lang, setLang]);

  return <AccessibilityContext.Provider value={value}>{children}</AccessibilityContext.Provider>;
};

export function useAccessibility(): AccessibilityContextType {
  const ctx = useContext(AccessibilityContext);
  if (!ctx) throw new Error('useAccessibility must be used within an AccessibilityProvider');
  return ctx;
}
