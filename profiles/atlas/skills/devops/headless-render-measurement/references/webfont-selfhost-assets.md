# Webfont self-host asset acquisition (Google Fonts)

Depth for the "fetch the @font-face blocks so the frontend lane can self-host
them" half of a font-wiring job. The deliverable is RAW CSS plus a byte budget,
not a summary.

## The UA is what selects the format

`fonts.googleapis.com/css2` content-negotiates on `User-Agent`. A default curl UA
(or reading your own browser's CSS) returns `format('truetype')` with `.ttf` URLs;
the modern woff2 set requires a Chrome UA. Always pass one explicitly or the
budget you hand back is 3-5x too large.

```bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
for spec in "is:family=Instrument+Sans:ital,wght@0,400..700;1,400..700" \
            "iserif:family=Instrument+Serif:ital@0;1" \
            "jbm:family=JetBrains+Mono:wght@400;500"; do
  n=${spec%%:*}; q=${spec#*:}
  curl -sS -A "$UA" "https://fonts.googleapis.com/css2?$q&display=swap" -o "$n.css" \
       -w "$n http_status=%{http_code} bytes=%{size_download}\n"
done
```

Record the `http_status` and byte size per stylesheet — they are part of the
evidence, and a 200 with a suspiciously small body is a truncated query string.

## Axis syntax, and what it does to the file count

| Axis form | Effect on the returned stylesheet |
|---|---|
| `wght@400;500` | One `@font-face` per weight per subset — static files |
| `wght@400..700` | ONE `@font-face` per subset, `font-weight: 400 700`, variable file |
| `ital,wght@0,400..700;1,400..700` | 2 styles x 1 variable file per subset = 4 blocks |
| `ital@0;1` | 2 styles, static, 4 blocks (2 styles x latin + latin-ext) |

A variable family (Instrument Sans) collapses the whole weight range into a single
woff2 per (style, subset). A static family requested at two weights (JetBrains
Mono) emits two blocks per subset that can still point at the SAME file URL — so
dedupe the URLs before downloading or you fetch the same bytes twice and double
the reported budget.

## Subsets

Google emits one trailing block per subset (`cyrillic-ext`, `cyrillic`, `greek`,
`vietnamese`, `latin-ext`, `latin`, plus more for larger families). Subsets come in
the same order every call but their COUNT varies by family, so never index blocks
positionally. Split on the `/* subset */` comment that precedes each block.

For a Latin-Indonesian surface, only `latin` and `latin-ext` are load-bearing; the
rest are dead bytes in a self-hosted deploy. Report latin and latin-ext separately
and note that the other subsets were dropped deliberately, listing what was dropped.

## Extracting and printing the CSS

Returns the FULL raw CSS per family, plus, per family, the woff2 filename and
`unicode-range` of the latin and latin-ext subsets only. Both shapes are useful:
the one-line-per-`@font-face` form keeps a wide unicode-range readable and is what
FRAME pastes.

```python
import re
from pathlib import Path

css = Path('is.css').read_text()
# split() with a capturing group puts the subset label at odd indices, its block at even
blocks = re.split(r'/\*\s*([a-z-]+)\s*\*/', css)
for i in range(1, len(blocks), 2):
    subset, body = blocks[i], blocks[i + 1]
    if subset not in ('latin', 'latin-ext'):
        continue
    d = dict(re.findall(r'^\s*([a-z-]+):\s*(.+?);\s*$', body, re.M))
    print("@font-face{font-family:%s;font-style:%s;font-weight:%s;font-stretch:%s;"
          "font-display:%s;src:%s;unicode-range:%s;} /* %s */"
          % (d['font-family'], d['font-style'], d['font-weight'], d.get('font-stretch', ''),
             d['font-display'], d['src'], d['unicode-range'], subset))
```

Parse each block's declarations into a dict and re-emit them from the dict rather
than regex-copying the block wholesale: that is what guarantees `font-stretch` and
`font-display` survive, and what makes the print order stable across families.
Print the block COUNT per family as a cross-check against the axis table above — a
count that does not match the expected (styles x subsets) means a truncated response.

Declarations are copied verbatim out of the response — do not rewrite `font-family`
quoting, reorder properties, or normalise the URL. The requester is diffing the
CSS against what they will paste.

## Byte budget

`curl -sSI` (HEAD) each distinct source URL for the latin subset and print HTTP
status plus `content-length`. Accept the same result on `content-length` and
`size_download`; if they disagree the transfer was chunked or truncated.

```bash
curl -sSI -A "$UA" "$u" | grep -i '^HTTP/\|^content-length\|^content-type' | tr -d '\r'
```

Then actually download each file to the scratch dir and report `du -sh` per file
plus the exact byte sum. `du` is block-granular (a 30092-byte file reports `32K`),
so print BOTH: `du -sh` per file AND `du -cb ... | tail -1` for the real total, and
label which is which, or the requester budgets 20% over.

Verify the magic bytes before calling anything a font: woff2 is `774f4632`
(`wOF2`). A 200 response with an HTML body is a redirect or a quota page.

## Naming what you downloaded locally

Name saved files `<Family>-<style>-<subset>.woff2` from the parsed `@font-face`
values, not from the hashed URL. The URL basename is an opaque hash and cannot be
matched back to a subset or style in the budget table.

## Report shape

Per family: the full one-line-per-`@font-face` CSS, the @font-face block count, then
the latin / latin-ext woff2 filenames and unicode-range. Then the HEAD table
(status + content-length per distinct URL), then `du -sh` per downloaded file and
the byte totals. Close with the two budget lines that matter: latin-only total, and
latin+latin-ext total. Add a note when a static family's two weights dedupe to one
file, since that halves the pair FRAME has to wire.
