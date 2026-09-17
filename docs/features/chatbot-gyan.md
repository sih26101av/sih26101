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
- `src/components/chat/GyanAvatar.tsx` — the assistant's artwork, shared by both
  widgets: `GyanBot` (head, used in the header and every bot bubble) and `GyanHero`
  (bot + chat bubbles + sparkles, used on the welcome screen). Pure inline SVG.
- `src/components/dashboard/ChatWidget.tsx` — floating widget on the dashboard;
  markdown rendering, suggestion chips, Web Speech voice input (`types/speech.d.ts`).
- `src/components/home/HomeChatWidget.tsx` — landing-page variant wired to
  `onScrollToSection` / `onOpenLogin` / `onLanguageChange`.
- Both widgets share one presentation: a 400px-max rounded panel (full-width minus
  gutters on mobile), navy header with the `GyanBot` avatar, online dot, chakra
  watermark and a language control (a dropdown on home, a toggle on the dashboard),
  a welcome screen of `GyanHero` + four `CAPABILITIES` cards + a "Try asking" list,
  and a pill input with mic + send plus the Shift+Enter / mic hints.
  Each capability card and suggestion row calls `handleSend` with a real prompt —
  none of them are decorative. There is deliberately **no** file-attach button: the
  chat engine has no upload path, so the icon would be dead.

## In / out

- In: `POST /api/v1/chat` with the message plus the dashboard's already-fetched
  skill gaps and recommendations (the bot does not query the DB itself).
- Out: `{reply, detected_language, engine, navigate_action, navigate_actions}`.
  Action shape: `{type: "tab"|"scroll"|"modal"|"redirect"|"theme"|"language",
  target, label}`.

## Connections

Consumes learner-dashboard state; drives UI via `useTheme`, tab state and the
landing page's scroll handlers. Shares the embedding model with the recommendation
engine, so the first chat request after startup may pay the model-load cost.

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
- Tier 3 (Ollama RAG) is dead code kept for a documented revert path.
