# WebGL 3D Creative Engineering & Performance Architecture

A production-grade engineering standard for building interactive 3D web experiences, multi-scene showcases, custom GLSL shaders, procedural audio-reactive visualizers, and headless browser validation.

## 1. Multi-Scene SPA Lifecycle & GPU Memory Teardown
Switching between WebGL scenes without explicit GPU buffer and listener cleanup causes memory leaks and `WEBGL_CONTEXT_LOST_WEBGL`.

Every 3D scene factory must return a standard lifecycle object with `update(delta)`, `resize(w, h)`, `setOption(key, val)`, and `destroy()`:
- Dispose camera controls: `controls.dispose()`.
- Dispose all geometries: `geometry.dispose()`.
- Dispose all materials and their textures (`map`, `normalMap`, `roughnessMap`).
- Dispose renderer: `renderer.dispose()` and detach canvas DOM element.
- Never bind window event listeners (`resize`, `pointermove`) inside scene factories without removing them in `destroy()`. Delegate window events to the root router.

## 2. Defensive WebGL Initialization & SwiftShader Fallback
In headless testing environments or browsers with disabled hardware acceleration, `new THREE.WebGLRenderer()` throws unhandled exceptions.
- Probe availability before instantiation: verify `canvas.getContext('webgl2') || canvas.getContext('webgl')`.
- Catch renderer instantiation errors and render an accessible 2D fallback notice rather than crashing the SPA shell.

## 3. Zero-Asset Procedural WebAudio 3D Audio-Reactivity
Never depend on external `.mp3` or `.wav` files for audio-reactive 3D visualizations (CORS blocks, latency, 404 risks).
- Synthesize audio procedurally using native Web Audio API (`AudioContext`, `OscillatorNode`, `GainNode`, and `BiquadFilterNode` running a pentatonic scale arpeggio) piped directly into an `AnalyserNode`.
- Read real-time frequency bins via `analyser.getByteFrequencyData(dataArray)` to modulate geometry vertex shaders or particle positions.

## 4. Showcase Portal Layout & Balanced Grid Geometry
- **Orphan Card Elimination:** Never layout 7 cards across 3 columns leaving 1 dangling card. Structure catalogs in balanced sets ($4 \times 2 = 8$ or $3 \times 2 = 6$) using `repeat(auto-fit, minmax(280px, 1fr))`.
- **Body Scroll Isolation:** Keep `#canvas-container` at `position: fixed; width: 100vw; height: 100vh;` while allowing HTML body to scroll naturally (`min-height: 100%; overflow-y: auto;`).

## 5. Headless Chrome SwiftShader Inspection
When verifying 3D WebGL scenes in automated CI on Linux without a GPU:
```bash
google-chrome --headless=new \
  --no-sandbox \
  --use-gl=angle \
  --use-angle=swiftshader \
  --enable-unsafe-swiftshader \
  --window-size=1440,900 \
  --hide-scrollbars \
  --screenshot=/tmp/screenshot_scene.png \
  "https://your-domain.com/route"
```
