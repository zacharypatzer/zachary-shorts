#!/usr/bin/env python3
"""Insert blank section breaks into lyrics.txt before every line starting with one of the given prefixes.
usage: sections.py SLUG "prefix one" "prefix two" ...
"""
import sys
slug = sys.argv[1]
p = f'/home/claude/songs/{slug}/lyrics.txt'
pre = sys.argv[2:]
lines = [l for l in open(p).read().split('\n')]
out = []
for l in lines:
    body = l.split(' ', 1)[1] if l.startswith('@') else l
    if any(body.startswith(x) for x in pre) and out and out[-1].strip() not in ('', '~'):
        out.append('')
    out.append(l)
open(p, 'w').write('\n'.join(out))
