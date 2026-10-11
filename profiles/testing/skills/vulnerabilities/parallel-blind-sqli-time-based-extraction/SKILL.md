---
name: parallel-blind-sqli-time-based-extraction
description: Use when blind time-based SQLi extraction is slow.
---

# Parallel blind (time-based) SQLi extraction

## When to use
Blind SQLi where the ONLY oracle is a timing side-channel (`sleep()` on a boolean
condition), so each character costs ~log2(charset) requests. Serial extraction of table
names / columns / values is painfully slow. This skill makes it tens of times faster and,
critically, keeps it ACCURATE.

## Operator ground rules (read-only by default)
On a LIVE authorized target, prove impact READ-ONLY unless the user explicitly clears state changes.
- Ground truth with boolean probes only: `LENGTH(x)>=1`, `(subquery)='value'`, `... LIMIT 1`. These are
  safe and sufficient to CONFIRM extraction and sample data.
- Do NOT run `CALL <proc>()`, `UPDATE`/`DELETE`/`INSERT`/`DROP`, `SELECT ... INTO OUTFILE/DUMPFILE`, or any
  stored procedure "to see what it does" — a stored procedure can mutate data or fire application logic.
  A flagged destructive request is still a decision for the user, not the agent.
- When a higher-impact path exists (a `DEFINER` stored procedure, an OS-command primitive), ENUMERATE it
  read-only (metadata/parameters) and DOCUMENT the escalation path; wait for an explicit go-ahead before
  executing anything that changes state. Reporting the reachable ceiling beats crossing it.

## Step 1 — Confirm the timing oracle is real
Probe whether the server actually executes sleep:
- TRUE  payload: `1' AND CASE WHEN (1=1) THEN sleep(0.8) ELSE 0 END-- -`  -> slow
- FALSE payload: `1' AND CASE WHEN (1=2) THEN sleep(0.8) ELSE 0 END-- -`  -> fast
Measure wall time. If TRUE ~0.8s and FALSE ~0.2s, oracle is valid. If both are fast
(server silently ignores the injected sleep), STOP — timing is not usable, find another channel.

## Step 2 — Test whether the server handles requests in PARALLEL
Fire N concurrent `sleep(1)` requests and compare wall time with a single one:
- 3x sleep(1) finishing in ~1.2s (not ~3s) => server processes concurrently => parallelize.
- If it serializes (wall ~3s), parallel threading will NOT help.
A remote MySQL behind a web app is usually parallel, and `sleep()` runs per-connection, so the
thread pool gives a near-linear speedup.

## Step 3 — Structure the parallel extraction
- Binary-search each character over an ASCII range (`ASCII(SUBSTRING(x,pos,1))>mid`), and
  the length with a `>mid` oracle. Binary search beats linear scanning by ~8x.
- Two levels of concurrency: across NAMES/rows (WORKERS), and across CHARACTER POSITIONS
  within one name (INNER).
- Cap total in-flight requests with a `threading.Semaphore` (e.g. 12-24) so parallel positions
  don't multiply into hundreds of sockets that trip the WAF or exhaust the app pool.
- Retry a request on connection reset (WAF) with a short backoff inside the oracle.
- Write each finished name to its own file `par/<idx>.txt` and append to the checkpoint, so a
  crash loses at most one name.

## Step 4 — HARDEN the oracle (the part that bites you)
Blind timing oracles fail in TWO different ways, and the fix is OPPOSITE for each. Diagnose
which one you have before choosing a rule:

- **False-POSITIVE noise** (a FALSE query reads slow): usually a warmed-up load / jitter, and a
  tight threshold too close to the baseline. Fix: longer sleep + higher threshold.
- **False-NEGATIVE noise** (a TRUE query reads FAST): the DB/app connection pool saturates under
  your own load, the app is restarted, or a cache/proxy returns a fast response, so `sleep()` never
  runs. This is the killer: it silently corrupts dumps (reads every value as empty/short).

Because oracles are asymmetric — **"slow" is reliable evidence, "fast" can be a false negative** —
use an ASYMMETRIC rule, NOT "N consecutive samples must agree":
- one sample `>= HI`  => True   (treat slow as proof)
- two samples `<= LO` => False  (don't believe a single fast reading)
- in the `LO..HI` band   => retry
If you require two CONSECUTIVE agreeing samples, an alternating `[slow, fast, slow]` TRUE stream
never agrees and you wrongly record FALSE for every bit. (This exact mistake produced 250/263
"empty" values in practice — always re-verify a run that reports mostly empty.)

Load is what creates false negatives, so DON'T crank concurrency: run MODERATE concurrency
(measured optimum was ~6 workers x 4 inner; 16 workers degraded throughput). Tune it: raise the
sleep so a genuine TRUE stays far above the false-negative ceiling (e.g. TRUE 1.2s vs FALSE 0.2s),
then pick the largest concurrency that still yields clean TRUE==slow samples on a probe loop.

Also:
- ALWAYS re-verify: after the dump, re-check each value with an equality oracle
  `(subquery)='value'`; re-dump mismatches. A single misread character still yields a value that
  LOOKS valid (a 32-hex hash with one wrong nibble is still 32 hex) — shape-correct is NOT correct;
  the equality oracle is the only proof. Treat a mostly-empty result as a red flag, not success.
- A verify-and-FIX pass is itself dangerous: if the oracle is noisy (server load, or OTHER traffic you
  generate — crawling/OCR/LFI probes hitting the same host), it can OVERWRITE good values with garbage
  (Unicode surrogate chars like `EFBFBD`, all-`FF` tails, spurious spaces). Run re-verify QUIET and
  single-threaded, sanity-check a known-good row before trusting any 'fix', and never let a noisy batch
  auto-write back — the 'fix' becomes the corruption.
- Sanity-check the oracle live (known-value test) before a big batch, and count the fraction of
  fast-vs-slow on a TRUE payload loop (false negatives should be ~0).

## Step 5 — Hash/binary values: extract HEX with an alphabet-restricted search
Not every value is printable text. Passwords, tokens, and password hashes are often stored as
binary (16-byte MD5, 20-byte SHA1, ...), so reading the raw column returns non-ASCII bytes that
surface as `~`/space garbage. Instead:
- Extract `HEX(col)` (or `TO_BASE64`) so every character is printable, then decode locally.
- Binary-search each character over ONLY the alphabet the encoding can produce, not the full
  32..126 range: hex needs 16 symbols (4 requests/char, vs 7 for full ASCII), base64 needs 64.
  Compare `ASCII(SUBSTRING(x,pos,1))` against the sorted alphabet bytes.
- Length-guard the result: a 16-byte value must yield exactly 32 hex chars. A wrong length means
  a noisy read — re-run that row, do not store it.

## Pitfalls
- Off-by-one in the length binary search: with `LENGTH(x)>mid`, the max m that is TRUE equals
  L-1, so the answer is `lo+1`. Getting this wrong silently truncates the LAST char of every name
  (looks plausible, so validate against a known row first).
- Do not trust short sanity checks: run a full known-value test (dump an index whose correct
  answer you already have) end-to-end before launching the whole batch.
- Treat WAF filtering as a TOKEN-CLASS allowlist, not a few blocked strings. Signature WAFs
  often reset the connection on whole families — aggregation/formatting (`count()`, `concat()`,
  `group by`, `floor(rand())`) as well as `union`/`or`/`from`/`information_schema`. Build an
  allowlist of tokens proven to pass (`select`, versioned comment `/*!50000*/`, scalar subqueries,
  `length()`, `substring()`, `ascii()`, `hex()`, `case when`) and assemble payloads from those.
  A connection reset is a BLOCK signal, not a transient error: do not retry the token, find a
  passing substitute (`length()`+`substring()` instead of `count()`/`concat()`).
- Before committing to blind timing, check the SAME endpoint for a faster channel. A syntax error
  that echoes the internal query proves injection but is only a PROOF channel — if the response
  never contains subquery DATA it cannot extract values, so do not rebuild the pipeline around it.
  Keep blind time-based as the extractor; only switch channels (UNION / error-based) after you have
  actually seen reflected DATA, not just the query text.

## WAF-bypass note (MySQL)
When an inline WAF resets on `FROM` / `information_schema` / `union`, MySQL version-comment
obfuscation still works: `(select/*!50000 table_name*/from information_schema.tables ...)`. The
comment sits between `select` and the column and hides the `from` from naive filters.
