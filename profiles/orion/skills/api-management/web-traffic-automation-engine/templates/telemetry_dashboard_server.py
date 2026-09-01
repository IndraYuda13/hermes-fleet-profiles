#!/usr/bin/env python3
"""
Multi-Account Telemetry Dashboard Server Template (Port 8280)
------------------------------------------------------------
Zero external dependencies HTTP dashboard with Apple-grade dark glass aesthetic,
withdrawal readiness hub, dual-view switcher, and multi-channel streaming logs.
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

STATE_FILE = Path("state/sessions.json")
LOG_FILE = Path("bot.log")


def get_telemetry_stats() -> dict:
    accounts_info = []
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            sessions = state.get("sessions", {})
            for acc_email, sess in sessions.items():
                cookie_str = sess.get("cookie_string", "")
                if cookie_str:
                    try:
                        opener = urllib.request.build_opener(urllib.request.ProxyHandler({"http": "http://127.0.0.1:31001", "https": "http://127.0.0.1:31001"}))
                        req = urllib.request.Request(
                            "https://luckywatch.pro/api/user/",
                            data=urllib.parse.urlencode({"method": "getCurrentUser"}).encode("utf-8"),
                            headers={"User-Agent": "Mozilla/5.0", "Cookie": cookie_str, "Content-Type": "application/x-www-form-urlencoded"},
                        )
                        res = json.loads(opener.open(req, timeout=5).read())
                        if res.get("status") == "ok" and "balance" in res.get("data", {}):
                            accounts_info.append({
                                "email": acc_email,
                                "email_redacted": acc_email[:2] + "***" + acc_email[acc_email.find("@") - 1:],
                                "balance": str(res["data"]["balance"]),
                                "clovers": int(res["data"].get("clover", 0)),
                                "status": "ACTIVE",
                            })
                    except Exception:
                        pass
        except Exception:
            pass

    total_bal = sum([float(a["balance"]) for a in accounts_info]) if accounts_info else 0.0
    total_clv = sum([int(a["clovers"]) for a in accounts_info]) if accounts_info else 0

    return {
        "summary": {
            "total_balance": f"{total_bal:.7f}",
            "total_clovers": total_clv,
            "total_accounts": len(accounts_info),
            "active_workers": len(accounts_info),
            "sleeping_workers": 0,
            "error_workers": 0,
        },
        "accounts": accounts_info,
        "logs": LOG_FILE.read_text().splitlines()[-60:] if LOG_FILE.exists() else [],
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
