# Provider setup and live acceptance

Gemini, Tavily and Sarvam are the selected providers. Credentials live only in the ignored local environment file or Render runtime environment. Authenticated smoke tests have passed for structured Gemini extraction, Tavily search, Gemini screenshot reading and Sarvam TTS-to-STT in English, Hindi and Kannada. Quotas and source availability are still recorded separately on every request.

## Local secrets

Run `python3 backend/setup_keys.py` from the repository root, or edit `backend/.env` locally. That file is ignored by Git and excluded from Docker. Restart `npm run dev` or `npm start` after changes. Never use `NEXT_PUBLIC_` for a provider secret.

| Key | Purpose | Where to obtain it |
| --- | --- | --- |
| `GEMINI_API_KEY` | Claim/tactic extraction, quote-grounded evidence comparison, opt-in cloud image reading | https://aistudio.google.com/api-keys |
| `SARVAM_API_KEY` | Uploaded or recorded speech transcription and read-aloud | https://dashboard.sarvam.ai/ |
| `BRAVE_API_KEY` | Live official-source Web Search | https://api-dashboard.search.brave.com/ |
| `TAVILY_API_KEY` | Alternative search provider; takes priority when both search keys exist | https://app.tavily.com/ |
| `GOOGLE_SAFE_BROWSING_KEY` | Optional threat-list checks | https://developers.google.com/safe-browsing/v4/get-started |

Use Gemini + Sarvam + Tavily for the selected configuration. Brave is an alternative and is not needed when Tavily is configured. OpenAI and Groq adapters are alternatives, not additional requirements. Model names are configurable. Current defaults follow the supplied master brief: `gemini-2.5-flash`, `saaras:v3`, and `bulbul:v3` with speaker `shubh`. Account access, model availability and quotas must be checked with the actual credentials.

## Brave instructions

1. Sign in to the Brave Search API dashboard.
2. Enable a plan/subscription that includes **Web Search API**. Review the dashboard's current terms, quota and billing before confirming any paid subscription.
3. Open the API keys section and generate a subscription key for that access.
4. Store the value as `BRAVE_API_KEY` in `backend/.env` or Render Environment. The backend sends it only in the `X-Subscription-Token` header to Brave's API.
5. Restart the server and inspect Connection status. “Configured” means present, not validated.
6. Run `npm run test:providers` to check authenticated structured output, search, and Sarvam TTS-to-STT in all three languages.

## Live acceptance after keys are added

- `/api/ready` must return `ready: true`. This checks presence only.
- `npm run test:providers` must pass. These calls consume provider quota.
- Test a novel redacted message. Trace must show successful Gemini extraction, Brave search, source retrieval and evidence comparison when sources are found.
- Inspect the cited quote against the actual official document. A search result snippet is never evidence.
- Test suspicious and genuine official content plus an ambiguous message; repeat in English, Hindi and Kannada.
- Upload a screenshot with cloud reading enabled and review the extracted text. Also test default local OCR.
- Upload and record a <=30-second voice note in each language after explicit consent. Test read-aloud and the device-voice fallback.
- Download the PDF. Its report ID, timestamp, verdict and hash must match the displayed report.
- Run Live benchmark. Inspect every failed case and each provider status; small synthetic-suite results do not estimate real-world accuracy.
- Exercise provider quota/invalid-key failures; the report must expose fallback and never imply a successful live check.

## API documentation used

- Gemini: https://ai.google.dev/api/generate-content and https://ai.google.dev/gemini-api/docs/structured-output
- Sarvam STT: https://docs.sarvam.ai/api-reference/speech-to-text/transcribe
- Sarvam TTS: https://docs.sarvam.ai/api-reference/text-to-speech/convert
- Brave: https://api-dashboard.search.brave.com/app/documentation/web-search/get-started
- Tavily: https://docs.tavily.com/documentation/api-reference/endpoint/search
- OpenAI alternative: https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=chat
- Groq alternative: https://console.groq.com/docs/api-reference
- Safe Browsing: https://developers.google.com/safe-browsing/v4/reference/rest/v4/threatMatches/find
