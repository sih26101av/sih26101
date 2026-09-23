/**
 * FILE: src/hooks/useVisitorCount.ts
 *
 * The visitor count GIGW asks a government site to display.
 *
 * There is no analytics backend behind this portal, so the number is counted
 * honestly in the browser — one increment per session — and the footer labels it
 * "Visits (this device)" rather than passing it off as a site-wide total.
 */

import { useEffect, useState } from 'react';

const LS_KEY = 'gov-visit-count';
const SESSION_KEY = 'gov-visit-counted';

export function useVisitorCount(): number {
  const [count, setCount] = useState(1);

  useEffect(() => {
    try {
      const stored = Number(window.localStorage.getItem(LS_KEY) ?? '0');
      const previous = Number.isFinite(stored) && stored > 0 ? stored : 0;

      // Count once per browser session, not once per route change.
      if (window.sessionStorage.getItem(SESSION_KEY)) {
        setCount(Math.max(previous, 1));
        return;
      }
      const next = previous + 1;
      window.localStorage.setItem(LS_KEY, String(next));
      window.sessionStorage.setItem(SESSION_KEY, '1');
      setCount(next);
    } catch {
      // Blocked storage — the footer just shows the opening value.
    }
  }, []);

  return count;
}
