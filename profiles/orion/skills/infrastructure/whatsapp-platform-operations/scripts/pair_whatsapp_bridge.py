#!/usr/bin/env python3
"""
WhatsApp Bridge Pairing Supervisor for Hermes Agent.
Runs Baileys bridge in headless mode with --pair-only and --pair-json,
renders real-time QR code images via PIL/qrcode, and tracks connection status.
"""
import argparse
import json
import os
import subprocess
import sys
import time

try:
    import qrcode
except ImportError:
    print("Error: 'qrcode' package is required. Install via 'pip install qrcode'.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Supervise WhatsApp bridge pairing and emit QR image.")
    parser.add_argument("--session", required=True, help="Path to WhatsApp session directory")
    parser.add_argument("--port", type=int, default=3001, help="Port for bridge (default: 3001)")
    parser.add_argument("--qr-output", required=True, help="Destination path for generated QR PNG")
    parser.add_argument("--status-output", required=True, help="Destination path for status JSON")
    parser.add_argument("--timeout", type=int, default=300, help="Pairing timeout in seconds (default: 300)")
    args = parser.parse_args()

    os.makedirs(args.session, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.qr_output)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.status_output)), exist_ok=True)

    # Clean up 0-byte corrupt creds if leftover from aborted runs
    creds_path = os.path.join(args.session, "creds.json")
    if os.path.exists(creds_path) and os.path.getsize(creds_path) == 0:
        os.remove(creds_path)

    with open(args.status_output, "w", encoding="utf-8") as f:
        json.dump({"status": "starting", "time": time.time()}, f)

    cmd = [
        "node",
        "/usr/local/lib/hermes-agent/scripts/whatsapp-bridge/bridge.js",
        "--session", args.session,
        "--port", str(args.port),
        "--pair-only",
        "--pair-json"
    ]

    print(f"Starting bridge pairing supervisor: {' '.join(cmd)}", flush=True)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    start_time = time.time()
    connected_detected = False

    try:
        for line in iter(proc.stdout.readline, ''):
            line_clean = line.strip()
            if not line_clean:
                continue
            try:
                data = json.loads(line_clean)
                event = data.get("event")
                if event == "qr":
                    qr_str = data.get("qr")
                    img = qrcode.make(qr_str)
                    img.save(args.qr_output)
                    print(f"[QR] Updated at {time.strftime('%H:%M:%S')}", flush=True)
                    with open(args.status_output, "w", encoding="utf-8") as f:
                        json.dump({"status": "waiting_for_scan", "qr_time": time.time(), "qr_file": args.qr_output}, f)
                elif event == "connected":
                    user_info = data.get("user")
                    print(f"[SUCCESS] WhatsApp connected: {user_info}. Waiting for Baileys to flush credentials...", flush=True)
                    with open(args.status_output, "w", encoding="utf-8") as f:
                        json.dump({"status": "connected", "user": user_info, "time": time.time()}, f)
                    connected_detected = True
                    break
                elif event == "error":
                    print(f"[ERROR] Bridge error: {data}", flush=True)
                    with open(args.status_output, "w", encoding="utf-8") as f:
                        json.dump({"status": "error", "error": data, "time": time.time()}, f)
                    break
            except json.JSONDecodeError:
                if "Connected" in line_clean or "connected" in line_clean:
                    print(f"[BRIDGE] {line_clean}", flush=True)

            if time.time() - start_time > args.timeout:
                print("[TIMEOUT] Pairing timed out.", flush=True)
                with open(args.status_output, "w", encoding="utf-8") as f:
                    json.dump({"status": "timeout", "time": time.time()}, f)
                break

        # Mandatory flush wait: Baileys bridge exits after a 1.5s timeout on --pair-only.
        # Do NOT terminate proc prematurely or creds.json will be saved as an empty 0-byte file!
        if connected_detected:
            try:
                proc.wait(timeout=10)
                print("[INFO] Bridge process exited cleanly after saving creds.json.", flush=True)
            except subprocess.TimeoutExpired:
                print("[WARN] Bridge process timed out on exit, terminating.", flush=True)
                proc.terminate()

    finally:
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()


if __name__ == "__main__":
    main()
