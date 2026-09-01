# Photorealistic Image Generation & Resolution Enhancement via Pollinations Flux

A reference guide for generating cinematic, high-definition photorealistic imagery using Flux models and post-processing upscaling.

---

## 1. Direct High-Resolution Prompting with Flux

Pollinations.ai provides direct endpoint access to open-weights models like Flux without complex local GPU installations.

### URL Construction:
```
https://image.pollinations.ai/prompt/<URL_ENCODED_PROMPT>?width=1920&height=1080&model=flux&nologo=true&seed=<RANDOM_INT>
```

### Prompt Engineering Guidelines for Photorealism:
1. **Camera & Lighting Specificity**: Include concrete lighting types (`soft orange sunrise lighting`, `golden hour`, `cinematic haze`, `rim lighting`, `specular reflections`).
2. **Subject & Material Details**: Detail surfaces (`crisp jet engine metallic reflections`, `glass skyscraper facades`, `volumetric morning mist`).
3. **Aspect Ratios**:
   - `16:9` Widescreen: `1920x1080` (or `1280x720`).
   - `1:1` Square: `1024x1024`.
   - `9:16` Portrait / Stories: `1080x1920`.

---

## 2. Post-Processing & Upscaling Pipeline (PIL Lanczos)

When raw generation outputs slightly compressed images (e.g. 1024x576 base), apply a clean Lanczos upscaler and slight sharpness enhancement in Python:

```python
import urllib.request, urllib.parse
from PIL import Image, ImageEnhance

prompt = "Ultra realistic commercial Boeing 737 airplane climbing and taking off into the dawn sky, modern glass skyscraper city skyline below in soft morning haze, glowing soft orange and pastel golden sunrise lighting, crisp jet engine details, 8k resolution, cinematic aviation photography"
encoded = urllib.parse.quote(prompt)

url = f"https://image.pollinations.ai/prompt/{encoded}?width=1920&height=1080&model=flux&nologo=true&seed=88"
raw_path = "/tmp/raw_generated.jpg"
final_path = "/root/final_hd_image.jpg"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=90) as resp:
    with open(raw_path, "wb") as f:
        f.write(resp.read())

# Clean Lanczos Upscale to 1920x1080 Full HD
im = Image.open(raw_path)
im_hd = im.resize((1920, 1080), Image.Resampling.LANCZOS)

# Subtle sharpness boost for metallic/edge clarity
enhancer = ImageEnhance.Sharpness(im_hd)
im_hd = enhancer.enhance(1.15)

im_hd.save(final_path, "JPEG", quality=98)
```
