# Nivaar

A web-first citizen fraud verification workspace. Check suspicious messages and links, read screenshots locally, dictate a transcript, examine manipulation tactics, follow official evidence, and prepare a complaint and evidence PDF.

## Run locally

Requires Node.js 22.13+ (Node 24 recommended).

```sh
npm ci
npm run dev
```

Open the Local URL printed by the dev server (usually http://localhost:5173). No API keys are required. Production build: `npm run build`; serve the built Worker with `npm start`.

```sh
npm run typecheck
npm test
curl http://localhost:5173/api/health
curl -X POST http://localhost:5173/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"Share your OTP immediately","language":"en"}'
curl -X POST http://localhost:5173/api/benchmark
```

## What works

- Desktop workspace with English, Hindi and Kannada verdict summaries and complaint drafts.
- Text/link intake, browser-local screenshot OCR, browser microphone dictation, and browser speech output.
- Browser and server number-pattern masking; inspect the exact masked payload before submission.
- Deterministic tactic spans, destination inspection, four-step execution trace, bounded live official-source fetching, and a conservative verdict matrix.
- Official reporting links, immediate emergency checklist, copyable complaint, session-only recent results, evidence PDF with original UTF-8 JSON attachment, and a live regression drawer.
- Keyless server API; unavailable external services return honest failure states.

## Limits

This is a bounded rule-based verification tool, not a general AI investigator. It has four registry documents and does not search the open web, authenticate senders, query malware reputation, or auto-file complaints. Official sites may be unavailable. A failed fetch produces no evidence. GENUINE is intentionally narrow; a trusted link alone does not verify a message.

OCR downloads its engine and language models from public CDNs; images stay in the browser. Mic dictation may send audio to your browser vendor. Language voice availability depends on the operating system. Uploaded audio transcription is not configured. Review OCR and dictation before checking. Pattern masking is not exhaustive de-identification.

PDF text uses a standard Latin font. The complete UTF-8 report is included as a PDF attachment; browser Print can preserve displayed Hindi/Kannada text. Downloading re-runs checks and creates a fresh report.

## Structure

- `app/`: web workspace and `/api/analyze`, `/api/health`, `/api/benchmark`, `/api/evidence-pdf`, and explicit unavailable speech routes.
- `lib/server/`: extraction, safe official fetching, verdict rules, orchestration and PDF generation.
- `lib/privacy.ts`, `lib/types.ts`: shared privacy filter and contracts.
- `data/`: sourced advisory registry and clearly labelled synthetic regression cases.
- `tests/`: verdict, injection, domain-boundary, privacy and report tests.
- `docs/ARCHITECTURE.md`: boundaries, limitations, architecture and brief adaptations.
- `.openai/hosting.json`, `worker/`, `scripts/`, `vite.config.ts`: Sites hosting and build configuration.

## Evaluation

Run the Live benchmark from the sidebar to execute the actual pipeline against 12 synthetic EN/HI/KN cases derived from official advisory patterns. Results are measured on demand, not prefilled. This small suite contains no genuine-labelled cases and is not a real-world accuracy claim. False-GENUINE counts must be read with that limitation.

## Hosting

This codebase is configured for a private Sites deployment. `.openai/hosting.json` retains the Site identity. The Sites source helper commits, pushes and packages the verified source before publication. Keep secrets out of Git. No secrets are used by this build. A separate Python server, Render or Vercel project is not needed.

Source records and their dates are in `data/verified_advisories.json`. Nivaar is independent and is not affiliated with PIB, RBI, SEBI, DoT or any government department. Guidance and file hashes are not legal certification.
