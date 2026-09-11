# 3D WebGL & Scrollytelling Storefront Integration

## 1. Procedural Geometry Architecture (Zero Network Asset Overhead)
Avoid multi-megabyte external `.gltf`/`.glb` models for hero focal elements in e-commerce storefronts. Use procedural primitives compiled in-memory via standard Three.js buffers (<2.5k triangles total):
- Outer Faceted Crystal: `THREE.IcosahedronGeometry(radius, 0)` (20 facets, 60 vertices).
- Inner Gyroscopic Core: `THREE.OctahedronGeometry(radius * 0.45, 0)` (8 facets, 24 vertices).
- Orbital Kinetic Nano-Rings: `THREE.TorusGeometry(radius * 1.45, tube, 16, 64)` (~2.048 triangles).

## 2. Render Loop Culling & Battery/GPU Preservation
E-commerce checkout flows require 100% thread responsiveness. Never run an unbounded WebGL render loop when the hero is off-screen or the browser tab is hidden.

```javascript
let isVisible = true;
let isTabActive = !document.hidden;
let rafId = null;

function animate() {
  if (!isVisible || !isTabActive) {
    rafId = null;
    return;
  }
  // Update uniforms, lerp rotation, render scene
  renderer.render(scene, camera);
  rafId = requestAnimationFrame(animate);
}

function resumeLoop() {
  if (!rafId && isVisible && isTabActive) {
    rafId = requestAnimationFrame(animate);
  }
}

// 1. Tab visibility culling
document.addEventListener('visibilitychange', () => {
  isTabActive = !document.hidden;
  if (isTabActive) resumeLoop();
});

// 2. Viewport culling (pause when scrolled down to checkout/wizard)
const heroObserver = new IntersectionObserver(([entry]) => {
  isVisible = entry.isIntersecting;
  if (isVisible) resumeLoop();
}, { threshold: 0.05 });

const heroElement = document.querySelector('#heroSpotlightPanel');
if (heroElement) heroObserver.observe(heroElement);

// 3. Accessibility: Reduced Motion kill-switch
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  vaultGroup.rotation.set(0.4, 0.6, 0); // Pristine static 3/4 pose
  renderer.render(scene, camera);
  isVisible = false; // Freeze loop permanently
}
```

## 3. Mobile Thermal & Pixel Ratio Guardrails
Heavy physical materials (`MeshPhysicalMaterial` with transmission, roughness, clearcoat) invoke Frame Buffer Object (FBO) readbacks:
- Desktop: `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2.0));`
- Mobile (<768px): `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));` to prevent GPU throttling and battery drain.
- Fallback: Detect low-power WebGL 1 contexts and degrade gracefully to `MeshStandardMaterial` with specular clearcoat.

## 4. DOM Layering & Pointer-Events Protection
Prevent 3D canvas overlays from intercepting clicks on search boxes, category chips, or cart buttons:
- Canvas Container: `pointer-events: auto;` scoped strictly to canvas bounds, with `z-index: 2` (never higher than interactive controls at `z-index: 5+`).
- Decorative Halo / Radial Glow: `pointer-events: none;`.
- Interactive DOM Controls: Ensure `position: relative; z-index: 10;` on all form elements and action buttons. If a canvas sits at higher z-index over buttons, synthetic automation (Playwright/Puppeteer) and touch taps will fail with pointer interception timeout errors.
- 3D Perspective Tilt Hit-Testing Fallback: Cards using 3D perspective tilt (`perspective(1000px) rotateX(...) rotateY(...) translateZ(...)`) experience visual hit-test drift. If synthetic clicks miss the inner CTA button and hit the card surface, attach the primary action listener to the card container as well as the inner button (`card.addEventListener('click', ...)`).
- State Synchronization: Listen to catalog state updates (e.g. brand selection or theme switches) and update 3D light colors (`light.color.setHex(...)`) via decoupled hooks, never by coupling 3D animation code directly into checkout validation logic.
- Backend Route Verification: Adding vendor or 3D scripts (`three-hero.js`, `vendor/three.min.js`) requires verifying that static server routes serve the paths with HTTP 200 and restarting background app daemons before running browser verification suites.
