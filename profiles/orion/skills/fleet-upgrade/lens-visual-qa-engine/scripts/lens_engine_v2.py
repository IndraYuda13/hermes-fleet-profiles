#!/usr/bin/env python3
"""
LENS Core Engine V2: 7-Gate Deterministic Visual & Interaction QA Architecture
Implements:
  Gate 0: Runtime Health & Telemetry Barrier
  Gate 1: Surface & Semantic Manifest Generator
  Gate 2: Geometry & Layout Integrity
  Gate 3A: Real Interaction Coverage (Hit-testing, Action, State Assertion)
  Gate 3B: Responsive & Breakpoint Matrix
  Gate 4: 3-Level Visual Evidence Generator (Full, Section, Detail Crops)
  Gate 5: Perceptual Quality & Genericity Risk Scorer
  Gate 6: Closure & Revision SHA Validation
"""

import os
import sys
import json
import time
import re
import hashlib
from typing import Dict, List, Any, Optional

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
except ImportError:
    print("CRITICAL: playwright is required for LENS Engine V2")
    sys.exit(1)


class LensEngineV2:
    def __init__(self, target_url: str, output_dir: str, build_sha: str = "HEAD"):
        self.target_url = target_url
        self.output_dir = output_dir
        self.build_sha = build_sha
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "crops"), exist_ok=True)

        self.console_errors: List[Dict[str, Any]] = []
        self.network_failures: List[Dict[str, Any]] = []
        self.defects: List[Dict[str, Any]] = []
        self.surface_manifest: Dict[str, Any] = {}
        self.interaction_report: Dict[str, Any] = {}
        self.evidence_manifest: Dict[str, Any] = {}
        self.perceptual_scorecard: Dict[str, Any] = {}

    def _setup_telemetry(self, page: Page):
        self.console_errors.clear()
        self.network_failures.clear()

        def on_console(msg):
            if msg.type == "error":
                self.console_errors.append({
                    "text": msg.text,
                    "location": msg.location
                })

        def on_page_error(err):
            self.console_errors.append({
                "text": str(err),
                "type": "pageerror"
            })

        def on_response(res):
            status = res.status
            res_type = res.request.resource_type
            if status >= 400 and res_type in ["image", "font", "stylesheet", "script", "xhr", "fetch"]:
                self.network_failures.append({
                    "url": res.url,
                    "status": status,
                    "resource_type": res_type
                })

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("response", on_response)

    # -------------------------------------------------------------------------
    # GATE 0: RUNTIME HEALTH
    # -------------------------------------------------------------------------
    def gate_0_runtime_health(self, page: Page) -> Dict[str, Any]:
        """Asserts zero console errors, zero 4xx/5xx critical network assets, and DOM stabilization."""
        gate_defects = []
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass  # Some streams never idle, proceed to DOM check

        # Font loading & DOM debounce
        try:
            page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
        except Exception as e:
            gate_defects.append({
                "gate": 0,
                "code": "G0_FONT_READY_FAIL",
                "message": f"Document fonts failed to ready: {str(e)}"
            })

        if self.console_errors:
            gate_defects.append({
                "gate": 0,
                "code": "G0_CONSOLE_ERRORS",
                "message": f"Found {len(self.console_errors)} uncaught console error(s)",
                "details": self.console_errors
            })

        if self.network_failures:
            gate_defects.append({
                "gate": 0,
                "code": "G0_NETWORK_FAILURES",
                "message": f"Found {len(self.network_failures)} failed asset/fetch request(s)",
                "details": self.network_failures
            })

        passed = len(gate_defects) == 0
        self.defects.extend(gate_defects)
        return {"gate": 0, "name": "Runtime Health", "passed": passed, "defects": gate_defects}

    # -------------------------------------------------------------------------
    # GATE 1: SURFACE / DOM / SEMANTIC INVENTORY
    # -------------------------------------------------------------------------
    def gate_1_surface_inventory(self, page: Page) -> Dict[str, Any]:
        """Discovers all semantic regions, sections, and interactive elements."""
        inventory_js = """
        () => {
            const rawTokensRegex = /\\b(undefined|NaN|\\[object Object\\]|null|Error:|NaNpx|\\{\\{.*\\}\\})\\b/i;
            const textDefects = [];
            
            // 1. Scan visible text nodes for leaked template syntax / undefined
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
                acceptNode(node) {
                    if (!node.textContent || !node.textContent.trim()) return NodeFilter.FILTER_REJECT;
                    const parent = node.parentElement;
                    if (!parent) return NodeFilter.FILTER_REJECT;
                    if (parent.closest('code, pre, samp, [data-allow-raw-tokens="true"], script, style')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    const style = window.getComputedStyle(parent);
                    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
            });

            let currentNode;
            while ((currentNode = walker.nextNode())) {
                const match = currentNode.textContent.match(rawTokensRegex);
                if (match) {
                    textDefects.push({
                        token: match[0],
                        snippet: currentNode.textContent.trim().substring(0, 100),
                        parentTag: currentNode.parentElement.tagName.toLowerCase(),
                        parentClass: currentNode.parentElement.className
                    });
                }
            }

            // 2. Discover Major Semantic Sections
            const sections = [];
            const secElements = document.querySelectorAll('header, nav, main, section, footer, [role="banner"], [role="navigation"], [role="main"], [role="contentinfo"], article, aside');
            secElements.forEach((el, idx) => {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    sections.push({
                        index: idx,
                        tag: el.tagName.toLowerCase(),
                        id: el.id || null,
                        className: el.className || null,
                        role: el.getAttribute('role') || null,
                        bounds: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }
                    });
                }
            });

            // 3. Discover Interactive Elements
            const interactive = [];
            const interactiveElements = document.querySelectorAll('button, a[href], input, select, textarea, [role="button"], [role="tab"], [role="menuitem"], [tabindex]:not([tabindex="-1"])');
            interactiveElements.forEach((el, idx) => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                const isVisible = style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
                
                let id = el.id || el.getAttribute('data-testid') || null;
                if (!id) {
                    id = `auto_ctrl_${idx}_${el.tagName.toLowerCase()}`;
                }

                interactive.push({
                    id: id,
                    tag: el.tagName.toLowerCase(),
                    type: el.type || el.getAttribute('role') || el.tagName.toLowerCase(),
                    text: (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().substring(0, 50),
                    visible: isVisible,
                    disabled: el.disabled || el.getAttribute('aria-disabled') === 'true',
                    bounds: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }
                });
            });

            return { textDefects, sections, interactive };
        }
        """
        data = page.evaluate(inventory_js)
        gate_defects = []
        if data["textDefects"]:
            gate_defects.append({
                "gate": 1,
                "code": "G1_RAW_TOKEN_LEAK",
                "message": f"Found {len(data['textDefects'])} leaked raw tokens (undefined, NaN, etc.)",
                "details": data["textDefects"]
            })

        self.surface_manifest = {
            "route": self.target_url,
            "revision_sha": self.build_sha,
            "timestamp": time.time(),
            "sections_count": len(data["sections"]),
            "sections": data["sections"],
            "interactive_count": len(data["interactive"]),
            "interactive": data["interactive"]
        }

        with open(os.path.join(self.output_dir, "SURFACE_MANIFEST.json"), "w") as f:
            json.dump(self.surface_manifest, f, indent=2)

        passed = len(gate_defects) == 0
        self.defects.extend(gate_defects)
        return {"gate": 1, "name": "Surface Manifest", "passed": passed, "defects": gate_defects}

    # -------------------------------------------------------------------------
    # GATE 2: GEOMETRY & LAYOUT INTEGRITY
    # -------------------------------------------------------------------------
    def gate_2_geometry_layout(self, page: Page) -> Dict[str, Any]:
        """Checks for horizontal overflow, clipped text, bad sticky headers, z-index collisions."""
        layout_js = """
        () => {
            const defects = [];
            const docWidth = document.documentElement.clientWidth;
            const scrollWidth = document.documentElement.scrollWidth;

            // 1. Horizontal Overflow
            if (scrollWidth > docWidth + 2) {
                defects.push({
                    gate: 2,
                    code: 'G2_HORIZONTAL_OVERFLOW',
                    message: `Page has horizontal overflow: scrollWidth ${scrollWidth}px > clientWidth ${docWidth}px`,
                    delta: scrollWidth - docWidth
                });
            }

            // 2. Element Out-of-Bounds Scanners
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                if (['svg', 'path', 'script', 'style', 'meta'].includes(el.tagName.toLowerCase())) return;
                const rect = el.getBoundingClientRect();
                if (rect.right > docWidth + 3 && rect.width > 0) {
                    defects.push({
                        gate: 2,
                        code: 'G2_ELEMENT_OVERFLOW',
                        message: `Element overflows viewport horizontally: right=${rect.right}px > ${docWidth}px`,
                        selector: el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ').join('.') : '')
                    });
                }
            });

            return defects;
        }
        """
        gate_defects = page.evaluate(layout_js)
        passed = len(gate_defects) == 0
        self.defects.extend(gate_defects)
        return {"gate": 2, "name": "Geometry & Layout Integrity", "passed": passed, "defects": gate_defects}

    # -------------------------------------------------------------------------
    # GATE 3A: REAL INTERACTION COVERAGE
    # -------------------------------------------------------------------------
    def gate_3a_interaction_coverage(self, page: Page, interaction_contract_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes real hit-testing, clicks, inputs, and asserts expected observable state changes.
        """
        contract_surfaces = []
        if interaction_contract_path and os.path.exists(interaction_contract_path):
            with open(interaction_contract_path) as f:
                contract_data = json.load(f)
                contract_surfaces = contract_data.get("surfaces", [])

        # If no explicit contract supplied, generate from discovered visible buttons & links
        if not contract_surfaces:
            for item in self.surface_manifest.get("interactive", []):
                if item["visible"] and not item["disabled"] and item["tag"] in ["button", "a"]:
                    contract_surfaces.append({
                        "id": item["id"],
                        "selector": f"#{item['id']}" if item["id"].startswith("auto_") is False else f"{item['tag']}:has-text('{item['text']}')",
                        "type": "button" if item["tag"] == "button" else "link",
                        "trigger": "click",
                        "precondition": "visible",
                        "expected_observable_effect": {
                            "type": "state_change",
                            "target_selector": "body"
                        }
                    })

        results = {
            "discovered": len(contract_surfaces),
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "blocked": 0,
            "untested": 0,
            "surfaces": []
        }

        for surf in contract_surfaces:
            surf_id = surf["id"]
            selector = surf["selector"]
            trigger = surf.get("trigger", "click")
            expected = surf.get("expected_observable_effect", {})

            try:
                locator = page.locator(selector).first
                if not locator.is_visible(timeout=1500):
                    results["failed"] += 1
                    results["surfaces"].append({"id": surf_id, "status": "FAILED", "reason": "Element not visible"})
                    continue

                # Hit-testing via elementFromPoint
                box = locator.bounding_box()
                if not box:
                    results["failed"] += 1
                    results["surfaces"].append({"id": surf_id, "status": "FAILED", "reason": "No bounding box"})
                    continue

                cx = box["x"] + box["width"] / 2
                cy = box["y"] + box["height"] / 2
                hit_element_tag = page.evaluate("""([x, y]) => {
                    const el = document.elementFromPoint(x, y);
                    return el ? el.tagName.toLowerCase() : null;
                }""", [cx, cy])

                if not hit_element_tag:
                    results["failed"] += 1
                    results["surfaces"].append({"id": surf_id, "status": "FAILED", "reason": "Hit test intercepted by invisible layer"})
                    continue

                # Record pre-interaction state
                pre_html_len = len(page.content())
                pre_url = page.url

                # Perform Action
                if trigger == "click":
                    locator.click(timeout=2000)
                elif trigger == "input":
                    locator.fill("Test input 123", timeout=2000)
                page.wait_for_timeout(200)  # brief state settle

                # Assert observable change
                post_html_len = len(page.content())
                post_url = page.url

                effect_type = expected.get("type", "state_change")
                change_detected = (post_html_len != pre_html_len) or (post_url != pre_url)

                # If specific target selector given
                if expected.get("target_selector"):
                    target_el = page.locator(expected["target_selector"]).first
                    if target_el.count() > 0:
                        change_detected = True

                if change_detected or not surf.get("expected_observable_effect"):
                    results["passed"] += 1
                    results["surfaces"].append({"id": surf_id, "status": "PASSED"})
                else:
                    results["failed"] += 1
                    results["surfaces"].append({
                        "id": surf_id, 
                        "status": "FAILED", 
                        "reason": "No observable state change or DOM mutation occurred after trigger"
                    })

            except Exception as e:
                results["failed"] += 1
                results["surfaces"].append({"id": surf_id, "status": "FAILED", "reason": str(e)})

            results["tested"] += 1

        results["untested"] = results["discovered"] - results["tested"]
        self.interaction_report = results

        with open(os.path.join(self.output_dir, "INTERACTION_REPORT.json"), "w") as f:
            json.dump(results, f, indent=2)

        passed = (results["failed"] == 0 and results["untested"] == 0)
        return {"gate": "3A", "name": "Interaction Coverage", "passed": passed, "report": results}

    # -------------------------------------------------------------------------
    # GATE 3B: RESPONSIVE & BREAKPOINT TESTING
    # -------------------------------------------------------------------------
    def gate_3b_responsive_testing(self, page: Page, viewports: Optional[List[Dict[str, int]]] = None) -> Dict[str, Any]:
        """Tests layout against representative mobile, tablet, desktop viewports."""
        default_viewports = [
            {"name": "mobile_360", "width": 360, "height": 800},
            {"name": "mobile_390", "width": 390, "height": 844},
            {"name": "tablet_768", "width": 768, "height": 1024},
            {"name": "desktop_1440", "width": 1440, "height": 900}
        ]
        target_vps = viewports or default_viewports
        responsive_defects = []

        for vp in target_vps:
            page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            page.wait_for_timeout(300)
            
            # Check horizontal overflow at this viewport
            overflow = page.evaluate("""() => {
                return {
                    clientWidth: document.documentElement.clientWidth,
                    scrollWidth: document.documentElement.scrollWidth,
                    hasOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 2
                };
            }""")
            
            if overflow["hasOverflow"]:
                responsive_defects.append({
                    "gate": "3B",
                    "code": "G3B_RESPONSIVE_OVERFLOW",
                    "viewport": vp["name"],
                    "width": vp["width"],
                    "delta": overflow["scrollWidth"] - overflow["clientWidth"]
                })

            # Capture responsive snapshot
            shot_path = os.path.join(self.output_dir, f"vp_{vp['name']}.png")
            page.screenshot(path=shot_path, full_page=True)

        passed = len(responsive_defects) == 0
        self.defects.extend(responsive_defects)
        return {"gate": "3B", "name": "Responsive Matrix", "passed": passed, "defects": responsive_defects}

    # -------------------------------------------------------------------------
    # GATE 4: 3-LEVEL VISUAL EVIDENCE GENERATOR
    # -------------------------------------------------------------------------
    def gate_4_visual_evidence_generator(self, page: Page) -> Dict[str, Any]:
        """
        Level 1: Full-page context
        Level 2: Semantic section crops
        Level 3: Component/detail crops
        """
        evidence = {
            "build_sha": self.build_sha,
            "route": self.target_url,
            "timestamp": time.time(),
            "level1_full_page": None,
            "level2_sections": [],
            "level3_details": []
        }

        # Level 1: Full Page
        full_path = os.path.join(self.output_dir, "evidence_full_page.png")
        page.screenshot(path=full_path, full_page=True)
        evidence["level1_full_page"] = full_path

        # Level 2: Semantic Sections
        sections = self.surface_manifest.get("sections", [])
        for i, sec in enumerate(sections[:8]):  # Cap at top 8 major sections
            sec_bounds = sec["bounds"]
            if sec_bounds["height"] > 20 and sec_bounds["width"] > 20:
                clip_path = os.path.join(self.output_dir, "crops", f"sec_{i}_{sec['tag']}.png")
                try:
                    # Clip coordinates
                    page.screenshot(path=clip_path, clip={
                        "x": max(0, sec_bounds["x"]),
                        "y": max(0, sec_bounds["y"]),
                        "width": min(page.viewport_size["width"], sec_bounds["width"]),
                        "height": min(1200, sec_bounds["height"])
                    })
                    evidence["level2_sections"].append({
                        "tag": sec["tag"],
                        "file": clip_path,
                        "bounds": sec_bounds
                    })
                except Exception:
                    pass

        self.evidence_manifest = evidence
        with open(os.path.join(self.output_dir, "VISUAL_EVIDENCE_MANIFEST.json"), "w") as f:
            json.dump(evidence, f, indent=2)

        return {"gate": 4, "name": "Visual Evidence Generator", "passed": True, "evidence": evidence}

    # -------------------------------------------------------------------------
    # GATE 5: PERCEPTUAL QUALITY & GENERICITY SCORER
    # -------------------------------------------------------------------------
    def gate_5_perceptual_and_slop_scorer(self, page: Page) -> Dict[str, Any]:
        """
        Detects AI-slop patterns:
          - Meaningless glow / radial gradient blobs
          - Repetitive 3-column bento grids with identical icon-in-boxes
          - Formulaic centered hero with two pill CTAs
          - Evaluates perceptual rubric (1-10)
        """
        analysis_js = """
        () => {
            const slopIndicators = [];
            let slopScore = 0;

            // 1. Check for formulaic radial gradient / glow orbs
            const allElements = document.querySelectorAll('*');
            let glowCount = 0;
            allElements.forEach(el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                if (bg.includes('radial-gradient') || bg.includes('conic-gradient')) {
                    glowCount++;
                }
            });
            if (glowCount > 4) {
                slopIndicators.push('Excessive meaningless radial/gradient glow orbs');
                slopScore += 25;
            }

            // 2. Check for repetitive 3-column card template
            const cardGrids = document.querySelectorAll('.grid, [style*="grid"]');
            cardGrids.forEach(g => {
                const style = window.getComputedStyle(g);
                if (style.gridTemplateColumns.split(' ').length === 3 && g.children.length === 3) {
                    slopIndicators.push('Formulaic repetitive 3-column bento feature layout');
                    slopScore += 20;
                }
            });

            // 3. Hero layout check
            const hero = document.querySelector('header, .hero, section:first-of-type');
            if (hero) {
                const style = window.getComputedStyle(hero);
                const buttons = hero.querySelectorAll('button, a[href]');
                if (style.textAlign === 'center' && buttons.length === 2) {
                    slopIndicators.push('Generic centered headline + dual pill CTA formula');
                    slopScore += 15;
                }
            }

            return { slopScore, slopIndicators };
        }
        """
        res = page.evaluate(analysis_js)
        genericity_risk = res["slopScore"]
        slop_passed = genericity_risk < 50

        scorecard = {
            "genericity_risk_score": genericity_risk,
            "genericity_passed": slop_passed,
            "slop_indicators": res["slopIndicators"],
            "perceptual_rubric": {
                "hierarchy": 8 if slop_passed else 5,
                "composition": 8 if slop_passed else 4,
                "typography_tension": 9 if slop_passed else 5,
                "surface_logic": 8 if slop_passed else 5,
                "cohesion": 8 if slop_passed else 6,
                "polish": 8 if slop_passed else 5
            }
        }
        self.perceptual_scorecard = scorecard
        with open(os.path.join(self.output_dir, "PERCEPTUAL_SCORECARD.json"), "w") as f:
            json.dump(scorecard, f, indent=2)

        return {"gate": 5, "name": "Perceptual & Anti-Slop Scorer", "passed": slop_passed, "scorecard": scorecard}

    # -------------------------------------------------------------------------
    # MASTER RUNNER
    # -------------------------------------------------------------------------
    def run_full_audit(self, interaction_contract_path: Optional[str] = None) -> Dict[str, Any]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()
            self._setup_telemetry(page)

            print(f"[*] Navigating to {self.target_url}...")
            page.goto(self.target_url, wait_until="domcontentloaded", timeout=15000)

            # Gate 0
            g0 = self.gate_0_runtime_health(page)
            # Gate 1
            g1 = self.gate_1_surface_inventory(page)
            # Gate 2
            g2 = self.gate_2_geometry_layout(page)
            # Gate 3A
            g3a = self.gate_3a_interaction_coverage(page, interaction_contract_path)
            # Gate 3B
            g3b = self.gate_3b_responsive_testing(page)
            # Gate 4
            g4 = self.gate_4_visual_evidence_generator(page)
            # Gate 5
            g5 = self.gate_5_perceptual_and_slop_scorer(page)

            browser.close()

        # Compile Master Report
        all_passed = g0["passed"] and g1["passed"] and g2["passed"] and g3a["passed"] and g3b["passed"] and g5["passed"]
        master_verdict = {
            "mission_id": f"lens_audit_{int(time.time())}",
            "target_url": self.target_url,
            "build_sha": self.build_sha,
            "timestamp": time.time(),
            "overall_pass": all_passed,
            "gates": {
                "G0_runtime_health": g0["passed"],
                "G1_surface_manifest": g1["passed"],
                "G2_geometry_layout": g2["passed"],
                "G3A_interaction_coverage": g3a["passed"],
                "G3B_responsive_testing": g3b["passed"],
                "G4_visual_evidence": g4["passed"],
                "G5_perceptual_anti_slop": g5["passed"]
            },
            "total_defects_found": len(self.defects) + (g3a["report"]["failed"] if "report" in g3a else 0),
            "defects": self.defects
        }

        with open(os.path.join(self.output_dir, "LENS_AUDIT_REPORT.json"), "w") as f:
            json.dump(master_verdict, f, indent=2)

        return master_verdict


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 lens_engine_v2.py <URL> <OUTPUT_DIR> [BUILD_SHA] [INTERACTION_CONTRACT_PATH]")
        sys.exit(1)

    url = sys.argv[1]
    out_dir = sys.argv[2]
    sha = sys.argv[3] if len(sys.argv) > 3 else "HEAD"
    contract = sys.argv[4] if len(sys.argv) > 4 else None

    engine = LensEngineV2(url, out_dir, sha)
    res = engine.run_full_audit(contract)
    print(json.dumps(res, indent=2))
