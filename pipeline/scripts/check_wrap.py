import sys, os, json
os.environ.setdefault('SONG_CFG', '/home/claude/songs/d_keep_on_breathing/cfg.json')
sys.path.insert(0, '/home/claude/scripts')
import render as R
for p in sys.argv[1:]:
    for raw in open(p):
        raw = raw.strip()
        if not raw or raw.startswith('#') or raw == '~': continue
        if raw.startswith('@'): raw = raw.split(' ', 1)[1]
        words = raw.replace(' / ', ' ').split()
        try:
            R.wrap_words(words, R.F_LYR)
        except Exception as e:
            print(p.split('/')[0], '|', raw)
