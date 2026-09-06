# Maritime & Telemetry Live Radar Patterns (Anti-Iframe Fallback)

## Problem & Context
Third-party live tracking providers (e.g., MarineTraffic, VesselFinder, FlightRadar24) enforce strict `X-Frame-Options: SAMEORIGIN` / `403 Forbidden` headers that prevent naive `<iframe>` embeds from rendering on external client websites.

## Architecture Pattern: Interactive Hybrid GIS Radar
To provide an interactive, branded, and 100% functional live tracking experience without paying enterprise API subscription fees or breaking with 403 errors:

### 1. Leaflet-Powered Vector Radar Engine
- Use lightweight Leaflet.js with CartoDB Voyager / Dark Matter tiles (`https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png`).
- Plot dynamic AIS markers via `L.circleMarker([lat, lon], {...})` styled with high-contrast nautical colors:
  - **Gold/Amber (`#E0A94A`)**: Dry Bulk Carriers / Ore
  - **Signal Red (`#E05347`)**: Tankers / CPO / Chemical
  - **Teal/Cyan (`#2EC4B6`)**: Tugboats, Pilot Launches, Escorts
  - **Blue (`#3A86FF`)**: Container & General Cargo

### 2. Anti-Clutter & Label Discipline
- Avoid permanent raw tooltips on closely clustered markers (which cause visual collisions on mobile).
- Use clean popups with structured telemetry (IMO, Vessel Type, Current Status, Speed Knots).
- Provide category filter tabs (All, Bulk, Tanker, Tug) in a 2x2 mobile-responsive grid.

### 3. Deep-Link Satellite Bridge
- Instead of broken iframes, provide a direct deep-link action button:
  `https://www.marinetraffic.com/en/ais/index/search/all/keyword:${encodeURIComponent(query)}`
- When the user searches an IMO/MMSI or clicks a vessel, display an instant client-side telemetry strip with a 1-tap bridge to the official live satellite view.

### 4. Mobile Viewport Safeguards
- Always set `scrollbar-width: none;` and `-webkit-scrollbar { display: none; }` on horizontal port jump bars.
- Place telemetry coordinate badges at top-right to prevent collision with Leaflet's zoom controls (`+` / `-` at top-left).
- Force `box-sizing: border-box !important;` and `max-width: 100%;` across all map wrapper containers.
