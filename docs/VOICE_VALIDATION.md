# Voice validation — November 1, 2026

Recording and transcription were the user's reported failure. Gemini and model configuration were left unchanged.

## Changes

- Browser recording negotiates supported WebM/Opus, Ogg/Opus or MP4 formats and uses the correct file extension. Mono, echo cancellation and noise suppression are requested where available.
- Tracks and timers are released on setup failure, cancellation, navigation and completion. A late permission response cannot start an abandoned recording. Cancelled recordings are discarded rather than transcribed.
- Recordings stop at 29 seconds, leaving margin below the provider's 30-second ceiling. Empty and very short recordings show a useful error; uploads with readable duration over 30 seconds are rejected before transmission. If the browser cannot read duration, the provider validates the file.
- Spoken language defaults to Sarvam automatic detection and can be selected explicitly. Report language is independent. Legacy API clients that supply only `language` retain their prior behaviour.
- Transcription has a bounded wait and safe handling of empty/malformed responses. Recognised M4A and other supported extensions work even if an uploader supplies no MIME type.
- Read-aloud remains in its playing state until completion, supports stopping/cancelling, handles autoplay restrictions with a second Play action without another API request, releases object URLs, and reads the summary plus next steps within the text limit. Device fallback requires a matching installed language voice.
- WAV output is explicit, and all returned WAV segments are preserved.

## Automated checks

`npm run test:voice`: 11 tests pass covering playback lifecycle, blocked autoplay, pending-response cancellation, microphone cleanup, late permissions, recording cancellation, actual recorded-file delivery, format labels, fallback language and readout length.

`npm test`: 190 tests pass, including automatic/spoken language routing, legacy compatibility, unlabelled M4A, empty input, invalid provider responses and multiple WAV segments. One existing FastAPI TestClient deprecation warning remains.

`npm run build`: production build and TypeScript checks pass.

## Live Sarvam checks

Configured models were retained. Only synthetic public sentences were sent; no user microphone audio or private voice notes were captured.

| Check | Result |
| --- | --- |
| English TTS → WAV → auto STT | Passed; detected en-IN; 3.33 seconds |
| Hindi TTS → WAV → auto STT | Passed; detected hi-IN; 3.84 seconds |
| Kannada TTS → WAV → auto STT | Passed; detected kn-IN; 5.72 seconds |
| English WebM/Opus → auto STT | Passed |
| English M4A/AAC → auto STT | Passed |
| English Ogg/Opus → auto STT | Passed |
| Browser upload of Hindi WAV, English report language | Passed; Hindi transcript displayed in review field |
| POST read-aloud through localhost:3000 frontend proxy | HTTP 200 audio/wav; 37,632 frames at 22,050 Hz |

These are integration smoke tests, not a representative accuracy benchmark. English returned “before send money” for “before sending money”; Hindi returned “जच” for “जाँच”. Kannada preserved the meaning with orthographic differences. Review remains necessary. No claim of perfect transcription or measured real-world word error rate is made.

Repeat Sarvam-only checks manually with `.venv/bin/python -m backend.verify_voice`. This consumes existing Sarvam quota. FFmpeg is optional for the additional browser-codec checks; WAV checks run without it. The script reports detected language and transcript and deletes temporary audio afterward.

## Remaining device-specific verification

Physical microphone capture, OS/browser permission prompts, noisy rooms and actual speaker output need a check on the user's own device. Browser recording lifecycle is covered with controlled test doubles; uploaded audio and live APIs were tested end to end. Browser dictation still depends on the browser's own recognition support and selected/derived language. No new API key, provider upgrade or paid tier is required by these changes.

Provider references: [Sarvam transcription API](https://docs.sarvam.ai/api-reference/speech-to-text/transcribe), [Bulbul v3 guidance](https://docs.sarvam.ai/api/api-guides-tutorials/text-to-speech/bulbul-v3-best-practices).

## Follow-up: reproduced recording HTTP 400

The original checks missed a distinction between an uploaded audio file and MediaRecorder metadata. A direct Sarvam call using the exact same WebM bytes returned HTTP 400 with `audio/webm;codecs=opus`, but HTTP 200 with `audio/webm`. Sarvam rejected the parameterised MIME type against its exact allowlist before decoding audio. This was a confirmed integration bug, independent of API quota or microphone permission.

The recorder now uses the base MIME type on its completed File while retaining codec selection for recording. The speech adapter independently strips MIME parameters, whitespace and case differences before forwarding to Sarvam, covering old browser tabs and other upload clients. Audio bytes are unchanged. Six regression cases cover the adapter and full upload route; the recorded-file test now checks the upload-safe MIME label.

After restarting localhost, real requests through `localhost:3000/api/transcribe` using `audio/webm;codecs=opus` and `audio/ogg;codecs=opus` both returned HTTP 200 and the expected synthetic English transcript. Updated totals: 196 backend tests and 11 browser voice lifecycle tests pass; production build passes. The repeatable Sarvam-only smoke test now includes browser-style codec parameters. Physical microphone capture remains device-specific and was not recorded during these checks.
