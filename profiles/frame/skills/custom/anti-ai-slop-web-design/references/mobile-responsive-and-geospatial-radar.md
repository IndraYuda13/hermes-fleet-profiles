# Mobile Responsiveness & Live Geospatial/Radar Embed Standards

## 1. Mobile-First Viewport & Zero-Overflow Invariants
When developing dense data dashboards, calculator forms, or technical portals for mobile viewports (360px - 412px):

- **Strict Box Model Reset**:
  ```css
  *, *::before, *::after {
    box-sizing: border-box !important;
    margin: 0;
    padding: 0;
    max-width: 100%;
  }
  html, body {
    width: 100%;
    max-width: 100vw;
    overflow-x: hidden !important;
  }
  ```
- **Text & Headline Wrapping**:
  Never rely on default text wrapping for technical or long headers. Enforce `overflow-wrap: break-word; word-break: break-word;` and responsive clamp fonts (e.g. `font-size: clamp(20px, 5.2vw, 38px);`).
- **Hero CTA Layout**:
  Do not place multiple wide action buttons side-by-side on mobile. Default to vertical stack (`flex-direction: column; width: 100%;`) below 480px.
- **Scrollbar Sanitization on Horizontal Tabs**:
  Horizontal chip bars (port filters, preset toggles) must scroll smoothly without ugly native scrollbars:
  ```css
  .chip-bar {
    display: flex;
    overflow-x: auto;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE/Edge */
  }
  .chip-bar::-webkit-scrollbar {
    display: none; /* Chrome, Safari */
  }
  ```

## 2. Live AIS & MarineTraffic Dual-Engine Integration
External maritime tracking providers (MarineTraffic, VesselFinder) frequently block raw iframe embeds (`X-Frame-Options: SAMEORIGIN` / 403 Forbidden) on unauthorized domains.

### Robust Dual-Engine Architecture:
1. **Primary Vector Radar (Leaflet.js)**:
   - High-contrast Voyager/Dark Matter tiles.
   - Vector circle/pin markers (`L.circleMarker`) with permanent name tooltips and status popups (IMO, Speed, Operation Status).
   - Zero CORS/iframe blocking risk, instant rendering, tactile interactions.
2. **Global Satellite Direct Search (MarineTraffic Bridge)**:
   - Dedicated fallback mode or 1-tap deep link:
     `https://www.marinetraffic.com/en/ais/index/search/all/keyword:${encodeURIComponent(query)}`
   - Allows users to seamlessly jump to global satellite AIS tracks for out-of-harbor vessels without breaking the local portal UI.

## 3. UI Control Separation on Interactive Maps
- Place floating telemetry/coordinates panels at the **top-right** or **bottom-left** of the map container to prevent collision with Leaflet's standard zoom controls (`+` / `-`) positioned at top-left.
