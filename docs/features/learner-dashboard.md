# Learner Dashboard (frontend shell)

The official's home screen at `/dashboard/:officialId`: a sidebar shell with eight
sections, all fed by the single `useLearnerDashboard` fetch.

## Code

- `src/pages/LearnerDashboard.tsx` — the shell, rendered inside `AppShell`.
  - `TabType = "dashboard" | "my-courses" | "skill-gap" | "recommendations" |
    "assessments" | "certificates" | "progress" | "karma"`; `SECTION_META` holds the
    title/subtitle/breadcrumb for each. Switching sections never refetches.
  - The chatbot still switches sections via `onNavigate`; its `tabMap` covers the
    three legacy targets plus the new ones (`skill-gap`, `recommendations`,
    `assessments`, `certificates`, `karma`) and aliases (`skill-gaps`, `courses`).
  - `dashboard` → (no `PageHeader`; the banner carries the date chip) `ProfileHeader` + 5 `StatCard` tiles (assessed, active gaps,
    mandatory gaps, recommendations, overall proficiency) + left column
    `CompetencyOverviewTable` then `RecentActivityList` (moved under the table so the
    left column no longer leaves a blank gap beside the taller right column)
    + right column (top→bottom) `LearningSnapshot`, `CareerReadinessCard` + a 3-card
    `RecommendationsPanel` preview.
  - `my-courses` → `MyCoursesView`; `progress` → `ProgressView` + `LearningSnapshot`.
  - `skill-gap` → 4 stat tiles + `SkillGapCard` (filtered by the topbar search).
  - `recommendations` → full `RecommendationsPanel` (honours the competency filter).
  - `assessments` → `StudioPromo` + `AssessmentUploadZone` + a top-5 gap list.
  - `certificates` → `components/dashboard/CertificateUploadZone.tsx` (posts to
    `/competencies/upload-certificate`, lists the official's submissions, calls
    `refetch` on success; see [certificate-evidence-extraction.md](certificate-evidence-extraction.md))
    + `RecentActivityList`.
  - `karma` → `KarmaRewardsView` (see `karma-points.md`).
  - Persistent: `ChatWidget` (rendered outside the shell, fixed).
  - Sidebar: `SidebarArt` (`public/sidebar-palace.webp` palace illustration, masked
    top/bottom, "Data for a Stronger India" + saffron/green underline; hidden below
    780px viewport height) above the `SidebarHelp` card.
  - Topbar search filters the competency set; the bell count is the mandatory-gap
    count and jumps to the Skill-Gap Centre.
- `src/components/shell/` — shared with the admin dashboard and Assessment Studio:
  - `AppShell.tsx` — GIGW utility strip + tricolour strip + navy NSO topbar
    (search, notifications, theme, account menu, sign-out) + sticky sidebar
    (mobile drawer under `lg`) + statutory footer.
    See "Responsive layout" below for the phone/tablet behaviour.
    Takes `groups`/`activeId`/`onNavigate`; owns no data. Optional `sidebarArt`
    slot renders between nav and `sidebarFooter` (desktop only; admin doesn't use it).
    The GIGW chrome — a skip link, `GovUtilityBar` (text size / contrast /
    language), landmark roles, and `GovFooter variant="compact"` — is described in
    [gigw-compliance.md](gigw-compliance.md). The utility strip sits *above* the
    sticky header and scrolls away, so the sidebar's sticky offset stays 62px; the
    sidebar uses `.shell-sidebar-h` so its height survives the A+ text zoom.
  - `PageHeader.tsx` — breadcrumb trail (now above the title and visible at every
    width, rendered as a semantic `nav > ol > li` by `components/gov/Breadcrumbs`;
    still accepts the plain `string[]` callers pass, first entry links to `/`),
    then the `<h1>` title, subtitle, date chip and action slot. Also the place
    each section's `document.title` is *not* set — that is `usePageTitle`, called
    from the page.
  - `SectionCard.tsx` (+ `SectionAction`) — titled panel; `padded={false}` for tables.
  - `StatCard.tsx` — KPI tile (`StatTone`, optional delta / caption / progress /
    `onClick`; renders as a `<button>` only when clickable).
- `src/hooks/useLearnerDashboard.ts` — single fetch orchestrator: profile + skill
  gaps, enrollments, recommendations, achievements, karma; exposes loading/error and
  a refetch used after a quiz pass. All requests fire in parallel; karma fills in
  after first paint. Stale-while-revalidate: a module-level cache per `officialId`
  renders instantly on remount (home → dashboard, back from the Assessment Studio)
  and refreshes silently; a failed background refresh keeps the cached data. The
  cache is wiped by `api.ts::onSessionEnd` when `setApiToken(null)` runs (logout).
  Backend side: see the competency-state memo in
  [skill-gap-analysis.md](skill-gap-analysis.md).
- `src/components/dashboard/`
  - `SkillGapCard.tsx` — `GapRow` per competency: `PipStrip` (current level),
    `ExactGlassGauge` (target), `CONFIDENCE_CONFIG` badge, `EvidenceBar` per channel,
    "find courses" callback that jumps to the recommendation list, a "Not yet
    assessed" section, and — when given `officialId` — fetches
    `/api/v1/learner/{id}/pathway` once to show "Suggested study order" and a
    per-gap "View learning path" ladder (`LearningPathway.tsx`; see
    [recommendation-engine.md](recommendation-engine.md)). Every gap carries an
    `OpportunityBadge` ("Opportunity to practise: Low this cycle → queued",
    tooltip = office sub-processes and hours share; SCIL v6 §4, see
    [workforce-insights.md](workforce-insights.md)); `StudyPlanSummary` marks
    opportunity tie-break picks "practise at work". By default the plan is
    "This quarter's study plan" (hours used of the ACBP quarterly budget),
    APAR-linked mandatory courses carry a "Mandatory (ACBP)" chip (also on the
    matching ladder step), completed mandatory courses are listed, and ladders
    that don't fit ("over budget" / "classroom cap") are listed as continued next
    quarter. `EvidenceCompletenessRow` shows which SCIL v6 §3 channels (K/A/U/S)
    carry evidence (tooltip: value + the equal placeholder weights) and the
    number of peer ratings ("context only, not scored"); the evidence breakdown
    adds Work sample / Used at work / Supervisor bars.
  - `CompetencyOverviewTable.tsx` — compact gap table for the overview: domain filter
    chips with live counts, `LevelPips` current vs target, gap chip, priority badge
    (`priorityOf`), per-row "find courses", "show all" toggle.
  - `LearningSnapshot.tsx` — enrolment donut (completed / in progress / not started)
    with mean progress in the centre; derived from `enrollments`.
  - `RecentActivityList.tsx` — achievement feed with relative dates.
  - `RecommendationsPanel.tsx` — the `CourseCard` grid plus the competency-filter
    chip; falls back to the full list when a filter matches nothing.
  - `CourseCard.tsx` — title, provider, duration, score chips, TPAC badge, match reasons.
  - `MyCoursesView.tsx`, `ProgressView.tsx`.
  - `ProfileHeader.tsx` — light hero over `public/profile-banner.webp` (waves, dotted
    India map, growth bars, chakra; a 3:1 layer sized to the banner height, pinned
    right with a left-edge mask fade so the art is never cropped, dimmed under a navy
    scrim in dark mode): tricolour-ring avatar, name + Verified chip, role, id /
    department / last-assessed chips, today's date chip, ministry strapline,
    LEARN·ANALYSE·CONTRIBUTE·GROW motto (xl+), saffron/green bottom accent.
  - `RightSidebar.tsx` — compact karma card + `CareerReadinessCard` (the sidebar
    itself is no longer mounted; the Karma tab uses `components/karma/KarmaRewardsView.tsx`).
  - `CareerReadinessCard.tsx` — mounted in the overview's right column. Reads
    `GET /api/v1/learner/{id}/career-readiness` (`fetchCareerReadiness`): readiness %
    for the next role, its largest gaps (NEW = not in the current role), the office
    tier ladder. Refetches when any level changes (`refreshKey`). See
    [skill-gap-analysis.md](skill-gap-analysis.md).
  - `LevelCheckModal.tsx` — opened from "Disagree with this level?" / "Check my
    level" on each gap row: records a level dispute and runs the adaptive level
    check in place, then calls `refetch`.
  - `AssessmentUploadZone.tsx` — now rendered (Assessment Studio section); it was
    orphaned before this redesign.
- `src/types/domain.ts` — `Official`, `SkillGapEntry`, `CourseRecommendation`,
  `Enrollment`, `Achievement`, `KarmaLedger`, `KarmaEventType`, `CompetencyDomain`.
- `src/hooks/useTheme.tsx` — light/dark provider (also driven by the chatbot).
- `src/services/api.ts` — all data access (`lmsFetch`, JWT + 401 retry).

## Visual design system (shared by every page)

- `tailwind.config.js` — `gov.*` palette (`ink`, `navy`, `blue`, `saffron`, `green`,
  `gold`, `paper`, `line`) plus `accent.*` (`blue`, `orange`, `green`, `purple`, `sky`,
  `rose` and their `-soft` tints) used by stat tiles, status chips and charts so the
  two never drift. `paper`/`line` are cool now (`#f4f7fb` / `#e4eaf2`), not warm beige.
  Body font is **Poppins** (`font-sans`), `font-serif` (Merriweather) is kept for the
  landing hero and formal headings. `shadow-gov`/`shadow-gov-lg`, animations `fade-up`,
  `fade-in`, `scale-in`, `shimmer`, `float`, `marquee`, `grow-x`, `spin-slow`.
  Fonts loaded in `index.html`.
- `src/index.css` — component classes: `tricolor-strip`, `gov-page-bg`, `gov-canvas`,
  `gov-card`, `gov-card-hover`, `gov-heading`, `gov-eyebrow`,
  `gov-btn-primary|saffron|outline`, `gov-input`, `skeleton`, `reveal`, `nav-link`,
  and the shell set: `shell-nav-item`, `shell-title`, `panel`, `panel-head`,
  `panel-title`, `chip`, `chip-filter`, `gov-table`.
  `prefers-reduced-motion` disables motion.
- `src/components/gov/GovUI.tsx` — `AshokaChakra` (SVG), `GovEmblem`, `Reveal`
  (IntersectionObserver fade-in), `CountUp` (animated numbers).
- **Product name: KarmaSkill.** The landing header, hero badge and footer lead with
  it; "Skill Intelligence Platform" is now the descriptor beneath. `index.html`
  `<title>` follows. The dashboard shells still carry the NSO Training Portal wording.
- `LandingPage.tsx` — GoI utility bar (EN/हिंदी, working screen reader, theme),
  ministry header (KarmaSkill is the primary line, ministry the eyebrow), sticky nav,
  "What's New" marquee (`NEWS_ITEMS`, static), hero with the `outcomes` rail
  (Assess Skill Gaps → Personalized Learning → Stronger Governance), clickable
  `capabilities` cards, count-up metrics, features, about timeline, footer
  (`id="contact"`). Section ids `home`/`features`/`about`/`contact` are used by
  `HomeChatWidget` scrolling.
- The hero uses `public/hero-bg-blue.png` (chakra + growth bars + orbit arc) as a
  `bg-cover` layer over the navy gradient, with a left-to-right scrim for legibility.
  The gradient stays behind it, so the section degrades gracefully if the image 404s.
- `src/hooks/useScreenReader.ts` — GIGW "Screen Reader Access" via SpeechSynthesis.
  `useScreenReader(lang)` returns `{supported, speaking, read, stop, toggle}`; the
  utility-bar button calls `toggle('#main')`. Prose is collected from headings /
  paragraphs / list items (skipping `aria-hidden` and `sr-only`), split into ≤220-char
  sentence chunks because engines truncate long utterances, and spoken as `hi-IN` or
  `en-IN`. The control hides itself when the browser lacks support; changing language
  stops playback. No external service — it works air-gapped.
- The old `animate-in fade-in slide-in-*` classes were no-ops (no plugin); replaced by
  `animate-fade-up`. `bg-mesh.png`, `hero-bg-dark.png`, `hero-bg-topo.png` and
  `bg-mesh1.png` are leftover unused assets in `public/`.
- All pages now share the system. Chat widgets keep their own styling.

## Responsive layout (phones 360–430px, tablets 768–1024px)

Breakpoints are Tailwind's (`sm` 640, `md` 768, `lg` 1024, `xl` 1280). Verified by
screenshots at 375 / 768 / 1024 / 1366 with no horizontal page scroll.

- **Shell (`AppShell`)** — below `lg` the sidebar is a slide-in drawer (`animate-drawer-in`,
  82vw max 300px) with the user's name/role at the top and a Sign out button; tapping any
  item (including the current one) closes it, and page scroll is locked while it is open.
  The topbar search is inline only from `lg`; below that a search icon opens a full-width
  search row under the bar (16px text so iOS doesn't zoom). Below `sm` the title reads
  "NSO Training Portal" and the theme toggle moves into the account menu.
  `<main>` carries `shell-main`: `index.css` gives every grid child inside it
  `min-width: 0`, so a wide table/chart can't stretch its grid column past the screen
  (this was the cause of the 633px-wide dashboard on phones).
- **`PageHeader`** hides the date chip below `sm`; **`SectionCard`** actions wrap on phones;
  `.panel-head` and `.shell-title` are tighter below `sm`.
- **`StatCard`** stacks the icon above a 2-line (hyphenated) label below `sm`. The overview's
  five tiles go 2 → 3 (`md`) → 5 (`xl`) columns, the odd last tile spans two on phones.
- **`ProfileHeader`** drops the banner art below `sm` (compact avatar, chips full width,
  date chip hidden) and only goes side-by-side from `xl` — at `lg` the sidebar leaves
  ~720px, too narrow for the two-column hero.
- **`CompetencyOverviewTable`** renders stacked cards below `md` and the table from `md`.
- **`SkillGapCard`** hides the redundant target pips below `sm` and centres the gauge.
- **Chat widgets** — the panel is `100vw − 1rem` wide on phones with `dvh`-based height;
  the bubble is 48px at `bottom-4 right-4` on phones.
- **Karma** summary tiles are 2 × 2 on phones.
- Admin: see [admin-dashboard.md](admin-dashboard.md) (filter bar, KPI grids).

## In / out

- In: `officialId` from the route (an iGOT `usr_…` id), JWT from `AuthContext`.
- Out: rendered UI; user actions call back into the quiz, karma and chat features.
- Backend endpoints consumed: `/api/v1/profile/{id}`, `/api/v1/learner/{id}/skill-gaps`,
  `/enrollments`, `/recommendations`, `/pathway`, `/achievements`, `/api/v1/learner/{id}/karma`.

## Connections

Reads from skill-gap analysis, recommendation engine and karma; feeds the chatbot the
gaps and recommendations it already has in state (the bot does not re-query them).

## TODOs / edge cases

- `AssessmentUploadZone` has a hardcoded default `userId = 'usr_720465595'` (the
  dashboard now always passes the real id).
- The static `CareerCard` (`CAREER_MATCH_PCT = 82`) and `MilestoneStepper` were
  removed. `CareerReadinessCard` replaces them with live data.
- Overall proficiency is `mean(min(1, current/required))` over `skillGaps`, computed
  client-side; there is no server-side equivalent.
- API base URLs are hardcoded to `http://localhost:8000` in `api.ts`, `authApi.ts`
  and the quiz components — no env-driven base URL for deployment.
- `fetchRecommendations` hardcodes `domain: 'Statistical'` for the bridged competency.
- Karma is fetched via `POST /karma/check-in` (daily check-in side effect); its DB
  work runs in the threadpool so it no longer blocks the event loop.
- The first-ever load after a backend restart waits on warm-up (readiness gate).
- Karma failures degrade to `null` silently; other fetch failures surface an
  `ErrorState` with retry.
- `/trainer` renders this same dashboard without an official id.
- Landing-page metrics (12.4k users etc.), the news ticker and the hero preview panel
  are static illustrative content, not backed by data.
