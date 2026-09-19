# Gyan — Multilingual Chat Assistant

Bilingual (English / Hindi / Hinglish / Devanagari) assistant that answers about
the user's own skill gaps, recommendations and the platform, and can *act* on the
UI (switch tab, scroll, toggle theme, change language, open the login modal).

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

Frontend:
- `src/services/chatApi.ts` — posts to `/api/v1/chat` (Vite proxies `/api` → :8000);
  on any failure falls back to a **client-side** reply engine (`detectLanguage`,
  `detectIntent`, `buildLocalReply`) so the widget never appears dead.
- `src/hooks/useChatEngine.ts` — message state, typing delay, executes `theme` and
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
  `chatCopy(lang).ask` — none of them are decorative. There is deliberately **no**
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

## Connections

Consumes learner-dashboard state; drives UI via `useTheme`, tab state and the
landing page's scroll handlers. Shares the embedding model with the recommendation
engine. The chat embedder and prototype vectors (disk-cached) load during
`main._warm_up`; `POST /api/v1/chat` waits in `_readiness_gate` until then,
while `GET /api/v1/chat/mode` answers immediately (`not_loaded` meanwhile).

## TODOs / edge cases

- `/api/v1/chat` has **no auth dependency**, and `user_id` is taken from the body.
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
