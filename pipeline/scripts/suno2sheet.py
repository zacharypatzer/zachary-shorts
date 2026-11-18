#!/usr/bin/env python3
"""Turn a Suno lyric box (with [Section] tags and stage directions) into a lyrics.txt sheet.
usage: suno2sheet.py SLUG TITLE"""
import sys, re
slug, title = sys.argv[1], sys.argv[2]
D = f'/home/claude/songs/{slug}'
out = [f'# {title} (Remastered) - as sung']
STAGE = re.compile(r'^\((spoken[^)]*|soft|building|choir|full choir[^)]*|sung[^)]*)\)\s*', re.I)
for raw in open(f'{D}/suno_lyrics.txt').read().split('\n'):
    l = raw.strip()
    if not l:
        continue
    if l.startswith('['):
        tag = l.lower()
        if any(k in tag for k in ('instrumental', 'solo', 'fade')):
            if out[-1] != '~':
                out.append('~')
        elif out[-1] not in ('', '~'):
            out.append('')
        continue
    l = STAGE.sub('', l)
    if l:
        out.append(l)
open(f'{D}/lyrics.txt', 'w').write('\n'.join(out).rstrip() + '\n')
print(slug, len(out))
