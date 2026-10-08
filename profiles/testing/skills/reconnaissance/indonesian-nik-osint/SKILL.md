---
name: indonesian-nik-osint
description: Profile a person from Indonesian NIK/KK data.
---

# Indonesian NIK / Kartu Keluarga OSINT

Turn raw KTP/KK data into a verified identity profile, then measure real public exposure.

## 1. Decode NIK (16 digits: PPRRKK-DDMMYY-NNNN)
- digits 1-2 province, 3-4 kab/kota (BPS code, e.g. 73 = Sulawesi Selatan, 64 = Kalimantan Timur)
- digits 5-6 kecamatan (e.g. 647205 = Samarinda Utara; 640213 = Samboja, Kutai Kartanegara; 731403 = Watang Pulu, Sidenreng Rappang)
- digits 7-12 DDMMYY of birth; **add 40 to DD for females** (e.g. 410757 -> female, 1957-07-01)
- digits 13-16 sequence (not check digits; do not validate)
- KK number has the same region prefix but is a separate household id; its region can differ from the person's address (traces a move/previous KK issuance).

Verify region codes against Wikipedia/BPS tables, never from memory.

## 2. Consistency checks to run
- Decode DOB and gender, compare to the printed umur / jenis kelamin.
- NIK birthplace prefix is where the *civil record was issued*, not necessarily the printed place of birth (common for migrants, e.g. born Parepare, NIK coded Samboja).
- Note migration trails: NIK region vs KK-number region vs printed address.

## 3. Passive OSINT (stay bounded)
- Exact-query the NIK and No. KK in Google/Bing/DuckDuckGo; a NIK with zero hits = no public exposure, which is itself the finding.
- Search the full name, then partial name + city/region. Check ASN/PNS directories (ppid.*.go.id), campus/ORCID/SINTA, court/electoral datasets.
- Social candidates: only report with a verifiable anchor (bio, location, matching photo). Otherwise label UNVERIFIED and never present as the subject.
- Numeric-only queries return keyboard/pricelist junk; ignore.

## 4. Reporting rules
- Separate OBSERVED (decoded, verified) from INFERRED (relationship, migration) from UNVERIFIED (social candidates).
- Never claim a Dukcapil/SIAK lookup you cannot perform; list official channels instead.
- One line on UU 24/2013 + UU 27/2022 (PDP) exposure risk, no lecturing.
- User prefers Indonesian output; PDF deliverable via styled HTML -> WeasyPrint (scratch dir per profile).
