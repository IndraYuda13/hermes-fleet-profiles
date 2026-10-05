# Real-Time AIS Satellite Telemetry Integration (AISStream.io)

This reference outlines the production WebSocket architecture for integrating live AIS (Automatic Identification System) vessel telemetry into operational maritime dashboards.

## 1. WebSocket Protocol & Handshake
Connect directly to the global AISStream gateway:
- **Endpoint:** `wss://stream.aisstream.io/v0/stream`
- **Authentication & Filtering:** Send subscription JSON immediately upon socket `onopen`.

### Subscription Schema
```json
{
  "Apikey": "YOUR_AISSTREAM_API_KEY",
  "BoundingBoxes": [
    [[-11.5, 94.5], [6.5, 141.5]] // LatMin, LonMin, LatMax, LonMax (e.g. Indonesian EEZ)
  ],
  "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
}
```

## 2. Inbound Message Parsing
AISStream sends binary Blobs in browser environments. Parse incoming event data safely:

```javascript
aisWs.onmessage = async (event) => {
  try {
    const text = typeof event.data.text === 'function' ? await event.data.text() : event.data;
    const msg = JSON.parse(text);

    if (msg.MessageType === 'PositionReport') {
      const shipName = (msg.MetaData?.ShipName || 'VESSEL ' + (msg.MetaData?.MMSI || '')).trim();
      const mmsi = msg.MetaData?.MMSI || '-';
      const lat = msg.MetaData?.latitude?.toFixed(4);
      const lng = msg.MetaData?.longitude?.toFixed(4);
      const sog = msg.Message?.PositionReport?.Sog ?? 0;
      const cog = msg.Message?.PositionReport?.TrueHeading ?? msg.Message?.PositionReport?.Cog ?? 0;
      const timeUtc = (msg.MetaData?.time_utc || '').split(' ')[1]?.split('.')[0] || 'LIVE';

      // Cross-reference with active operational asset
      if (activeAssetMatches(shipName, mmsi)) {
        updateOperationalReadout({ lat, lng, sog, cog, timeUtc });
      }

      // Prepend to rolling live stream list (max 25 entries)
      prependStreamItem({ shipName, mmsi, lat, lng, sog, timeUtc });
    }
  } catch (err) {
    console.warn('AIS payload error:', err);
  }
};
```

## 3. UI Radar Visualization (CSS/SVG Light-weight)
Avoid heavy GIS/mapping bundles when glanceability is paramount:
1. **Radar Frame:** Circular container with dark maritime gradient (`background: radial-gradient(circle, #0b1a2d 0%, #060d16 100%); border: 1px solid rgba(0, 229, 255, 0.25);`).
2. **Concentric Range Rings:** Absolute-positioned circles at 25%, 50%, 75%, and 100% radius.
3. **Cardinal Crosshairs:** Thin crosshair lines (`rgba(0, 229, 255, 0.15)`).
4. **Radar Sweep Animation:** Conic gradient rotating 360° continuously (`animation: radarSweep 4s linear infinite;`).
5. **Target Blip:** CSS pulse dot centered or offset by GPS offset, labeled with ship name and operational status.

## 4. Reconnection & Resilience Pattern
Field network connections at ports and outer anchorages are notoriously unstable:
- Handle `onclose` and `onerror` by queueing `setTimeout(initAISStream, 5000);`.
- Show visual status badge: `MENGHUBUNGKAN` (amber), `LIVE STREAMING` (emerald), `MENYAMBUNG ULANG` (amber).
- Never blank out current metrics during reconnects — freeze last known good telemetry until fresh packets arrive.
