#!/usr/bin/env python3
"""WCAG contrast gate for a candidate palette against every page background token.

Usage:
  python3 contrast_audit.py --fg '#5F6B78,#57626E' [--bg '#FFFFFF,#F4F6F5,#ECEFEE'] \\
      [--threshold 4.5] [--json]

Defaults to the three storefront surfaces white / canvas / surface-2. Always
reports the minimum ratio across backgrounds, because the tinted surface is the
binding constraint: a colour that clears on #FFFFFF routinely fails beside it.
Run it again with the page's CURRENT tokens (--fg from its CSS custom
properties) so the report shows which surface the existing value loses on.
"""
import argparse
import json
import sys


def _lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    h = hex_color.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--fg', required=True, help="candidates, comma separated")
    ap.add_argument('--bg', default='#FFFFFF,#F4F6F5,#ECEFEE')
    ap.add_argument('--threshold', type=float, default=4.5)
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()

    fgs = [s.strip() for s in args.fg.split(',') if s.strip()]
    bgs = [s.strip() for s in args.bg.split(',') if s.strip()]

    rows = []
    for fg in fgs:
        ratios = {bg: contrast(fg, bg) for bg in bgs}
        lo = min(ratios.values())
        rows.append({'fg': fg,
                     'ratios': {k: round(v, 2) for k, v in ratios.items()},
                     'min': round(lo, 2),
                     'pass': lo >= args.threshold})
    rows.sort(key=lambda r: r['min'], reverse=True)
    passing = [r['fg'] for r in rows if r['pass']]

    if args.json:
        print(json.dumps({'threshold': args.threshold, 'backgrounds': bgs,
                          'rows': rows, 'passing': passing,
                          'best_single': rows[0]['fg'] if rows else None}, indent=1))
        return 0

    print('threshold %.2f  backgrounds %s' % (args.threshold, ' '.join(bgs)))
    for r in rows:
        cells = ' '.join('%s=%.2f' % (k, v) for k, v in r['ratios'].items())
        print('%-9s %s min=%.2f %s' % (r['fg'], cells, r['min'], 'PASS' if r['pass'] else 'FAIL'))
    print()
    print('passing all backgrounds: %s' % (', '.join(passing) if passing else 'NONE'))
    if rows:
        print('best single value: %s (min %.2f)' % (rows[0]['fg'], rows[0]['min']))
    if len(passing) < len(rows):
        print('no single value clears every background -> consider a 2-value split, '
              'one per surface family, and say which background each half is for')
    return 0


if __name__ == '__main__':
    sys.exit(main())
