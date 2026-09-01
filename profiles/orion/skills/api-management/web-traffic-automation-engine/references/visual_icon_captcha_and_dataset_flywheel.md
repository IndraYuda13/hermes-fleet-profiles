# Visual Sequence Icon Captcha Solving & Dataset Flywheel SOP

Complete operational guide for reverse-engineering, automating, and dataset-harvesting custom visual sequence click captchas (e.g. 3-icon queue matching on scattered canvas) using multimodal Vision LLMs and transition to standalone local models.

---

## 1. Captcha Mechanism & Structure

1. **Trigger Condition:**
   - Server-side checkpoint triggered at fixed intervals (e.g. `curDay % 15 == 0`) during task claim verification.
2. **Payload Structure:**
   - Endpoint: `POST /api/user/captcha/check/`
   - Response when challenged:
     ```json
     {
       "status": "ok",
       "data": {
         "queue": "data:image/png;base64,iVBORw0KGgo...",
         "image": "data:image/png;base64,iVBORw0KGgo..."
       }
     }
     ```
   - **`queue` Image:** `88 x 24 px` horizontal banner displaying exactly 3 target outline icons arranged from left to right.
   - **`image` Canvas:** `240 x 200 px` canvas image with dark textured background containing 4 neon colored icons scattered at random positions.

---

## 2. Mathematical Coordinate Extraction & Normalization

1. **Submission Format:**
   - Target API requires 3 coordinate points corresponding to the 3 queue icons in exact order:
     ```
     coor[0][x]=168&coor[0][y]=76&coor[1][x]=218&coor[1][y]=22&coor[2][x]=28&coor[2][y]=78
     ```
2. **Boundary Clamping & Even-Parity Invariant:**
   - Canvas coordinate bounds: $0 \le X \le 240$, $0 \le Y \le 200$.
   - **Parity Normalization:** Client frontend uses even pixel rounding (`x = x % 2 ? x - 1 : x`). Always normalize output coordinates to even integers.

---

## 3. Vision LLM Solver Microservice Architecture

Run a dedicated Python HTTP microservice (Port `5073`) so claimer bots remain pure HTTP without AI library overhead.

### Model Selection & Latency Constraints:
* **Failure Mode with Heavy Reasoning Models:**
  - Models such as `gemma-4-31b-it` generate extensive reasoning traces taking 35–45 seconds.
  - Captcha challenges enforce strict 30s server-side timeouts, causing `timeIsOver` errors and socket disconnects.
* **Recommended High-Speed Vision Models:**
  - Primary: `ag/gemini-3.7-flash-high` or `gemini/gemini-3.6-flash` (~3–5 seconds latency, 100% accuracy).
  - Fallback Cascade: Primary Flash -> Secondary Flash -> Heavy Model (with 15s timeout).

### System Prompt Template for Vision LLM:
```text
You are an expert OCR and icon matching vision system.
You are given two images:
1. Target Queue (88x24 px): Displays 3 target icon outlines from LEFT to RIGHT.
2. Main Canvas (240x200 px): Displays 4 scattered icons on a 240x200 pixel canvas.

Your task:
Identify the 3 icons from the queue in exact left-to-right order, find their corresponding matching icons on the 240x200 canvas, and return the center (x, y) coordinates for each on the canvas.

Rules:
- Output MUST be valid JSON array of 3 coordinate objects: [{"x": int, "y": int}, {"x": int, "y": int}, {"x": int, "y": int}]
- Canvas coordinates: X is 0..240, Y is 0..200.
- Return ONLY the JSON array, zero prose.
```

---

## 4. Self-Training Dataset Harvester Flywheel

To eliminate cloud LLM token costs over time:
1. **Lossless Image Logging:**
   - Save every processed queue banner as `dataset/images/sample_<timestamp>_<id>_queue.png` (88x24).
   - Save every main canvas as `dataset/images/sample_<timestamp>_<id>_canvas.png` (240x200).
2. **JSONL Annotation Storage:**
   - Append prediction records to `dataset/annotations.jsonl`:
     ```json
     {"sample_id": "sample_20260830_112254_7305ce", "queue_file": "...", "canvas_file": "...", "coordinates": [{"x": 214, "y": 166}, {"x": 122, "y": 26}, {"x": 168, "y": 72}], "verified_by_server": false, "timestamp": "2026-08-30T11:22:54Z"}
     ```
3. **Verification Feedback Loop:**
   - When the bot receives `{"status": "ok", "message": "Проверка пройдена"}` from the target server, send `POST /feedback` with `sample_id` to mark `verified_by_server: true`.
4. **Local Model Training Roadmap:**
   - 500+ verified samples: Fine-tune YOLOv8-pose (keypoint detection for 3 target centers) or Siamese CNN.
   - Deploy as ONNX runtime microservice (<50ms latency, zero API token cost).

---

## 5. In-Place Fresh Challenge Auto-Retry Handling

### The Server-Side Offset Challenge Pattern:
- If submitted click coordinates have a minor pixel deviation or land on an icon boundary, the target platform often does not fail the claim immediately.
- Instead of returning an error, `POST /user/captcha/check/` responds with `{"status": "data", "data": {"queue": "...", "image": "..."}}` containing a freshly generated image/canvas pair.

### Client-Side In-Place Resolution Rule:
- When `submit_captcha_coordinates` receives a `status == 'data'` response with a new image:
  1. Do NOT drop the task or trigger a generic error backoff.
  2. Immediately feed the new `image` and `queue` (or fallback to the original queue if omitted) to the Vision solver in-place.
  3. Submit the second coordinate set. If verified (`status == "ok"` and `reward` present), reward the worker and send feedback to the dataset harvester.
  4. This in-place retry prevents wasted video playback durations (12–15s) and boosts task completion efficiency to near 100%.

