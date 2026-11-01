# Nivaar

Desktop-first fraud-verification web app: **standard Next.js + FastAPI**, deployable as one Docker service on Render. No ChatGPT login or Sites runtime.

## Local setup

Requires Node.js 22.13+ and Python 3.11+. Node 24 is supported locally.

```sh
git clone https://github.com/hemishsrichandra/Nivaar.git
cd Nivaar
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.lock
npm ci
npm run dev
```

Open **http://localhost:3000**. `npm run dev` starts both FastAPI on loopback port 8000 and Next.js on port 3000. Stop both with Ctrl+C.

Provider secrets belong in the ignored `backend/.env` file. Copy the template and add your **Gemini, Sarvam, and Tavily** credentials locally:

```sh
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your preferred editor. Restart the app after changes. Missing or unavailable providers are explicitly shown as basic/fallback checks in the interface. Provider keys alone do not guarantee quota or source availability.

See [provider setup and acceptance checks](docs/PROVIDER_SETUP.md) for dashboard links, Brave instructions, supported alternatives and the exact live test checklist.

## Production locally

```sh
npm run build
npm start
```

`npm start` runs the actual production Next.js server and FastAPI together. No dev server, Cloudflare Worker or external tunnel is required.

## Render deployment

1. Connect this repository to Render. Do not commit `backend/.env`.
2. In Render, create a **Blueprint** from that repository using the root `render.yaml`. Alternatively create a Docker Web Service using the root Dockerfile. If the repository contains a parent workspace, set the service root directory to `nivaar`.
3. Set `GEMINI_API_KEY`, `SARVAM_API_KEY` and `TAVILY_API_KEY` in Render Environment. Keep `REQUIRE_LIVE_PROVIDERS=true` for the production service.
4. The Blueprint generates `REPORT_SIGNING_SECRET` and `BENCHMARK_TOKEN`. For manual setup, generate stable random values yourself. Use only the benchmark token in the Live benchmark dialog; provider keys never go into the webpage.
5. Deploy. The app listens on Render's `PORT` (default 10000) and health check is `/api/health`. `/api/ready` reports missing provider keys separately. An `onrender.com` URL or your own custom domain works without ChatGPT authentication.
6. Run the live acceptance checks after credentials are installed. No Render deployment is claimed until an actual build and live service are verified.

The root Dockerfile uses the pinned Python lockfile and Next.js standalone build. Container-image execution can be verified on Docker or Render. The equivalent production process is testable with `npm start`.

## Implemented features

- Text and link intake, local screenshot OCR, opt-in cloud image reading, uploaded/recorded voice-note transcription, and browser dictation fallback.
- Gemini extraction and evidence comparison; optional OpenAI/Groq alternatives.
- Brave or Tavily live official-source search, bounded official document retrieval, and optional Google Safe Browsing checks.
- Exact-span tactic X-ray, deterministic authority/action/destination verdicts, and actual streamed investigation trace.
- English, Hindi and Kannada summaries, action guidance and complaint drafts. Sarvam read-aloud with device-speech fallback.
- Immediate emergency checklist, official action routing, copyable complaint and signed snapshot evidence PDFs with multilingual fonts.
- Session-only recent results, connection diagnostics and a live regression benchmark with synthetic provenance and a genuine official excerpt.

## Verification commands

```sh
npm run typecheck
npm test
npm run test:providers  # real provider calls; run after adding keys
curl http://localhost:3000/api/health
curl http://localhost:3000/api/ready
```

`npm test` uses deterministic fixtures and mocked HTTP provider contracts; it never validates real credentials. Authenticated provider tests are intentionally deferred until keys are supplied. Official-source availability can still be tested without credentials.

## API

- `GET /api/health`, `/api/ready`, `/api/config`
- `POST /api/analyze`, `/api/analyze/stream`
- `POST /api/ocr` — multipart image + explicit consent
- `POST /api/transcribe` — multipart short audio + language + explicit consent
- `POST /api/speak` — localized text to audio
- `POST /api/evidence-pdf` — exact report + signature, no repeated investigation
- `POST /api/benchmark` — production benchmark access token required

API schemas are available directly on the backend at http://127.0.0.1:8000/docs during local development.

## Boundaries

The app does not authenticate a sender, guarantee fraud detection, automatically file complaints or provide legal certification. AI interpretation can be wrong despite quote validation. Inspect the evidence. Number masking is not exhaustive de-identification. Upload consent and provider data handling are explained in the UI.

No database is required for the selected core workflow. Raw messages and uploads are not retained by the application; recent results live in page memory. Provider retention and infrastructure metadata are separate. Read [architecture and operational limits](docs/ARCHITECTURE.md).

Detection evaluation, free-tier budgets, protected monitoring and load-test instructions: [implementation and measured limits](docs/DETECTION_IMPROVEMENTS.md).
