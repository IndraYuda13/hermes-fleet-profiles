# GIS Map Dashboard & GeoJSON Telemetry Reference

When building GIS dashboards, Leaflet/Mapbox telemetry visualizations, or Cell ID / BTS simulation maps, follow these established patterns and pitfalls discovered during production implementation.

## 1. Double-Encoded GeoJSON Parsing Pattern
Crowdsourced or legacy PHP backend APIs frequently return GeoJSON strings nested as double-escaped JSON strings inside JSON responses.
```javascript
let geojsonParsed = null;
try {
    geojsonParsed = typeof item.geojson === 'string' ? JSON.parse(JSON.parse(item.geojson)) : item.geojson;
} catch(e) {
    console.error("GeoJSON parse error", e);
}
```

## 2. Polygon Geometry Bounding Box Sanitization
Corrupt telemetry items or invalid azimuth calculations can produce massive outlier polygons that span hundreds of kilometers, creating giant solid fill artifacts that cover the map canvas.
```javascript
// Filter out corrupt / giant outlier polygons (> 0.05 lat/lon delta ~ 5.5km radius)
const coords = feat.geometry.coordinates[0];
if (coords && coords.length) {
    const lons = coords.map(p => p[0]);
    const lats = coords.map(p => p[1]);
    const dLon = Math.max(...lons) - Math.min(...lons);
    const dLat = Math.max(...lats) - Math.min(...lats);
    if (dLon > 0.05 || dLat > 0.05) return; // Skip outlier polygon
}
```

## 3. Search & Highlighting Workflow
When implementing location search (Nominatim Geocoding) and Cell ID / LAC search:
1. Use `map.flyTo([lat, lon], zoom, { duration: 1.5 })` for smooth camera transitions.
2. Remove any previous `highlightMarker` before creating a new pulsing `L.circleMarker` at target coordinates.
3. Automatically trigger the detail panel drawer/modal for the searched entity upon selection.

## 4. Collapsible Floating Sidebar Drawer
For full-screen map applications, ensure the control sidebar can be hidden and unhidden smoothly without breaking Leaflet touch/click propagation.
- **CSS Transition:** `transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;`
- **Collapsed Class:** `.sidebar.collapsed { transform: translateX(-410px); opacity: 0; pointer-events: none; }`
- **Floating Button:** Position fixed/absolute at `top: 15px; left: 15px; z-index: 1001;` so it remains clickable when the sidebar is hidden.
