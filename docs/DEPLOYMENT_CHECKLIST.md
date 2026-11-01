# Deployment checklist — upgrade validation, 1 November 2026

Target preserved: one Render Docker web service, Next.js public port and FastAPI loopback 8000, same-origin /api proxy. No Render deployment has been performed in this task.

- [x] Baseline recorded: 59 tests passed; audit's four failures not reproduced.
- [x] Windows-independent PDF temporary paths and explicit UTF-8 JSONL reads; existing assertions retained.
- [x] Shared typed API extensions; old request fields and SSE event types preserved.
- [x] Report digest/HMAC and PDF tamper rejection regression tests.
- [x] Upload consent, body/file limits, source allowlist, DNS pinning and redirect revalidation regression tests.
- [x] Quota cooldown, application budgets, concurrency, operations token and benchmark token protections tested. Benchmark now requires token in local mode too.
- [x] Real provider checks recorded in validation/upgrade-provider-tests.txt: Tavily PASS; Sarvam TTS/STT EN/HI/KN PASS; Gemini HTTP 429, unavailable. A configured key is not proof of working quota.
- [x] Frontend production build / type check succeeded during implementation. Final results and browser checks are in UPGRADE_VALIDATION.md.
- [ ] Docker container execution on Linux. Docker is not installed in this environment; Linux/native font dependencies have not been executed here.
- [ ] Python 3.11 container suite and native dependencies; local suite ran under Python 3.13. Python 3.14 is not installed and not claimed supported/tested.
- [ ] Actual Render build and hosted health/SSE/media/PDF smoke checks. Requires a connected Render service; no hosted URL is claimed.
- [ ] Successful live Gemini extraction/comparison once free-tier quota permits. Do not upgrade tiers merely for this validation.

## Hosting settings

Use existing GEMINI_API_KEY, TAVILY_API_KEY and SARVAM_API_KEY in hosting environment only. GOOGLE_SAFE_BROWSING_KEY stays optional; threat-list absence is never a safety conclusion. No new paid API is required. Keep REPORT_SIGNING_SECRET stable and BENCHMARK_TOKEN private; optionally separate MONITORING_TOKEN. Configuration templates contain placeholders only. Do not copy backend/.env into Git or image contexts.

Set ALLOWED_ORIGINS to exact deployed origins (no wildcard); RENDER_EXTERNAL_URL is also recognized by origin protection. Keep public access through Node; backend binds only loopback. Never trust user-supplied forwarded IP headers for identity. For durable budgets/alert records set OPERATIONS_DB on a persistent writable disk; default /tmp survives worker restart but not container replacement. Free Render hosting does not imply durable storage. SQLite is single-instance, not distributed.

SOURCE_CACHE_TTL_SECONDS and SOURCE_CACHE_PDF_TTL_SECONDS default to 900. Cached evidence retains original UTC retrieval time. Publication dates are nullable and independently validated. Store all backend times in UTC; the browser renders local time. Source page availability is not guaranteed.

Five request-scoped external investigation operations are shared by AI, search, reputation, source fetch and retry. A transient 502/503/504 permits at most one retry if both operation and free-tier budgets permit. 429 triggers cooldown without retry bursts. Exhausted checks degrade explicitly. Request/file limits remain 12 MB whole body, 8 MB images, 10 MB audio; recorder 30-second limit and provider duration enforcement remain as before. Uploads are request-scoped; no persistent user-upload store exists. Submitted images/audio leave the device only with consent.

Operational logs use application-owned event labels and durations, never raw messages, submitted URLs, phone numbers, VPAs or provider response bodies. A secret scan should be repeated before publication. Error alerts are available through structured logs/protected ops; off-device delivery is not configured.

Run `npm test`, `npm run build`, `npm run test:providers`, then smoke-test `/api/health`, `/api/ready`, `/api/analyze/stream`, consented media and signed PDF through the actual hosted proxy. `/api/ready` checks presence only. Do not run the entire live benchmark as a credential test; it consumes many quota-limited operations.
