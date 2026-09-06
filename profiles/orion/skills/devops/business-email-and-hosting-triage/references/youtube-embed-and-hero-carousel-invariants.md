# YouTube Shorts Embedding & Hero Carousel Invariants

## 1. YouTube "Error 153" & Autoplay Embed Syntax

### Root Cause
When embedding YouTube Shorts or videos into external websites via standard `<iframe>`, YouTube frequently blocks playback with `Video player configuration error (Error 153)` due to:
- **Audio Copyright & Distribution Locks (Most Common for Shorts):** YouTube Shorts that utilize trending/commercial audio or copyrighted music tracks are hard-blocked by YouTube's backend from external iframe playback. In this state, the video CANNOT be embedded on any third-party domain—even direct requests to `https://www.youtube.com/embed/<VIDEO_ID>` will return Error 153.
- **YouTube Studio Embedding Restrictions:** The channel owner or platform policy has "Allow embedding" unchecked.
- Missing or misconfigured `referrerpolicy` (YouTube requires origin verification to prevent unauthorized embed hijacking).
- Domain/origin mismatches when tested from preview environments, subfolders, or sandboxed iframes.
- Conflicts between autoplay, mute, and loop parameters on vertical Shorts formats.

### The "Client Provided Script" Pitfall
When a user pastes an iframe snippet from an existing template (e.g. with `autoplay=1&mute=1&loop=1&playlist=<ID>&rel=0&playsinline=1`) insisting it should autoplay, test the embed URL directly in a browser or curl first. If YouTube has locked the video's audio, re-applying the user's snippet will still display the black "Error 153" screen, triggering user frustration. Do not simply wrap or re-apply the snippet without verifying embed playability.

### Autoplay-Loop Production Pattern (When Mandated by User & Embed Permitted)
When the user explicitly requests autoplaying Shorts/videos without user-interaction click gates, implement the exact YouTube URL parameters:
```html
<iframe loading="lazy"
  style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
  src="https://www.youtube.com/embed/<VIDEO_ID>?autoplay=1&mute=1&loop=1&playlist=<VIDEO_ID>&rel=0&playsinline=1"
  title="Video Title"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
  referrerpolicy="strict-origin-when-cross-origin"
  allowfullscreen>
</iframe>
```
*Crucial parameters for uninterrupted loop:*
- `autoplay=1&mute=1`: Browsers block unmuted autoplay; muting is mandatory for autonomous start.
- `loop=1&playlist=<VIDEO_ID>`: YouTube requires the video ID repeated in the `playlist` parameter for single-video loops to cycle continuously.
- `playsinline=1`: Prevents mobile iOS Safari from forcing fullscreen takeover on play.
- `referrerpolicy="strict-origin-when-cross-origin"`: Solves Error 153 configuration handshake issues.

### The Definitive Fail-Safe: YouTube Shorts Showcase Card Pattern
When YouTube hard-blocks iframe embedding with Error 153 (due to audio licensing or studio policies), replace the broken iframe with an interactive Shorts Showcase Card:
1. Render a responsive container with a 9:16 aspect ratio (`padding-top: 177.78%`).
2. Display the official high-resolution video thumbnail (`https://i.ytimg.com/vi/<VIDEO_ID>/hqdefault.jpg`) as an `<img>` poster with `object-fit: cover`.
3. Overlay a semi-transparent dark tint and a centered glowing YouTube Play button (`#FF0000` circle with white triangle).
4. Add a prominent badge or button: `▶ Tonton di YouTube Shorts` linked directly to `https://www.youtube.com/shorts/<VIDEO_ID>` with `target="_blank" rel="noopener"`.
5. This pattern 100% eliminates Error 153, loads 10x faster (zero heavy iframe scripts), guarantees seamless playback in the YouTube app or mobile browser, and ensures the landing page looks polished and premium.

---

## 2. Hero Section Carousel Black-Screen Invariants

### The Deferred Script Deletion Bug
In legacy Bootstrap carousel themes (e.g. BizPage), template scripts in `js/main.js` often execute:
```javascript
$(this).css("background-image", "url('" + $(this).children(".carousel-background").children("img").attr("src") + "')")
       .children(".carousel-background").remove();
```
When scripts are loaded with `defer` or delayed by network conditions:
1. The `.carousel-background` element and its `<img>` are deleted from the DOM.
2. The CSS `background-image` property is set asynchronously after page render.
3. If `#intro` has a default `background: #000;` and `.carousel-item::before` has an opaque black overlay, the hero section displays a pitch-black screen on initial load.

### Fix: Inline CSS & Transparent Overlay Precedence
1. Set the background image directly on the `.carousel-item` tag in the initial HTML:
   ```html
   <div class="carousel-item active" style="background-image: url('img/intro-carousel/1.webp'); background-size: cover; background-position: center;">
   ```
2. In CSS, avoid solid black or heavily opaque overlays (`rgba(0,0,0,0.75)`). Use balanced linear gradients (`rgba(0,0,0,0.40)` to `rgba(0,0,0,0.65)`) so background textures, industrial sparks, and workshop imagery remain clearly visible while maintaining WCAG text contrast for white headlines.
3. Apply `padding-top: 60px` to `.carousel-container` to prevent fixed navigation bars and brand logos from overlapping centered H1 hero headlines.
