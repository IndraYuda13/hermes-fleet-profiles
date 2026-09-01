# Macro-Compositional Diversity & Anti-Template Normalization Protocol

## 1. The Token-Level Diversity Fallacy (Why Diversity Gates Fail)
A visual diversity check fails when it operates purely as CSS token diffing:
- Changing background from `#0F172A` (Slate) to `#0B0B10` (Carbon) is NOT diversity.
- Changing accent from `#3B82F6` (Blue) to `#F59E0B` (Amber) is NOT diversity.
- Changing font from `Inter` to `Space Grotesk` while keeping the exact same layout is NOT diversity.
- Comparing a dark operations dashboard against a light botanical app (e.g., LeafNote) to claim "0/6 collisions" while ignoring consecutive dark telemetry dashboards is a fatal cherry-picking flaw.

## 2. Mandatory 30-Day Fleet Portfolio Audit
Before LENS or AURORA issues a `DIVERSITY: PASS`, the design must be compared against **every project built by the fleet in the past 30 days** across 5 Macro-Compositional Dimensions:

| Dimension | Prohibited Repetition (If used in recent projects) | Required Variation |
|---|---|---|
| **1. Layout Archetype & Shell** | Fixed Topbar + 220px Left Sidebar Rail + Right Panel | Horizontal Command Strip, Full-Screen HUD Canvas, Asymmetric Split-Screen, Floating Modular HUD, Terminal Ledger Window |
| **2. Metric / Telemetry Layout** | 4-Card Horizontal KPI Row (Title + Top-Right Icon + Big Monospace Number + Subtext Delta) | Integrated Telemetry Ribbon, High-Density Matrix Grid, Sparkline Oscilloscope Strip, Spatial Node Clusters, Inline Status Ticker |
| **3. Navigation Model** | Standard Left Vertical List with Pill Badges | Top Tab Bar, Command Palette HUD (`Cmd+K`), Segmented Switcher, Workspace Zoom Navigation |
| **4. Data Presentation** | Standard zebra-striped table with search input + filter dropdown | Interactive Matrix Grid, Split Master-Detail Ledger, Expandable Card Accordions, Node Topology Flow |
| **5. Visual Surface Hierarchy** | Flat dark rectangles with 1px border on pure black | Recessed cockpit cutouts, brutalist hard offsets, industrial metal rails, dynamic status glow zones |

## 3. Candidate Exploration Integrity Rules (AURORA)
1. **Architectural Divergence:** The 3 generated candidates MUST represent 3 completely different spatial/layout paradigms, not 3 color palettes on the same wireframe.
2. **Anti-Strawman Rule:** AURORA must never generate artificially crippled candidates (e.g., luxury serifs on an ops dashboard or broken bento grids) to force the selection of an obvious default.
3. **Domain Fitness Validation:** Every candidate's typography and density must match the actual product type before entering scoring.

## 4. Anti-Normalization Invariant during Implementation (FRAME)
1. **Zero-Fallback to Familiar Wireframes:** FRAME must never convert an innovative layout from `DESIGN_CONTRACT.md` back into a standard flexbox sidebar + 4-card grid for coding convenience.
2. **Signature Element Verification:** FRAME must explicitly verify that 100% of AURORA's designated "Signature Elements" exist and function in the rendered DOM.

## 5. Dual-Mode LENS Verification Standard
LENS must issue two separate diversity scores:
1. `TOKEN_DIVERSITY: PASS | FAIL` (Colors, fonts, borders, contrast)
2. `MACRO_COMPOSITION_DIVERSITY: PASS | MACRO_COLLISION` (Layout shell, KPI presentation, zoning vs 30-day fleet portfolio)
If `MACRO_COMPOSITION_DIVERSITY` is `MACRO_COLLISION`, the overall verdict MUST be `FAIL`.
