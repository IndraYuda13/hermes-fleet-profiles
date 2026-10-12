#!/usr/bin/env python3
"""Bounce ONE profile's adapters on a live multiplexed gateway — no gateway restart.

Usage:
    /usr/local/lib/hermes-agent/venv/bin/python multiplex_bounce_profile.py <profile> [gateway_home]

<gateway_home> defaults to $HERMES_GATEWAY_HOME or /root/.hermes (the DEFAULT home whose
gateway serves the profiles). Prints the served set + gateway pid before/after; the pid
must be unchanged. Exit 0 = profile served again, 1 = failure, 2 = usage.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.environ.get("HERMES_SRC", "/usr/local/lib/hermes-agent"))

from gateway.control_socket import (  # noqa: E402
    identify_gateway,
    request_serve_profile_hot,
    request_unserve_profile,
)


def served(home):
    """(served_profiles, pid) or (None, None) when no gateway answers."""
    ident = identify_gateway(home)
    if not isinstance(ident, dict):
        return None, None
    return ident.get("served_profiles") or [], ident.get("pid")


def wait_for(home, profile, want_present, tries=25, delay=2.0):
    """Poll the served set until (profile in set) == want_present; return last seen set."""
    current = None
    for _ in range(tries):
        time.sleep(delay)
        current, _pid = served(home)
        if current is None:
            continue
        if (profile in current) == want_present:
            return current
    return current


def main(argv):
    if not 1 <= len(argv) <= 2:
        print(__doc__)
        return 2
    profile = argv[0]
    home = Path(argv[1] if len(argv) == 2 else os.environ.get("HERMES_GATEWAY_HOME", "/root/.hermes"))

    before, pid0 = served(home)
    if before is None:
        print(f"no gateway answers on {home}")
        return 1
    print("BEFORE:", before, "| pid:", pid0)
    if profile not in before:
        print(f"'{profile}' is not served by this gateway")
        return 1

    print("unserve-profile:", request_unserve_profile(home, profile))
    current = wait_for(home, profile, want_present=False)
    if current is None or profile in current:
        print("profile never left the served set; not issuing serve")
        return 1
    print("AFTER-UNSERVE:", current)

    print("serve-profile:", request_serve_profile_hot(home, profile))
    current = wait_for(home, profile, want_present=True)
    after, pid1 = served(home)
    print("AFTER-SERVE:", after, "| pid:", pid1, "| pid unchanged:", pid0 == pid1)
    if after is None or profile not in after:
        return 1
    print(f"OK — adapters of '{profile}' rebuilt from current config/.env")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
