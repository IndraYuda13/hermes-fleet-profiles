#!/usr/bin/env python3
"""Enumerate a paginated listing + its detail pages and verify anonymous access.

Purpose: for Laravel list pages that paginate via query params (e.g. ?page_x=1..N),
collect every detail link, dedupe, then confirm which detail URLs are reachable with
NO session/cookie (an authz leak). Stdlib only.

Example:
  python3 enumerate_paginated_exposure.py \
      --base https://target.example \
      --list-path /kesiswaan \
      --page-params page_pelanggaran,page_konseling,page_terlambat \
      --max-pages 20 --json out.json

  # then eyeball: every detail URL that reports verified=200 is an exposure
"""
import argparse, json, re, sys, time, urllib.request, urllib.error

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def fetch(url, ua=UA, method="GET"):
    req = urllib.request.Request(url, method=method, headers={
        "User-Agent": ua, "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
    })
    # No Cookie header is ever set -> every request is anonymous.
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read() if method == "GET" else b""
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return 0, ("ERR %s" % e).encode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="scheme://host (no trailing slash)")
    ap.add_argument("--list-path", required=True, help="/kesiswaan")
    ap.add_argument("--page-params", default="page",
                    help="comma-separated page param names, e.g. page_pelanggaran,page_konseling")
    ap.add_argument("--max-pages", type=int, default=20)
    ap.add_argument("--detail-regex", default=r'href="([^"]+)"',
                    help="regex capturing candidate detail URLs from the listing")
    ap.add_argument("--include", default=None,
                    help="only keep detail URLs containing this substring (default: base)")
    ap.add_argument("--delay", type=float, default=0.15)
    ap.add_argument("--no-verify", action="store_true",
                    help="skip anonymous re-request of each detail URL")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    base = args.base.rstrip("/")
    params = [p.strip() for p in args.page_params.split(",") if p.strip()]
    include = args.include or base
    detail_re = re.compile(args.detail_regex)

    links = {}
    for page in range(1, args.max_pages + 1):
        q = "&".join("%s=%d" % (p, page) for p in params)
        url = "%s%s?%s" % (base, args.list_path, q)
        status, body = fetch(url)
        html = body.decode("utf-8", "replace")
        n = 0
        for m in detail_re.finditer(html):
            href = m.group(1)
            if href.startswith("/"):
                href = base + href
            if href.startswith(base) and include in href and "?" not in href:
                if href not in links:
                    links[href] = page
                    n += 1
        print("[page %d] status=%s new_links=%d total=%d" % (page, status, n, len(links)),
              file=sys.stderr)
        if n == 0 and page > 1:
            break  # pagination exhausted
        time.sleep(args.delay)

    result = {"listing": base + args.list_path, "unique_detail_links": len(links), "details": {}}
    verified_200 = 0
    for url in links:
        if args.no_verify:
            result["details"][url] = {"verified": None}
            continue
        status, body = fetch(url)
        result["details"][url] = {"verified": status, "size": len(body)}
        if status == 200:
            verified_200 += 1
        time.sleep(args.delay)

    result["reachable_without_auth"] = verified_200
    print("unique detail links: %d" % len(links))
    if not args.no_verify:
        print("reachable WITHOUT auth (200): %d" % verified_200)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, ensure_ascii=False)
        print("wrote %s" % args.json)


if __name__ == "__main__":
    main()
