#!/usr/bin/env python3
"""
Automated Client-Side Armor & Obfuscation Build Script
Transforms clean HTML/CSS/JS source into a hardened, 1-line production artifact with anti-inspect protection.
"""

import os
import re
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_HTML = os.path.join(BASE_DIR, "index.html")
DIST_DIR = os.path.join(os.path.dirname(BASE_DIR), "dist")
DIST_HTML = os.path.join(DIST_DIR, "index.html")

print("Starting client-side armor build...")

if not os.path.exists(SRC_HTML):
    print(f"Error: Source file not found at {SRC_HTML}")
    exit(1)

with open(SRC_HTML, "r", encoding="utf-8") as f:
    src_code = f.read()

s_tag = "<script>"
e_tag = "</script>"
s_idx = src_code.find(s_tag)
e_idx = src_code.rfind(e_tag)

if s_idx == -1 or e_idx == -1:
    print("Error: <script> tag not found.")
    exit(1)

html_before = src_code[:s_idx]
js_code = src_code[s_idx + len(s_tag):e_idx].strip()
html_after = src_code[e_idx + len(e_tag):]

# Extract function names to preserve on window
function_names = re.findall(r"function\s+([a-zA-Z0-9_]+)\s*\(", js_code)
window_exports = "\n".join([f"window.{fn} = {fn};" for fn in set(function_names)])

anti_inspect = """
(function() {
  document.addEventListener('contextmenu', function(e) { e.preventDefault(); return false; }, { capture: true });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'F12' || e.keyCode === 123) { e.preventDefault(); e.stopPropagation(); return false; }
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && ['I','i','J','j','C','c'].includes(e.key)) { e.preventDefault(); e.stopPropagation(); return false; }
    if ((e.ctrlKey || e.metaKey) && (e.key === 'U' || e.key === 'u')) { e.preventDefault(); e.stopPropagation(); return false; }
    if ((e.ctrlKey || e.metaKey) && (e.key === 'S' || e.key === 's')) { e.preventDefault(); e.stopPropagation(); return false; }
  }, { capture: true });
  setInterval(function() { if (window.console) { try { console.clear(); } catch(e) {} } }, 1000);
})();
"""

full_js = anti_inspect + "\n" + js_code + "\n" + window_exports

temp_in = "/tmp/armor_build_in.js"
temp_out = "/tmp/armor_build_out.js"

with open(temp_in, "w", encoding="utf-8") as f:
    f.write(full_js)

cmd = [
    "npx", "--yes", "javascript-obfuscator", temp_in,
    "--output", temp_out,
    "--compact", "true",
    "--control-flow-flattening", "true",
    "--control-flow-flattening-threshold", "0.7",
    "--dead-code-injection", "true",
    "--dead-code-injection-threshold", "0.25",
    "--string-array", "true",
    "--string-array-encoding", "base64",
    "--string-array-threshold", "0.75",
    "--split-strings", "true",
    "--split-strings-chunk-length", "5",
    "--identifier-names-generator", "hexadecimal",
    "--reserved-names", ",".join(set(function_names))
]

print("Running AST obfuscation...")
subprocess.run(cmd, check=True)

with open(temp_out, "r", encoding="utf-8") as f:
    obf_js = f.read().strip()

def minify_css(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([\{\}\:\;\,])\s*', r'\1', css)
    return css.strip()

style_s = html_before.find("<style>")
style_e = html_before.find("</style>")
if style_s != -1 and style_e != -1:
    raw_css = html_before[style_s+7:style_e]
    min_css = minify_css(raw_css)
    html_before = html_before[:style_s+7] + min_css + html_before[style_e:]

def minify_html(html_str):
    html_str = re.sub(r'<!--.*?-->', '', html_str, flags=re.DOTALL)
    html_str = re.sub(r'\s+', ' ', html_str)
    html_str = re.sub(r'>\s+<', '><', html_str)
    return html_str.strip()

min_before = minify_html(html_before)
min_after = minify_html(html_after)

final_html = min_before + "<script>" + obf_js + "</script>" + min_after

os.makedirs(DIST_DIR, exist_ok=True)
with open(DIST_HTML, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Build complete: {DIST_HTML} ({len(final_html)} bytes, 1 line)")
