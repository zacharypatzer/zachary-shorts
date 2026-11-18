#!/usr/bin/env python3
"""Merge windowed Parakeet output into one word list with absolute times."""
import json, re, sys

log, out = sys.argv[1], sys.argv[2]
HOP, WIN, EDGE = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
txt = open(log).read()
# results are printed as:  <path>\n{json}
items = re.findall(r'(\S+?w_(\d+)\.wav)\s*\n(\{.*?\})\s*\n', txt)
words = []
for path, off, js in items:
    off = float(off)
    d = json.loads(js)
    toks, ts, du = d['tokens'], d['timestamps'], d['durations']
    cur = None
    ws = []
    for tok, t, dd in zip(toks, ts, du):
        if tok.startswith(' ') or cur is None:
            if cur:
                ws.append(cur)
            cur = {'w': tok.strip(), 's': t + off, 'e': t + dd + off}
        else:
            cur['w'] += tok
            cur['e'] = t + dd + off
    if cur:
        ws.append(cur)
    lo = off + (EDGE if off > 0 else -1)
    hi = off + HOP + EDGE
    for w in ws:
        if lo <= w['s'] < hi and re.search(r'\w', w['w']):
            words.append(w)
words.sort(key=lambda w: w['s'])
# overlapping windows can both emit a word at the boundary: drop near-simultaneous repeats
_n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
dd = []
for w in words:
    if dd and _n(dd[-1]['w']) == _n(w['w']) and abs(w['s'] - dd[-1]['s']) < 0.25:
        continue
    dd.append(w)
words = dd
json.dump(words, open(out, 'w'), indent=0)
# pretty transcript: break where gap > 0.6 s
line, last = [], None
for w in words:
    if last is not None and w['s'] - last > 0.6:
        print(f"{line[0]['s']:7.2f}-{line[-1]['e']:7.2f}  " + ' '.join(x['w'] for x in line))
        line = []
    line.append(w)
    last = w['e']
if line:
    print(f"{line[0]['s']:7.2f}-{line[-1]['e']:7.2f}  " + ' '.join(x['w'] for x in line))
