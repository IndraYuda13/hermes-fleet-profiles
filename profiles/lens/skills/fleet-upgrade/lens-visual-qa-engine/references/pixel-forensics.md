# Pixel Forensics — Falsifying Render Claims From Raster

Depth for when your evidence is PNGs (a peer's render, a delivered shot set, a screenshot you must verify) rather than a live DOM. Use with §7 of SKILL.md.

**Reach for the DOM first when you have it.** `getBoundingClientRect` is exact for geometry; the raster only gives you colour, thickness, and "did anything paint here". Use pixels to *confirm* a DOM/human claim, or when no DOM exists — not to replace a measurement you could take exactly.

## 1. PNG identity without an image library

`run` manifests want file, pixel size, bytes, md5. Read the IHDR directly — width at byte 16, height at byte 20, big-endian:

```python
import hashlib
b = open(path, "rb").read()
w = int.from_bytes(b[16:20], "big"); h = int.from_bytes(b[20:24], "big")
print(f"{path} {w}x{h} {len(b)}B md5={hashlib.md5(b).hexdigest()}")
```

Verify a PNG is real content (not a blank/failed capture) before citing it as evidence.

## 2. Rule thickness and colour — column scan

Scan a fixed column for the first contiguous run of dark pixels; that run is the rule.

```python
from PIL import Image
im = Image.open(path).convert("RGB"); px = im.load()
col = 600
ys = [y for y in range(0, 120) if sum(px[col, y]) < 300]
run = [ys[0]]
for y in ys[1:]:
    if y == run[-1] + 1: run.append(y)
    else: break
print(run[0], run[-1], len(run), px[col, run[0]])   # y0, y1, thickness, RGB
```

A 2px rule returns `len(run) == 2`. Repeat on a second column to confirm it is continuous, not an artefact. Report the RGB, not a colour name — "near-black `rgb(20,33,43)`" beats "dark rule".

## 3. Text vs band — the anti-aliasing trap

A classifier like "amber if R high and B low" fires on **anti-aliased glyph edges** and fabricates a horizontal band that does not exist. Disprove it by printing a row-by-row map (a run of sampled columns at each y): real text shows *broken* runs across many rows; a real ruled band shows a *solid* run at `y` and `y+1` only.

Rule: never escalate a band you first saw only in a downscaled crop. Confirm on full-resolution pixels first, and report only the confirmed result. A "band" that dissolves into glyph fragments was misread vision, not a defect.

## 4. Edge bleed vs the container's own border

Scan the 1-2px border ring for pixels far from the corner/background colour (`px[2,2]`), then classify before reporting:

- a thin stroke present on **all four edges** at a constant inset = the container border;
- a blob consolidated on **one edge** = content touching or escaping the frame.

A full-bleed background legitimately paints edge-to-edge: distinguish "painted to the edge" from "escaping the frame". Compare against the sampled background, not a hard-coded colour.

## 5. Content bounding box — title-safe sanity

Find the min/max non-background coordinate, then the four margins:

```python
def hspan(px, W, bg, tol=22, y0=100, y1=600):
    minx, maxx = W, 0
    for x in range(W):
        for y in range(y0, y1, 2):
            if any(abs(c - d) > tol for c, d in zip(px[x, y], bg)):
                minx, maxx = min(minx, x), max(maxx, x); break
    return minx, W - 1 - maxx        # left margin, right margin
```

A bottom margin of 0 is usually the foot-row sitting exactly at the safe inset — pair with the DOM check (containment, not collision) before calling it a clip.

## 6. Your own probe is the first suspect

A raster scan that reports a glyph **absent**, or paint **inside** a glyph, is more often a probe bug than a defect. Two failure modes, both silent:

- **Mixed coordinate spaces.** A DOM probe returns one coordinate frame (viewport), the element screenshot and its decoded pixels use another (element-local). Reusing a viewport x as an element-local x lands the scan window on empty background and reports `0 ink` for text that is plainly visible. Before scanning, print the mapping (`element_box`, `target_box - element_origin`) and confirm the window contains the target on the *first* sample y. A lone label reading 0 ink while every sibling reads non-zero is the tell — fix the window, do not file a finding.
- **Window straddling two features.** A generous bounding window captures the feature above the target (an axis rule, a border) as well as the glyph, so an "ink" count silently sums both and a "teal" count picks up the rule's anti-aliasing. Size the window to the target band and print a full ASCII pixel map (`#` = feature colour, `@` = dark ink, `.` = mid grey) over the region before drawing any conclusion. The map shows the true stacking order — marker end, rule, tick stub, glyph — in one glance and makes a false positive obvious.

## 7. Hue-difference classifiers fire on subpixel text

A classifier written as "feature colour if `G-R > 40 and B-R > 40`" (or any hue-difference test) fires on the **LCD subpixel fringes** of dark glyphs, because antialiased dark text on a light ground carries warm and cool fringe pixels. Sample the glyph core instead: dark text reads as a low-saturation, dark RGB across its stroke, while real accent paint reads as saturated. Confirm by sampling explicit coordinates inside the glyph and printing the RGB tuples — if the values are dark and near-neutral, the "feature colour inside the glyph" is a fringe artifact, not the feature occluding the text. State the stacking order you measured (feature ends at `y=a`, rule at `y=b`, glyph ink `y=c..d`, gap = `c-a` px) rather than asserting "not covered".

## 8. Reporting shape

Per file: `{file, px, md5, rule_runs, bleed_classification, margins}`, then state for each finding whether it is a **raster observation** or **DOM-asserted geometry**, and name the file it came from. Do not present a thickness or colour you did not scan.
