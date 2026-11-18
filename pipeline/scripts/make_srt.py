#!/usr/bin/env python3
"""Closed-caption .srt files for R2/R3 Shorts, from the song's aligned lyrics.
usage: make_srt.py  (reads pipeline/shorts/round2/jobs.txt, writes shorts/captions/<name>.srt)"""
import json, os
P = 'pipeline'
def ts(t):
    t = max(0, t); h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int(round((s % 1) * 1000)) % 1000:03}"
jobs = {}
for row in open(f'{P}/shorts/round2/jobs.txt'):
    slug, a, b, name = row.split('\t')[:4]; jobs[name] = (slug, float(a), float(b))
todo = [(n, *v) for n, v in jobs.items()]
# Story Shorts: audio is a 21 s cut of an R2/R3 Short (offset found by audio match)
for row in open(f'{P}/shorts/story_offsets.tsv'):
    f, src, off = row.split('\t'); slug, a, _ = jobs[os.path.basename(src)]
    st = a + float(off); todo.append((os.path.basename(f), slug, st, st + 21.0))
for name, slug, a, b in todo:
    lines = [l for l in json.load(open(f'{P}/songs/{slug}/aligned.json')) if l.get('words')]
    cues = []
    for i, l in enumerate(lines):
        s, e = l['words'][0]['s'], l['words'][-1]['e'] + 0.4
        if i + 1 < len(lines): e = min(e, lines[i + 1]['words'][0]['s'])  # no overlap
        s, e = max(s, a), min(e, b)
        if e - s < 0.6: continue  # skip slivers cut by the clip edge
        cues.append((s - a, e - a, ' '.join(w['w'] for w in l['words'])))
    out = [f"{n}\n{ts(s)} --> {ts(e)}\n{t}\n" for n, (s, e, t) in enumerate(cues, 1)]
    n = len(cues)
    open(f"shorts/captions/{name[:-4]}.srt", 'w').write('\n'.join(out))
    print(name, n)
