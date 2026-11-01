# Upgrade validation — 1 November 2026

## Implemented behavior

Existing Next.js/FastAPI architecture and design were extended. The result adds typed per-claim findings, explicit authority/action/destination reasons, conservative phone/UPI/platform findings, source-conflict handling and deterministic Evidence Coverage. The four advisory families have reviewed official provenance and OFFICIAL_WARNING strength, never universal denial rules. The existing emergency dialog and main-input situation selector reuse the canonical EN/HI/KN checklist data shared with the backend. Claim text, suspicious spellings, source quotations and identifiers remain faithful; explicit phone numbers are preserved locally, then phone/UPI tokens are removed from AI text payloads. Bare national numbers/unknown prefixes are UNPARSED rather than assigned a country. No subscriber, telecom network or payee ownership lookup is present. The only same-purpose official phone comparison currently supported is the published outgoing national financial-cyber-fraud helpline when its matching official evidence is actually available; incoming caller IDs are never authenticated.

Comparison validation checks exact quotations, IDs, material numbers, capitalized identifiers, negation and scoped relation conditions. Rejected material comparison entries block a positive authority conclusion. This conservative mechanism is not a proof of semantic entailment and can abstain on valid claims. General advice never establishes a private account/application event. A verified public excerpt does not identify its sender. No final verdict or public success-rate claim comes directly from a model.

## Tests and measurements

- Baseline: `npm test` — 59 passed, 0 failed, 0 skipped. The supplied audit's four failures did not reproduce. Its three language-specific hardcoded PDF paths and platform-default JSONL read were nevertheless fixed without deleting assertions. See validation/upgrade-baseline-tests.txt.
- Final: `npm test -- --tb=short` — **162 passed, 0 failed, 0 skipped**, one existing FastAPI/Starlette TestClient deprecation warning. See validation/upgrade-final-tests.txt. Local Python 3.13 only.
- `npm run build`: PASS, including Next.js TypeScript compilation. `npm run typecheck` also passed during implementation.
- Added tests cover parsing/negative cases, platform lookalikes, scoped advisory applicability, private/generic evidence, exact quotes/negation, conflicts, coverage/N-A/determinism, model tactic provenance, shared situation guidance in all languages, schema references, transient retry, strict operation budget, cached timestamps/expiry, DNS revalidation and IPv4/IPv6/private/alternate URL forms, privacy and signed-PDF compatibility.
- Internal benchmark data now includes additional authored family/identifier cases; protected endpoint reports false-SCAM and false-GENUINE separately, abstentions, per-language/group outcomes, source-validation failures and per-case latency. Zero evidence alone is not counted as a source-validation failure. Official-source cases and consented-message files are separate. No new real-world accuracy percentage is claimed. No consented private dataset was supplied; its file is intentionally empty.

## Actual integrations

`npm run test:providers` used real credentials, without printing them:

- Gemini structured output: HTTP 429 (RATE_LIMITED); no successful new live Gemini reasoning result is claimed.
- Tavily official-source search: PASS.
- Sarvam actual TTS followed by STT: PASS in English, Hindi and Kannada.
- Safe Browsing: not configured; no new key required, absence is visible.

Full output: validation/upgrade-provider-tests.txt. Mocked HTTP contract tests cover Gemini structured extraction, OCR, transcription and read-aloud failure/success paths; they are not authenticated provider results.

## Local production and browser checks

Production standalone Next.js and FastAPI started successfully at localhost:3000. Health/ready/config returned 200; ops and benchmark without a token returned 403. Readiness checks presence only. See validation/upgrade-local-http.json.

An authored customs private-account SMS example exercised actual live official-source retrieval and the production SSE proxy, then a repeated request exercised explicit cached evidence. Result: SCAM from the scoped requested-action rule, two material input clauses left NOT_FOUND, authority/recipient not authenticated, 25/100 coverage, Gemini quota fallback visible, and money-sent guidance with 1930 first. This is a real pipeline execution on a synthetic input, NOT a real victim message or accuracy measurement. Six trace events were observed. The PDF returned 200 with valid PDF bytes; modifying the signed report returned 400. Publication date stayed 2024-06-16 and original retrieval timestamps were preserved on cache hits. See validation/upgrade-live-flow.json.

Browser inspection verified the new disclosure hierarchy, exact source behind the customs-process assessment, removal of an unrelated trade result, immediate money-sent checklist, the existing emergency dialog switching to credential-recovery guidance without a payment-first checklist, current-session history and clearing only our authored test result. Kannada SIM guidance and selector were checked at 390px: page width equalled viewport width, no horizontal overflow. Existing mobile menu, keyboard focus and reduced-motion styles are retained. Some technical and pre-existing interface labels remain English; this is not a claim of complete UI translation. The report's summaries, rescue actions and principal finding explanations support EN/HI/KN. Live device microphone permissions and all OS-specific dictation paths were not revalidated.

## Gemini handoff

After the validation above, the owner asked that another collaborator handle Gemini/model selection. No further Gemini calls, model-setting edits or client changes were performed after that request. Earlier reliability changes in backend/services/llm_client.py remain visible for that collaborator to review; they were not reverted over possible concurrent work. The test/provider outcomes above describe the completed checks before this handoff.

## Remaining deployment and evidence limits

No Render deployment was performed. Docker, Python 3.11 and Python 3.14 are not installed here; Linux native PDF dependencies and the actual hosted proxy need verification on the target environment. Do not advertise Python 3.14 support from this run. See DEPLOYMENT_CHECKLIST.md for owner hosting actions. Application behavior was checked locally, not against a public production URL.

Some official leads were blocked. The lottery booklet was verified using web PDF extraction while local HTTP returned HTML; it is not served as a successful runtime fetch. RBI FAME was successfully downloaded between intermittent failures. Source failures are retained in the inventory. Runtime evidence still requires a successful bounded safe fetch/cache. One in-process five-operation budget covers investigation provider/search/reputation/fetch/retry operations; skipped checks reduce coverage and stay visible. PDF parsing and native speech behavior remain dependent on supported libraries/providers. SQLite operational state is single-instance and is lost on ephemeral container replacement unless a persistent path is configured.

Known-secret matching found zero configured credential values in tracked/proposed files and production client JavaScript. .env is ignored. No raw input or identifiers were added to operations logging. No automatic complaint filing, message sending, payments, new accounts, extra provider or persistent investigation history was added.

## Exact file inventory

The following paths are the files changed/added relative to the initial clean checkout. No commit or push was performed as part of this upgrade.

- `.env.example`
- `Dockerfile`
- `README.md`
- `app/cinematic.css`
- `app/page.tsx`
- `backend/.env.example`
- `backend/data/benchmark_cases.jsonl`
- `backend/data/verified_advisories.json`
- `backend/main.py`
- `backend/schemas.py`
- `backend/services/action_router.py`
- `backend/services/claim_extractor.py`
- `backend/services/evidence_pdf.py`
- `backend/services/input_parser.py`
- `backend/services/investigation_agent.py`
- `backend/services/llm_client.py`
- `backend/services/official_fetcher.py`
- `backend/services/official_search.py`
- `backend/services/source_ranking.py`
- `backend/services/url_checker.py`
- `backend/services/verdict_engine.py`
- `backend/tests/test_core.py`
- `backend/tests/test_operations.py`
- `data/verified_advisories.json`
- `docs/ARCHITECTURE.md`
- `lib/privacy.ts`
- `lib/types.ts`
- `backend/data/evaluation/GROUPS.md`
- `backend/data/evaluation/consented_redacted_cases.jsonl`
- `backend/data/evaluation/official_source_cases.json`
- `backend/data/reporting_channels.json`
- `backend/data/situation_guidance.json`
- `backend/data/source_inventory/alt_loan.txt`
- `backend/data/source_inventory/alt_sim.txt`
- `backend/data/source_inventory/customs.txt`
- `backend/data/source_inventory/helpline.txt`
- `backend/data/source_inventory/loan.txt`
- `backend/data/source_inventory/manifest.json`
- `backend/data/source_inventory/phone.txt`
- `backend/services/finding_language.py`
- `backend/services/identifiers.py`
- `backend/services/query_builder.py`
- `backend/services/report_findings.py`
- `backend/services/situations.py`
- `backend/tests/test_upgrade.py`
- `components/situation-control.tsx`
- `components/verification-findings.tsx`
- `docs/ADVISORY_SOURCES.md`
- `docs/DEPLOYMENT_CHECKLIST.md`
- `docs/UPGRADE_BASELINE.md`
- `docs/UPGRADE_VALIDATION.md`
- `docs/validation/upgrade-baseline-tests.txt`
- `docs/validation/upgrade-final-tests.txt`
- `docs/validation/upgrade-live-flow.json`
- `docs/validation/upgrade-local-http.json`
- `docs/validation/upgrade-provider-tests.txt`
- `scripts/verify_upgrade_sources.py`
