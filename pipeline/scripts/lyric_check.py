#!/usr/bin/env python3
"""Pre-release lyric check for a new song draft (Suno lyrics with [Section] tags).

usage: lyric_check.py draft.txt "Title" [catalog_dir]

Reports: 4+ word phrases already used in any catalog song (must be zero), syllables per line
(flags lines far off their section's average), most repeated words, how often the title is
sung, and total characters (Suno limit 5000).
"""
import re, sys, glob, collections

path, title = sys.argv[1], sys.argv[2]
cat_dir = sys.argv[3] if len(sys.argv) > 3 else '/home/claude/zachary-shorts/pipeline/songs'
txt = open(path).read()


def syl(w):
    w = w.lower().strip(".,!?\"…()").replace("'", "")
    if not w:
        return 0
    n = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('e') and not w.endswith(('le', 'ee')) and n > 1:
        n -= 1
    return max(1, n)


body = '\n'.join(l for l in txt.splitlines() if not l.startswith('['))
words = re.findall(r"[a-z']+", body.lower())
cat = ' '.join(open(f).read().lower() for f in glob.glob(f'{cat_dir}/*/lyrics.txt'))
cw = re.findall(r"[a-z']+", cat)
grams = set(tuple(cw[i:i + 4]) for i in range(len(cw) - 3))
hits = sorted(set(' '.join(words[i:i + 4]) for i in range(len(words) - 3) if tuple(words[i:i + 4]) in grams))
print('CATALOG OVERLAPS (4+ words):', hits or 'none')

print('\nSYLLABLES (! = far off section average)')
sec, rows = None, []
for l in txt.splitlines() + ['[end]']:
    if l.startswith('['):
        if rows:
            avg = sum(n for n, _ in rows) / len(rows)
            for n, t in rows:
                print(f"{'!' if abs(n - avg) > 4 else ' '}{n:3d}  {t}")
        sec, rows = l, []
        if l != '[end]':
            print(l)
        continue
    if l.strip():
        rows.append((sum(syl(w) for w in l.split()), l))

stop = set('the and you that they for with but when there this what your from have will just been were into them then than our are its'.split())
c = collections.Counter(w for w in words if len(w) > 3 and w not in stop)
print('\nMOST REPEATED:', c.most_common(15))
print('TITLE SUNG:', body.lower().count(title.lower()), 'times')
print('CHARACTERS:', len(txt), '(Suno max 5000)')
