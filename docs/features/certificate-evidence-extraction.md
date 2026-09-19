# Certificate / Resume Evidence Extraction

An official uploads a PDF or image certificate (or resume). The platform maps it to
FRAC competencies with levels, dates and justifications, and writes them to
`EvidenceLog` right away as **documented** evidence, so the skill gap moves at once
(MEDIUM confidence, ceiling 3.5). An admin then approves the certificate, which makes
the evidence **verified** (HIGH, ceiling 5.0), or rejects it, which removes the evidence.

## Code

- `main-lms-backend/services/document_extractor.py`
  - `ExtractedCompetency` — `competency_id`, `competency_name`, `extracted_level`
    (1–5; 2.0 beginner / 3.0 intermediate / 4.0 advanced), `issue_date`,
    `justification`, `match_score` (local path only).
  - `CertificateExtractionResult` — `is_valid_credential`, `issuing_organization`,
    `extracted_competencies[]` (max 3), `extractor` (`"gemini"` | `"ocr+e5"`).
  - `frac_dictionary()` / `frac_by_id()` — the **canonical**
    `mock-igot-server/data/frac_competencies.json` (40 entries). These are the same
    ids that the recommendation engine and the skill-gap crosswalk use.
  - `DocumentExtractorService.extract(data: bytes, filename)` (async, in memory, nothing
    written to disk):
    1. `.pdf` → pypdf text layer. If a PDF has less than 40 characters of text (a scan),
       the embedded image of each of its first 3 pages is used instead.
       `.png/.jpg/.jpeg/.webp` → the image.
    2. **Gemini** if `GEMINI_API_KEY` is set: `services/media_quiz/llm.gemini_json`
       (async, model fallback chain, temperature 0). It is given the FRAC reference plus
       the text, or the images for scans. `_validated` keeps only real FRAC ids
       (an unknown id is re-matched by exact name, otherwise dropped), clamps levels
       to 1–5 and normalises dates.
    3. **Fallback `ocr+e5`**, used when there is no key or Gemini fails. Text for
       images comes from RapidOCR (`media_quiz.probe.get_ocr`). Each line of the
       document is embedded with multilingual-e5 (`get_embedder("chat")`) and compared
       by cosine with the FRAC descriptions (`encode_cached`, so it runs once). A
       competency is kept if it reaches `CERT_MATCH_FLOOR` (0.80) and is within 0.02 of
       the best match, top 3. Level, issuer and date come from keyword and regex rules
       (`_LEVEL_RULES`, `_issuer`, `normalise_date`: ISO, DD/MM/YYYY, "Aug 15, 2023",
       "15 Aug 2023", "Sept 2019", year only; future dates → None).
    - `ExtractionError` is raised when a document has no readable text, or when OCR
      is not installed and Gemini is not configured.
  - `python -m services.document_extractor` runs the local path on a mock certificate.
- `main-lms-backend/models/models.py::CertificateSubmission` (`certificate_submissions`)
  - `userId` (iGOT id), `filename`, `sha256` (unique per user, so re-uploads are
    deduplicated), `issuingOrganization`, `extractor`, `extraction` (JSON),
    `evidenceIds` (the EvidenceLog rows it wrote), `status`
    `PENDING | VERIFIED | REJECTED`, `reviewedBy`, `reviewNote`, `reviewedAt`.
    The table is created by `create_all` at startup.
- `main-lms-backend/routers/competency.py`
  - `POST /api/v1/competencies/upload-certificate` (any signed-in user). The user is
    always `current_user.username`, never taken from the request. Checks: extension
    allow-list, `CERT_MAX_MB` (default 10) → 413, empty file → 400, filename reduced
    to its `basename`. A SHA-256 duplicate returns the existing submission. For each
    competency it upserts a `Competency` row (the FK) and writes one `DOCUMENTED_CERT`
    `EvidenceLog` row: `grantedValue` = level, `issueDate` = the certificate date
    (today if none; this drives recency decay), and
    `metadata_payload{source:"certificate_upload", certificateId, verification, issuer,
    justification, extractor, matchScore}`. Then `app_state.invalidate_user`.
  - `GET /api/v1/competencies/certificates` — the caller's submissions.
  - `GET /api/v1/competencies/certificates/review?status=PENDING|VERIFIED|REJECTED|ALL`
    (admin) → `{certificates[] (+userId, reviewedBy, isValidCredential), pendingCount}`.
  - `POST /api/v1/competencies/certificates/{id}/review` (admin)
    `{decision: "approve"|"reject", note?}`. Approve → rows become `VERIFIED_CERT` and
    status `VERIFIED`. Reject → rows are deleted and status `REJECTED`. Reviewing an
    already reviewed certificate → 409. Both call `invalidate_user`.
- `main-lms-backend/services/baseline_assembler.py` — `VERIFIED_EVIDENCE =
  {VERIFIED_IGOT, VERIFIED_CERT}` feeds the verified channel (Pass 1). `VERIFIED_CERT`
  is also in `_DATED_EVIDENCE`. `DOCUMENTED_CERT` still feeds the documented channel.
- Frontend
  - `src/components/dashboard/CertificateUploadZone.tsx` (Certificates section of
    `LearnerDashboard`). It uploads through `api.uploadCertificate`, lists
    `fetchMyCertificates` with status chips (Documented · awaiting review / Verified /
    Rejected + reviewer note), and calls `onUploaded` (the dashboard's `refetch`) so
    the gaps update.
  - `src/components/admin/CertificateReviewQueue.tsx` — on the Admin **Actions** tab,
    below `AdminActions`. It has status filter pills, competency and level details
    with justification, and Approve / Reject with an optional note.
  - `src/services/api.ts` — `uploadCertificate`, `fetchMyCertificates`,
    `fetchCertificateReviews`, `reviewCertificate`. `lmsFetch` omits the JSON
    Content-Type header for `FormData` bodies.
- Tests: `main-lms-backend/tests/test_certificate_evidence.py` (upload → documented
  rows, dedupe, invalid document, admin approve/reject, 403 for learners, VERIFIED_CERT
  gives HIGH vs DOCUMENTED_CERT MEDIUM, invented LLM ids dropped, date parsing).

## In / out

- In: multipart `file` (PDF / PNG / JPG / WEBP ≤ 10 MB) + JWT.
- Out: `{status: "success"|"duplicate"|"no_evidence", message, certificate?, data?}`,
  where `certificate` is `{id, filename, issuingOrganization, extractor, status,
  verification: documented|verified|rejected, competencies[], reviewNote, createdAt,
  reviewedAt}`. `no_evidence` (not a credential, or no FRAC match) writes nothing.

## Connections

Feeds the **documented** channel (`DOCUMENTED_CERT`, weight .15, MEDIUM) and, after
approval, the **verified** channel (`VERIFIED_CERT`, weight .45, HIGH) of the baseline
formula in [skill-gap-analysis.md](skill-gap-analysis.md). `issue_date` drives recency
decay. Ids match the crosswalk's catalogue ids, so `rows_for` finds them under the
role competency too.

## TODOs / edge cases

- A certificate that matches only competencies outside the official's role profile is
  stored, but it does not change a gap on the dashboard (the career-readiness view
  still reads it).
- Approval does not award karma. Verified certificates are not listed in
  `/achievements`, which only lists iGOT completions.
- The admin cannot edit extracted levels or competencies before approving; the only
  choices are approve or reject.
- An approved certificate's level is not bounded by its provider's quality. A
  self-uploaded "Advanced" certificate from any issuer gives up to level 4 in the
  verified channel.
- The local path works best on English certificates. e5 is multilingual, but the
  level and issuer rules are English-only.
- Scanned PDFs use only the first embedded image of each page. PDFs made of vector
  drawings with no raster image and no text layer cannot be read without Gemini.
