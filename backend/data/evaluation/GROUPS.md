# Evaluation groups

Unit fixtures: cases.jsonl, benchmark_cases.jsonl and backend/tests contain synthetic regression examples. They are not real-world accuracy.

Official-source cases: official_source_cases.json contains real public official materials, dated provenance and expected contextual relation. Full successfully downloaded text is in ../source_inventory; lottery was verified using web PDF extraction while local HTTP was blocked. These are not independent victim messages.

Consented redacted cases: consented_redacted_cases.jsonl is intentionally empty. No real private communications or consent records have been supplied. Do not invent them. Any future row must document consent, redaction, independent annotation and held-out status.

Public SMS diagnostic remains separate; spam/ham is not fraud ground truth. No sample above supports a national accuracy claim.
