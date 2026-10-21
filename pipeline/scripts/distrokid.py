#!/usr/bin/env python3
"""DistroKid lyric box text from a song's lyrics.txt.

Blank lines and '~' in lyrics.txt mark section breaks. Output: no section tags, every chorus written out,
blank line between sections, no end-of-line punctuation, no quotation marks.
usage: distrokid.py SLUG  -> prints text and writes SLUG/distrokid.txt
"""
import sys, re

slug = sys.argv[1]
D = f'/home/claude/songs/{slug}'
out, sec = [], []
for raw in open(f'{D}/lyrics.txt'):
    raw = raw.rstrip('\n')
    if raw.startswith('#'):
        continue
    if not raw.strip() or raw.strip() == '~':
        if sec:
            out.append(sec)
            sec = []
        continue
    raw = re.sub(r'^@[\d.]+\s+', '', raw).replace(' / ', ' ')
    PROPER = {'Doc', 'Mama', 'God', 'Lord', 'Daddy', 'Kaiser', 'I'}
    def _low(m):
        w = m.group(1)
        word = re.match(r"[A-Za-z]+", w).group(0)
        return w if (word in PROPER or w.startswith("I'") or m.start() == 0) else w[0].lower() + w[1:]
    raw = re.sub(r'["“]([A-Z][A-Za-z\']*)', _low, raw)
    raw = raw.replace('"', '').replace('“', '').replace('”', '')
    raw = re.sub(r'!\s+', ', ', raw).replace('!', '').replace(', (', ' (')
    raw = re.sub(r'[\s.,!?;:]+$', '', raw)
    raw = re.sub(r'[.,!?;:]+\)$', ')', raw)
    if raw.strip():
        sec.append(raw[0].upper() + raw[1:])
if sec:
    out.append(sec)
txt = '\n\n'.join('\n'.join(s) for s in out) + '\n'
open(f'{D}/distrokid.txt', 'w').write(txt)
print(txt)
