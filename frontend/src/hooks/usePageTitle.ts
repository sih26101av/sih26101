/**
 * FILE: src/hooks/usePageTitle.ts
 *
 * GIGW 3.0 asks every page to carry a unique, descriptive title so that a
 * screen reader announces where the user has landed and a bookmark is legible.
 * A single-page app has to set it per route, which is what this does.
 */

import { useEffect } from 'react';

export const SITE_TITLE = 'KarmaSkill · MoSPI Skill Intelligence Platform';

export function usePageTitle(title?: string, description?: string) {
  useEffect(() => {
    document.title = title ? `${title} | ${SITE_TITLE}` : SITE_TITLE;
    if (description) {
      let meta = document.querySelector('meta[name="description"]');
      if (!meta) {
        meta = document.createElement('meta');
        meta.setAttribute('name', 'description');
        document.head.appendChild(meta);
      }
      meta.setAttribute('content', description);
    }
  }, [title, description]);
}
