/**
 * FILE: src/components/gov/GovUtilityBar.tsx
 *
 * The statutory strip that sits above the masthead on every page of the portal.
 *
 * GIGW 3.0 asks a Government of India site to carry, at the very top and in a
 * consistent position on every page:
 *   · the "भारत सरकार | Government of India" identifier
 *   · a "Skip to main content" link (the first focusable element on the page)
 *   · Screen Reader Access
 *   · a text-size control (A‑ / A / A+)
 *   · a high-contrast toggle
 *   · a language switch
 *
 * State for the last four lives in `context/AccessibilityContext.tsx` so the
 * setting follows the user from the landing page into the dashboards.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Accessibility, Contrast, Moon, Square, Sun } from 'lucide-react';
import { useAccessibility } from '../../context/AccessibilityContext';
import { useTheme } from '../../hooks/useTheme';
import type { ScreenReader } from '../../hooks/useScreenReader';

interface GovUtilityBarProps {
  /** Anchor the skip link + the screen reader point at. */
  mainId?: string;
  /** Pass a `useScreenReader(...)` instance to show the read-aloud toggle. */
  screenReader?: ScreenReader;
  /** Hide the dark/light control where the page already offers one. */
  showTheme?: boolean;
  className?: string;
}

const LABELS = {
  en: {
    skip: 'Skip to main content',
    sr: 'Screen Reader Access',
    read: 'Listen to this page',
    stop: 'Stop reading',
    decrease: 'Decrease text size',
    normal: 'Reset text size',
    increase: 'Increase text size',
    contrast: 'High contrast',
    goi: 'Government of India',
  },
  hi: {
    skip: 'मुख्य सामग्री पर जाएं',
    sr: 'स्क्रीन रीडर एक्सेस',
    read: 'यह पृष्ठ सुनें',
    stop: 'पढ़ना बंद करें',
    decrease: 'पाठ का आकार घटाएं',
    normal: 'सामान्य आकार',
    increase: 'पाठ का आकार बढ़ाएं',
    contrast: 'उच्च कंट्रास्ट',
    goi: 'भारत सरकार',
  },
} as const;

const Divider = () => <span className="hidden h-3.5 w-px bg-white/25 sm:inline-block" aria-hidden="true" />;

const GovUtilityBar: React.FC<GovUtilityBarProps> = ({
  mainId = 'main-content',
  screenReader,
  showTheme = true,
  className = '',
}) => {
  const {
    textPercent, increaseText, decreaseText, resetText, canIncrease, canDecrease,
    highContrast, toggleHighContrast, lang, setLang,
  } = useAccessibility();
  const { theme, toggleTheme } = useTheme();
  const t = LABELS[lang];

  const pill = 'rounded px-1.5 py-0.5 font-semibold transition-colors hover:bg-white/15 hover:text-white disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent';

  return (
    <div className={`gov-utility-bar relative z-30 bg-gov-ink text-[11.5px] text-white/80 print:hidden ${className}`}>
      <div className="mx-auto flex h-9 max-w-[1440px] items-center justify-between gap-3 px-3 md:px-6">
        {/* Identity — required wording, Hindi first. */}
        <p className="flex min-w-0 items-center gap-2 font-semibold">
          <span lang="hi" className="whitespace-nowrap">भारत सरकार</span>
          <span className="h-3.5 w-px bg-white/25" aria-hidden="true" />
          <span className="hidden whitespace-nowrap tracking-wide sm:inline">GOVERNMENT OF INDIA</span>
          <span className="tracking-wide sm:hidden">GOI</span>
        </p>

        <div className="flex flex-shrink-0 items-center gap-1.5 sm:gap-2.5">
          <a href={`#${mainId}`} className="hidden hover:text-white hover:underline md:inline">{t.skip}</a>
          <Divider />

          <Link to="/policy/screen-reader-access" className="hidden hover:text-white hover:underline lg:inline">
            {t.sr}
          </Link>

          {screenReader?.supported && (
            <button
              type="button"
              onClick={() => screenReader.toggle(`#${mainId}`)}
              aria-pressed={screenReader.speaking}
              title={screenReader.speaking ? t.stop : t.read}
              className={`hidden items-center gap-1.5 rounded-full px-2.5 py-0.5 font-semibold transition-colors sm:flex ${
                screenReader.speaking ? 'bg-gov-saffron text-gov-ink' : 'hover:bg-white/15 hover:text-white'
              }`}
            >
              {screenReader.speaking
                ? <><Square size={10} className="fill-current" aria-hidden="true" /> {t.stop}</>
                : <><Accessibility size={13} aria-hidden="true" /> {t.read}</>}
            </button>
          )}
          <Divider />

          {/* Text size — GIGW's A- / A / A+ control. */}
          <div
            className="flex items-center gap-0.5"
            role="group"
            aria-label={`${lang === 'hi' ? 'पाठ का आकार' : 'Text size'} — ${textPercent}%`}
          >
            <button type="button" onClick={decreaseText} disabled={!canDecrease} className={pill} title={t.decrease} aria-label={t.decrease}>
              A<span aria-hidden="true">&minus;</span>
            </button>
            <button type="button" onClick={resetText} className={pill} title={`${t.normal} (${textPercent}%)`} aria-label={t.normal}>
              A
            </button>
            <button type="button" onClick={increaseText} disabled={!canIncrease} className={pill} title={t.increase} aria-label={t.increase}>
              A<span aria-hidden="true">+</span>
            </button>
          </div>
          <Divider />

          <button
            type="button"
            onClick={toggleHighContrast}
            aria-pressed={highContrast}
            title={t.contrast}
            aria-label={t.contrast}
            className={`rounded-full p-1 transition-colors ${highContrast ? 'bg-gov-saffron text-gov-ink' : 'hover:bg-white/15 hover:text-white'}`}
          >
            <Contrast size={14} aria-hidden="true" />
          </button>

          {showTheme && (
            <button
              type="button"
              onClick={toggleTheme}
              className="rounded-full p-1 transition-colors hover:bg-white/15 hover:text-white"
              aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              {theme === 'dark' ? <Sun size={14} aria-hidden="true" /> : <Moon size={14} aria-hidden="true" />}
            </button>
          )}

          <div className="flex items-center rounded-full bg-white/10 p-0.5" role="group" aria-label="Site language">
            <button
              type="button"
              onClick={() => { screenReader?.stop(); setLang('en'); }}
              aria-pressed={lang === 'en'}
              className={`rounded-full px-2 py-0.5 font-bold transition-all ${lang === 'en' ? 'bg-white text-gov-ink' : 'hover:text-white'}`}
            >
              EN
            </button>
            <button
              type="button"
              onClick={() => { screenReader?.stop(); setLang('hi'); }}
              aria-pressed={lang === 'hi'}
              lang="hi"
              className={`rounded-full px-2 py-0.5 font-bold transition-all ${lang === 'hi' ? 'bg-white text-gov-ink' : 'hover:text-white'}`}
            >
              हिंदी
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GovUtilityBar;
