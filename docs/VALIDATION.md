# Validation — 1 November 2026

Selected UI: Civic Clarity, with navy/cobalt branding per the user's preference. UI UX Pro Max local design guidance and 21st public stepper/upload references informed the redesign. The 21st CLI design context and local UI review ran; review findings were informational colour-token consistency notes.

Verified locally:
- Next.js type check and production standalone build pass.
- 51 backend/security/provider-contract regression tests pass.
- The production standalone Node frontend and FastAPI backend run together on localhost:3000; frontend and proxied API return HTTP 200. /api/ready reports all three required credentials present (presence is not a quota guarantee).
- Actual Gemini structured extraction and image reading passed authenticated smoke tests.
- Actual Tavily allowlisted search passed.
- Actual Sarvam text-to-speech then speech-to-text passed in EN, HI and KN.
- A 14-case live regression rerun returned 14 expected verdicts and zero false-GENUINE results. The suite contains synthetic messages and one official excerpt and is not an accuracy estimate. Gemini returned HTTP 429 during batch evaluation; those cases used the disclosed rule/registry fallbacks.
- An initial false-GENUINE on a Hindi personal-application notice was fixed: generic public documents cannot verify private status, and verified content requires a matching supplied official reference. Four dedicated regression tests cover this guard.
- Browser checks covered the redesigned form, keyboard tab navigation, emergency dialog dismissal, streamed investigation, result focus, evidence grouping and a 390px responsive breakpoint. A fresh browser reload verified the production frontend with no development overlay.

Remaining external validation:
- Docker image execution and actual Render deployment have not been performed because Docker is not installed here and no Render service/repository has been selected.
- Provider quotas, upstream outages and model interpretation remain operational constraints. The UI now exposes degraded AI/search checks prominently rather than only inside the trace.

Credentials are kept in ignored backend/.env and were not printed, committed or copied into frontend assets. Required: GEMINI_API_KEY, TAVILY_API_KEY, SARVAM_API_KEY. Optional: GOOGLE_SAFE_BROWSING_KEY. Brave is an alternative search provider and is not required for this configuration.
