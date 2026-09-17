# Certificate / Resume Evidence Extraction

Upload a PDF certificate or resume; a **local** LLM maps its contents to FRAC
competencies with levels, dates and justifications. Fully offline — no cloud call.

## Code

- `main-lms-backend/services/document_extractor.py`
  - `ExtractedCompetency` — `competency_id`, `competency_name`, `extracted_level`
    (2.0 beginner / 3.0 intermediate / 4.0 advanced), `issue_date`, `justification`.
  - `CertificateExtractionResult` — `is_valid_credential`, `issuing_organization`,
    `extracted_competencies[]`.
  - `DocumentExtractorService` (`http://localhost:11434`, `llama3.2:3b`)
    - `extract_text_from_pdf(path)` — pypdf.
    - `parse_document(text, frac_dictionary)` — posts to Ollama `/api/generate`
      with `format = CertificateExtractionResult.model_json_schema()`,
      `temperature 0.0`, and an auditor system prompt (extract issuer, map to the
      nearest FRAC entry, normalise dates, no hallucination).
  - `python services/document_extractor.py` runs a self-test against a mock certificate.
- `main-lms-backend/routers/competency.py::POST /api/v1/competencies/upload-certificate`
  - PDF-only; writes to a temp file, builds the FRAC dictionary by scanning
    `competencies_v3` across `MockIgotAdapter.fetch_catalog()`, extracts, parses,
    and always deletes the temp file in `finally`.
- Frontend: `CertificateUploadZone` inside `src/pages/LearnerDashboard.tsx`.

## In / out

- In: multipart PDF.
- Out: `{status: "success", data: CertificateExtractionResult}`.

## Connections

Designed to feed the **Documented** evidence channel of the baseline formula
(`DOCUMENTED_CERT` rows in `EvidenceLog`, with `issue_date` driving recency decay).

## TODOs / edge cases

- **Incomplete:** the endpoint returns extracted competencies but does **not** persist
  an `EvidenceLog` row — the loop back into skill-gap analysis is not wired up.
- No auth dependency on the endpoint.
- Requires a running local Ollama with `llama3.2:3b`; otherwise it raises and the
  route returns a 500 with the Ollama error text.
- Temp file name is derived from the uploaded filename and written to the process
  CWD (`temp_upload_<filename>`) — no sanitisation, collisions possible under
  concurrency.
- `requests` is used here (sync) while the rest of the backend uses `httpx`; the
  call is synchronous inside an `async def` route, so it blocks the event loop.
- Uses a FRAC dictionary rebuilt from the course catalog rather than
  `data/frac_competencies.json`, so ids can differ from the recommendation engine's.
