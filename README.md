# Nivaar

**Clarity before action.**

Nivaar is a web app that helps people assess suspicious messages, links, screenshots and voice notes. It identifies dangerous requests, compares factual claims with available official evidence, and gives practical next steps.

Designed for English, Hindi and Kannada, Nivaar brings scam-pattern detection and source-based verification into one place. It is an independent tool and is not affiliated with any government agency.

## What you can check

| Input | How Nivaar handles it |
| --- | --- |
| Messages | Examines the text for manipulation, dangerous instructions and factual claims. |
| Links | Inspects destination patterns alongside the surrounding message. Submitted links are not opened by the verification pipeline. |
| Screenshots | Extracts text for review using local OCR, with an optional consent-based cloud reading path. |
| Voice notes | Transcribes uploaded or recorded audio with Sarvam, then checks the reviewed transcript. |

Audio transcription supports automatic spoken-language detection or an explicit language choice. Spoken language and report language are separate. Voice uploads are limited to 30 seconds and 10 MB; browser recording stops at 29 seconds to leave a small margin. Browser dictation is also available where supported.

## How a check works

1. **Add the suspicious content.** Review extracted text or a voice transcript, correct recognition mistakes, and remove personal details.
2. **Choose your situation.** Indicate whether you only received the message, sent money, shared credentials, granted app or remote access, suspect SIM compromise, or are unsure.
3. **Follow the investigation.** Nivaar identifies claims and tactics, inspects destinations, searches for relevant official material, and compares available evidence.
4. **Review the assessment.** Read the detected risks, claim-level findings, source quotations and limitations.
5. **Take a safer next step.** Use the situation-specific checklist, official reporting links, complaint draft or downloadable evidence report.

## Scam patterns covered

Nivaar combines local rules with AI-assisted extraction. Its action-risk checks include:

- Digital-arrest threats, coercive payment demands and transfers into so-called safe or verification accounts.
- Customs impersonation demanding payment into personal or private accounts, including English, Hindi and Kannada wording.
- Requests to disclose OTPs, PINs, passwords, passcodes or CVVs, including spoken variants such as “O T P” and “one-time password.”
- Remote-access and screen-control requests, including common remote-support application names.
- Task or rating jobs requiring deposits or wallet recharges to unlock commissions.
- Advance-fee prize or loan-release demands and payment requests promising guaranteed investment profits.
- Suspicious link patterns and authority-impersonation cues.

Negation and advisory checks help distinguish requests such as “share your OTP” from warnings such as “never share your OTP.” A warning in one part of a message does not automatically cancel a dangerous instruction elsewhere. Quoted speech, unfamiliar wording and transcription mistakes can still be misinterpreted.

## Understanding the result

| Result | What it means |
| --- | --- |
| **Scam signals detected** | A dangerous action or destination pattern, or sufficiently specific contradictory official evidence, was identified. It is a warning about the content, not proof of the sender’s identity. |
| **Matches official information** | The factual content meets the app’s source-verification requirements. This does not authenticate the sender or authorize a separate payment request. |
| **High-risk warning signs detected** | Risk signals are present even though factual verification remains inconclusive. The message should not be treated as safe to act on. |
| **We couldn’t verify this message** | Available evidence is insufficient to establish the material claims. This is neither a fraud finding nor a safety guarantee. |

High-risk results use a distinct red assessment card, a prominent **HIGH RISK** badge and an alert icon. The report explains authority, requested action and destination separately. A dangerous action can remain flagged even when the surrounding factual claims cannot be verified.

**Evidence Coverage measures how much could be checked against relevant source evidence. It is not a probability of fraud, a confidence score or an accuracy percentage.** Unresolved source conflicts remain visible in the claim ledger; they do not override an independently detected dangerous action.

## Evidence you can inspect

Nivaar uses a curated official-source registry and live search to discover relevant material. Source handling includes relevance ranking, publication-date metadata, bounded retrieval, exact-quote validation and retrieval timestamps. Cached material retains its original retrieval time.

Reports include a claim ledger, scoped explanations, source links and available official quotations. General advisories provide context; they do not prove that an individual parcel was seized, an account was suspended, or a caller represents an institution. Search snippets are not presented as fetched official evidence.

Limited phone, UPI and messaging-link checks explain syntax and context without claiming subscriber or payee ownership. Absence from a threat list is not evidence of safety.

## Support after a suspicious message

- English, Hindi and Kannada report summaries, guidance and complaint drafts.
- Sarvam read-aloud with stop controls, autoplay recovery and a matching-language device-voice fallback where available.
- An immediate-help checklist for people who already paid or shared sensitive information.
- Official reporting routes selected according to the situation the user reports.
- A copyable complaint draft for review; Nivaar does not submit complaints automatically.
- Signed report snapshots exported as evidence PDFs, plus printing and session-only recent checks.

## Privacy and reliability

Sensitive number patterns are masked before analysis, but this does not catch every personal detail. Review content before submitting it. Cloud image reading and Sarvam transcription require explicit consent. Browser dictation may use the browser’s own speech provider.

The application does not persist investigations or uploaded media. Recent checks remain in page memory. A bounded SQLite operations store tracks application events and request/provider budgets separately; third-party retention and infrastructure metadata have their own policies.

Provider availability and quota limits can reduce the checks that complete. Nivaar shows degraded operation and uses local checks where possible. It also includes request limits, upload bounds, concurrency controls, protected monitoring and structured operational alerts. These controls have single-instance limits; external notification delivery is not configured.

## Technology

Nivaar uses **Next.js and React** for the web interface and **FastAPI** for the investigation API. Gemini supports structured extraction and evidence comparison; Tavily or Brave supports source discovery; Sarvam handles transcription and speech output. Local Python rules determine verdicts rather than accepting an AI-generated verdict directly.

## Validation and limits

The latest detection update passed **251 backend tests** and the production build. Voice lifecycle checks cover recording cleanup, cancellation, format labels, playback state and autoplay recovery. Live Sarvam checks covered English, Hindi, Kannada and common browser audio formats; a codec-labelled MIME rejection was reproduced and fixed.

A focused 49-case development set contains 25 dangerous examples and 24 controls. After the detection changes, all 25 dangerous examples were detected and none of the controls was labelled a scam. This set was used to develop the rules: **it is not an independent benchmark or a real-world accuracy claim.** Broader detection still needs independently labelled, representative evaluation.

Nivaar cannot guarantee scam detection, authenticate senders, establish private account events or provide legal certification. AI interpretation, OCR, speech recognition and local rules can all be wrong. Inspect the evidence and verify consequential requests independently.

Further details:

- [Detection changes and focused evaluation](docs/DETECTION_QUALITY_2026_11_01.md)
- [Voice validation and recording fixes](docs/VOICE_VALIDATION.md)
- [Official advisory sources and their scope](docs/ADVISORY_SOURCES.md)
- [Architecture and operational boundaries](docs/ARCHITECTURE.md)
