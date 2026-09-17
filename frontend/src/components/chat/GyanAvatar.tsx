/**
 * FILE: src/components/chat/GyanAvatar.tsx
 *
 * Inline SVG artwork for the Gyan assistant — shared by the homepage and
 * dashboard chat widgets so both read as the same character.
 *
 * `GyanBot`   — the bot head on its own (header avatar, message bubbles).
 * `GyanHero`  — the bot flanked by chat bubbles and sparkles (welcome screen).
 */

import React from 'react';

/** The bot head. `tone="light"` draws a white-bodied bot for dark backgrounds. */
export const GyanBot: React.FC<{ size?: number; className?: string }> = ({ size = 40, className = '' }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 64 64"
    fill="none"
    className={className}
    role="img"
    aria-label="Gyan assistant"
  >
    {/* antenna */}
    <line x1="32" y1="6" x2="32" y2="13" stroke="#1e3a8a" strokeWidth="2.4" strokeLinecap="round" />
    <circle cx="32" cy="5" r="3" fill="#ff9933" />

    {/* head */}
    <rect x="9" y="13" width="46" height="38" rx="13" fill="#ffffff" stroke="#1e3a8a" strokeWidth="2.6" />

    {/* ears */}
    <rect x="3.5" y="26" width="6" height="12" rx="3" fill="#1e3a8a" />
    <rect x="54.5" y="26" width="6" height="12" rx="3" fill="#1e3a8a" />

    {/* visor */}
    <rect x="15" y="20" width="34" height="24" rx="10" fill="#12407f" />

    {/* eyes */}
    <circle cx="25" cy="30" r="3.6" fill="#ffffff" />
    <circle cx="39" cy="30" r="3.6" fill="#ffffff" />

    {/* smile */}
    <path d="M25 37.5c2.2 2.4 4.6 3.6 7 3.6s4.8-1.2 7-3.6" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" fill="none" />
  </svg>
);

/** Welcome-screen illustration: bot, chat bubbles, sparkles. */
export const GyanHero: React.FC<{ className?: string }> = ({ className = '' }) => (
  <svg
    width="228"
    height="104"
    viewBox="0 0 228 104"
    fill="none"
    className={className}
    aria-hidden="true"
  >
    {/* left bubble */}
    <g opacity="0.9">
      <rect x="6" y="30" width="52" height="30" rx="12" fill="#dbeafe" />
      <path d="M22 60l-3 7 10-7z" fill="#dbeafe" />
      <circle cx="23" cy="45" r="3" fill="#60a5fa" />
      <circle cx="32" cy="45" r="3" fill="#60a5fa" />
      <circle cx="41" cy="45" r="3" fill="#60a5fa" />
    </g>

    {/* right bubble */}
    <g opacity="0.9">
      <rect x="170" y="30" width="52" height="30" rx="12" fill="#ffedd5" />
      <path d="M206 60l3 7-10-7z" fill="#ffedd5" />
      <circle cx="187" cy="45" r="3" fill="#fb923c" />
      <circle cx="196" cy="45" r="3" fill="#fb923c" />
      <circle cx="205" cy="45" r="3" fill="#fb923c" />
    </g>

    {/* halo */}
    <circle cx="114" cy="54" r="42" fill="#eff6ff" />

    {/* bot */}
    <g transform="translate(82, 16)">
      <line x1="32" y1="4" x2="32" y2="12" stroke="#1e3a8a" strokeWidth="2.6" strokeLinecap="round" />
      <circle cx="32" cy="3" r="3.4" fill="#ff9933" />
      <rect x="8" y="12" width="48" height="40" rx="14" fill="#ffffff" stroke="#1e3a8a" strokeWidth="2.8" />
      <rect x="2" y="26" width="6.5" height="13" rx="3.2" fill="#1e3a8a" />
      <rect x="55.5" y="26" width="6.5" height="13" rx="3.2" fill="#1e3a8a" />
      <rect x="14" y="19" width="36" height="26" rx="11" fill="#12407f" />
      <circle cx="24.5" cy="30" r="3.9" fill="#ffffff" />
      <circle cx="39.5" cy="30" r="3.9" fill="#ffffff" />
      <path d="M24.5 38c2.4 2.6 5 3.9 7.5 3.9s5.1-1.3 7.5-3.9" stroke="#ffffff" strokeWidth="2.4" strokeLinecap="round" fill="none" />
      {/* chest badge — a small bar chart, echoing the statistical mission */}
      <rect x="22" y="54" width="20" height="16" rx="5" fill="#2563eb" />
      <rect x="26" y="62" width="2.6" height="4" rx="1.3" fill="#ffffff" />
      <rect x="30.7" y="59" width="2.6" height="7" rx="1.3" fill="#ffffff" />
      <rect x="35.4" y="56.5" width="2.6" height="9.5" rx="1.3" fill="#ffffff" />
    </g>

    {/* sparkles */}
    <path d="M72 22l1.8 4.2 4.2 1.8-4.2 1.8L72 34l-1.8-4.2-4.2-1.8 4.2-1.8z" fill="#60a5fa" />
    <path d="M158 18l1.5 3.5 3.5 1.5-3.5 1.5-1.5 3.5-1.5-3.5-3.5-1.5 3.5-1.5z" fill="#fbbf24" />
    <path d="M150 62l1.2 2.8 2.8 1.2-2.8 1.2-1.2 2.8-1.2-2.8-2.8-1.2 2.8-1.2z" fill="#fb923c" />
  </svg>
);

export default GyanBot;
