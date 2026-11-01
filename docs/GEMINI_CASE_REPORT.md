# Gemini-enabled supplied-case results — 1 November 2026

The owner explicitly authorized Gemini testing after the earlier handoff. Model/configuration and API client were left unchanged. Both local settings and the running localhost app reported `gemini-3.1-flash-lite`.

Command: `.venv/bin/python scripts/evaluate_supplied_cases.py docs/validation/supplied-cases-gemini.json --live`

All 11 supplied authored cases ran through the actual investigation pipeline with live Gemini extraction and evidence comparison. The runner observes real HTTP status codes without storing request headers, keys or response bodies. Tavily and official-source retrieval/caching remained enabled, with the existing deterministic verdict matrix and operation/provider budgets. Case starts were paced at least 33 seconds apart; no safeguards were disabled.

## Measured result

- Gemini HTTP requests: 22/22 returned 200.
- Structured extraction: 11/11 completed successfully.
- Evidence comparison: 11/11 completed successfully.
- No Gemini rate-limit or fallback outcome occurred in this run.
- Supplied verdict expectations: 10/11 matched; risk levels: 11/11 matched.
- Verdicts changed from the corrected Gemini-disabled run: 0.
- Median pipeline duration excluding deliberate between-case pacing: 5711 ms. Median individual Gemini HTTP duration: 1674 ms. These are local-run timings, not hosted latency guarantees.

| # | Case | Result | Supplied verdict match |
|---|---|---|---|
| 1 | Digital Arrest & CBI Impersonation | SCAM / HIGH | Yes |
| 2 | India Post Phishing Link | SCAM / HIGH | Yes |
| 3 | Fake Government Recruitment (Official PIB Contradiction) | UNSURE / HIGH | Expectation requires review |
| 4 | Remote Access / AnyDesk Banking Refund | SCAM / HIGH | Yes |
| 5 | Telegram / Part-Time Job Recharge Scam | SCAM / HIGH | Yes |
| 6 | Customs Duty Private Account Scam | SCAM / HIGH | Yes |
| 7 | 🛡️ Adversarial Prompt Injection Attack (Hackathon Showstopper!) | SCAM / HIGH | Yes |
| 8 | Official Cabinet Secretariat PIB Denial Notice | GENUINE / LOW | Yes |
| 9 | Negated Security Warning (Not a Scam) | UNSURE / MEDIUM | Yes |
| 10 | Normal Telegram Community Link (Not Phishing) | UNSURE / MEDIUM | Yes |
| 11 | Vague Non-Specific Notice | UNSURE / MEDIUM | Yes |

## Interpretation

Gemini is responding successfully with the configured model. Final verdicts still come from deterministic backend rules and validated evidence; enabling Gemini does not make every link safe or every suspicious claim provably false. The ordinary Telegram link and private application notice correctly remain unverified. The exact PIB excerpt plus matching official reference is GENUINE/LOW within the content-only scope; it does not authenticate a sender.

Case 3 remains UNSURE/HIGH: the supplied notice asserts a new 2026 recruitment, while the cited PIB denial was published on 23 May 2025. A historical denial alone does not establish whether that newly dated notice exists. This is the same documented expectation discrepancy as the previous run, not a Gemini availability failure.

The cases are authored development examples, not representative victim communications. Expectation-match counts are not real-world accuracy. HTTP 200 plus schema validation proves a response succeeded; it does not prove semantic interpretation is infallible. Safe Browsing remains unconfigured. No model settings or provider client changes were made for this test.

Raw per-case checks, source relationships, provider status, operational summaries, actual Gemini HTTP statuses and timings are in `validation/supplied-cases-gemini.json`. The ordinary unit suite also passed: **178 passed, 0 failed, 0 skipped**, with its existing TestClient deprecation warning.
