#!/usr/bin/env python3
"""Focused word timings: ASR on chosen windows, merged into one word list with absolute times.

usage: winwords.py SLUG out.json mix|voc:t0-t1 [mix|voc:t0-t1 ...]
"""
import sys, subprocess, json, re, tempfile, os

slug, outp = sys.argv[1], sys.argv[2]
D = f'/home/claude/songs/{slug}'
M = '/home/claude/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8'
tmp = tempfile.mkdtemp(dir='/tmp/claude-0/-home-claude/7e2b6de3-c1a2-50ff-9aa8-ba533aa956e4/scratchpad')
jobs = []
for spec in sys.argv[3:]:
    src, rg = spec.split(':')
    a, b = map(float, rg.split('-'))
    f = f'{tmp}/{len(jobs)}.wav'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{a:.2f}', '-t', f'{b - a:.2f}', '-i',
                    f'{D}/{"stereo44.wav" if src == "mix" else "vocals.wav"}', '-ar', '16000', '-ac', '1', f], check=True)
    jobs.append((f, a))
raw = subprocess.run(['python3', '/home/claude/scripts/wsasr.py'] + [x if isinstance(x, str) else x[0] for x in (files if 'files' in dir() else jobs)],
                     capture_output=True, text=True).stdout
lines = raw.split('\n')
res = {}
for i, l in enumerate(lines):
    if l.startswith('{"lang"'):
        res[lines[i - 1].strip()] = json.loads(l)
words = []
for f, off in jobs:
    d = res.get(f)
    if not d:
        continue
    cur = None
    for tok, t, dd in zip(d['tokens'], d['timestamps'], d['durations']):
        if tok.startswith(' ') or cur is None:
            if cur:
                words.append(cur)
            cur = {'w': tok.strip(), 's': round(t + off, 3), 'e': round(t + dd + off, 3)}
        else:
            cur['w'] += tok
            cur['e'] = round(t + dd + off, 3)
    if cur:
        words.append(cur)
    print(f'{off:7.2f}  ' + d['text'].strip())
words = [w for w in words if re.search(r'\w', w['w'])]
words.sort(key=lambda w: w['s'])
json.dump({'windows': [[off, off + float(spec.split(':')[1].split('-')[1]) - float(spec.split(':')[1].split('-')[0])] for (f, off), spec in zip(jobs, sys.argv[3:])], 'words': words}, open(outp, 'w'), indent=0)
subprocess.run(['rm', '-rf', tmp])
