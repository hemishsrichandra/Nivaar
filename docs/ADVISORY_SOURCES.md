# Curated upgrade source inventory — checked 1 November 2026

These are reviewed source leads and contextual advisories, not stored investigation results. Runtime evidence always requires a successful safe fetch or an explicitly marked, unexpired runtime cache. Search snippets are never evidence. Full local retrieval records and normalized-text hashes are in `backend/data/source_inventory/manifest.json`. Publication date is separate from check/retrieval time. Where a source has no printed date it remains null; filenames are not dates.

| Family / ID | Official publisher and exact URL | Published | Applicability and limits |
|---|---|---|---|
| lottery_fraud / maharashtra-lottery-2020 | Maharashtra Cyber, Home Department; hosted by NCRP: https://cybercrime.gov.in/pdf/Cyber%20Security%20Awareness%20Booklet%20for%20Citizens.pdf | 2020-01-10, printed cover | OFFICIAL_WARNING. Printed page 17 illustrates unsolicited winnings with an advance/token payment. Does not deny every lottery or identify an organiser. Verified through web PDF extraction; local HTTP returned HTML. Its original publisher is Maharashtra Cyber, not an invented national authority. |
| sim_swap / delhi-police-sim | Delhi Police Cyber Crime Cell: https://cyber.delhipolice.gov.in/netbanking.html | Not printed / unknown | OFFICIAL_WARNING. Explains fraudulent replacement SIM issuance and receipt of OTPs/alerts. Cannot determine an individual SIM's network state. Local document retrieval succeeded. |
| customs_fraud / pib-2025648 | CBIC / PIB: https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2025648&lang=2&reg=48 | 2024-06-16 | OFFICIAL_WARNING, scoped to duty demands by phone/SMS/email into explicitly private accounts. Not a denial of all customs charges or proof of parcel status. Supplies DIN verification at https://esanchar.cbic.gov.in/DIN/DINSearch. Local retrieval succeeded. |
| loan_app_fraud / rbi-fame-digital-lending | RBI FAME, message 25: https://www.rbi.org.in/commonman/images/FAME202426022024.pdf | No publication date confidently extracted | OFFICIAL_WARNING. Check the bank/NBFC relationship on the lender's official site, review KFS/loan documents and app permissions. Does not verify a named app or its current registration. An initial HTTP failure was followed by a successful actual PDF download and text extraction; its successful snapshot is retained even if a later attempt fails. |

No new record has DIRECT_DENIAL strength. Applicability, exclusions, covered indicators, source retrieval time and `last_verified_at` are stored per record. General warnings remain context-only unless a separately validated process instruction exactly matches the submitted request. The customs rule never infers that an account is private merely from its UPI suffix.

Additional verified leads:

- PIB/MHA CFCFRMS reporting and 1930: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2290377&lang=1&reg=22 — posted 2026-07-28. Actual fetched text confirms 1930 and cybercrime reporting. Used for outgoing guidance, never incoming caller authentication.
- DoT Annual Report 2024–2025: https://www.dot.gov.in/static/uploads/2025/07/8df49d5b579439471bb8e506906d913a.pdf — publication date unknown; the report discusses international incoming spoofed calls. The supplied customs PIB URL is not a DoT WhatsApp advisory and is not misattributed as one.
- PIB publication of RBI lending warning: https://www.pib.gov.in/PressReleasePage.aspx?PRID=1749169&lang=2&reg=48 — 2021-08-26. Fetched successfully; historical supporting source, not represented as the latest lending regulation.

Unavailable leads (not inserted as live verified evidence): NCRP crime-category page returned unhelpful content; the supplied RBI systemhealth notification failed connection; NPCI product booklet failed HTTP; the Eluru alternate failed connection. See manifest for actual attempts. The application has no payee ownership API; it describes a UPI handle as a routing namespace only. It does not rely on an unavailable NPCI page as live evidence. Some other curated fallback leads also failed; failures are retained, not silently relabelled successful.

No consented private-message dataset was supplied. `evaluation/consented_redacted_cases.jsonl` is empty. Source snapshots and synthetic fixtures are never counted as national fraud accuracy.
