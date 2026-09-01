#!/usr/bin/env python3
"""
Multi-Account Worker Daemon Template (Pure Python HTTP)
------------------------------------------------------
Concurrent multi-account task runner with isolated proxy per account,
session cookie caching, exponential login retries, and dynamic limit rollover.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("MultiAccountWorker")


class AccountWorker(threading.Thread):
    def __init__(self, account_config: Dict[str, Any], global_config: Dict[str, Any], daemon_mode: bool = True):
        super().__init__(name=account_config.get("email", "Worker").split("@")[0])
        self.account = account_config
        self.email = account_config["email"]
        self.password = account_config["password"]
        self.global_config = global_config
        self.daemon_mode = daemon_mode
        self.stop_event = threading.Event()

        # Dedicated proxy isolation (1 Account : 1 Proxy)
        self.proxy_url = self.account.get("proxy") or self.global_config.get("proxy", {}).get("url")
        self.base_url = self.global_config.get("app", {}).get("base_url", "").rstrip("/")
        self.api_url = f"{self.base_url}/api"
        self.cookie_string = ""
        self.state_file = Path("state/sessions.json")
        self._opener = self._build_opener()

    def _build_opener(self) -> urllib.request.OpenerDirector:
        handlers: List[urllib.request.BaseHandler] = []
        if self.proxy_url:
            handlers.append(urllib.request.ProxyHandler({"http": self.proxy_url, "https": self.proxy_url}))
        return urllib.request.build_opener(*handlers)

    def load_saved_session(self) -> bool:
        """Hydrate session cookie string from local state file."""
        if not self.state_file.exists():
            return False
        try:
            state = json.loads(self.state_file.read_text())
            session = state.get("sessions", {}).get(self.email)
            if session and session.get("cookie_string"):
                self.cookie_string = session["cookie_string"]
                return True
        except Exception:
            pass
        return False

    def seconds_until_next_hour(self) -> int:
        """Compute precise seconds until next hour (:00:15) with sub-minute accuracy."""
        now = datetime.now()
        next_hour = (now + timedelta(hours=1)).replace(minute=0, second=15, microsecond=0)
        return max(5, int((next_hour - now).total_seconds()))

    def seconds_until_next_day(self) -> int:
        """Compute precise seconds until next UTC day (00:00:30) with buffer."""
        now_utc = datetime.now(timezone.utc)
        next_day = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=30, microsecond=0)
        return max(30, int((next_day - now_utc).total_seconds()))

    def adaptive_sleep(self, total_seconds: int, reason: str = "limit"):
        """Interruptible 1-second step sleep loop."""
        start = time.time()
        while not self.stop_event.is_set():
            if time.time() - start >= total_seconds:
                break
            time.sleep(1)

    def run(self):
        logger.info(f"Worker started for {self.email} via proxy {self.proxy_url} (Dynamic 24/7 Engine)")
        cycle = 0
        while not self.stop_event.is_set():
            cycle += 1
            # Dynamic task execution loop without arbitrary batch caps
            # Handles limitInHour with seconds_until_next_hour() and queue empty with 15s fast backoff
            time.sleep(2)
            if not self.daemon_mode:
                break


class MultiBotManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.workers: List[AccountWorker] = []

    def start_all(self, daemon_mode: bool = True):
        accounts = [a for a in self.config.get("accounts", []) if a.get("active", True)]
        logger.info(f"Starting MultiBotManager with {len(accounts)} worker(s)...")
        for acc in accounts:
            w = AccountWorker(account_config=acc, global_config=self.config, daemon_mode=daemon_mode)
            self.workers.append(w)
            w.start()
        for w in self.workers:
            w.join()
