# Galileo Smartpoint Cryptic Command Cheat Sheet

## 1. Availability & Schedule Commands
- `A12JANCGKSIN` : Availability all airlines
- `A12JANCGKSIN*GA` : Availability Garuda Indonesia only
- `A12JANCGKSIN1700` : Availability departures around 17:00
- `A#2` : Availability +2 days
- `A-1` : Availability -1 day
- `AR*TG` : Return availability with Thai Airways
- `TTBKKSYD` : Timetable BKK to SYD
- `TTL1` : Journey details from Availability line 1

## 2. Selling Flight Segments
- `N1Y1` : Sell 1 seat in Y class from line 1
- `N2Y1J2` : Sell connecting flight (Line 1 class Y, Line 2 class J for 2 pax)
- `N1Y3LL` : Waitlist segment
- `N1Y1AK` : Passive segment
- `0SQ151Y10DECCGKSINNN1` : Direct sell active segment

## 3. Mandatory PNR Elements (P.R.I.N.T.)
- **Phone:** `P.T*AGENCY NAME 021-123456 REF.ANDI`
- **Received:** `R.INDRA`
- **Itinerary:** (From `N1Y1` sell)
- **Name:** `N.SURNAME/FIRSTNAME MR`
  - Child: `N.SURNAME/FIRSTNAME MSTR*P-C08 DOB11NOV16`
  - Infant: `N.I/SURNAME/FIRSTNAME MISS*10JUN24`
- **Ticketing/Time Limit:** `T.TAU/15DEC`
- **Save PNR:** `E` or `ET` or `ER`

## 4. SSR, OSI, Seat & Passport (APIS)
- `SI.MOML` : Muslim Meal all pax
- `SI.P1/WCHR*PAX SICK` : Wheelchair request
- `SI.P1/SSRCTCMBAHK1/08123456789` : Passenger mobile phone
- `SI.P1/SSRCTCEYYHK1/NAME//GMAIL.COM` : Passenger email ('//' = '@')
- `GC*449/38/DOCS` : APIS Passport format entry
- `SA*S1` : Seat map segment 1
- `S.S1P1/14A` : Assign seat 14A for Pax 1 on Segment 1

## 5. Pricing & Ticketing Issuance
- `FDCGKSIN/GA` : Fare Display
- `FQN` : Fare notes and penalty rules
- `FS2JKT20NOVSIN25NOVJKT` : Fare shopping for 2 pax without booking
- `FQCSQ;` : Auto-price all segments & all passengers
- `*FF1` : Display stored Fare Calculation / TSF
- `TMU1Z0` : Set Agent Commission 0%
- `TMU1FINVAGT` : Set Form of Payment Invoice Agent
- `TKPDTD` : Issue electronic ticket
- `HMPR*E` : Display ticket sales report today
- `TRV/6181234567890` : Void ticket same-day
- `TRNE6181234567890/DDMMMYY` : Auto refund ticket

## 6. Advanced Troubleshooting & Pricing Workarounds
### A. Codeshare/Partner Sub-Class Mismatch & Open-Jaw Through-Fare
- **Problem:** International long-haul flight uses booking class B/H, but connecting partner flight (e.g. SQ codeshare operated by SAS / Lufthansa) only has class W/S available as live inventory (`HK1`), triggering `NO FARE FOR CLASS` or `CHECK ITINERARY`.
- **Solution (Passive Ghost Segment Trick):**
  1. Keep live segments active (`HK1`) on the available class (e.g. W/S).
  2. Direct-sell passive segments (`AK1`) matching the parent international booking class (e.g. B/H):
     `0SQ2736B12SEPCPHARNAK1`
     `0SQ2639H23SEPOSLCPHAK1`
  3. Price explicitly skipping mismatched live segments and including passive segments:
     `FQCSQ/S1-2.4.6-8`
  4. Store fare quote into PNR:
     `T:P1/S1-2.4.6-8/CSQ` (or `T.T1`)
  5. Verify stored calculation via `*FF1`, add TMU commission & payment, then issue via `TKPDTD`.

### B. Open-Jaw Surface Discontinuity
- Insert ARUNK segment when passenger travels overland between cities (e.g. ARN to OSL):
  `0A/3` or `Y3` (insert after segment 3).
