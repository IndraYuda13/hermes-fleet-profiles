---
name: burp-mcp-headless-revival
description: Use when Burp MCP SSE :9876 is down or Burp wizard is stuck.
version: 1.0.0
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [burp, mcp, xvfb, headless, revival, web-pentest]
    related_skills: [rea-ghidra-hermes-setup, web-pentest-indonesia]
---

# Reviving Burp Suite + BurpMCP-Ultra on a headless Xvfb display

## When to Use

Load this skill when `hermes -p <profile> mcp test burp` fails with a connection
refused on 127.0.0.1:9876 (or the user reports Burp tools missing after a reboot),
especially while a Burp java process is still alive on the box.

Burp runs on Xvfb :99 (`/usr/bin/Xvfb :99 -screen 0 1024x768x16 -ac +extension RANDR`)
with the BurpMCP-Ultra extension (`/opt/burp-extensions/burpmcp-ultra-2.3.0.jar`, 150
tools) registered in `/root/.BurpSuite/UserConfigCommunity.json`
(`user_options/extender/extensions[0]`, `loaded: true`). After a reboot the Burp JVM
survives but sits stuck in the startup wizard — no SSE on 9876 — and Hermes reports
burp as connection-refused. Symptom chain: `mcp test burp` -> "Connect call failed
('127.0.0.1', 9876)" while a `/opt/burpsuite/jre/bin/java` process IS alive.

## Diagnose first

- `ss -tlnp | grep 9876` — dead means the extension is not serving.
- `ps -eo pid,ppid,lstart,cmd | grep burpsuite/jre` — TWO java processes are NORMAL
  (install4j splash JVM + app JVM). An app JVM with PPID 1 that is not yours is an
  ORPHAN from a previous launch: kill it by PID (never `pkill` — denied in the
  testing profile). An orphan owns an overlapping window at the same position and
  silently steals your clicks.
- Burp dialogs are invisible to Hermes; drive them with xdotool on DISPLAY=:99.

## Wizard flow (repeats on EVERY JVM launch, including the install4j relaunch)

1. Temp-files dialog "Delete old temporary files?" (518x151; buttons at the
   BOTTOM RIGHT, local x~395/462, y~113 — NOT centered):
   `xdotool windowraise <id>` then click `pos+395, pos+113` (left = yes/delete).
2. Welcome screen ("Temporary project in memory"): the Start button is ORANGE
   (RGB ~(255,101,49)), bottom-right. Find it by scanning the screenshot pixels for
   that color, then click its center. `xdotool key Return` does NOT work — raw Xvfb
   has no window manager, synthetic key events go nowhere; only real clicks land.
3. "Select the configuration..." page: click its orange Start button again.
4. install4j then RELAUNCHES a fresh JVM — the whole wizard REPEATS on the new JVM
   (temp-files dialog — this variant has Delete/Leave buttons; answer **Leave** so
   the previous JVM's temp dir survives — then welcome + config pages again).
   Click through both orange Start buttons on the NEW window.
5. Poll `ss -tlnp | grep 9876` — it comes up within ~10-60s of the final Start.
6. Kill the pre-relaunch JVM afterwards (black window, overlapping).

## Reading the headless GUI without a vision model

`tesseract` 5.3.4 + `DISPLAY=:99 import -window <id> x.png` gives OCR with word
boxes: `tesseract x.png stdout tsv` then read columns 7/8 (x,y) and 12 (word).
Upscale crops 2-4x for small button labels. When OCR misses a button, scan pixels
for the Burp orange (255,101,49) or the Java button gray; ASCII-art rendering of a
downscaled screenshot is a good last resort for layout.

## Verify

`hermes -p <profile> mcp test burp` -> "Tools discovered: 150". Hermes burp config:
SSE `http://127.0.0.1:9876/` with `Authorization: Bearer <token>` under
`mcp_servers.burp` (token stays in config.yaml — never print it).

## Multi-profile entries for the same Burp server

Several profiles (and the default home, targeted as `hermes -p default`) may carry a
`burpmcp` entry for the same SSE server WITHOUT the token — those fail with HTTP 401
"unauthorized: missing or invalid token" even while Burp is healthy. Fix per profile
(never bulk-edit): read the token from a known-good profile's config in Python,
`hermes -p <profile> config set mcp_servers.<name>.headers.Authorization "$TOKEN"`,
pin `mcp_servers.<name>.transport` to `sse`, backup the config.yaml first. Bare
`hermes` resolves to the sticky active profile — always pass `-p <name>` explicitly.
