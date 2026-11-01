# Supplied-case and link-handling report — 1 November 2026

## Scope

Eleven authored cases supplied by the owner were run through the existing investigation pipeline before and after fixes. Gemini was deliberately disabled inside the evaluation process only, respecting the owner’s separate Gemini/model work. No Gemini key, model setting, client or running-process configuration was changed by this evaluation. Tavily and safe official-document fetching were real; their status, source URLs, publication dates and caching are recorded in the JSON artifacts. This is not a full-provider test, a live server API benchmark, a representative dataset, or real-world accuracy.

## Why links often return UNSURE

The verdict matrix requires verified content/authority plus acceptable action and destination checks before GENUINE. A bare URL supplies no factual assertion or sender identity to verify. An official-looking domain, a legitimate messaging platform, or absence of a threat-list match is insufficient. Safe Browsing is not configured in this project. Arbitrary user URLs are never fetched directly; only reviewed official-source hosts are fetched for evidence. An unrecognized link therefore usually remains unverified, which is expected.

The claim that every message with a link returns UNSURE was not reproduced: supplied case 2 (India Post phishing context + lookalike link) returns SCAM/HIGH, while case 8 (exact official excerpt + matching reference) returns GENUINE/LOW. Case 10 is intentionally UNSURE/MEDIUM. Bare unknown HTTPS links now remain UNVERIFIED/MEDIUM instead of automatically raising HIGH risk. Bare official links also remain UNSURE without verified factual content. The link-only summary explicitly explains these limits and asks for the surrounding message.

## Findings and fixes

- Credential rule missed “share your bank PIN.” Added bank/banking/account qualifiers and kept negated warnings harmless.
- Ordinary messaging/unknown HTTPS links were treated as suspicious merely because their destination was unverified, producing inflated HIGH risk. Neutral unknown destinations remain UNVERIFIED; unsafe structure, sensitive context, explicit impersonation and threat-list signals retain separate handling.
- PIB language/region/query/path variants could consume both document slots and lose curated advisory IDs. Reviewed PIB releases are deduplicated by PRID and preserve registry metadata. Positive content-reference checks also recognize official page/share redirects for the same PRID. Submitted suspicious URL spellings are not rewritten.
- A historical recruitment denial cannot automatically contradict a newly dated notice. Added a date-scope guard rather than forcing the supplied 2026 case to SCAM.

## Results

Before: 9/11 verdict matches; 9/11 risk matches.

After: 10/11 verdict matches; 11/11 risk matches. The remaining verdict discrepancy is case 3's unsupported expectation, described below. These are expectation-match counts, not detection accuracy.

| # | Supplied expected verdict | Before | After | Match / explanation |
|---|---|---|---|---|
| 1 | SCAM | SCAM / HIGH | SCAM / HIGH | Dangerous arrest/secrecy/payment request. |
| 2 | SCAM | SCAM / HIGH | SCAM / HIGH | India Post claim conflicts with the supplied lookalike destination. |
| 3 | SCAM | UNSURE / HIGH | UNSURE / HIGH | Expectation needs review: the cited denial is from 23 May 2025; the input asserts a new 2026 recruitment. Kept UNSURE/HIGH without contemporary evidence. |
| 4 | SCAM | SCAM / HIGH | SCAM / HIGH | Remote-access installation and OTP disclosure request. |
| 5 | SCAM | SCAM / HIGH | SCAM / HIGH | Task deposit / commission-unlock request. |
| 6 | SCAM | SCAM / HIGH | SCAM / HIGH | Explicit private-account customs-duty demand matches fetched CBIC process warning. The @ybl suffix does not establish fraud or ownership. |
| 7 | SCAM | UNSURE / MEDIUM | SCAM / HIGH | Fixed missed bank-PIN wording. This tests the deterministic fallback, not universal LLM injection immunity. |
| 8 | GENUINE | GENUINE / LOW | GENUINE / LOW | Exact factual content matched a successfully fetched PIB release and corresponding official reference. Sender is not authenticated. |
| 9 | UNSURE | UNSURE / MEDIUM | UNSURE / MEDIUM | Negated credential warning; no dangerous request inferred. |
| 10 | UNSURE | UNSURE / HIGH | UNSURE / MEDIUM | Fixed risk inflation: ordinary Telegram destination remains unverified, not inherently suspicious. |
| 11 | UNSURE | UNSURE / MEDIUM | UNSURE / MEDIUM | Private application event cannot be verified using general public sources. |

## Source/expectation caveats

The exact cited PIB recruitment clarification is dated **23 May 2025**: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2130875. It denies the advertisement described at that time. A 2026 date in the submitted notice requires current matching evidence; retrieving the 2025 page today does not change its publication date. The input is suspicious, but this test does not establish it is definitively false.

Case 6's private-account instruction is the decisive scoped signal, corroborated against CBIC's guidance: https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2025648&lang=2&reg=48. A PSP suffix such as @ybl alone never establishes mismatch or payee identity.

## Verification artifacts

- `scripts/evaluate_supplied_cases.py docs/validation/supplied-cases-before.json` — baseline evaluation before fixes.
- `scripts/evaluate_supplied_cases.py docs/validation/supplied-cases-after.json` — rerun after fixes.
- Inputs: `backend/data/evaluation/user_supplied_2026_11_01.json`.
- `npm test -- --tb=short`: **178 passed, 0 failed, 0 skipped**; one pre-existing TestClient deprecation warning. Includes deterministic regressions for the supplied cases, neutral links, canonical source IDs, chronology and negation.
- No Gemini invocation or claim that the friend's model integration was validated.

Changes were made locally for review; no automatic GitHub push was performed for this task.
