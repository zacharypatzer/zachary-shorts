#!/usr/bin/env python3
"""find_seg.py SLUG "first line prefix"[#n] "last line prefix"[#n] -> start/end/duration and lines"""
import sys, json
slug, a, b = sys.argv[1:4]
d = json.load(open(f'/home/claude/songs/{slug}/lyrics_final.json'))
L = [(it['words'][0]['s'], it['words'][-1]['e'], ' '.join(w['w'] for w in it['words'])) for it in d if 'words' in it]
def find(spec, after=0):
    p, n = (spec.rsplit('#', 1) + ['1'])[:2] if '#' in spec else (spec, '1')
    hits = [i for i, x in enumerate(L) if x[2].lower().startswith(p.lower()) and i >= after]
    return hits[int(n) - 1]
i = find(a); j = find(b, i)
s = L[i][0] - 0.5; e = L[j][1] + 0.9
nxt = L[j + 1][0] if j + 1 < len(L) else 1e9
e = min(e, nxt - 0.15)
print(f'{slug}: {s:.2f} -> {e:.2f}  ({e - s:.1f}s)')
for k in range(i, j + 1):
    print(f'   {L[k][0]:7.2f} {L[k][2][:70]}')
