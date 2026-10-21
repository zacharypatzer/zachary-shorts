#!/usr/bin/env python3
"""Refine aligned lyric timings with the isolated-vocal energy envelope.

* reports the systematic offset between word starts and vocal onsets
* extends word ends across held notes (until the voice drops or the next word starts)
"""
import json, sys
import numpy as np
import scipy.io.wavfile as wf

src, dst = sys.argv[1:3]
sr, v = wf.read(sys.argv[3])
v = v.astype(np.float32) / 32768.0
HOP = 160  # 10 ms
n = len(v) // HOP
rms = np.sqrt(np.mean(v[:n * HOP].reshape(n, HOP) ** 2, axis=1))
db = 20 * np.log10(rms + 1e-6)
# smooth 30 ms
k = np.ones(3) / 3
db = np.convolve(db, k, mode='same')
floor = np.percentile(db, 20)
peak = np.percentile(db, 97)
thr = floor + 0.35 * (peak - floor)
voiced = db > thr
# onset strength: positive slope of dB
on = np.maximum(np.diff(db, prepend=db[0]), 0)

data = json.load(open(src))
words = [w for it in data if 'words' in it for w in it['words']]

# global offset estimate: correlate word-start impulses with onset strength
imp = np.zeros(n)
for w in words:
    i = int(w['s'] * 100)
    if 0 <= i < n:
        imp[i] = 1
best = None
for lag in range(-25, 26):           # +-250 ms
    sc = float(np.sum(np.roll(imp, lag) * on))
    if best is None or sc > best[0]:
        best = (sc, lag)
scores = {lag: float(np.sum(np.roll(imp, lag) * on)) for lag in range(-25, 26, 5)}
print('onset correlation by lag (10ms units):', {k: round(v_, 1) for k, v_ in scores.items()})
print('best lag (ms):', best[1] * 10)

# extend word ends across held notes
ext = 0
for i, w in enumerate(words):
    nxt = words[i + 1]['s'] if i + 1 < len(words) else w['e'] + 3
    limit = min(nxt - 0.04, w['s'] + 3.0)
    j = int(w['e'] * 100)
    while j < n and j / 100 < limit and voiced[j]:
        j += 1
    new_e = max(w['e'], min(j / 100, limit))
    if new_e > w['e'] + 0.05:
        ext += 1
    w['e'] = round(new_e, 3)
print('extended', ext, 'of', len(words), 'word ends')
json.dump(data, open(dst, 'w'), indent=1)
