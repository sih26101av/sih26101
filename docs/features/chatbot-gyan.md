# Gyan — Multilingual Chat Assistant

Assistant that answers about the user's own skill gaps, recommendations and the
platform, and can *act* on the UI (switch tab, scroll, toggle theme, change
language, open the login modal). Understands and replies in **8 languages**:
English, Hindi (Devanagari **and** romanized Hinglish), Marathi, Bengali,
Gujarati, Odia, Tamil, Telugu — replying in the script the user typed in.

## Code

Backend:
- `main-lms-backend/routers/chatbot.py` (mounted at `/api/v1`) — routing only, no
  reply text.
  - Models: `ChatRequest` (message, history, profile fields, `context`:
    `"home" | "dashboard"`, `skill_gaps[]`, `recommendations[]`), `ChatResponse`
    (`reply`, `detected_language`, `engine`, `navigate_action`, `navigate_actions`).
  - `POST /chat` pipeline:
    1. **English regex intercepts** (`_intercept`) for commands the classifier has
       historically mis-scored: "who am i", homepage scroll-to-section, compound
       theme+language, language switch, theme toggle, login, celebrity/out-of-scope.
       Ordering is deliberate — compound *before* the single-command patterns.
    2. **Semantic intent** — `ai.semantic_engine.classify_intent`. Its answer is
       final: weak matches already come back as `out_of_scope`, so the keyword tier
       must not second-guess it (otherwise "course gap dashboard banana" gets real
       recommendations).
    3. **Keyword tier** (`detect_intent_keyword`) — only when the embedder is
       unavailable, i.e. `classify_intent` returned `"general"`.
  - `GET /chat/mode` — reports the live engine + chat model (frontend badge).
- `main-lms-backend/ai/semantic_engine.py`
  - Prototype phrases live in `ai/intent_corpus/<lang>.json` — one file per language
    (32 intents each) so a native speaker can review their own language in isolation.
  - `classify_intent(query, lang) -> (intent, confidence)`; scores each intent by its
    nearest prototype (`TOP_K = 1`, measured best) **within the query's language pool**
    only. Below `low_confidence_threshold()` the result is downgraded to `out_of_scope`.
  - `_correct_tokens` — typo repair for Latin-script queries: an explicit shorthand
    table (`u`→`you`, `r`→`are`, `plz`→`please`) plus difflib matching against
    `VOCABULARY`, every word used in a Latin prototype. Words already in the
    vocabulary are never rewritten.
  - `vectorize_profile(skill_gaps)`, `is_semantic_engine_ready()`.
- `main-lms-backend/services/chat_messages/` — the reply catalogue. One
  strings-only module per language variant (`en`, `hi`, `hi_latn`, `mr`, `bn`, `gu`,
  `or_`, `ta`, `te`); all branching (home vs dashboard, gaps vs none, progress
  thresholds) lives once in `__init__.render`. Translators never touch logic.
- `main-lms-backend/services/language_service.py` — `detect_chat_variant` (script
  ranges + Hinglish marker words + `langdetect` for Hindi/Marathi), `to_iso`.
- `main-lms-backend/services/chat_actions.py` — `detect_ui_actions`, so theme and
  language requests work in *any* supported language, not just English.
- `main-lms-backend/ai/embedder.py` — role-based models, see `shared-embedder.md`.
  Chat uses `intfloat/multilingual-e5-small`; the course catalogue uses
  `all-MiniLM-L6-v2`.

Frontend:
- `src/services/chatApi.ts` — posts to `/api/v1/chat`; on failure falls back to a
  **client-side** engine that only speaks English/Hindi and `console.warn`s, so a
  broken backend is visible rather than silently masked.
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

## In / out

- In: `POST /api/v1/chat` with the message, the optional `preferred_language`
  (`en`/`hi`/… or `hi_latn`), plus the dashboard's already-fetched skill gaps and
  recommendations (the bot does not query the DB itself). `preferred_language` is
  optional and defaults to `None`, so older clients behave exactly as before.
- Out: `{reply, detected_language, engine, navigate_action, navigate_actions}`.
  Action shape: `{type: "tab"|"scroll"|"modal"|"redirect"|"theme"|"language",
  target, label}`. `detected_language` is always ISO (`hi_latn` reports as `hi`).

## Measuring changes

```bash
cd main-lms-backend
python scripts/eval_intents.py --robustness   # accuracy per language + typos + gibberish
python -m pytest tests/test_typo_and_gibberish.py tests/test_chat_endpoint.py
```

Held-out data (never copied from the prototypes): `tests/data/intent_eval/<lang>.json`
(864 phrases), `tests/data/typo_eval.json`, `tests/data/gibberish_eval.json`.
Current: **84.6% macro** intent accuracy, **90%** on misspelled queries, **98%** of
nonsense/off-topic refused. Reply text is snapshot-tested in
`tests/test_reply_regression.py`.

## Connections

Consumes learner-dashboard state; drives UI via `useTheme`, tab state and the landing
page's scroll handlers. Shares `ai/embedder.py` with the recommendation engine, which
warms both models at startup (~30s) so the first chat request is instant.

## TODOs / edge cases

- `/api/v1/chat` has **no auth dependency**, and `user_id` is taken from the body.
- Replies are templated, not generative — accuracy depends on the intent corpus and
  the regex intercept ordering, which is delicate (intercepts run before the classifier
  precisely because it mis-scored these cases).
- The prototype phrases and translated replies were written by an LLM, not native
  speakers; **they need a native-speaker review** before the corpus is trusted.
- Hinglish is the weakest language (≈70%); Marathi is detected as Hindi ~10% of the
  time (reply is still correct, just in the sibling language).
- Raising `_LOW_CONFIDENCE` trades recall for refusals: at 0.89 about 6 of 906 real
  queries get "I don't know". Re-tune with `--robustness` if the chat model changes.
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
