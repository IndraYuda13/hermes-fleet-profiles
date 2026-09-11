---
name: galileo-smartpoint-ticketing
description: "Use when operating Galileo GDS, Smartpoint, & ticketing."
version: 1.0.0
author: ORION
license: MIT
metadata:
  hermes:
    tags: [galileo, travelport, smartpoint, gds, ticketing, airline-reservation, pnr, iata, ndc]
    category: productivity
---

# Galileo Smartpoint & IATA Ticketing

Comprehensive reference and execution guide for Travelport Galileo Smartpoint GDS (Global Distribution System), PNR management, cryptic command flows, fare shopping, auto-pricing, manual fare building, and e-ticket issuance/servicing.

## Core Navigation & Terminal Syntax

| Symbol | Function |
| :--- | :--- |
| `@` | Change / Edit entry |
| `*` | Display / Retrieve data |
| `-` | Dash / Minus |
| `+` | Plus |
| `Y` / `0A` | ARUNK (Arrival Unknown / Open-jaw segment) |
| `>` | Start of Message (SOM) |
| `I` | Ignore current transaction / buffer |
| `MD` / `MU` | Move Down / Move Up |
| `MB` / `MT` | Move Bottom / Move Top |
| `Ctrl + W` | Clear active command window |
| `Ctrl + S` | Clear all command windows |
| `Ctrl + B` | Print screen / grid view |

## Encode / Decode Reference

```text
.CE BANGKOK          # Encode City Name -> BKK
.CD SIN              # Decode Airport Code -> Singapore
.AE GARUDA           # Encode Airline -> GA
.AD SQ               # Decode Airline Code -> Singapore Airlines
.LE INDONESIA        # Encode Country -> ID
.LD NL               # Decode Country -> Netherlands
.EE BOEING 777       # Encode Aircraft Equipment
.ED 77W              # Decode Equipment Code
@LT LAX              # Check Local Time at airport/city
DCTSIN               # Display Minimum Connecting Time (MCT) at SIN
```

## Mandatory PNR Elements (P.R.I.N.T. Cycle)

Every valid Booking File / PNR requires all 5 mandatory fields before End Transaction:

```text
1. PHONE (P.)
   P.T*VAYA TOUR 021-123456 REF.ANDI     (Agency contact)
   P.B*COMPANY 021-7654321 REF.BUDI      (Business phone)
   P.JKTE*NAME--SURNAME//GMAIL.COM       (Email: '//' = '@', '--' = '_')

2. RECEIVED (R.)
   R.INDRA                               (Received from caller/agent)

3. ITINERARY (Sell Segment)
   A12JANCGKSIN*GA                       (Check availability)
   N1Y1                                  (Sell 1 seat class Y from line 1)
   N1Y1J2                                (Connecting: Class Y line 1, Class J line 2)
   0SQ151Y10DECCGKSINNN1                 (Direct sell active segment)

4. NAME (N.)
   N.SURNAME/FIRSTNAME MR                (Adult)
   N.SURNAME/FIRSTNAME MSTR*P-C08 DOB11NOV16  (Child with DOB/age)
   N.I/SURNAME/FIRSTNAME MISS*10JUN24    (Infant with DOB)

5. TICKETING / TIME LIMIT (T.)
   T.TAU/15DEC                           (Ticket limit date)

END TRANSACTION:
   E / ET / ER                           (Save and display assigned PNR code)
```

## Optional PNR Fields & SSR / APIS

```text
# Contact & Mobile SSR (IATA Standard)
SI.P1/SSRCTCMBAHK1/08123456789           # Mobile phone contact
SI.P1/SSRCTCEYYHK1/USER//DOMAIN.COM      # Email address contact

# Passport Data (APIS / DOCS)
GC*449/38/DOCS                           # APIS Passport template format

# Frequent Flyer
M.P1/SQ88256123                          # Add FFP number to Passenger 1

# Special Service Requirement (SSR) & Meals
SI.MOML                                  # Muslim Meal for all pax
SI.P1/VGML                               # Vegetarian Meal for Pax 1
SI.P1/WCHR*UNABLE TO WALK DUE ILLNESS    # Wheelchair request

# Advance Seat Request
SA*S1                                    # View seat map for Segment 1
S.S1P1/14A                               # Assign seat 14A for Pax 1 on Segment 1
```

## PNR Maintenance & Servicing

```text
# Retrieve PNR
*PNRCODE                                 # Retrieve by Record Locator
*-SURNAME                                # Retrieve by passenger name
*VL                                      # View Vendor Locator (Airline PNR)

# Split PNR
*PNRCODE
DP1                                      # Divide Passenger 1
R.AGENT
F                                        # File split
R.AGENT
ER                                       # End and save split PNRs

# Copy PNR
*PNRCODE
REALL                                    # Repeat all data into fresh booking
RESALL                                   # Repeat all flight segments

# Cancellation & Segment Cleanup
X2                                       # Cancel Segment 2
XI                                       # Cancel entire itinerary
@1XK                                     # Purge cancelled/HX/UC/NO segments

# Queue Management
QCA                                      # Check active queues
Q/40                                     # Open Queue 40
QR                                       # Remove from queue & next
QEB/75CI                                 # Transfer PNR to specific PCC
```

## Fare Pricing, Shopping & Ticket Issuance

```text
# Fare Display & Shopping
FDCGKSIN/GA                              # Fare Display point-to-point
FQN                                      # Display Fare Rules & Penalties
FS2JKT20NOVSIN25NOVJKT                   # Low-Fare Shopping without PNR
FS++-BUSNS                               # Fare shopping for Business cabin

# Auto-Pricing (FQ)
FQCSQ;                                   # Price all segments & passengers
FQCGA/S2-4/P1.3                          # Price specific segments & pax
*FF1                                     # Display stored Fare Calculation (TSF)
FXALL                                    # Purge stored unissued fare quotes

# Ticketing Issuance (Auto-Price)
TMU1Z0                                   # Set Commission to 0%
TMU1FINVAGT                              # Set Form of Payment (Invoice/Cash)
TKPDTD                                   # Issue e-tickets for stored fare quote

# Daily Reports, Void & Refund
HMPR*E                                   # Display daily ticket sales report
TRV/6181234567890                        # Void e-ticket (same-day issuance)
TRNE6181234567890/DDMMMYY                # Process Automated Ticket Refund
```

## Advanced Workaround: Codeshare / Interline Fare Alignment (Passive Segment Pricing)

When long-haul flights (e.g. SQ long-haul class `B` or `H`) require partner/codeshare connecting flights (e.g. SAS intra-Europe) to match the international parent booking class for through-fare calculation, but partner live inventory only has lower/different classes (e.g. `W` or `S` `HK1`), auto-pricing fails (`NO FARE FOR CLASS`).

**Resolution Protocol:**
1. Retain live segments (`HK1`) on available classes (e.g. Seg 3 class W, Seg 5 class S).
2. Book passive ghost segments (`AK1`) matching the parent international class:
   ```text
   0SQ2736B12SEPCPHARNAK1
   0SQ2639H23SEPOSLCPHAK1
   ```
3. Price explicitly skipping mismatched live segments:
   ```text
   FQCSQ/S1-2.4.6-8
   ```
4. File/Store the valid fare quote:
   ```text
   T:P1/S1-2.4.6-8/CSQ
   ```
5. Confirm stored fare (`*FF1`), attach commission (`TMU1Z0`) and form of payment (`TMU1FINVAGT`), then issue e-ticket (`TKPDTD`).

## Smartpoint NDC vs Traditional EDIFACT

* **NDC Content:** Sourced directly from airline offer APIs; features dynamic pricing, zero GDS distribution surcharges, and interactive seat/ancillary selection.
* **Order Management:** NDC bookings use `Offer ID` and `Order ID` alongside standard GDS record locators.
* **Servicing:** Void and refund actions on NDC tickets are handled through dedicated Smartpoint NDC servicing panels or airline direct agency portals.
