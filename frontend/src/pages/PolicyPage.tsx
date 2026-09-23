/**
 * FILE: src/pages/PolicyPage.tsx
 *
 * Renders any one of the statutory pages held in `content/policies.tsx` at
 * `/policy/:slug`. One route covers all of them so the footer, the sitemap and
 * the accessibility bar can link to a page that is guaranteed to exist.
 *
 * The rendering is deliberately plain: a readable measure, ordered headings and
 * a print stylesheet. These are pages people read once, or print and file.
 */

import React from 'react';
import { Link, Navigate, useParams } from 'react-router-dom';
import { ChevronRight, Printer } from 'lucide-react';
import GovPublicShell from '../components/gov/GovPublicShell';
import { LAST_UPDATED } from '../components/gov/GovFooter';
import { getPolicy, POLICY_LINKS, type PolicyBlock } from '../content/policies';

const Block: React.FC<{ block: PolicyBlock; index: number }> = ({ block, index }) => (
  <section className="mb-7" aria-labelledby={block.heading ? `sec-${index}` : undefined}>
    {block.heading && (
      <h2 id={`sec-${index}`} className="mb-3 text-[17px] font-semibold tracking-tight text-gov-ink dark:text-white">
        {block.heading}
      </h2>
    )}

    {block.p?.map((text, i) => (
      <p key={i} className="mb-3 text-[14.5px] leading-[1.8] text-slate-700 dark:text-slate-300">{text}</p>
    ))}

    {block.ul && (
      <ul className="mb-3 space-y-2.5">
        {block.ul.map((item, i) => (
          <li key={i} className="flex gap-3 text-[14.5px] leading-[1.75] text-slate-700 dark:text-slate-300">
            <span aria-hidden="true" className="mt-[0.62em] h-1.5 w-1.5 flex-shrink-0 rounded-full bg-gov-saffron" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    )}

    {block.table && (
      <div className="overflow-x-auto rounded-xl border border-gov-line dark:border-slate-700/60">
        <table className="gov-table">
          {block.table.caption && <caption className="sr-only">{block.table.caption}</caption>}
          <thead>
            <tr>{block.table.rows[0].map((cell) => <th key={cell} scope="col">{cell}</th>)}</tr>
          </thead>
          <tbody>
            {block.table.rows.slice(1).map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  j === 0
                    ? <th key={j} scope="row" className="px-4 py-3.5 text-left align-middle text-[13px] font-semibold text-gov-ink dark:text-white">{cell}</th>
                    : <td key={j}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )}

    {block.links && (
      <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {block.links.map((link) => (
          <li key={link.label + link.to}>
            <Link
              to={link.to}
              className="group flex items-start gap-2 rounded-lg border border-gov-line bg-white px-3.5 py-2.5 transition-colors hover:border-gov-blue/40 dark:border-slate-700/60 dark:bg-slate-900/60"
            >
              <ChevronRight size={14} className="mt-1 flex-shrink-0 text-gov-saffron" aria-hidden="true" />
              <span>
                <span className="block text-[13.5px] font-semibold text-gov-navy group-hover:underline dark:text-sky-300">{link.label}</span>
                {link.note && <span className="mt-0.5 block text-[12px] leading-relaxed text-slate-500 dark:text-slate-400">{link.note}</span>}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    )}
  </section>
);

const PolicyPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const policy = getPolicy(slug);

  if (!policy) return <Navigate to="/not-found" replace />;

  return (
    <GovPublicShell
      title={policy.title}
      titleHi={policy.titleHi}
      subtitle={policy.summary}
      breadcrumb={[{ label: 'Home', to: '/' }, { label: 'Website Policies', to: '/policy/sitemap' }, { label: policy.title }]}
      headerMeta={
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-[12px] text-slate-500 dark:text-slate-400">
          <span>Last reviewed: <span className="font-semibold text-gov-navy dark:text-slate-200">{LAST_UPDATED}</span></span>
          <button
            type="button"
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gov-line px-2.5 py-1 font-semibold text-gov-navy transition-colors hover:border-gov-blue/40 hover:bg-white dark:border-slate-700 dark:text-slate-200 print:hidden"
          >
            <Printer size={13} aria-hidden="true" /> Print this page
          </button>
        </div>
      }
    >
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_250px]">
        <article className="min-w-0 max-w-3xl">
          {policy.blocks.map((block, i) => <Block key={i} block={block} index={i} />)}
        </article>

        {/* Sibling policies — GIGW expects every policy page to reach the others. */}
        <nav aria-labelledby="other-policies" className="print:hidden">
          <div className="panel sticky top-6 p-4">
            <h2 id="other-policies" className="panel-title mb-3">Website Policies</h2>
            <ul className="space-y-1">
              {POLICY_LINKS.map((link) => (
                <li key={link.slug}>
                  <Link
                    to={`/policy/${link.slug}`}
                    aria-current={link.slug === policy.slug ? 'page' : undefined}
                    className={`block rounded-lg px-2.5 py-1.5 text-[13px] transition-colors ${
                      link.slug === policy.slug
                        ? 'bg-gov-blue/[0.09] font-semibold text-gov-navy dark:bg-sky-500/15 dark:text-white'
                        : 'text-slate-600 hover:bg-gov-blue/[0.05] hover:text-gov-navy dark:text-slate-300 dark:hover:text-white'
                    }`}
                  >
                    {link.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </nav>
      </div>
    </GovPublicShell>
  );
};

export default PolicyPage;
