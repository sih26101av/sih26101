/**
 * FILE: src/components/gov/GovFooter.tsx
 *
 * The statutory footer every Government of India site has to carry (GIGW 3.0,
 * "Mandatory elements of a website"):
 *   · links to the policy pages — Terms, Privacy, Copyright, Hyperlinking,
 *     Disclaimer, Accessibility Statement, Help, Feedback, Sitemap
 *   · who owns and updates the content
 *   · the Web Information Manager (the named officer responsible for the site)
 *   · when the content was last updated
 *   · a visitor count
 *   · the accessibility / standards conformance claim
 *
 * `variant="full"` is the public-page footer (landing page, policy pages); the
 * optional `brand` slot becomes its first column, which is how the landing page
 * keeps its blurb and quick links without duplicating this markup.
 * `variant="compact"` drops the column block for the dashboard shells, where the
 * same statutory lines still have to appear but must not dominate a working
 * screen.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import { POLICY_LINKS } from '../../content/policies';
import { useVisitorCount } from '../../hooks/useVisitorCount';

/** The related national portals every MoSPI property links out to. */
const RELATED_PORTALS: [string, string][] = [
  ['iGOT Karmayogi', 'https://igotkarmayogi.gov.in'],
  ['MoSPI', 'https://www.mospi.gov.in'],
  ['National Portal of India', 'https://www.india.gov.in'],
  ['data.gov.in', 'https://data.gov.in'],
  ['MyGov', 'https://www.mygov.in'],
  ['DARPG', 'https://darpg.gov.in'],
];

export const LAST_UPDATED = (() => {
  const iso = typeof __BUILD_DATE__ === 'string' ? __BUILD_DATE__ : new Date().toISOString();
  return new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
})();

/** Marks a link that leaves the portal — GIGW requires the destination be obvious. */
export const ExternalGovLink: React.FC<{ href: string; children: React.ReactNode; className?: string }> = ({
  href, children, className = '',
}) => (
  <a
    href={href}
    target="_blank"
    rel="noopener noreferrer"
    className={`inline-flex items-center gap-1.5 hover:text-gov-saffron hover:underline ${className}`}
  >
    {children}
    <ExternalLink size={11} className="opacity-70" aria-hidden="true" />
    <span className="sr-only">(external site, opens in a new window)</span>
  </a>
);

interface GovFooterProps {
  variant?: 'full' | 'compact';
  /** First column of the full footer — brand blurb, quick links, anything. */
  brand?: React.ReactNode;
  /** Anchor id, so an in-page "Contact" nav link can target the footer. */
  id?: string;
  className?: string;
}

const GovFooter: React.FC<GovFooterProps> = ({ variant = 'full', brand, id, className = '' }) => {
  const visits = useVisitorCount();

  return (
    <footer id={id} role="contentinfo" className={`mt-auto scroll-mt-12 bg-gov-ink text-white/70 print:bg-white print:text-black ${className}`}>
      <div className="tricolor-strip" />

      {variant === 'full' && (
        <div className={`mx-auto grid max-w-[1440px] grid-cols-1 gap-8 px-4 py-10 sm:grid-cols-2 md:px-6 ${brand ? 'lg:grid-cols-4' : 'lg:grid-cols-3'}`}>
          {brand}

          <nav aria-labelledby="footer-policies">
            <h2 id="footer-policies" className="mb-3.5 text-[12px] font-bold uppercase tracking-[0.16em] text-white">
              Website Policies
            </h2>
            <ul className="grid grid-cols-1 gap-2 text-[13px] sm:grid-cols-2 lg:grid-cols-1">
              {/* Every one of these has a page — GIGW requires them all. */}
              {POLICY_LINKS.map(({ slug, title }) => (
                <li key={slug}>
                  <Link to={`/policy/${slug}`} className="hover:text-gov-saffron hover:underline">{title}</Link>
                </li>
              ))}
            </ul>
          </nav>

          <nav aria-labelledby="footer-portals">
            <h2 id="footer-portals" className="mb-3.5 text-[12px] font-bold uppercase tracking-[0.16em] text-white">
              Related Portals
            </h2>
            <ul className="space-y-2 text-[13px]">
              {RELATED_PORTALS.map(([label, href]) => (
                <li key={label}><ExternalGovLink href={href}>{label}</ExternalGovLink></li>
              ))}
            </ul>
          </nav>

          <section aria-labelledby="footer-wim">
            <h2 id="footer-wim" className="mb-3.5 text-[12px] font-bold uppercase tracking-[0.16em] text-white">
              Web Information Manager
            </h2>
            <address className="space-y-1.5 text-[13px] not-italic leading-relaxed">
              <p className="font-semibold text-white/90">Director (Training Division)</p>
              <p>National Statistical Office, Ministry of Statistics &amp; Programme Implementation</p>
              <p>Sardar Patel Bhavan, Sansad Marg, New Delhi&nbsp;&minus;&nbsp;110001</p>
              <p>
                Queries about this portal go to your division&apos;s training nodal officer, or use the{' '}
                <Link to="/policy/feedback" className="font-semibold text-gov-saffron hover:underline">feedback form</Link>.
              </p>
            </address>
          </section>
        </div>
      )}

      {/* Statutory lines — present on every page, both variants. */}
      <div className={`border-white/10 ${variant === 'full' ? 'border-t' : ''}`}>
        <div className="mx-auto max-w-[1440px] space-y-2.5 px-4 py-4 text-[11.5px] leading-relaxed md:px-6">
          {variant === 'compact' && (
            <nav aria-label="Website policies" className="flex flex-wrap items-center gap-x-4 gap-y-1.5">
              {POLICY_LINKS.map(({ slug, title }) => (
                <Link key={slug} to={`/policy/${slug}`} className="hover:text-white hover:underline">{title}</Link>
              ))}
            </nav>
          )}

          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <p>
              Content owned, updated and maintained by the{' '}
              <span className="text-white/90">Ministry of Statistics &amp; Programme Implementation, Government of India</span>.
              Built on the iGOT&nbsp;Karmayogi platform under Mission Karmayogi.
            </p>
            <p className="flex flex-wrap items-center gap-x-3 gap-y-1 text-white/55 md:justify-end md:text-right">
              <span>Last updated: <span className="font-semibold text-white/80">{LAST_UPDATED}</span></span>
              <span className="hidden h-3 w-px bg-white/20 md:inline-block" aria-hidden="true" />
              <span>Visits (this device): <span className="font-semibold text-white/80">{visits.toLocaleString('en-IN')}</span></span>
            </p>
          </div>

          <div className="flex flex-col gap-1.5 border-t border-white/10 pt-2.5 text-white/55 md:flex-row md:items-center md:justify-between">
            <p>© {new Date().getFullYear()} Ministry of Statistics and Programme Implementation · Government of India</p>
            <p className="flex flex-wrap items-center gap-x-3 gap-y-1">
              <Link to="/policy/accessibility-statement" className="hover:text-white hover:underline">
                Conforms to WCAG&nbsp;2.1 level&nbsp;AA · GIGW&nbsp;3.0
              </Link>
              <span className="hidden h-3 w-px bg-white/20 md:inline-block" aria-hidden="true" />
              <span>Prototype · Smart India Hackathon 2026</span>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default GovFooter;
