"""prune_lyrics.py DIR [thresh] : drop lyric lines the vocal never sings (match fraction < thresh), print what was dropped."""
import sys, json, subprocess, os, re
D = sys.argv[1]; th = float(sys.argv[2]) if len(sys.argv) > 2 else 0.34
os.chdir(D)
src = 'words_mix.json,words_voc.json' + (',win.json' if os.path.exists('win.json') else '')
subprocess.run(['python3', '/home/claude/scripts/align.py', 'lyrics.txt', src, 'aligned.json'], env={**os.environ, 'MATCHDUMP': '/tmp/m.json'}, capture_output=True)
M = {int(k): v for k, v in json.load(open('/tmp/m.json')).items()}
raw = open('lyrics.txt').read().split('\n')
li = -1; out = []; dropped = []
for r in raw:
    if not r.strip() or r.startswith('#'):
        out.append(r); continue
    li += 1
    if r.strip() == '~':
        out.append(r); continue
    if M.get(li, 1) < th:
        dropped.append(r); continue
    out.append(r)
txt = '\n'.join(out)
txt = re.sub(r'\n{3,}', '\n\n', txt)
txt = re.sub(r'(\n~)+\n(\n?~\n)+', '\n~\n', txt)
open('lyrics.txt', 'w').write(txt)
print(f'dropped {len(dropped)} lines')
for d in dropped: print('  -', d)
