#!/usr/bin/env python3
"""Align a hand-corrected lyric sheet to ASR word timestamps.

lyrics.txt format: one displayed line per row. Optional ' / ' marks a forced row break.
Lines starting with '#' are comments. A line '~' inserts an instrumental-dots marker
(timed automatically from the surrounding lines).
"""
import json, re, sys
from difflib import SequenceMatcher

lyr_path, words_path, out_path = sys.argv[1:4]
# several word lists may be given, comma separated, in priority order (e.g. focused windows, mix, vocals)
SOURCES = [json.load(open(p_)) for p_ in words_path.split(',')]


def norm(w):
    w = w.lower().replace('’', "'")
    w = re.sub(r"[^a-z0-9']", '', w)
    w = w.strip("'")
    w = {'them': 'em', "'em": 'em', 'ma': 'my'}.get(w, w)
    if w.endswith('ing'):
        w = w[:-1]
    if w.endswith("in'"):
        w = w[:-1]
    return w.replace("'", '')


lines = []
for raw in open(lyr_path):
    raw = raw.rstrip('\n')
    if not raw.strip() or raw.startswith('#'):
        continue
    if raw.strip() == '~':
        lines.append({'kind': 'dots'})
        continue
    parts = [p.strip() for p in raw.split(' / ')]
    words, breaks = [], []
    for p in parts:
        ws = p.split()
        words += ws
        breaks.append(len(ws))
    lines.append({'kind': 'line', 'text': words, 'breaks': breaks if len(parts) > 1 else None})

import numpy as np
L = [(li, wi, w) for li, ln in enumerate(lines) if ln['kind'] == 'line' for wi, w in enumerate(ln['text'])]
Ln = [norm(w) for _, _, w in L]

sim_cache = {}


def sim(a, b):
    k = (a, b)
    if k not in sim_cache:
        r = SequenceMatcher(None, a, b).ratio() if a and b else 0
        sim_cache[k] = 2.0 if a == b else (1.2 if r >= 0.75 else (0.2 if r >= 0.5 else -1.0))
    return sim_cache[k]


def nw_match(asr):
    A = [norm(w['w']) for w in asr]
    # Needleman-Wunsch
    n, m = len(Ln), len(A)
    GAP = -0.6
    S = np.zeros((n + 1, m + 1), np.float32)
    B = np.zeros((n + 1, m + 1), np.int8)
    S[:, 0] = np.arange(n + 1) * GAP
    S[0, :] = np.arange(m + 1) * GAP
    sim_cache = {}


    def sim(a, b):
        k = (a, b)
        if k not in sim_cache:
            r = SequenceMatcher(None, a, b).ratio() if a and b else 0
            sim_cache[k] = 2.0 if a == b else (1.2 if r >= 0.75 else (0.2 if r >= 0.5 else -1.0))
        return sim_cache[k]


    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d = S[i - 1, j - 1] + sim(Ln[i - 1], A[j - 1])
            u = S[i - 1, j] + GAP
            l = S[i, j - 1] + GAP
            if d >= u and d >= l:
                S[i, j], B[i, j] = d, 0
            elif u >= l:
                S[i, j], B[i, j] = u, 1
            else:
                S[i, j], B[i, j] = l, 2
    i, j = n, m
    match = [None] * n
    while i > 0 and j > 0:
        if B[i, j] == 0:
            if sim(Ln[i - 1], A[j - 1]) > 0:
                match[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif B[i, j] == 1:
            i -= 1
        else:
            j -= 1


    return [None if j is None else (asr[j]['s'], asr[j]['e']) for j in match]


times = [None] * n
for src in SOURCES:
    mt = nw_match(src)
    for k in range(n):
        if times[k] is None and mt[k] is not None:
            times[k] = list(mt[k])
# drop matches that break time order against their matched neighbours
changed = True
while changed:
    changed = False
    idx_ = [k for k in range(n) if times[k] is not None]
    for x, y in zip(idx_, idx_[1:]):
        if times[y][0] < times[x][0] - 0.05:
            # drop the one that conflicts with more neighbours: simple rule, drop the later one
            times[y] = None
            changed = True
            break
# interpolate the gaps
k = 0
unmatched = []
while k < n:
    if times[k] is None:
        a = k
        while k < n and times[k] is None:
            k += 1
        b = k
        t0 = times[a - 1][1] if a > 0 else (times[b][0] - 0.3 * (b - a))
        t1 = times[b][0] if b < n else t0 + 0.35 * (b - a)
        span = max(t1 - t0, 0.12 * (b - a))
        lens = [len(L[x][2]) + 1 for x in range(a, b)]
        tot = sum(lens)
        c = t0
        for x, ln_ in zip(range(a, b), lens):
            d = span * ln_ / tot
            times[x] = [c, c + d * 0.92]
            c += d
            unmatched.append((L[x][2], round(times[x][0], 2)))
    else:
        k += 1

out = []
idx = 0
for ln in lines:
    if ln['kind'] == 'dots':
        out.append({'kind': 'dots'})
        continue
    ws = []
    for w in ln['text']:
        s, e = times[idx]
        ws.append({'w': w, 's': round(float(s), 3), 'e': round(float(e), 3)})
        idx += 1
    item = {'words': ws}
    if ln['breaks']:
        item['breaks'] = ln['breaks']
    out.append(item)

# time the dots markers: from previous line end + 0.9 s to next line start - 0.5 s
for k, it in enumerate(out):
    if it.get('kind') == 'dots':
        prev_end = out[k - 1]['words'][-1]['e'] if k > 0 else 0.0
        nxt = out[k + 1]['words'][0]['s']
        it['start'] = round(prev_end + (0.9 if k > 0 else 1.2), 3)
        it['end'] = round(nxt - 0.55, 3)

# sanity: monotonic words
flat = [w for it in out if 'words' in it for w in it['words']]
for a, b in zip(flat, flat[1:]):
    if b['s'] < a['s'] - 0.01:
        print('NON-MONOTONIC', a, b)
json.dump(out, open(out_path, 'w'), indent=1)
print('unmatched lyric words (interpolated):', len(unmatched))
for u in unmatched:
    print('   ', u)
for it in out:
    if 'words' in it:
        print(f"{it['words'][0]['s']:7.2f} {it['words'][-1]['e']:7.2f}  " + ' '.join(w['w'] for w in it['words']))
    else:
        print(f"{it['start']:7.2f} {it['end']:7.2f}  ~ dots")
