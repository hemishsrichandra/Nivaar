# Detection and high-risk presentation — November 1, 2026

## Confirmed failure and fix

The supplied Kannada voice transcript contains a customs SMS demanding payment of 12,500 into a personal account, followed by a safety warning. The old action rules missed Kannada payment wording, spoken credential variants and several dangerous compound requests. With no specific claim contradiction, those misses produced `UNSURE`; the UI gave even a high-risk result a generic “couldn't verify” heading.

The exact transcript now produces `SCAM / HIGH` in a full localhost browser investigation. The summary identifies the customs payment into a personal/private account. The live check fetched the CBIC/PIB customs advisory as background context; no individual parcel seizure or sender identity was declared verified. Both successful and unavailable AI extraction are covered in controlled pipeline tests, with no fetched documents required to recognize the dangerous action.

The warning at the end of this transcript is preserved. Classification flags the unsafe embedded request; it does not establish who authored the narrative. A standalone Kannada safety advisory remains outside the scam class.

## Detection changes

- Added local patterns for spoken OTP/one-time-password variants, credential disclosure, remote-control requests, digital-arrest claims, so-called safe accounts, task deposits, advance-fee payout demands and payment requests promising guaranteed investment profits.
- Recognized English, Hindi and Kannada private-account customs demands, including the user's original transcription spelling. Matching uses action and private-account context in the same clause.
- Scoped negation and advisory handling protect “never share”, anti-scam warnings and benign payment controls. A caution in one sentence does not erase a dangerous demand in another.
- Model-generated tactic labels cannot independently promote a verdict. Dangerous action/destination findings take precedence over unresolved conflicts in public factual claims; conflicts remain visible in the claim ledger.
- Preserved conservative handling of bare links, ordinary notices, unknown sender identity and unverified public claims. Insufficient evidence alone never establishes fraud or authenticity.
- High risk now has a distinct red card, a bright filled uppercase badge with an alert icon, and a risk-specific headline even when factual verification remains inconclusive. Dangerous-action summaries name the detected reason.

## Focused regression results

Dataset: `backend/data/evaluation/action_quality_2026_11_01.json`. It contains 48 synthetic paraphrases/controls derived from official advisories and the user's exact transcript. Labels concern whether an unsafe scam-pattern request appears, not factual verification of a sender.

| Metric on these 49 cases | Before | After |
| --- | ---: | ---: |
| Dangerous requests detected | 4 / 25 | 25 / 25 |
| Dangerous requests missed | 21 | 0 |
| Controls incorrectly labelled scam | 3 / 24 | 0 / 24 |
| Precision | 57.1% | 100% |
| Recall | 16.0% | 100% |

These are development regression results. The set was used to develop the rules, is small and intentionally focused on known gaps, and is not an independent holdout or a population accuracy estimate. The original failure's transcript was pasted into the browser; new physical microphone capture was not tested in this follow-up. Ordinary speech-recognition errors remain possible.

Three additional unseen-wording controls exposed an overly broad loan-fee rule during development; it was narrowed. Normal official-portal loan processing fees remain inconclusive rather than automatic fraud. All 251 backend tests and the production build pass. Existing voice lifecycle tests previously passed and voice files were not changed by the detection patch.

Repeat the offline focused evaluation without using API quota:

```
.venv/bin/python -m backend.evaluate_actions
```

## Official source basis

- [CBIC customs impersonation and private-account payment advisory](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2025648) — posted June 16, 2024; fetched during the live browser test as context.
- [MHA digital-arrest impersonation advisory](https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=2020570&lang=2&reg=48).
- [RBI digital banking safeguards](https://rbikehtahai.rbi.org.in/safeguards-for-digital-banking.html).
- [SEBI scam warning signs](https://investor.sebi.gov.in/spot-any-scam.html).
- [MHA investment/task-fraud advisory](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1982936&lang=2&reg=48).
- [Bank of Baroda cyber-fraud awareness](https://bankofbaroda.bank.in/cyber-fraud-awareness).

No Gemini model, API key or tier settings were changed. Existing local voice MIME fixes remain in the checkout.
