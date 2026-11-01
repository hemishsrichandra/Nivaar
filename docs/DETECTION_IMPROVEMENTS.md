# Detection and operations implementation — 1 November 2026

Plan implemented: establish reproducible source provenance and scoped metrics; fix false positives and expand deterministic coverage; rank official evidence; preserve free-tier budgets; add persistent single-instance abuse controls and operational visibility; run regression and load checks.

## Evaluation scope

`backend/data/evaluation/sources.json` records downloads, hashes, retrieval timestamps, known publication dates, and failures. Snapshots are official public material, not a dataset of labelled victim messages. RBI's challenge/blocked page is explicitly unavailable. `cases.jsonl` contains 28 manually authored development examples derived from the advisories: 14 scam, 9 benign safety notices, 5 ambiguous. They include English, Hindi and Kannada examples but do not establish per-language accuracy. This is a development set used while changing rules, NOT an independent holdout or population accuracy estimate. No genuine-content verification is evaluated by the offline harness. Benign and ambiguous content should abstain, not authenticate a sender.

Reproduce: `.venv/bin/python scripts/collect_evaluation_sources.py`, then `.venv/bin/python scripts/evaluate_detection.py`. Results include scam precision/recall/F1, confusion counts, abstention, false-scam and false-genuine counts in `docs/detection-evaluation.json`. Comparing successive runs on this development set is a regression check only. We have not established an independently measured before/after improvement on real user messages. Next evaluation requires independent human labels, source/family-disjoint holdout cases, real consented messages, and separate full-provider and degraded-mode measurements.

Changes fix credential-warning negation and avoid treating OTP entry in an app as automatically dangerous. Kannada/Hindi credential requests and task-deposit/withdrawal-unlock patterns are covered. Unknown notices remain UNSURE. Deterministic rules can still misread quoted or reported speech; inspect evidence.

## Sources and free-tier behavior

Search candidates are ranked by query relevance, explicit official-reference matches, dated metadata and penalties for generic newsletters. Registry results no longer automatically occupy every slot. Exact duplicate URLs are removed. Allowlist expanded to CERT-In, UIDAI, NPCI, NIC and selected police authorities; arbitrary `.gov.in` hosts are not automatically trusted. HTML date metadata and PIB publication timestamps are parsed; future/invalid dates become unknown. Date is a ranking feature, not a guarantee a notice remains effective. Search snippets remain discovery-only.

Search results and fetched official documents have bounded 15-minute in-memory caches. Cached evidence retains its original retrieval timestamp. No submitted-message or AI-response cache is written. Gemini 429 starts a 60-second cooldown instead of repeating calls. Conservative local AI-call budgets default to 4/minute and 100/day; these are protective app settings, NOT a statement of provider entitlements. They can be lowered with `LLM_CALLS_PER_MINUTE` and `LLM_CALLS_PER_DAY`. Actual provider quotas may be lower. Exhaustion remains visible as fallback; no subscription upgrade is needed for these controls.

## Monitoring and alerts

`GET /api/ops` requires `Authorization: Bearer <MONITORING_TOKEN>` (or BENCHMARK_TOKEN if the former is absent). It returns bounded event counts and latest alert records. Requests, stage success/degradation, stage durations, provider HTTP failures, server errors and abuse blocks are recorded. Errors/provider failures/abuse blocks also emit structured warning logs immediately. No message bodies, keys, IP addresses or exception payloads are logged by this telemetry. This is a pull endpoint plus log alerts; external email, SMS or pager delivery is not configured. Render log collection or an external monitor must be connected for off-device notifications.

## Abuse and storage limits

SQLite transactions enforce global minute/day budgets (60 requests/minute, 500/day by default) plus signed browser-session budgets. Resetting cookies cannot bypass the global cap; forwarded IP headers are ignored. Explicit cross-origin submissions are blocked. Existing upload/body bounds and investigation concurrency limits remain. This protects provider costs even though Next proxies all clients through loopback. Session budgets are not user identity and global budgets can be exhausted by an attacker; a gateway challenge/distributed store would be needed for broader scale.

Set OPERATIONS_DB to a writable persistent-disk path to retain budgets/alerts across container replacement. Default `/tmp/nivaar-operations.sqlite3` survives app-worker restarts only; Render ephemeral filesystem replacement resets it. Free-tier deployment does not imply durable storage. Single-instance SQLite is not a distributed limiter. REPORT_SIGNING_SECRET should be stable for signed sessions.

## Load test

`.venv/bin/python scripts/load_test.py` sends 120 ASGI requests at concurrency 20 with stubbed analysis, enforcing real middleware/SQLite budgets. It makes no paid provider calls. `docs/load-test.json` records latency, statuses and failures. This measures app plumbing and abuse controls, not Gemini throughput, internet latency, Docker or Render capacity. Real deployed load testing remains necessary.

## Independent public SMS diagnostic

`scripts/evaluate_public_sms.py` downloads the UCI SMS Spam Collection (Almeida & Hidalgo, DOI 10.24432/C5CC84, CC BY 4.0). The archived ZIP hash and actual parsed counts are in `docs/public-sms-evaluation.json`. The local action-only engine abstained on all 5,574 records: 4,827 ham and 747 spam. This is an honest coverage limitation, not evidence of excellent specificity: the action rules also flagged none of the spam, and neither label certifies fraud. The corpus is historical and mostly outside the intended Indian multilingual use case. No tuning or training was performed on this corpus; keep it separate from the authored development set. Do not advertise a real-world accuracy percentage based on either evaluation.

## Verified results

59 automated tests pass; TypeScript passes. The 28-case authored development run has 14/14 scam examples flagged, zero false scam flags on 14 benign/ambiguous examples, 50% abstention and no GENUINE outputs. This is an intentionally conservative local-rule regression, not a full-pipeline accuracy score. Load run: 120 requests, concurrency 20, 60 accepted, 60 budget-blocked, zero server errors; p95 around 111 ms in this environment with upstream analysis stubbed. Production localhost was restarted with the changes; health is 200 and a browser-origin request through the frontend proxy reaches input validation (422 for an empty body).
