#!/usr/bin/env python3
"""Measure streaming decode throughput (tok/s) of an OpenAI-compatible endpoint.

Reads token counts from the real `usage` block, never estimates from characters.
Reports per content shape (dense vs prose) and reasoning on vs off, because those
differ by ~2.5x and a single number is meaningless without them.

Usage:
  python3 bench_stream_tok_s.py --base-url http://127.0.0.1:20128/v1 --model ds
  python3 bench_stream_tok_s.py --base-url ... --model ds --effort none --runs 3
  python3 bench_stream_tok_s.py --base-url ... --model ds --concurrency 4

Notes:
  * stream_options.include_usage is mandatory or there is no usage block to read.
  * Non-streaming POSTs get the router's retry middleware; streaming ones do not, so
    this script retries itself with backoff on 502/503/504.
"""
from __future__ import annotations

import argparse
import json
import statistics
import threading
import time
import urllib.error
import urllib.request

NUM_ZN = "Output the integers from 1 to 1200 in order, comma separated on one line, no other text."
PROSE = (
    "Write a ~1300 word detailed technical essay on DNS resolution, recursive vs "
    "authoritative servers, and caching TTL behaviour. Do not stop early."
)
SHAPES = {"dense": NUM_ZN, "prose": PROSE}


def stream_once(base_url, model, prompt, max_tokens, effort, api_key, tries=6):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    if effort:
        body["reasoning_effort"] = effort
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + (api_key or "x")}

    for attempt in range(tries):
        req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=data, headers=headers)
        t0 = time.time()
        first = last = None
        usage = None
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                for raw in resp:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        obj = json.loads(payload)
                    except ValueError:
                        continue
                    if obj.get("usage"):
                        usage = obj["usage"]
                    choices = obj.get("choices") or []
                    if choices:
                        delta = choices[0].get("delta") or {}
                        if delta.get("content") or delta.get("reasoning_content") or delta.get("reasoning"):
                            now = time.time()
                            if first is None:
                                first = now
                            last = now
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(min(30, 4 * (attempt + 1)))
                continue
            return {"error": "HTTP %s" % e.code}
        except Exception as e:  # network hiccup
            time.sleep(min(30, 4 * (attempt + 1)))
            if attempt == tries - 1:
                return {"error": str(e)}
            continue

        if not usage or first is None or last is None:
            return {"error": "no usage/tokens in stream"}
        ct = usage.get("completion_tokens", 0)
        details = usage.get("completion_tokens_details") or {}
        gen = last - first
        return {
            "completion_tokens": ct,
            "reasoning_tokens": details.get("reasoning_tokens"),
            "ttft": round(first - t0, 3),
            "gen_seconds": round(gen, 3),
            "decode_tok_s": round(ct / gen, 1) if gen > 0 and ct else None,
            "wall_tok_s": round(ct / (last - t0), 1) if ct else None,
        }
    return {"error": "retries exhausted"}


def run_serial(base_url, model, prompt, max_tokens, effort, api_key, runs):
    out = [stream_once(base_url, model, prompt, max_tokens, effort, api_key) for _ in range(runs)]
    ok = [r["decode_tok_s"] for r in out if r.get("decode_tok_s")]
    summary = None
    if ok:
        summary = {
            "median_decode_tok_s": statistics.median(ok),
            "min": min(ok),
            "max": max(ok),
            "median_ttft": statistics.median([r["ttft"] for r in out if r.get("ttft") is not None]),
        }
    return out, summary


def run_concurrent(base_url, model, prompt, max_tokens, effort, api_key, n):
    results = [None] * n

    def worker(i):
        results[i] = stream_once(base_url, model, prompt, max_tokens, effort, api_key)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    t0 = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall = time.time() - t0
    per_stream = [r["decode_tok_s"] for r in results if r and r.get("decode_tok_s")]
    total = sum(r["completion_tokens"] for r in results if r and r.get("completion_tokens"))
    return results, {
        "per_stream": per_stream,
        "aggregate_wall_tok_s": round(total / wall, 1) if wall else None,
        "scaling": "flat per-stream = upstream not throughput-sharing",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", required=True, help="e.g. http://127.0.0.1:20128/v1")
    ap.add_argument("--model", required=True)
    ap.add_argument("--api-key", default="")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--max-tokens", type=int, default=1400)
    ap.add_argument("--effort", default=None, help="reasoning_effort (e.g. none, high, max); omit for the endpoint default")
    ap.add_argument("--concurrency", type=int, default=0, help="if >1, run N parallel streams instead of the serial matrix")
    args = ap.parse_args()

    if args.concurrency > 1:
        rows, summary = run_concurrent(
            args.base_url, args.model, SHAPES["dense"], args.max_tokens, args.effort, args.api_key, args.concurrency
        )
        print(json.dumps({"concurrency": args.concurrency, "per_run": rows, "summary": summary}, indent=2))
        return

    report = {}
    for shape, prompt in SHAPES.items():
        rows, summary = run_serial(
            args.base_url, args.model, prompt, args.max_tokens, args.effort, args.api_key, args.runs
        )
        report[shape] = {"runs": rows, "summary": summary}
        if summary:
            print("%-6s effort=%-8s -> %.1f tok/s median (ttft %.2fs)" % (
                shape, args.effort or "default", summary["median_decode_tok_s"], summary["median_ttft"]))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
