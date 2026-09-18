# SCIL v6 — mock data + blocked features: progress report

Branch: `feat/scil-v6-mock-data` (local only, never pushed).
Baseline commit of the previous session's pathway work: `1353c45`.

Everything the mock server serves is **synthetic**. It comes from
`mock-igot-server/generate_mock_data.py` (seed `20260918`). Where this report says
an estimator "recovers" an effect, it means a **planted synthetic effect**, not a
validation against real officials.

## Status

| Item | Status | Commit | Notes |
|---|---|---|---|
| Preflight (baseline commit, servers, baseline metrics) | done | `1353c45` | Metrics in `docs/reports/metrics-baseline.json` |
| A1 One competency id space | done | `5e646b5` | 100% of served role competencies are catalogue ids; `frac_crosswalk.json` for the 331 CID dictionary |
| A2 Catalogue that teaches its tags | done | `5e646b5` | Tag support 100% (597/597); 34/40 full ladders; 6 documented holes |
| A3 Durations + quality fields | done | `5e646b5` | Seconds; 4 formats; `modality`; ~10% missing per quality field |
| A4 One catalogue source | done | `5e646b5` | `POST /api/composite/v1/search` → adapter → engine; disk fallback with warning |
| A5 Enrollments / history | done | `5e646b5` | Status 2 ⇔ 100%; dates over 3 years; 5 planted out-of-order learners |
| B2+B1 GSBPM + opportunity | done | `8c8f495` | `gsbpm_map.json` + `offices.json`; 80% scope report (13 core sub-processes = 80.8% of hours → 28 in / 12 out); opportunity badge; ordinal tie-break (band 10%) |
| B3 ACBP + budget + modality | done | `aaa6356` | `acbp.json` (org + role APAR-linked mandatory courses, hours/quarter); mandatory first even over budget; default budget = quarterly hours; classroom cap 30 h/quarter; `?unbudgeted=true` |
| B4 Prerequisite DAG | done | `e9dcdee` | 18 expert edges, cycle-checked with the ladders (cyclic set rejected); gate orders/blocks rungs, unknown levels advisory; data-driven suggestions (OLS + BH-FDR 10% + bootstrap CI) never applied; recovers both planted precedence effects |
| B5 Measured gain / uplift | done | `1761b34` | IPW (ATT) uplift per course + shrinkage κ=5 + bootstrap CI; mis-tag flag; all 4 planted zero-uplift courses flagged (and nothing else); r=0.91 vs planted truth (n≥15); flagged courses demoted in pathways; admin effectiveness view |
| B6 Evidence channels U/S/A | done | `d2f50f6` | `workplace_evidence.json` (supervisor w/ leniency+halo, utility + confirmation, 10-competency work samples, peer); K/A/U/S fused with equal 0.25 placeholder weights; work-sample / confirmed-use floors; completeness indicator; peer never scored |
| B8 Decay + cold start + foresight | done | (B8 commit) | `hrms.json`; θ~N(μ,σ²) with two-class dated decay toward population mean (6.5 / 12 mo), expected-shortfall gap, refresher flag; cohort prior (GSBPM phase × tenure band) with divergence check; background workforce snapshot; capability risk / SPOF, 36-month attrition × decay projection, draft TPAC agenda; n<5 suppression |
| B7 Item bank + IRT + CAT | pending | | |

## Before / after metrics

The baseline was measured on the pre-change data (preflight). "Phase A" is the
regenerated data. Both were measured with
`python -m scripts.mock_data_metrics` (backend + mock running, 20 users =
the first 20 in the roster).

| Metric | Baseline | After Phase A |
|---|---|---|
| Served role competencies whose id is a catalogue id | **0%** (0/1282) | **100%** (869/869) |
| Crosswalk method mix (20 users) | 38 semantic, 128 none | 112 exact |
| Tag-support rate (existing `_tag_support_threshold` check) | **52.4%** (211/403) | **100%** (597/597) |
| Competencies with a full L1–L5 ladder | 23/40 | 34/40 (6 documented holes) |
| Competencies with no L1 course | 11 | 0 |
| Course duration min / median / p90 (h) | 0.1 / 0.1 / 1.5 | 0.5 / 7.0 / 48.0 |
| /pathway status mix (20 users) | ready 19, met 59, **no_content 87**, partial 1 | ready 77, met 35, no_content 0, partial 0 |
| Pathway totalHours (ready/partial) min / median / p90 / max | 0.1 / 0.2 / 1.6 / 3.1 | 0.5 / 11.9 / 56.4 / 96.0 |
| Study plan totalHours median / max | 0.1 / 3.4 | 72.7 / 209.9 |
| Dashboard-vs-recommendation gap mismatches | 0 | 0 |
| Level-gate violations | 0 | 0 |

Duration by format after Phase A (min / median / p90 / max, hours):

| Format | n | min | median | p90 | max |
|---|---|---|---|---|---|
| micro_learning | 79 | 0.5 | 1.2 | 1.8 | 2.0 |
| self_paced_course | 243 | 2.0 | 5.5 | 7.5 | 8.0 |
| nssta_workshop | 121 | 6.0 | 12.5 | 15.5 | 16.0 |
| tpac_programme | 71 | 24.0 | 48.0 | 60.0 | 60.0 |

## Decisions log (made without the user)

1. **Kept identities, regenerated everything else (A1).** The 151 user ids,
   names, emails, govIds, experience, education, career history and tier were
   frozen into `mockdata/roster_seed.json`. This keeps auth usernames and the
   derived default passwords valid. The generator never reads its own output.
2. **Replaced `jobProfile.title` / designation with MoSPI designations.** The old
   titles were random NCO roles ("Police Constable", "Consul General") that
   cannot be mapped to statistical competencies. Designation now comes from tier
   + experience (ISS/SSS ladder). `department` is now the office's division
   name. `position_id` = `roleId`.
3. **Roles = office × designation** (76 roles). Every role requires its office's
   lead subject. Required levels come from `REQUIRED_LEVEL_BY_TIER`.
4. **Three profile-incomplete recruits** (experience 0, no education or career,
   `profileStatus: HRMS_SYNC_PENDING`). Without them `UNASSESSED` is
   unreachable: tenure and education always give some evidence. This modifies
   "kept" fields for 3 users on purpose.
5. **Profile `status` is derived from the self-claim, not from the hidden truth**,
   so it doesn't leak the latent level.
6. **Deleted `data/users.json`.** It was orphaned (nothing read it) and used
   different names for the same user ids.
7. **`courses.json` / `courses_1.json` are no longer loaded but were not
   deleted.** They are about 50 MB of real iGOT exports. Deleting them is easy to
   do later (`git rm`), while re-adding real data is not. Only the legacy
   `mock-igot-server/main.py` and `test_lang.py` still read `courses.json`.
8. **`/api/courses/enriched` now serves the one catalogue** in the old enriched
   shape. `frac_competencies` items are now `{id, name, category, level}`.
   Nothing in the repo calls this endpoint.
9. **`/api/frac/competencies` now returns the 40 catalogue competencies.** Items
   are a superset of the old `{competency_id, name, category, description}`
   shape. The admin FRAC table therefore shows the id space roles use.
   `?dictionary=igot` still returns the 331-entry CID dictionary.
10. **Rewrote FRAC descriptions.** They were lorem ipsum ("Qui doloribus
    consequuntur."), and they are the engine's retrieval query. Ids, names and
    types are unchanged. Level descriptors are per-type templates naming the
    subject.
11. **Crosswalk file = keyword rules, all `confirmed: false`.** 119/331 CIDs map.
    There is no human confirmation, so none is claimed. The engine consults it
    after `exact` and before embeddings (`curated_crosswalk`).
12. **Explicit `is_tpac: false` is authoritative** in the engine. Previously an
    NSSTA creator name alone made a course "inferred TPAC", which contradicts the
    catalogue saying otherwise. Absent field → old name heuristic.
13. **`_TIER_SENIORITY` aliases.** Profiles use `TIER1_APEX` / `TIER2_SENIOR`,
    which the table didn't know, so they silently fell to the junior default.
    They now map to the same bands as `TIER1_SENIOR` / `TIER2_UPPER`.
14. **Enrollment hours = catalogue `duration`** (via
    `HybridRecommendationEngine.course_hours`). The old 0.5 h × leafNodesCount
    rule remains as fallback for courses not in the catalogue.
15. **`MockIgotAdapter` reads `IGOT_MOCK_BASE_URL` / `IGOT_MOCK_TOKEN`** (same
    defaults). New external calls go through the adapter.
16. **Content-state snapshots only for in-progress enrolments.** Completed ones
    are derived by the mock server at request time. This keeps the data dir small
    (the TPAC programmes have 60–180 modules).
17. **GSBPM v5.1 sub-process list** is used although "5.2" was requested. I could
    not confirm a 5.2 sub-process list. The map is data (`mockdata/domain.py`),
    so a renumbering is a one-file change.
18. **Old generators retired.** `seed_data.py` is now a shim that calls
    `generate_mock_data.py`. `enrich_catalog.py` and the empty
    `generate_userdata.py` were removed. Running two generators is exactly how
    the data drifted.
19. **Format mix.** The TPAC share was tuned down (L3 6%, L4 22%, L5 40%),
    giving 71/514 TPAC programmes. With the first draft, 46% of courses were
    NSSTA-made.
20. **Data sizes.** `content_states.json`, `userdata.json`, `enrollments.json`
    and `course_outcomes.json` are written one record per line. Other files
    use `indent=1`. Content-state `progressdetails` is kept only on the module
    being read; completed modules keep `contentId/status/completionPercentage/lastAccessTime`.
    The data dir was 5.0 MB after B4 data and is 3.9 MB after these changes.
21. **Metrics script** `main-lms-backend/scripts/mock_data_metrics.py` computes
    every before/after number above, so they are reproducible.

22. **B1/B2 opportunity bands.** High is ≥ 20% of the office's officer-hours in
    the competency's sub-processes (about a day a week), Medium is ≥ 5%, and
    Low is anything less. The tie band is `OPPORTUNITY_TIE_BAND = 0.10` of the
    best gain/hour, which is well inside the noise of hour estimates, so it
    only reorders near-ties. Opportunity is never a multiplier and never hides
    a gap.
23. **Office workload model.** Officer-hours = sanctioned headcount (all staff,
    not only the 151 platform users) × 480 h per quarter × the office's
    sub-process weight share × U(0.85, 1.15). The cycle is FY 2026-27 Q2.
    Behavioural and management competencies map to GSBPM overarching processes
    (`OA.*`), so they can be scoped too.
24. **Admin views live in a new "Insights" tab**
    (`components/admin/WorkforceInsights.tsx`). This keeps AdminDashboard edits
    minimal; every later Phase B admin panel goes there too. Admin endpoints are
    in `routers/insights.py`. Singletons are shared through
    `services/app_state.py`, which avoids a circular import on `main`.
25. **Reference data loading.** `services/reference_data.py` loads each SCIL v6
    dataset through the adapter once at startup. It falls back to disk per
    file, with a warning, the same rule as the catalogue.
26. **Dev-server note.** `uvicorn --reload` watches all of `main-lms-backend/`,
    so editing tests or scripts restarts the backend (about 40 s). Once, an
    edit left a worker hung. I killed only that worker process (PID 16684) and
    the reloader started a fresh one. The user's reloader process was not
    touched.
27. **B3 mandatory course choice.** One organisation-wide course: the shortest
    non-classroom L1 information-security/data-privacy course. One per role:
    junior/mid roles get their lead subject at L2; senior/apex roles get their
    first behavioural competency at L3. Both are always the shortest
    non-classroom course, since APAR-linked mandatory courses are short online
    courses in practice. 7 of the 76 roles have no such course, so only the
    org-wide course applies to them.
28. **Mandatory courses are force-included even over budget**, and the plan
    reports `overBudget: true`. "Force-included" was the requirement. They are
    scheduled first. A later rung that a mandatory course already covers is
    absorbed, so no course is scheduled twice.
29. **Default plan = this quarter.** When `budgetHours` is absent, the budget is
    the ACBP `learningHoursPerQuarter` and the classroom cap applies.
    `?budgetHours=` gives a custom budget without the cap. `?unbudgeted=true`
    (new, additive) gives the full plan. This changes the default
    `/pathway` study plan: long plans are now split into "this quarter" plus
    "deferred". The frontend was updated to show that.
30. **Classroom cap = 30 h per quarter** (`CLASSROOM_CAP_HOURS_PER_QUARTER`),
    i.e. five 6-hour training days away from the desk. A 36–60 h TPAC programme
    therefore needs a quarter planned around it and shows as deferred with
    reason `classroom cap`.
31. **Learning hours per quarter** come from a choice list by tier, with 4 h
    less for field (FOD) staff and a floor of 14 h (56 h/year ≥ Karmayogi's
    50 h/year guidance).
32. **Metrics script.** It re-logs in on 401 (the access token expires during a
    151-user run) and measures pathways with `?unbudgeted=true`, so the numbers
    stay comparable with Phase A.

33. **B4 generates the B5 outcome dataset.** The data-driven edge inference
    needs measured pre/post gains, so `course_outcomes.json` (the B5 data) is
    generated in B4. B5 adds the uplift estimator on the same data.
34. **Outcome data is platform-wide.** Per-course effects on only the 151
    roster officials would rest on 1–3 learners per course. The iGOT
    assessment service covers every learner, so anonymised `lrn_…` learners
    are added in proportion to each course's enrolment count. Roster
    completions are included 1:1.
35. **Unknown prerequisite level → advisory, not blocking.** Blocking on an
    unmeasured level would dead-end plans for anyone with an UNASSESSED or
    out-of-profile prerequisite.
36. **A cyclic prerequisite set is rejected as a whole** rather than dropping
    one edge. There is no principled choice of which expert edge to drop, so a
    human must fix it; the cycle is logged and shown to the admin.
37. **Inference thresholds.** Min 8 learners per side, BH-FDR 10%, min effect
    0.20 levels, 400 seeded bootstrap resamples. Only the 2 planted groups
    reach the minimum size, so the screen's false-positive rate is untested
    here.
38. **Planted-group sample size.** Courses in a planted-precedence group get
    ≥ 18 platform takers (`PLANTED_GROUP_TAKERS`). Without that, the planted
    effects had 2–3 learners with the prerequisite, which was untestable.

39. **B5 propensity model.** Features are `[1, z, z², tenure, statistics
    degree]`, with z = preθ − (level − 0.5). A linear term alone could not
    represent "takers sit just below the course level", and IPW then barely
    beat naive.
40. **Comparison episodes spread uniformly over ability** (`U(0.1, 4.9)`, 60 per
    competency). With the first triangular draw only about 3 controls per
    competency had θ < 1. They are shared by every L1 course on that
    competency, which made the estimates noisy.
41. **The flag uses the unshrunk IPW CI**, and q̂ (shrunk) is used for
    display and ranking. Shrinking toward a positive level prior hid 2 of the
    4 planted courses from the flag.
42. **Measured uplift demotes, it does not re-score.** A flagged course is
    treated like a content-unsupported tag (last resort at its level, reason
    note, still shown). q̂ is not blended into `finalScore`, because most
    courses have few learners and all of this is synthetic.
43. **CI coverage of the planted truth is 80%, not 95%.** The intervals are
    conditional on the fitted propensity model and share control pools. This is
    stated in the doc and not hidden.

44. **K = the existing 6-term baseline.** SCIL v6 §3 names four channels.
    The old six terms (courses, certificates, quizzes, tenure, education,
    seniority, self-report) are the knowledge/prior side, so their b_k is
    channel K. A, U and S are fused with it. With no workplace evidence the
    fused score equals b_k exactly, so nothing changes for those competencies
    and the existing tests stay green.
45. **Channel values on the level scale.**
    - A: a passed Level-L work sample = L; a failed one = L − 0.5 ("not yet L").
    - U: the highest course level whose use the supervisor confirmed.
    - S: the latest rating.
46. **Floors.** A passed work sample (HIGH) and confirmed use (MEDIUM) are
    monotone floors in `resolve_level`, like course completion. A supervisor
    rating is never a floor, because raters are lenient.
47. **No leniency correction.** Estimating each rater's leniency needs
    repeated ratings per rater. With the equal placeholder weights, lenient
    ratings raise fused levels where K is weak; the confidence ceilings bound
    that when no objective evidence exists. This is documented as a TODO.
48. **Workplace evidence is served by the mock iGOT side** (APAR / utility
    survey / work-sample service) and merged per request with the LMS's own
    `EvidenceLog` rows. It is not written into `auth.db`, so the fixtures stay
    the single source.

49. **Decay does not change the displayed level.** The displayed FRAC level stays
    the monotone floor level; B6 requires `resolve_level` to stay monotone,
    and decaying it would make finishing a course eventually lower a level.
    Decay acts on the probabilistic μ/σ layer: the "estimated now" line, the
    expected-shortfall gap, the refresher flag and the foresight projection.
50. **Decay clock = newest dated objective evidence**, including the annual
    supervisor rating. A recent APAR rating therefore refreshes the clock for
    most competencies (evidence ages are mostly ~4 months). This is defensible
    because someone observed recent performance, but it limits how much decay
    shows up today.
51. **Population prior per competency** = the mean and SD of the fused μ over
    officials with assessed evidence in the workforce snapshot. The SD floor is
    0.6. Until the snapshot is built, the defaults are 2.0 ± 1.1.
52. **The workforce snapshot is built in the background** after startup
    (~2–3 min for 151 officials against the dev mock, sequential), with an admin
    refresh endpoint. Endpoints that need it return 503 until it is ready.
53. **New recruits have no APAR rating or work sample** (generator). Otherwise
    the workplace evidence made every competency assessed, and cold start was
    unreachable. This is also more realistic: a new recruit has not been
    through an appraisal cycle yet.
54. **Suppression: 1–4 are suppressed, 0 is shown.** A zero identifies nobody
    and is the most important risk signal. The single-point-of-failure flag is
    kept, as requested, even though it implies a count of one; the exact
    counts stay suppressed.
55. **Foresight constants.** `CAPABLE_LEVEL = 3` (FRAC "independently carries
    out the work") and `ANNUAL_ATTRITION = 0.03` are placeholders, not
    measured. There is a 36-month horizon with 6-monthly points and an
    "attrition only" comparison series.
56. **The TPAC agenda is drafts only.** Items are generated from four sources
    (coverage gaps with demand, capability risk, near-zero-uplift courses, new
    prerequisite suggestions), each `status: "draft"`. Nothing is decided or
    sent anywhere.

## Could not do / blocked

(nothing yet)

## Noticed but out of scope (not fixed)

- `routers/competency.py::upload_certificate` builds its FRAC list from course
  tags on each call, now over the whole catalogue (514 courses). It would be
  cheaper to read `fetch_frac_competencies()`.
- A stray backend process from an earlier session is listening on port 8077
  (`python -m uvicorn main:app --port 8077`). I left it alone.
- `datetime.utcnow()` deprecation warnings in `baseline_assembler.py`.
- The three chat test files fail to collect (`tests.fixtures` import). This was
  pre-existing and not touched.
