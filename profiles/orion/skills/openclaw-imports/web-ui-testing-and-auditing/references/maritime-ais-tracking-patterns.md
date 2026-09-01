# Maritime AIS Tracking, MarineTraffic Integration & Mapbox/Leaflet Radar Patterns

This reference document compiles production-tested patterns, anti-iframe bypass architectures, and Leaflet telemetry conventions for maritime shipping agency platforms, live AIS vessel tracking, and port radar dashboards.

---

## 1. The Iframe Anti-Embed Wall in Global Maritime Services
Major maritime vessel tracking providers (**MarineTraffic**, **VesselFinder**, **MyShipTracking**) protect their live maps aggressively against third-party iframe embedding:
- **Header Blocks:** `X-Frame-Options: SAMEORIGIN` or `403 Forbidden` response codes.
- **WAF / Challenge Gateways:** Cloudflare Bot Management challenging automated headless browser or embed requests.

### Architectural Solution for Production:
1. **Never rely on naive `<iframe>` embeds** of third-party portals without enterprise paid API keys.
2. **Implement Native Leaflet Vector Radar as Primary UI:**
   - Render high-contrast vector markers (`L.circleMarker` or custom SVG icons) for fleet vessels.
   - Categorize vessels with distinct color tokens (e.g. Amber `#E0A94A` for Bulk Carriers, Red `#E05347` for Tankers, Teal `#2EC4B6` for Tugs/Pilot boats).
3. **Seamless Direct Deep-Linking for Extended Satellite View:**
   - Provide direct 1-click external navigation into official MarineTraffic/VesselFinder vessel profiles (`https://www.marinetraffic.com/en/ais/index/search/all/keyword:${encodeURIComponent(query)}`).
   - Allow enterprise users with official API keys (`/exportvessel/{api_key}`, `/exportvessels/{api_key}`) to pipe live coordinate streams directly into Leaflet layers.

---

## 2. Leaflet Maritime Radar Implementation Pitfalls

### Pitfall A: Zoom Control vs Telemetry Badge Collision
- **Problem:** Positioning floating location/telemetry badges at `top: 8px; left: 8px;` directly covers the Leaflet standard `+` / `-` zoom control buttons.
- **Fix:** Position telemetry badges at `top: 8px; right: 8px; left: auto;` with `text-align: right;` and `pointer-events: none;`.

### Pitfall B: Cluttered Marker Tooltips & Overlap
- **Problem:** Rendering permanent SVG tooltips (`permanent: true`) on tightly clustered vessels at anchorage (e.g. 5+ ships at Taboneo or Cigading) causes unreadable overlapping text blocks.
- **Fix:** 
  - Keep marker radius compact (`radius: 9px` with `weight: 2.5px`).
  - Use concise tooltips (`direction: 'top'`, `offset: [0, -10]`) or bind interactive popups on click rather than permanent large multi-line tooltips.
  - Apply distinct category colors so users can identify vessel type at a glance without reading text.

### Pitfall C: Mobile Category Button & Port Tab Overflow
- **Problem:** Horizontal rows of category filter buttons (`Semua Kapal`, `Bulk Carrier`, `Tanker`, `Tugboat`) overflow and get clipped on mobile viewports (< 480px).
- **Fix:**
  - Layout category filters using a 2x2 responsive grid on mobile (`grid-template-columns: repeat(2, 1fr)`).
  - For horizontal scrollable port chips, hide default desktop scrollbars cleanly using:
    ```css
    .radar-ports-bar {
      display: flex;
      gap: 4px;
      overflow-x: auto;
      scrollbar-width: none;
      -ms-overflow-style: none;
    }
    .radar-ports-bar::-webkit-scrollbar {
      display: none;
    }
    ```

---

## 3. MarineTraffic REST API Endpoint Summary
When communicating with official MarineTraffic OpenAPI endpoints (`https://services.marinetraffic.com/api`):

| Endpoint | Method | Key Parameters | Output |
| :--- | :--- | :--- | :--- |
| `/exportvessels/{api_key}` | `GET` | `v=2`, `port_unlocode`, `protocol=json` | List of vessels currently in/near specified port |
| `/exportvessel/{api_key}` | `GET` | `v=2`, `mmsi`, `protocol=json` | Live GPS coordinate, speed, course, status of 1 ship |
| `/exportvesseltrack/{api_key}` | `GET` | `v=2`, `mmsi`, `days`, `protocol=json` | Historical voyage track points |
| `/portcalls/{api_key}` | `GET` | `v=2`, `port_id`, `timespan`, `protocol=json` | Port arrival/departure event history |
