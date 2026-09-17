/**
 * FILE: src/hooks/useScreenReader.ts
 *
 * GIGW-style "Screen Reader Access": reads the page's visible prose aloud with the
 * browser's SpeechSynthesis API, in the language the page is currently set to.
 *
 * It is deliberately self-contained — no external service, so it works inside an
 * air-gapped intranet deployment like the rest of the platform.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

/** Elements whose text is worth reading, in document order. */
const READABLE = 'h1, h2, h3, h4, h5, p, li, blockquote, figcaption, dd, dt';

/** Speech engines truncate very long utterances, so prose is split on sentences. */
const MAX_CHUNK = 220;

function isHidden(el: Element): boolean {
  if (el.getAttribute('aria-hidden') === 'true') return true;
  if (el.classList.contains('sr-only')) return true;
  const style = window.getComputedStyle(el);
  return style.display === 'none' || style.visibility === 'hidden';
}

/** Collect visible prose under `root`, skipping nested duplicates and hidden nodes. */
function extractReadableText(root: Element): string {
  const seen: string[] = [];
  root.querySelectorAll(READABLE).forEach((el) => {
    if (isHidden(el)) return;
    // Skip a node whose ancestor we already captured (avoids reading text twice).
    if (el.parentElement?.closest(READABLE)) return;
    const text = (el.textContent ?? '').replace(/\s+/g, ' ').trim();
    if (text.length > 1) seen.push(text);
  });
  return seen.join('. ');
}

function chunkText(text: string): string[] {
  const sentences = text.split(/(?<=[.!?।])\s+/);
  const chunks: string[] = [];
  let current = '';
  for (const s of sentences) {
    if ((current + ' ' + s).trim().length > MAX_CHUNK) {
      if (current) chunks.push(current.trim());
      current = s;
    } else {
      current = `${current} ${s}`;
    }
  }
  if (current.trim()) chunks.push(current.trim());
  return chunks;
}

export interface ScreenReader {
  /** False when the browser has no SpeechSynthesis support — hide the control. */
  supported: boolean;
  speaking: boolean;
  /** Read everything inside the element matching `selector` (e.g. '#main'). */
  read: (selector: string) => void;
  stop: () => void;
  /** Read if idle, stop if speaking. */
  toggle: (selector: string) => void;
}

export function useScreenReader(lang: 'en' | 'hi'): ScreenReader {
  const [speaking, setSpeaking] = useState(false);
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window;
  const speakingRef = useRef(false);

  const stop = useCallback(() => {
    if (!supported) return;
    window.speechSynthesis.cancel();
    speakingRef.current = false;
    setSpeaking(false);
  }, [supported]);

  const read = useCallback((selector: string) => {
    if (!supported) return;
    window.speechSynthesis.cancel();

    const root = document.querySelector(selector);
    if (!root) return;

    const chunks = chunkText(extractReadableText(root));
    if (chunks.length === 0) return;

    chunks.forEach((chunk, i) => {
      const utterance = new SpeechSynthesisUtterance(chunk);
      utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
      utterance.rate = 0.95;
      if (i === chunks.length - 1) {
        utterance.onend = () => { speakingRef.current = false; setSpeaking(false); };
      }
      utterance.onerror = () => { speakingRef.current = false; setSpeaking(false); };
      window.speechSynthesis.speak(utterance);
    });

    speakingRef.current = true;
    setSpeaking(true);
  }, [lang, supported]);

  const toggle = useCallback((selector: string) => {
    if (speakingRef.current) stop();
    else read(selector);
  }, [read, stop]);

  // Never leave speech running after the page unmounts.
  useEffect(() => () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }, []);

  return { supported, speaking, read, stop, toggle };
}
