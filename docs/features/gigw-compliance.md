# GIGW compliance & accessibility (frontend chrome)

Everything that makes this a Government of India portal rather than a good
dashboard: the statutory chrome carried on every page, the accessibility
controls, the policy pages, and the WCAG fixes applied across the app.

The target is **GIGW 3.0** (Guidelines for Indian Government Websites, the DARPG /
NIC standard) plus **WCAG 2.1 level AA**, which the Rights of Persons with
Disabilities Act, 2016 makes binding on government sites.

## The chrome, and where it comes from

Every page — public, policy and signed-in — carries the same four things, in the
same order:

| Element | Component | Notes |
|---|---|---|
| "Skip to main content" | `.skip-link` in `index.css` + `<a href="#main…">` | First focusable element on the page; the target is the `<main>` landmark, which carries `tabIndex={-1}` so focus actually lands there |
| GoI utility strip | `src/components/gov/GovUtilityBar.tsx` | भारत सरकार identity, screen-reader link + read-aloud, A−/A/A+, contrast, language, theme |
| Tricolour strip | `.tricolor-strip` | Under the utility strip, above the masthead |
| Statutory footer | `src/components/gov/GovFooter.tsx` | Policy links, content owner, Web Information Manager, last-updated, visit count, conformance claim |

Where each page picks them up:

- `src/pages/LandingPage.tsx` — `GovUtilityBar` + its own rich masthead +
  `GovFooter variant="full"` with the landing blurb and quick links passed
  through the `brand` slot.
- `src/components/gov/GovPublicShell.tsx` — the plain public chrome (utility
  strip, masthead, breadcrumb, `<main>`, full footer) used by `PolicyPage` and
  `NotFoundPage`.
- `src/components/shell/AppShell.tsx` — the dashboards. The utility strip sits
  *above* the sticky navy topbar and scrolls away, so a working screen keeps its
  vertical room and the sidebar's sticky offset stays at 62px. Footer is
  `variant="compact"`: one policy-link row plus the statutory lines.
- `src/pages/LoginPage.tsx` (standalone route only — the `isModal` form keeps the
  landing page's chrome) and `src/pages/ChangePasswordPage.tsx`.

## Accessibility preferences

`src/context/AccessibilityContext.tsx` owns three portal-wide preferences, all
persisted in `localStorage` and applied to `<html>`:

| Preference | Storage key | Applied as | CSS |
|---|---|---|---|
| Text size, 5 steps (90 – 115%) | `gov-text-step` | `--gov-zoom` | `body { zoom: var(--gov-zoom) }` |
| High contrast | `gov-high-contrast` | `.hc` class | the `html.hc` override block |
| Language (`en` / `hi`) | `gov-lang` | `<html lang>` | — |

**Why `zoom` and not root font-size.** Most type in this app is authored in px
(`text-[13px]`), so scaling `html { font-size }` would change almost nothing.
`zoom` scales the whole layout. Viewport units ignore zoom, so `index.css`
divides it back out of `.min-h-screen` and `.shell-sidebar-h`; those two rules
sit *after* the Tailwind utility layer on purpose so they win at equal
specificity. At the default step the value is `1`, a no-op.

**High contrast** is an override layer (`html.hc …`) rather than a second theme,
so it composes with either light or dark: black surfaces, white text, `#ffd400`
links and icons, every border made visible, underlined links. The tricolour
strip is re-asserted afterwards because it carries meaning.

`useScreenReader(lang)` (pre-existing) supplies the read-aloud toggle on the
public pages; it uses the browser's own `SpeechSynthesis`, so it still works in
an air-gapped intranet deployment.

## Statutory pages

`src/content/policies.tsx` holds all ten as data — `{ slug, title, titleHi,
summary, blocks[] }`, where a block is paragraphs, a bullet list, a table or a
link list. `src/pages/PolicyPage.tsx` renders any of them at `/policy/:slug`
inside `GovPublicShell`, with a "Print this page" button and a sibling-policy nav.

`POLICY_LINKS` is the single ordered list the footer, the sitemap page and the
policy sidebar all read, so a page can never be linked without existing:

`terms-and-conditions` · `privacy-policy` · `copyright-policy` ·
`hyperlinking-policy` · `disclaimer` · `accessibility-statement` ·
`screen-reader-access` · `help` · `feedback` · `sitemap`

Redirect aliases: `/sitemap` and `/accessibility`. An unknown slug falls through
to `NotFoundPage`.

> Officer names and phone numbers in the Web Information Manager and Feedback
> blocks are left as **roles**, not invented individuals. Fill them in before a
> real launch.

## Other GIGW / WCAG work applied across the app

- **Unique page titles** — `src/hooks/usePageTitle.ts`, called per section in
  `LearnerDashboard`, `AdminDashboard`, `AssessmentPage`, `LoginPage` and every
  policy page, so a screen reader announces where the user landed.
- **Breadcrumbs** — `src/components/gov/Breadcrumbs.tsx` renders a real
  `nav > ol > li` with `aria-current="page"` on the last crumb.
  `shell/PageHeader.tsx` shows it at every width (it used to appear only above
  1280px) and still accepts the plain `string[]` its callers pass; the first
  entry links to `/`.
- **404** — `src/pages/NotFoundPage.tsx` replaces the old silent
  `<Navigate to="/" />`: it names the requested path and offers four ways on.
- **Forms** — `LoginPage` and `ChangePasswordPage` inputs now have `id` +
  `htmlFor`, `autoComplete`, `aria-invalid` / `aria-describedby`, and errors are
  `role="alert"`. Password reveal buttons are named and back in the tab order.
- **Tables** — every `<th>` in a `<thead>` carries `scope="col"`.
- **Moving content (WCAG 2.2.2)** — the landing page's "What's New" marquee has a
  pause/play button and pauses on hover *and* keyboard focus; the duplicated
  marquee copy is `aria-hidden` so headlines are announced once.
- **Text contrast (WCAG 1.4.3)** — `text-slate-400`, this app's muted-caption
  token (~360 uses), sits at about 2.6:1 on the light canvas. `index.css` pulls
  it to `#64748b` under `html:not(.dark)`, which clears AA; dark mode already
  passed and is untouched, and the selector is scoped so a `dark:` variant still
  wins where one is set.
- **Print** — a print stylesheet drops the chrome, flattens cards and spells out
  external URLs. GIGW asks for printer-friendly pages.
- **Document head** — `index.html` carries description / author / publisher /
  keywords metadata, the emblem favicon (`public/emblem.svg`) and a `<noscript>`
  block that says what is wrong and who to contact.
- **Visitor count** — `src/hooks/useVisitorCount.ts`. There is no analytics
  backend, so it counts once per browser session and the footer labels it
  "Visits (this device)" rather than passing it off as a site-wide total.
- **Last updated** — `__BUILD_DATE__`, defined in `vite.config.ts` and typed in
  `src/vite-env.d.ts`; `GovFooter` exports the formatted `LAST_UPDATED`.

## Verifying a change here

```bash
cd frontend && npm run build      # tsc + vite; the only automated gate
```

There is no test runner in the frontend. The chrome was last checked by
server-rendering `PolicyPage`, `NotFoundPage` and `LoginPage` inside the
providers and asserting the statutory strings are in the output — worth
repeating with a throwaway `--ssr` entry if this chrome is restructured, since a
missing provider is the failure mode a build will not catch.

Manual pass when touching this area:

1. Tab from a cold page load — the first stop must be "Skip to main content".
2. A+ three times on the learner dashboard — no horizontal scrollbar, the
   sidebar still ends at the viewport bottom.
3. High contrast on, over both themes — hero, cards, tables and charts legible.
4. Print preview of a policy page and of the skill-gap view.

## TODO

- Charts (`recharts`) are still graphical-only. Each is paired with the same
  figures in a table or summary, but they are not independently navigable; the
  Accessibility Statement declares this as a known limitation.
- The Feedback page tells the user where to write; it is not yet a form that
  posts anywhere.
- `useVisitorCount` should read a real counter once an analytics endpoint exists,
  and the footer label can drop "(this device)" at that point.
- Hindi currently covers the landing page and the utility strip. The dashboards,
  the policy bodies and the 404 are English-only; GIGW expects full bilingual
  content for a live GoI site.
- The UserWay widget in `index.html` is a third-party overlay loaded from a CDN.
  The in-house controls above do not depend on it, and it would not survive an
  air-gapped deployment — decide whether to keep it before launch.
