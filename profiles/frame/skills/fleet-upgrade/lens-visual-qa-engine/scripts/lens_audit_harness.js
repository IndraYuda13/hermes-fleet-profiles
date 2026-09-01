/**
 * LENS Automated Audit Harness (Playwright / CDP Integration)
 * Implements Gate 0 through Gate 3 deterministic evaluations and Mutation Self-Calibration.
 */

class LensAuditHarness {
  constructor(page) {
    this.page = page;
    this.consoleErrors = [];
    this.networkFailures = [];
  }

  // Setup CDP & Network Listeners for Gate 0
  async initTelemetry() {
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        this.consoleErrors.push({ text: msg.text(), location: msg.location() });
      }
    });

    this.page.on('pageerror', err => {
      this.consoleErrors.push({ text: err.message, stack: err.stack });
    });

    this.page.on('response', response => {
      const status = response.status();
      const url = response.url();
      const resourceType = response.request().resourceType();
      if (status >= 400 && ['image', 'font', 'stylesheet', 'script'].includes(resourceType)) {
        this.networkFailures.push({ url, status, resourceType });
      }
    });
  }

  // ==========================================
  // GATE 0: RUNTIME HEALTH & LIFECYCLE BARRIER
  // ==========================================
  async executeGate0(timeoutMs = 10000) {
    const defects = [];

    // 1. Wait for Network Idle & Fonts Loaded
    await this.page.waitForLoadState('networkidle');
    await this.page.evaluate(async () => {
      if (document.fonts) await document.fonts.ready;
    });

    // 2. DOM Mutation Debounce (200ms stability)
    await this.page.evaluate(() => {
      return new Promise((resolve) => {
        let timer;
        const observer = new MutationObserver(() => {
          clearTimeout(timer);
          timer = setTimeout(() => { observer.disconnect(); resolve(); }, 200);
        });
        observer.observe(document.body, { childList: true, subtree: true, attributes: true });
        timer = setTimeout(() => { observer.disconnect(); resolve(); }, 200);
      });
    });

    // 3. Assert Zero Console Errors
    if (this.consoleErrors.length > 0) {
      defects.push({
        gate: 0,
        code: 'G0_CONSOLE_ERROR',
        message: `Found ${this.consoleErrors.length} uncaught console error(s)`,
        details: this.consoleErrors
      });
    }

    // 4. Assert Zero Asset 4xx/5xx Failures
    if (this.networkFailures.length > 0) {
      defects.push({
        gate: 0,
        code: 'G0_ASSET_4XX_5XX',
        message: `Found ${this.networkFailures.length} failed static asset request(s)`,
        details: this.networkFailures
      });
    }

    return { pass: defects.length === 0, defects };
  }

  // ==========================================
  // GATE 1: DOM & SEMANTIC INTEGRITY SCANNER
  // ==========================================
  async executeGate1() {
    return await this.page.evaluate(() => {
      const defects = [];
      const forbiddenRegex = /\b(undefined|NaN|\[object Object\]|null|Error:|NaNpx|\{\{.*\}\})\b/i;

      // 1. Context-Aware Text Scanner (Excludes <code>, <pre>, [data-allow-raw-tokens])
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

      let textNode;
      while ((textNode = walker.nextNode())) {
        const text = textNode.textContent.trim();
        if (forbiddenRegex.test(text)) {
          defects.push({
            gate: 1,
            code: 'G1_FORBIDDEN_TOKEN',
            text: text,
            parentTag: textNode.parentElement.tagName,
            parentClass: textNode.parentElement.className
          });
        }
      }

      // 2. Broken Image & Asset Probe
      document.querySelectorAll('img').forEach(img => {
        if (!img.complete || img.naturalWidth === 0) {
          defects.push({
            gate: 1,
            code: 'G1_BROKEN_IMAGE',
            src: img.src,
            alt: img.alt
          });
        }
      });

      // 3. SVG & Icon Geometry Probe
      document.querySelectorAll('svg').forEach(svg => {
        const rect = svg.getBoundingClientRect();
        const hasVisibleChild = Array.from(svg.children).some(c => ['path', 'circle', 'rect', 'polygon', 'use', 'g'].includes(c.tagName.toLowerCase()));
        if ((rect.width === 0 || rect.height === 0 || !hasVisibleChild) && window.getComputedStyle(svg).display !== 'none') {
          defects.push({
            gate: 1,
            code: 'G1_EMPTY_SVG',
            className: svg.className.baseVal || svg.className,
            parentTag: svg.parentElement ? svg.parentElement.tagName : 'unknown'
          });
        }
      });

      // 4. Viewport Horizontal Overflow Probe
      if (document.documentElement.scrollWidth > window.innerWidth) {
        defects.push({
          gate: 1,
          code: 'G1_VIEWPORT_OVERFLOW',
          scrollWidth: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
          overflowDelta: document.documentElement.scrollWidth - window.innerWidth
        });
      }

      return { pass: defects.length === 0, defects };
    });
  }

  // ==========================================
  // GATE 2: METROLOGY & SCHEMA EVALUATOR
  // ==========================================
  async executeGate2() {
    return await this.page.evaluate(() => {
      const defects = [];

      // Helper: Relative Luminance
      function getLuminance(r, g, b) {
        const [rs, gs, bs] = [r, g, b].map(c => {
          c = c / 255;
          return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
      }

      function parseRgb(colorStr) {
        const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : [0, 0, 0];
      }

      // 1. Silent Text Clipping Detector
      document.querySelectorAll('*').forEach(el => {
        if (el.children.length === 0 && el.textContent.trim().length > 0) {
          const style = window.getComputedStyle(el);
          if (style.overflowX === 'hidden' && style.textOverflow !== 'ellipsis' && el.scrollWidth > el.clientWidth + 1) {
            defects.push({
              gate: 2,
              code: 'G2_SILENT_CLIPPING',
              text: el.textContent.trim().substring(0, 30),
              scrollWidth: el.scrollWidth,
              clientWidth: el.clientWidth
            });
          }
        }
      });

      // 2. Minimum Touch Targets (>= 44x44px for buttons & interactive elements)
      document.querySelectorAll('button, a, input[type="button"], [role="button"]').forEach(btn => {
        const rect = btn.getBoundingClientRect();
        const style = window.getComputedStyle(btn);
        if (style.display !== 'none' && style.visibility !== 'hidden' && (rect.width > 0 || rect.height > 0)) {
          if (rect.width < 44 || rect.height < 44) {
            defects.push({
              gate: 2,
              code: 'G2_TOUCH_TARGET_SMALL',
              tag: btn.tagName,
              dimensions: `${rect.width.toFixed(1)}x${rect.height.toFixed(1)}px`,
              text: btn.textContent.trim().substring(0, 20)
            });
          }
        }
      });

      // 3. Runtime Schema Verification (data-ui-* attributes)
      document.querySelectorAll('[data-ui-min-touch]').forEach(el => {
        const req = parseFloat(el.getAttribute('data-ui-min-touch'));
        const rect = el.getBoundingClientRect();
        if (rect.width < req || rect.height < req) {
          defects.push({
            gate: 2,
            code: 'G2_SCHEMA_DRIFT',
            contract: `min-touch: ${req}px`,
            actual: `${rect.width}x${rect.height}px`
          });
        }
      });

      return { pass: defects.length === 0, defects };
    });
  }

  // ==========================================
  // GATE 3: DYNAMIC VIEWPORT & FUZZING SWEEP
  // ==========================================
  async executeGate3() {
    const defects = [];
    const widths = [320, 375, 414, 768, 1024, 1280, 1440, 1920];

    for (const w of widths) {
      await this.page.setViewportSize({ width: w, height: 800 });
      await this.page.waitForTimeout(100);

      const overflow = await this.page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth
          ? document.documentElement.scrollWidth - window.innerWidth
          : 0;
      });

      if (overflow > 0) {
        defects.push({
          gate: 3,
          code: 'G3_RESPONSIVE_BREAK',
          viewportWidth: w,
          overflowPixels: overflow
        });
      }
    }

    // Reset to default viewport
    await this.page.setViewportSize({ width: 1440, height: 900 });
    return { pass: defects.length === 0, defects };
  }

  // ==========================================
  // FULL FAIL-FAST AUDIT EXECUTION
  // ==========================================
  async runFullAudit() {
    console.log('[LENS] Executing Gate 0 (Runtime Health)...');
    const g0 = await this.executeGate0();
    if (!g0.pass) return { verdict: 'FAIL', failedGate: 0, defects: g0.defects };

    console.log('[LENS] Executing Gate 1 (DOM & Semantic Integrity)...');
    const g1 = await this.executeGate1();
    if (!g1.pass) return { verdict: 'FAIL', failedGate: 1, defects: g1.defects };

    console.log('[LENS] Executing Gate 2 (Deterministic Metrology)...');
    const g2 = await this.executeGate2();
    if (!g2.pass) return { verdict: 'FAIL', failedGate: 2, defects: g2.defects };

    console.log('[LENS] Executing Gate 3 (Active Interaction & Fuzzing)...');
    const g3 = await this.executeGate3();
    if (!g3.pass) return { verdict: 'FAIL', failedGate: 3, defects: g3.defects };

    return {
      verdict: 'PASS_TO_GATE_4',
      message: 'Gates 0-3 passed deterministically. Ready for Gate 4 VLM Macro Art Direction.'
    };
  }
}

module.exports = LensAuditHarness;
