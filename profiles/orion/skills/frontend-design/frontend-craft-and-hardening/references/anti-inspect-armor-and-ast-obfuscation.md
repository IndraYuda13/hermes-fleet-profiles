# Anti-Inspect Armor & AST Hexadecimal Obfuscation Pipeline

A battle-tested production pipeline for hardening single-page applications, static landing pages, and interactive client-side tools against casual source inspection, devtools snooping, and code tampering.

---

## 1. The Inline Event Handler Trap (`ReferenceError`)

### The Problem
When compressing and obfuscating JavaScript with tools like `javascript-obfuscator`, top-level function declarations (`function calculateRate() {...}`) are renamed into randomized hex identifiers (e.g. `_0x4f1a`) or wrapped in an isolated module scope / IIFE.

However, HTML elements frequently trigger logic via inline attributes:
```html
<button onclick="calculateRate()">Hitung</button>
<select onchange="onCategoryChange(this.value)">...</select>
```
Inline attributes resolve against the global `window` object. If `calculateRate` is renamed or scoped locally, browser execution throws:
```text
Uncaught ReferenceError: calculateRate is not defined
```

### The Solution: Pre-Build Event Extraction & Global Export Bridge
Parse HTML before obfuscation, extract every function called by inline event handlers (`onclick`, `onchange`, `onsubmit`, `oninput`, etc.), and append explicit global window assignments:

```python
import re

def extract_inline_handlers(html_content):
    # Match inline handler patterns: onxxx="funcName(arg1, arg2)"
    pattern = r'''(?:on\w+)\s*=\s*["']\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\('''
    matches = set(re.findall(pattern, html_content))
    return sorted(list(matches))

# Generate export bridge
def generate_window_exports(function_names):
    lines = ["\n/* --- EXPLICIT GLOBAL EXPORT BRIDGE --- */"]
    for fn in function_names:
        lines.append(f"if (typeof {fn} !== 'undefined') window.{fn} = {fn};")
    return "\n".join(lines)
```

---

## 2. Multi-Vector DevTools Defense & Infinite Debugger Trap

### Intercepting Shortcuts & Mouse Clicks
```javascript
// Disable context menu
document.addEventListener('contextmenu', (e) => e.preventDefault(), true);

// Intercept DevTools and Source Shortcuts
document.addEventListener('keydown', (e) => {
    // F12
    if (e.key === 'F12' || e.keyCode === 123) {
        e.preventDefault();
        return false;
    }
    // Ctrl+Shift+I (DevTools), Ctrl+Shift+J (Console), Ctrl+Shift+C (Inspect)
    // Mac: Cmd+Opt+I, Cmd+Opt+J, Cmd+Opt+C
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'I' || e.key === 'i' || e.key === 'J' || e.key === 'j' || e.key === 'C' || e.key === 'c')) {
        e.preventDefault();
        return false;
    }
    // Ctrl+U (View Page Source)
    if ((e.ctrlKey || e.metaKey) && (e.key === 'U' || e.key === 'u')) {
        e.preventDefault();
        return false;
    }
    // Ctrl+S (Save Page)
    if ((e.ctrlKey || e.metaKey) && (e.key === 'S' || e.key === 's')) {
        e.preventDefault();
        return false;
    }
}, true);
```

### The DevTools Killer (Infinite Recursive / Timer Debugger)
Browser shortcuts can be bypassed by opening DevTools via the application menu (*More Tools -> Developer Tools*). To neutralize this, run a recurring dynamic constructor debugger loop:

```javascript
setInterval(() => {
    (function () {
        try {
            (function b(i) {
                if (('' + (i / i)).length !== 1 || i % 20 === 0) {
                    (function () {}).constructor('debugger')();
                } else {
                    debugger;
                }
                b(++i);
            })(0);
        } catch (e) {
            setTimeout(a, 100);
        }
    })();
}, 100);

// Keep console cleared
setInterval(() => {
    console.clear();
}, 1000);
```
**Mechanism:** When DevTools is closed, `debugger` statements execute as no-ops in negligible sub-millisecond time. The instant DevTools opens, execution hits breakpoints 10 times per second, freezing script execution and locking DevTools interaction.

---

## 3. High-Security AST Obfuscation Profile

Use `javascript-obfuscator` CLI with maximum entropy settings:

```bash
javascript-obfuscator input.js --output output.js \
  --compact true \
  --control-flow-flattening true \
  --control-flow-flattening-threshold 0.75 \
  --dead-code-injection true \
  --dead-code-injection-threshold 0.4 \
  --string-array true \
  --string-array-encoding 'base64' \
  --string-array-threshold 0.8 \
  --split-strings true \
  --split-strings-chunk-length 5 \
  --identifier-names-generator hexadecimal \
  --transform-object-keys true \
  --self-defending false
```

*Note on `--self-defending`:* Keep `self-defending: false` if single-line packaging or subsequent post-processing modifies whitespace; otherwise the self-defending runtime check triggers an intentional browser crash.

---

## 4. Single-Line Production Packing

Convert multi-line markup and code into a single continuous stream:
```python
def single_line_pack(html_content):
    # Collapse multiple whitespace/newlines between tags
    packed = re.sub(r'>\s+<', '><', html_content)
    # Collapse remaining line breaks
    packed = re.sub(r'[\r\n]+', ' ', packed)
    # Normalize excessive spaces
    packed = re.sub(r'\s{2,}', ' ', packed).strip()
    return packed
```

---

## 5. cPanel Fileman API Deployment Rules

When deploying large armored single-line files (> 300KB) to cPanel using `/execute/Fileman/save_file_content`:
1. **Payload Expansion:** `urllib.parse.urlencode` expands hexadecimal and encoded strings by 25-35%.
2. **Timeout Invariant:** Over HTTP proxies/tunnels, transmitting a ~500KB POST body takes 35-50 seconds. Set `timeout >= 120`s in `urllib.request.urlopen` or `requests` to prevent connection drops.
