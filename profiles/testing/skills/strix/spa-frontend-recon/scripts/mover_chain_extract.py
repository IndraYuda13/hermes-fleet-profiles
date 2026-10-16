#!/usr/bin/env python3
"""
Mover-style signed-chain extractor (embed -> player -> API -> wasm decrypt -> token -> media).

Verified end-to-end for film + TV against a live aggregator's chain family:

  [1] GET https://<mover-host>/embed/{tmdb}            (+ /{s}-{e} for TV)
  [2] GET https://<mover-host>/vs_src.php?type=..&id=.. -> {"src":"<signed embed url>"}
  [3] GET the signed embed page                          -> "playerUrl": "..."
  [4] GET player page                                    -> window.CONFIG {apiToken, api|streamBase}
  [5] GET {api|streamBase}&stream_urls&api_token=<jwt>   (token as QUERY param, not Bearer)
        -> data.stream_urls (encrypted) + vs.wasm_url
  [6] tiny wasm decrypt via node (alloc/decrypt; output at ptr+12)
  [7] GET https://<stream-origin>/generate.php           -> fresh one-time JWT
  [8] GET {master.m3u8}?token={jwt}                      -> #EXTM3U
  [9] GET {origin}{variant}                              -> sub-playlist (token: test per level)
  [10] GET {origin}{segment}                             -> MPEG-TS/fMP4, verify with ffprobe

Upstream hostnames rotate: if a hop 404s, refetch the current embed page and update the
hosts. ALL steps must run from ONE sticky IP (residential proxy) because the final tokens
are IP-CIDR bound; see web-surface-triage -> references/datacenter-blocked-targets.md section 5.

Usage:
    python3 mover_chain_extract.py 27205 movie
    python3 mover_chain_extract.py 1396 tv 1 1
Env:
    VENUS_PROXY  proxy URL (default http://127.0.0.1:31004, a local residential pool node)

NOTE for wiring this into a long-lived service: this script shells out to `node` for the
wasm decrypt (fast to iterate, but adds a binary dependency to the service environment).
For a service, run the same tiny wasm from Python via `wasmtime`/`wasmer` if available
(alloc/decrypt/memory; output at ptr+12) and install it into the SERVICE venv. See
references/provider-replication-engineering.md section 3.
"""
import json, os, re, subprocess, sys

PROXY = os.environ.get("VENUS_PROXY", "http://127.0.0.1:31004")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
MOVER_HOST = "https://ythd.org"
PLAYER_HOST = "https://stellarconductornexus.com"


def curl(url, referer=None, save=None, timeout=60):
    cmd = ["curl", "-s", "-m", str(timeout)]
    if PROXY:
        cmd += ["-x", PROXY]
    cmd += ["-A", UA]
    if referer:
        cmd += ["-H", f"Referer: {referer}"]
    if save:
        cmd += ["-o", save]
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True).stdout


def wasm_decrypt(enc_b64, wasm_url):
    curl(wasm_url, save="/tmp/venus_wasm.bin")
    open("/tmp/venus_enc.txt", "w").write(enc_b64)
    js = """const fs=require('fs');
(async()=>{
  const enc=fs.readFileSync('/tmp/venus_enc.txt','utf8').trim();
  const buf=fs.readFileSync('/tmp/venus_wasm.bin');
  const {instance}=await WebAssembly.instantiate(buf,{});
  const ex=instance.exports;
  const bin=Buffer.from(enc,'base64');
  const ptr=ex.alloc(bin.length);
  new Uint8Array(ex.memory.buffer,ptr,bin.length).set(bin);
  const n=ex.decrypt(ptr,bin.length);
  console.log(new TextDecoder().decode(new Uint8Array(ex.memory.buffer,ptr+12,n)));
})();"""
    open("/tmp/venus_dec.js", "w").write(js)
    out = subprocess.run(["node", "/tmp/venus_dec.js"], capture_output=True, text=True).stdout
    return [u for u in out.split("\n") if u.startswith("http")]


def main(tmdb, mtype="movie", season=None, episode=None):
    # [1] mover embed
    embed_path = f"{tmdb}/{season}-{episode}" if mtype == "tv" else str(tmdb)
    r1 = curl(f"{MOVER_HOST}/embed/{embed_path}", referer="https://vidup.to/")
    assert b"vs_src.php" in r1 or b"player_iframe" in r1, f"[1] embed failed: {r1[:120]}"
    print(f"[1] mover embed OK ({len(r1)}B)")

    # [2] signed src
    q = f"type={mtype}&id={tmdb}" + (f"&season={season}&episode={episode}" if mtype == "tv" else "")
    r2 = curl(f"{MOVER_HOST}/vs_src.php?{q}", referer=f"{MOVER_HOST}/embed/{embed_path}")
    m = re.search(rb'"src":"(https://[^"]+)"', r2)
    assert m, f"[2] vs_src failed: {r2[:150]}"
    src = m.group(1).decode()
    print(f"[2] signed embed: {src[:90]}...")

    # [3] embed -> playerUrl
    r3 = curl(src, referer=MOVER_HOST + "/")
    m2 = re.search(rb'"playerUrl":"([^"]+)"', r3)
    assert m2, f"[3] no playerUrl: {r3[:200]}"
    player = PLAYER_HOST + m2.group(1).decode().replace("\\u0026", "&")
    print(f"[3] player page: {player[:100]}...")

    # [4] CONFIG
    r4 = curl(player, referer=PLAYER_HOST + "/")
    mt = re.search(rb'"apiToken":"([^"]+)"', r4)
    ma = re.search(rb'"api":"([^"]+)"', r4)
    mb = re.search(rb'"streamBase":"([^"]+)"', r4)
    api = (ma.group(1) if ma else mb.group(1)).decode().replace("\\u0026", "&")
    tok = mt.group(1).decode()
    print(f"[4] apiToken len={len(tok)} | api={api[:90]}")

    # [5] stream_urls (token as QUERY param exactly as the client does)
    r5 = curl(api + ("&" if "?" in api else "?") + "stream_urls&api_token=" + tok,
              referer=PLAYER_HOST + "/")
    j = json.loads(r5)
    d = j.get("data") or {}
    su = d.get("stream_urls")
    if isinstance(su, list):
        urls = su
        print(f"[5] stream_urls PLAIN: {len(urls)}")
    else:
        urls = wasm_decrypt(su, (j.get("vs") or {})["wasm_url"])
        print(f"[5-6] stream_urls DECRYPTED: {len(urls)} master URLs")

    for u in urls[:3]:
        print("      ", u[:105])

    # [7-10] follow the first master
    u0 = urls[0]
    origin = re.match(r"https://[^/]+", u0).group(0)
    tk = curl(origin + "/generate.php", referer=PLAYER_HOST + "/").decode().strip()
    print(f"[7] /generate.php token len={len(tk)}")

    r8 = curl(u0 + "?token=" + tk)
    assert r8.startswith(b"#EXTM3U"), f"[8] master failed: {r8[:120]}"
    print(f"[8] master.m3u8 OK ({len(r8)}B)")

    v = [l for l in r8.decode().split("\n") if l and not l.startswith("#")][0]
    r9 = curl(origin + v)
    segs = [l for l in r9.decode().split("\n") if l and not l.startswith("#")]
    print(f"[9] sub-playlist OK ({len(r9)}B, {len(segs)} segments)")

    curl(origin + segs[0], save="/tmp/venus_seg.ts", timeout=120)
    sz = os.path.getsize("/tmp/venus_seg.ts")
    print(f"[10] segment downloaded: {sz}B -> /tmp/venus_seg.ts")
    ff = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "/tmp/venus_seg.ts"],
                        capture_output=True, text=True).stdout
    for line in ff.split("\n"):
        if any(k in line for k in ("codec_name", "width", "height", "codec_type")):
            print("      ", line.strip())


if __name__ == "__main__":
    tmdb = sys.argv[1]
    mt = sys.argv[2] if len(sys.argv) > 2 else "movie"
    s = sys.argv[3] if len(sys.argv) > 3 else None
    e = sys.argv[4] if len(sys.argv) > 4 else None
    main(tmdb, mt, s, e)
