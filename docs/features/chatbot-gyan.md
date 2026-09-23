# Gyan — Multilingual Chat Assistant

Bilingual (English / Hindi / Hinglish / Devanagari) assistant that answers about
the user's own skill gaps, recommendations and the platform, and can *act* on the
UI (switch tab, scroll, toggle theme, change language, open the login modal).

It runs in three places — the landing page, the learner dashboard and the **admin
console**. The admin widget is the same assistant with an extra tier that reads
live console data (KPIs, compliance, ACBP, departments, shortages, emerging
skills, trends, health, nudges, plans and **any single official**); see
"Admin console tier" below.

## Code

Backend:
- `main-lms-backend/routers/chatbot.py` (mounted at `/api/v1`)
  - Models: `ChatRequest` (message, history, profile fields, `context`:
    `"home" | "dashboard"`, `skill_gaps[]`, `recommendations[]`), `ChatResponse`
    (`reply`, `detected_language`, `engine`, `navigate_action`, `navigate_actions`).
  - `detect_language` — Devanagari regex + `_HINGLISH_WORDS` set.
  - `POST /chat` — ordered pipeline:
    1. Regex intercepts that bypass the classifier: "who am i", homepage
       scroll-to-section, language switch, **compound** theme+language commands,
       theme toggle, login, out-of-scope (entertainment/celebrity) guard.
    2. **Tier 1** semantic: `ai.semantic_engine.classify_intent`; matches below
       confidence `0.50` fall through (except `CONFIDENT_ALWAYS` intents).
       Reply built by `_handle_semantic(intent, req, lang)`; `navigate_action`
       chosen from `_home_nav_map` or `_dash_nav_map` by context.
    3. **Tier 2** fallback: `detect_intent_keyword` (`_INTENTS` regex table) +
       `_generate_template_response`.
    4. **Tier 3** Ollama RAG — commented out, marked `REVERT_OLLAMA`.
  - `GET /chat/mode` — reports which engine is live (frontend badge).
  - **Sidebar navigation.** `_DASHBOARD_NAV` maps an intent to a `tab` action
    whose `target` is a `LearnerDashboard` `TabType` id: `navigation_dashboard`,
    `_my_courses`, `_skill_gap` (Skill-Gap Centre), `_recommendations`,
    `_ai_quiz` (Assessment Studio → `assessments`), `_certificates`, `_progress`,
    `_karma`. Each has prototype phrases in all 9 `ai/intent_corpus/*.json` and a
    reply in all 9 `services/chat_messages/*.py`. The Latin keyword fallback lists
    these nav patterns **before** `skill_gaps`/`recommend`, and they require a
    navigation verb or a section word, so "what are my skill gaps" still answers in
    chat. Nav phrases that echo informational ones ("show recommended courses" vs
    "show ongoing courses") steal intents — check `scripts/eval_intents.py`
    (baseline 84.6% macro) and `tests/test_chat_endpoint.py::test_sidebar_section_navigation`.
  - Helpers `_fmt_gaps`, `_fmt_recs`, `_top_gap` render profile context into markdown.
- `main-lms-backend/ai/semantic_engine.py`
  - `INTENT_CORPUS` — prototype phrases per intent in English, Hinglish and
    Devanagari (greeting, bot_identity, user_identity, skill gaps, recommend,
    navigation_*, out_of_scope, …).
  - `_correct_tokens` — difflib typo correction against `_NAV_VOCAB`.
  - `_ensure_prototypes` — lazily encodes prototypes on first call.
  - `classify_intent(query) -> (intent, confidence)` — cosine similarity via the
    shared embedder; cross-lingual by construction (no translation API).
  - `is_semantic_engine_ready()`, `vectorize_profile(skill_gaps)`.
- `main-lms-backend/ai/embedder.py` — shared singleton, see `shared-embedder.md`.

### Admin console tier

- `main-lms-backend/routers/admin_chat.py` (mounted at `/api/v1/admin/console`)
  - `POST /chat` — `require_role("admin")`. `AdminChatRequest` is
    `{message, history[], preferred_language, filters{department,grade,office},
    full_name, job_role, department}`; the response adds `intent` to the shape
    `/api/v1/chat` returns. Order of a request:
    1. **Identity lookup** — a `usr_…`, `EMP-…` or an email in the message, or a
       name after a lead-in ("tell me about …"), answers that official's brief
       straight away. This runs *before* `chatbot._intercept`, because
       "tell me about Ramesh Sharma" is exactly the shape `_OUT_OF_SCOPE_RE`
       refuses. A lookup-shaped message of **two or more** words that matches
       nobody replies "not on the roster"; one word ("photosynthesis") keeps the
       out-of-scope refusal.
    2. **Both classifiers** — `ADMIN_INDEX.classify` and `classify_intent`, same
       embedder and cosine scale. Admin wins when it clears the threshold and is
       within `ADMIN_MARGIN` (0.02) of the general score.
    3. **Shared intercepts** — `chatbot._intercept`, unchanged, so theme,
       language, "who am I" and login behave exactly as on the learner widget.
    4. **Admin answer** (`_answer_admin`) or **fall-through** to
       `chat_messages.render` for everything Gyan already knew (MoSPI, FRAC,
       GDP/CPI, farewell, motivation…).
  - `_LEARNER_TO_ADMIN` remaps the learner intents that are meaningless here —
    `greeting`/`about_platform` → capabilities, `profile_stats` → overview,
    `skill_gaps` → shortages, `recommend` → emerging, `progress` → trends. An
    admin has no skill gaps of their own, so the un-remapped reply was a list of
    zeroes.
  - `_ADMIN_TABS` maps a navigation intent to an `AdminTab` id; `_ADMIN_REDIRECTS`
    and `_LEARNER_INTENT_NAV` send learner-side intents to `/dashboard`,
    `/assessment`, `/` or the nearest admin tab (certificates → Actions, which
    holds the review queue).
  - `GET /chat/mode` — admin-tier badge (corpus size + readiness).
- `main-lms-backend/services/admin_chat_data.py` — the facts, as plain numbers:
  `find_officials` (userId → govId → email → fuzzy name, summed per-token scores
  so "Shika Takur" beats everyone who shares one name), `resolve_scope`
  (a department / office / service tier **named in the message** overrides the
  dashboard's filter bar; whole-word match so the department "Data" never fires
  on "data governance"), `overview_facts`, `department_facts`, `shortage_facts`,
  `needs_training_facts`, `behind_facts`, `trend_facts`, `official_facts` and
  `learner_db_facts` (karma, nudges, assigned plans). It reuses
  `routers.admin_console._roster()` — a lazy, one-way import, so the 60 s roster
  cache, the stale-copy fallback and the filter semantics stay in one place.
- `main-lms-backend/services/chat_messages/admin.py` — the admin reply
  catalogue. Deliberately **one** module rather than nine: admin answers are a
  one-line lead-in around a block of numbers, so the strings split into `LEAD`
  (one sentence per answer × 9 variants) and `LABEL` (the one-word metric names),
  with builders composing them. It must stay out of the per-language `T` tables —
  `tests/test_chat_messages.py` asserts those are key-identical across variants.
  `_count()` renders `workforce_service.cell()` dicts through their `display`
  field, so a group of 1–4 prints `<5`.
- `main-lms-backend/ai/intent_corpus_admin/<lang>.json` — 24 admin intents in all
  nine languages (~460 prototypes). Kept **separate** from `ai/intent_corpus/`:
  adding these intents there would move every learner classification and break
  `test_chat_messages.test_every_classifier_intent_has_a_reply`.
- `main-lms-backend/ai/semantic_engine.py` — `CorpusIndex` + `ADMIN_INDEX`.
  Two deliberate differences from the learner index: it is **lazy** (encoded on
  the first admin question, disk-memoised by `encode_cached`, ~7 s once) and it
  does **no language pooling** — every prototype is searched whatever the query's
  language, because the admin vocabulary is small and largely English loanwords.
- Tests: `main-lms-backend/tests/test_admin_chat.py` (roster, DB and both
  classifiers stubbed).

Frontend:
- `src/components/chat/ChatPrimitives.tsx` — the pieces all three widgets draw
  identically: `renderMarkdown`, `TypingIndicator`, `MessageBubble`,
  `NavConfirmBanner`, `VoiceButton`. Lifted out of `ChatWidget.tsx` when the admin
  console got its own widget. Styling unchanged and deliberately light-on-white
  everywhere: the panel is its own surface floating over the page, so Gyan looks
  the same on a dark admin console as on the landing page.
- `src/services/chatApi.ts` — posts to `${API_BASE_URL}/api/v1/chat` (`src/config.ts`; a bare `/api/...` path breaks on Vercel);
  on any failure falls back to a **client-side** reply engine (`detectLanguage`,
  `detectIntent`, `buildLocalReply`) so the widget never appears dead.
- `src/hooks/useChatEngine.ts` — takes an optional `transport` (`ChatTransport`)
  that replaces the default `sendChatMessage` call; everything after it — typing
  delay, action execution, the confirmation banner — is identical whichever
  endpoint answered. The admin widget passes its own. It also holds message
  state, executes `theme` and
  `language` actions immediately, routes other actions through a confirmation banner
  (`pendingNav` → `confirmNav` / `cancelNav`).
- `src/i18n/chatLanguages.ts` — **the** language table for both widgets:
  `CHAT_LANGUAGES` (code, native name, English name, header pill, Web Speech
  BCP-47 tag) and `chatCopy(code)`, which returns every user-visible string in
  that language (tagline, greeting, placeholders, hints, nav-confirm wording,
  error text, capability labels, and the prompts the cards/suggestions send).
  `chatCopy` falls back to English for anything unmapped. The nine codes mirror
  the backend exactly — `SUPPORTED_CHAT_LANGUAGES` plus `hi_latn` — so adding a
  row here without adding `services/chat_messages/<code>.py` would offer an
  option that silently answers in English.
- `src/components/chat/LanguageMenu.tsx` — the header language control, shared by
  both widgets: pill button (`Languages` icon + code + chevron) opening a
  scrollable menu of native name / English name / check mark, closed by Esc or an
  outside click.
- **Language selection.** Nine options: English, हिंदी, Hinglish (`hi_latn`),
  मराठी, ગુજરાતી, తెలుగు, தமிழ், ଓଡ଼ିଆ, বাংলা. The picked language reaches the
  backend as `preferred_language` on `POST /api/v1/chat`.
  `resolve_chat_variant(text, preferred)` in `services/language_service.py`
  applies it: a signal in the message always wins (Devanagari input gets
  Devanagari back even when the picker says EN), and the preference only decides
  when the text gives nothing away — the case that used to fall through to
  English and made the picker look broken.
  `detect_chat_variant_or_none` is the signal-only detector; `detect_chat_variant`
  keeps the old "default to en" behaviour for other callers. The browser fallback in
  `chatApi.ts` mirrors the same rule, but only ships English/Hindi templates.
  Ownership: `ChatWidget` owns its `lang` outright (no page-level language on the
  dashboard). On the landing page the page owns `lang` — but only in EN/HI, the
  two the page is translated into — and `HomeChatWidget` holds a `chatLang` that
  it seeds from that prop and re-syncs whenever the prop changes. Picking EN or
  हिंदी in the widget calls `onLanguageChange` so the whole page follows
  (`isPageLanguage` is the guard); picking a regional language moves the
  conversation only. Both widgets also accept the bot's own `language` action
  through the same handler.
- `src/components/chat/GyanAvatar.tsx` — the assistant's artwork, shared by both
  widgets: `GyanBot` (head, used in the header and every bot bubble) and `GyanHero`
  (bot + chat bubbles + sparkles, used on the welcome screen). Pure inline SVG.
- `src/components/admin/AdminChatWidget.tsx` — the admin console widget. Same
  panel, header, language menu, welcome screen and mic as the learner widget; it
  differs only in its `transport` (`sendAdminChatMessage` in `services/api.ts`,
  authenticated, **no** browser fallback — invented roster numbers would be worse
  than an error bubble), its four cards (Workforce / Mandatory Training / An
  Official / What to Train Next) and having no document attach. Mounted in
  `AdminDashboard.tsx`, which turns a `tab` action into an `AdminTab` and a
  `redirect` into a route, and passes its filter bar down as the default scope.
- `src/services/api.ts` (ADMIN CONSOLE section) — `sendAdminChatMessage`, through
  `lmsFetch` so it carries the bearer token and the 401 refresh.
- `src/i18n/chatLanguages.ts` — `adminChatCopy(code)` adds the console-specific
  strings (tagline, subtitle, placeholder, four card labels, eight prompts) in all
  nine languages, merged over English. Everything else — greeting, hints, yes/no,
  nav-confirm wording, error text — is the shared `chatCopy`.
- `src/components/dashboard/ChatWidget.tsx` — floating widget on the dashboard;
  markdown rendering, suggestion chips, Web Speech voice input (`types/speech.d.ts`).
- `src/components/home/HomeChatWidget.tsx` — landing-page variant wired to
  `onScrollToSection` / `onOpenLogin` / `onLanguageChange`.
- Both widgets share one presentation: a 400px-max rounded panel (full-width minus
  gutters on mobile), navy gradient header with the `GyanBot` avatar, pulsing online
  dot, chakra watermark, the shared `LanguageMenu` and a tricolour rule along the
  header's bottom edge; a welcome screen of `GyanHero` + four `CAPABILITIES` cards +
  a "Try asking" list; and a pill input with mic + send plus the Shift+Enter / mic
  hints. Bubbles animate in with `animate-bubble-in` (keyframe in
  `tailwind.config.js`); the send button is grey until there is text to send.
  Each capability card and suggestion row calls `handleSend` with a real prompt from
  `chatCopy(lang).ask` — none of them are decorative. The cards are `min-w-0` with
  hyphenating/`overflow-wrap:anywhere` labels so long words wrap
  inside the narrow 4-column grid instead of spilling out (same in `ChatWidget.tsx`). There is deliberately **no**
  file-attach button: the chat engine has no upload path, so the icon would be dead.
- The chat textarea carries `focus-visible:ring-0 focus-visible:ring-offset-0`. The
  global `:focus-visible` rule in `index.css` paints a saffron **ring**, which
  `focus:outline-none` does not suppress, so without this the input showed a yellow
  box on top of the pill's own `focus-within` treatment.
- **Document attach → Assessment Studio hand-off.** `ChatWidget.tsx` (dashboard
  widget only, not `HomeChatWidget`) has a paperclip button next to the mic
  (`accept=".pdf,.docx,.pptx,.txt"`, hidden `<input type="file">`). Gyan never
  reads the file — it stays fully offline/no-API-key by design — it only
  carries it to the Assessment Studio, which has `GEMINI_API_KEY` wired up.
  Attaching a file shows a banner above the input bar with two buttons,
  **"📝 Generate a quiz"** and **"📖 Help me study this"** (Learning Mode). If
  the learner types instead of tapping a button, a local regex
  (`QUIZ_INTENT_RE` / `LEARN_INTENT_RE`) reads the message for intent; an
  ambiguous message falls through to the normal `/api/v1/chat` call (the
  banner stays up so the learner can still pick explicitly). Picking a mode
  calls `setPendingStudioUpload(file, mode)`
  (`services/pendingStudioUpload.ts`, a plain module singleton — a `File`
  can't survive `sessionStorage` or router `state` across a lazy-loaded
  route) and fires a synthetic `{type: "redirect", target: "/assessment"}`
  through the existing `onNavigate` prop, reusing `LearnerDashboard.tsx`'s
  existing `"redirect"` handling. `AssessmentPage.tsx` consumes the singleton
  on mount and auto-starts quiz generation or Learning Mode with that file —
  see `docs/features/learning-mode.md`.

## In / out

- In: `POST /api/v1/chat` with the message, the optional `preferred_language`
  (`en`/`hi`/… or `hi_latn`), plus the dashboard's already-fetched skill gaps and
  recommendations (the bot does not query the DB itself). `preferred_language` is
  optional and defaults to `None`, so older clients behave exactly as before.
- Out: `{reply, detected_language, engine, navigate_action, navigate_actions}`.
  Action shape: `{type: "tab"|"scroll"|"modal"|"redirect"|"theme"|"language",
  target, label}`.
- Admin: `POST /api/v1/admin/console/chat` (admin JWT) with
  `{message, history[], preferred_language, filters{department,grade,office},
  full_name}`. Out: the same shape plus `intent`; `engine` is
  `semantic-admin` when the console tier answered. It carries **no** skill gaps
  or recommendations — the backend reads the roster itself.

## Connections

Consumes learner-dashboard state; drives UI via `useTheme`, tab state and the
landing page's scroll handlers. The admin tier reads the admin console's cached
roster and the same pure aggregates its panels use (`services/admin_analytics`,
`app_state.snapshot`, `services/system_health`), so a chat answer and the panel
beside it cannot disagree — see [admin-dashboard.md](admin-dashboard.md). Shares the embedding model with the recommendation
engine. The chat embedder and prototype vectors (disk-cached) load during
`main._warm_up`; `POST /api/v1/chat` waits in `_readiness_gate` until then,
while `GET /api/v1/chat/mode` answers immediately (`not_loaded` meanwhile).

## TODOs / edge cases

- `/api/v1/chat` has **no auth dependency**, and `user_id` is taken from the body.
  `/api/v1/admin/console/chat` does: `require_role("admin")`, and it never takes a
  user id from the body — an official is resolved from the message against the
  roster.
- The admin tier answers about **any** official, including their karma total and
  nudge history. That is the same data the Officials tab and the CSV exports
  already expose to an admin, but it is now one sentence away, so treat the
  endpoint as the same disclosure surface as `/export/roster.csv`.
- Small-cell suppression is carried through (`<5`), but only where the underlying
  aggregate already applied it — a single-official lookup is never suppressed,
  exactly as in the roster table.
- Admin replies localise the lead-in and the metric labels in all nine languages;
  numbers, department names, competency names, course titles and
  `recommendedAction` stay in English, because that is what the console, the CSVs
  and iGOT show.
- `ADMIN_MARGIN` (0.02) and the two-word rule for a failed name lookup were tuned
  by hand against the live roster, like the learner tier's `0.50` threshold.
  `scripts/eval_intents.py` does not cover the admin corpus.
- Replies are templated, not generative — accuracy depends on the intent corpus and
  the regex intercept ordering, which is delicate (intercepts run before the classifier
  precisely because it mis-scored these cases).
- `GET /chat/mode` still reports `model: "all-MiniLM-L6-v2"`; the actual model is
  `paraphrase-multilingual-MiniLM-L12-v2`.
- Confidence threshold `0.50` and `CONFIDENT_ALWAYS` were tuned by hand; slang and
  entertainment queries were the failure mode.
- The frontend fallback engine duplicates backend logic in TypeScript — changes to
  reply content need to be made in both places to stay consistent.
- **Malayalam is not supported.** Adding it means a `services/chat_messages/ml.py`
  template module, a `[ഀ-ൿ]` row in `_SCRIPT_LANGUAGE_PATTERNS`, `ml` in
  `SUPPORTED_CHAT_LANGUAGES` and an `ml` row in `CORPUS_LANGUAGES` — then one entry
  in `CHAT_LANGUAGES`. The picker deliberately lists only languages the backend has
  templates for.
- Widget chrome is localized in all nine languages, but the browser fallback replies
  (backend down) and the capability-card *content* behind them are English/Hindi only.
- Tier 3 (Ollama RAG) is dead code kept for a documented revert path.
