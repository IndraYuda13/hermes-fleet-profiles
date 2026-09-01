# Real-Time Live Chat Architecture & Shared Inbox (Crisp-Like MVP)

Architecture patterns and reference implementation for building zero-dependency, lightweight live chat systems with customer widget and admin shared inbox.

## 1. Domain & Routing Topology

Single Node.js service binding both customer and admin domains on one port (e.g. 8150):
- **Customer domain** (`customer.indrayuda.my.id` or `/customer`):
  - Serves responsive customer web interface and embeddable `/widget.js`.
  - Generates persistent UUID `session_id` in browser `localStorage`.
- **Admin domain** (`admin.indrayuda.my.id` or `/admin`):
  - Serves 3-pane shared inbox dashboard.
  - Subscribes to `admin_channel` for incoming message broadcasts and visitor telemetry.

## 2. Socket.IO Room Isolation Model

- **Customer Sockets**: Join room `session:<session_id>`.
  - Emits: `customer_join`, `send_message`, `typing`, `visitor_update`.
  - Receives: `receive_message`, `typing`, `read_status`.
- **Admin Sockets**: Join room `admin_channel`.
  - Emits: `admin_join`, `send_message`, `typing`, `mark_read`.
  - Receives: `new_customer_message`, `session_list`, `customer_typing`, `visitor_online`.

## 3. Zero-Dependency Audio Alert via Web Audio API

To avoid missing assets or CDN dependency issues, generate chime alerts directly using browser Web Audio API:

```javascript
function playIncomingChime() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc.frequency.setValueAtTime(880, ctx.currentTime + 0.1); // A5
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.4);
  } catch (e) {
    console.warn('Audio alert not allowed before interaction', e);
  }
}
```

## 4. MVP Scoping Guidelines

When requested for live chat / customer interaction tools:
1. Deliver core bi-directional messaging, read states, unread counters, and typing indicators first.
2. Park advanced capabilities (file uploads, multi-role auth, canned responses, bot automation) in the backlog until core chat stability is verified.
