#!/usr/bin/env python3
"""Targeted re-listen: ASR on short snippets of the mix and the vocals, several crops each.

usage: probe.py SLUG t0-t1 [t0-t1 ...]
"""
import sys, os, subprocess, json, re, tempfile

slug = sys.argv[1]
D = f'/home/claude/songs/{slug}'
M = '/home/claude/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8'
tmp = tempfile.mkdtemp(dir='/tmp/claude-0/-home-claude/7e2b6de3-c1a2-50ff-9aa8-ba533aa956e4/scratchpad')
files = []
for rg in sys.argv[2:]:
    a, b = map(float, rg.split('-'))
    for src, fn in (('mix', 'stereo44.wav'), ('voc', 'vocals.wav')):
        for k, (da, db) in enumerate(((-0.4, 0.4), (-1.2, 0.0), (0.0, 1.0))[:int(os.environ.get('CROPS', '2'))]):
            out = f'{tmp}/{rg}_{src}_{k}.wav'
            s, e = max(0, a + da), b + db
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{s:.2f}', '-t', f'{e - s:.2f}', '-i', f'{D}/{fn}',
                            '-ar', '16000', '-ac', '1', out], check=True)
            files.append(out)
raw = subprocess.run(['python3', '/home/claude/scripts/wsasr.py'] + [x if isinstance(x, str) else x[0] for x in (files if 'files' in dir() else jobs)],
                     capture_output=True, text=True).stdout
lines = raw.split('\n')
res = {}
for i, l in enumerate(lines):
    if l.startswith('{"lang"'):
        res[lines[i - 1].strip()] = json.loads(l)['text'].strip()
last = None
for f in files:
    rg = os.path.basename(f).split('_')[0]
    if rg != last:
        print(f'--- {rg}')
        last = rg
    tag = os.path.basename(f)[len(rg) + 1:-4]
    print(f'  {tag:6s} {res.get(f, "?")}')
subprocess.run(["rm", "-rf", tmp])
