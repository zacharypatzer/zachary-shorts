#!/usr/bin/env python3
"""Align a hand-corrected lyric sheet to ASR word timestamps.

usage: align.py lyrics.txt words1.json[,words2.json,...] out.json

lyrics.txt: one displayed line per row; ' / ' forces a row break; '#' comments; '~' = instrumental dots.
A row may start with '@SECONDS ' to pin the first word's start time (used where the transcript is lost).
Several word lists may be given (comma separated, priority order); each lyric word takes its time from the
first list that matches it, matches that break time order are dropped, the rest is interpolated.
"""
import json, re, sys
import numpy as np
from difflib import SequenceMatcher

lyr_path, words_path, out_path = sys.argv[1:4]
SOURCES, OVERRIDES = [], []
for p in words_path.split(','):
    d = json.load(open(p))
    (OVERRIDES if isinstance(d, dict) else SOURCES).append(d)
# focused windows (from winwords.py) replace the first source's words inside their time ranges
for ov in OVERRIDES:
    inside = lambda t: any(a <= t < b for a, b in ov['windows'])
    SOURCES[0] = sorted([w for w in SOURCES[0] if not inside(w['s'])] + ov['words'], key=lambda w: w['s'])


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
    pin = None
    m = re.match(r'@([\d.]+)\s+(.*)', raw)
    if m:
        pin, raw = float(m.group(1)), m.group(2)
    parts = [p.strip() for p in raw.split(' / ')]
    words, breaks = [], []
    for p in parts:
        ws = p.split()
        words += ws
        breaks.append(len(ws))
    lines.append({'kind': 'line', 'text': words, 'breaks': breaks if len(parts) > 1 else None, 'pin': pin})

L = [(li, wi, w) for li, ln in enumerate(lines) if ln['kind'] == 'line' for wi, w in enumerate(ln['text'])]
Ln = [norm(w) for _, _, w in L]
n = len(Ln)
sim_cache = {}


def sim(a, b):
    k = (a, b)
    if k not in sim_cache:
        r = SequenceMatcher(None, a, b).ratio() if a and b else 0
        sim_cache[k] = 2.0 if a == b else (1.2 if r >= 0.75 else (0.2 if r >= 0.5 else -1.0))
    return sim_cache[k]


def nw_match(asr, lo=0, hi=None):
    """NW alignment of lyric words lo..hi against asr; returns list (len n) of (s, e) or None."""
    hi = n if hi is None else hi
    A = [norm(w['w']) for w in asr]
    m = len(A)
    nn = hi - lo
    match = [None] * n
    if nn <= 0 or m == 0:
        return match
    GAP = -0.6
    S = np.zeros((n + 1, m + 1), np.float32)
    B = np.zeros((n + 1, m + 1), np.int8)
    S[:, 0] = np.arange(n + 1) * GAP
    S[0, :] = np.arange(m + 1) * GAP
    for i in range(1, n + 1):
        li = Ln[i - 1]
        for j in range(1, m + 1):
            d = S[i - 1, j - 1] + sim(li, A[j - 1])
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
                match[i - 1] = (asr[j - 1]['s'], asr[j - 1]['e'])
            i, j = i - 1, j - 1
        elif B[i, j] == 1:
            i -= 1
        else:
            j -= 1
    return match


times = [None] * n
pinned = set()
k = 0
for ln in lines:
    if ln['kind'] != 'line':
        continue
    if ln['pin'] is not None:
        times[k] = [ln['pin'], ln['pin'] + 0.25]
        pinned.add(k)
    k += len(ln['text'])
def fix_order():
  changed = True
  while changed:
    changed = False
    changed = False
    idx = [k for k in range(n) if times[k] is not None]
    for a_, b_ in zip(idx, idx[1:]):
        if times[b_][0] < times[a_][0] - 0.05:
            victim = b_ if (b_ not in pinned) else a_
            if victim in pinned:
                continue
            times[victim] = None
            changed = True
            break


mt = nw_match(SOURCES[0])
for k in range(n):
    if times[k] is None and mt[k] is not None:
        times[k] = list(mt[k])
fix_order()
# other sources only fill gaps, aligned locally between the surrounding matched words
for src in SOURCES[1:]:
    k = 0
    while k < n:
        if times[k] is not None:
            k += 1
            continue
        a = k
        while k < n and times[k] is None:
            k += 1
        b = k
        t0 = times[a - 1][1] if a > 0 else 0.0
        t1 = times[b][0] if b < n else 1e9
        cand = [w for w in src if t0 - 0.05 <= w['s'] and w['e'] <= t1 + 0.05]
        mt = nw_match(cand, a, b)
        for x in range(a, b):
            if mt[x] is not None:
                times[x] = list(mt[x])
    fix_order()
import os
import scipy.io.wavfile as _wf
_VOC = None
if os.path.exists('vocals16.wav'):
    _sr, _v = _wf.read('vocals16.wav')
    _v = _v.astype(np.float32) / 32768.0
    _VOC = (_sr, _v)


def vocal_energy(a, b):
    if _VOC is None:
        return 0.0
    sr, v = _VOC
    seg = v[max(0, int(a * sr)):max(0, int(b * sr))]
    return float(np.sqrt(np.mean(seg * seg))) if len(seg) else 0.0


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
        natural = 0.42 * (b - a) + 0.3
        if span > natural * 1.6:
            # long gap (instrumental): keep the words together, next to the side they belong to
            span = natural
            mid_line_start = L[a][1] != 0                      # run continues a line already being sung
            joins_next = b < n and L[b][0] == L[b - 1][0]      # run leads into a matched word of its own line
            if mid_line_start and not joins_next:
                t0 = t0 + 0.05
            elif joins_next and not mid_line_start:
                t0 = t1 - span - 0.1
            else:
                # pick the side of the gap where the isolated vocal is louder
                e_after = vocal_energy(t0 + 0.05, t0 + 0.05 + span)
                e_before = vocal_energy(t1 - 0.1 - span, t1 - 0.1)
                t0 = t1 - span - 0.1 if e_before > e_after else t0 + 0.05
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

# final pass: word starts must not run backwards (overlapping sources / interpolation)
for k in range(n - 2, -1, -1):
    if times[k][0] > times[k + 1][0] - 0.02:
        times[k][0] = times[k + 1][0] - 0.02
    if times[k][1] > times[k + 1][0] and times[k][1] - times[k][0] > 0.1:
        times[k][1] = max(times[k][0] + 0.08, times[k + 1][0])

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

for k, it in enumerate(out):
    if it.get('kind') == 'dots':
        prev_end = out[k - 1]['words'][-1]['e'] if k > 0 else 0.0
        nxt = out[k + 1]['words'][0]['s']
        it['start'] = round(prev_end + (0.9 if k > 0 else 1.2), 3)
        it['end'] = round(nxt - 0.55, 3)

out = [it for it in out if not (it.get('kind') == 'dots' and it['end'] - it['start'] < 2.5)]
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
