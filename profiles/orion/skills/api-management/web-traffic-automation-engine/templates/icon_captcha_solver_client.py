#!/usr/bin/env python3
"""
IconCaptchaSolver Microservice Template (Port 5073)
--------------------------------------------------
Multimodal Vision LLM microservice for solving 3-icon sequence captchas
with ground-truth dataset harvesting flywheel.
"""

from __future__ import annotations

import base64
import json
import logging
import re
import time
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("IconCaptchaSolver")
DATASET_DIR = Path("dataset")
IMAGES_DIR = DATASET_DIR / "images"
ANNOTATIONS_FILE = DATASET_DIR / "annotations.jsonl"


class CaptchaSolver:
    def __init__(self, api_base: str, api_key: str, primary_model: str, fallback_model: str):
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    def solve(self, queue_b64: str, canvas_b64: str) -> Dict[str, Any]:
        """Solve 3-icon captcha using Vision LLM with fallback cascade."""
        t0 = time.time()
        sample_id = f"sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(3).hex()}"

        # Persist lossless PNG images for dataset harvesting
        queue_path = IMAGES_DIR / f"{sample_id}_queue.png"
        canvas_path = IMAGES_DIR / f"{sample_id}_canvas.png"
        queue_path.write_bytes(base64.b64decode(queue_b64.split(",")[-1]))
        canvas_path.write_bytes(base64.b64decode(canvas_b64.split(",")[-1]))

        prompt = (
            "You are an expert OCR and icon matching vision system.\n"
            "Given: 1. Target Queue (88x24 px, 3 icons left-to-right), 2. Main Canvas (240x200 px, 4 scattered icons).\n"
            "Find the 3 queue icons on the canvas in order. Return center (x,y) on the 240x200 canvas.\n"
            "Output MUST be valid JSON array: [{\"x\": int, \"y\": int}, {\"x\": int, \"y\": int}, {\"x\": int, \"y\": int}].\n"
            "Return ONLY the JSON array, zero prose."
        )

        for model in [self.primary_model, self.fallback_model]:
            try:
                coords = self._call_vision_llm(model, prompt, queue_b64, canvas_b64)
                if coords and len(coords) == 3:
                    # Normalize to even pixels and clamp bounds
                    norm_coords = []
                    for pt in coords:
                        x = max(0, min(240, int(pt.get("x", 0))))
                        y = max(0, min(200, int(pt.get("y", 0))))
                        x = x if x % 2 == 0 else max(0, x - 1)
                        y = y if y % 2 == 0 else max(0, y - 1)
                        norm_coords.append({"x": x, "y": y})

                    elapsed_ms = int((time.time() - t0) * 1000)
                    self._record_annotation(sample_id, norm_coords, model)
                    return {"status": "ok", "coordinates": norm_coords, "sample_id": sample_id, "latency_ms": elapsed_ms}
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")

        raise RuntimeError("All vision solver models failed to resolve captcha")

    def _call_vision_llm(self, model: str, prompt: str, q_b64: str, c_b64: str) -> List[Dict[str, int]]:
        req_body = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{q_b64}" if not q_b64.startswith("data:") else q_b64}},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{c_b64}" if not c_b64.startswith("data:") else c_b64}},
                    ],
                }
            ],
            "temperature": 0.1,
        }
        req = urllib.request.Request(
            f"{self.api_base}/chat/completions",
            data=json.dumps(req_body).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read())
            content = data["choices"][0]["message"]["content"]
            match = re.search(r"\[\s*\{.*?\}\s*\]", content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        return []

    def _record_annotation(self, sample_id: str, coords: List[Dict[str, int]], model: str):
        record = {
            "sample_id": sample_id,
            "coordinates": coords,
            "model": model,
            "verified_by_server": False,
            "timestamp": datetime.now().isoformat(),
        }
        with open(ANNOTATIONS_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")

    def mark_verified(self, sample_id: str):
        """Mark annotation as ground truth when verified by server reward claim."""
        if not ANNOTATIONS_FILE.exists():
            return
        lines = ANNOTATIONS_FILE.read_text().splitlines()
        updated = []
        for line in lines:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("sample_id") == sample_id:
                rec["verified_by_server"] = True
            updated.append(json.dumps(rec))
        ANNOTATIONS_FILE.write_text("\n".join(updated) + "\n")
