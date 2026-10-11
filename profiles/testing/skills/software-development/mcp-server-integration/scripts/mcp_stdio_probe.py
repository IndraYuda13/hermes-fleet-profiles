#!/usr/bin/env python3
"""Probe an MCP stdio server before registering it.

Usage:
    mcp_stdio_probe.py <command> [args...]
    mcp_stdio_probe.py /abs/path/to/cli mcp
    mcp_stdio_probe.py npx -y some-mcp-server

Performs the real JSON-RPC handshake (initialize -> notifications/initialized ->
tools/list) over stdin/stdout and prints a one-shot JSON summary. Exit code 0
means the server answered initialize; 1 means it did not.
"""
import json
import subprocess
import sys


def probe(cmd: list[str]) -> dict:
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    def send(obj: dict) -> None:
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()

    def read() -> str:
        # Skip blank/notification lines until a JSON object arrives.
        while True:
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError("server closed stdout before replying")
            line = line.strip()
            if line.startswith("{"):
                return line

    try:
        send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "mcp_stdio_probe", "version": "1"},
            },
        })
        init = json.loads(read())
        if "error" in init:
            raise RuntimeError(f"initialize error: {init['error']}")

        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = json.loads(read())
        names = [t.get("name") for t in tools.get("result", {}).get("tools", [])]

        result = init.get("result", {})
        return {
            "ok": True,
            "server": result.get("serverInfo", {}),
            "protocol_version": result.get("protocolVersion"),
            "tool_count": len(names),
            "tools_sample": names[:10],
        }
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> int:
    cmd = sys.argv[1:]
    if not cmd:
        print(__doc__)
        return 2
    try:
        out = probe(cmd)
    except Exception as exc:  # noqa: BLE001 - report any failure as a probe failure
        print(json.dumps({"ok": False, "command": cmd, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
