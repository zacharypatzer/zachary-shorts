#!/usr/bin/env python3
"""Render every Short in plan.py (skips finished ones). usage: batch.py v2|qh"""
import sys, os, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from plan import V2, QH, ACCENT
P = '/home/claude/zachary-shorts/pipeline'
OUT = '/home/claude/zachary-shorts/shorts/new6'
os.makedirs(OUT, exist_ok=True); os.makedirs(f'{P}/shorts/new6/cfg', exist_ok=True)
PAY = {'A': ['That was 4 years ago.', 'STILL HERE.'], 'B': ["Stage 4 Hodgkin's.", '3 BELLS RUNG.'], 'C': ['Send this to someone', 'WHO NEEDS IT.']}
PUNCH = ['stage', 'four', 'chemo', 'cancer', 'bell', 'scared', 'stuck', 'love', 'fine', 'up', 'accidental', 'behind', 'tryin\'', 'life', 'tough', 'brave', 'real', 'enough']
def snap(slug, a, b):
    L = [x for x in json.load(open(f'{P}/songs/{slug}/lyrics_final.json')) if x.get('words')]
    ins = [x for x in L if x['words'][0]['s'] >= a - 0.6 and x['words'][-1]['e'] <= b + 0.9]
    return ins[0]['words'][0]['s'], ins[-1]['words'][-1]['e']
mode = sys.argv[1]
if mode == 'v2':
    for slug, name, a, b, h1, h2 in V2:
        out = f'{OUT}/{name}.mp4'
        if os.path.exists(out): continue
        s0, s1 = snap(slug, a, b)
        st, en = max(0, s0 - 0.5), s1 + 1.0
        assert en - st <= 59.5, (name, en - st)
        raw = f'{OUT}/{name}_raw.mp4'
        subprocess.run(['python3', f'{P}/scripts/make_short_v2.py', slug, f'{st:.2f}', f'{en:.2f}', raw, h1, h2, '--accent', ACCENT[slug]], check=True)
        subprocess.run(['bash', f'{P}/scripts/norm_short.sh', raw, out], check=True); os.remove(raw)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '0.6', '-i', out, '-frames:v', '1', '-q:v', '2', f'{OUT}/{name}_cover.jpg'], check=True)
        print('done', name, round(en - st, 1), flush=True)
else:
    for slug, name, a, b, l1, big, pk in QH:
        out = f'{OUT}/{name}.mp4'
        if os.path.exists(out): continue
        s0, s1 = snap(slug, a, b); s0 -= 0.15; s1 += 0.25
        cover = f'/home/claude/songs/{slug}/cover.png'
        sz = 1668
        top = 0.30 if slug == 'accidental_motivation' else 0.245
        cfg = dict(lyrics=f'{P}/songs/{slug}/lyrics_final.json', cover=cover, song_start=round(s0, 3), song_end=round(s1, 3),
                   audio_src=f'/home/claude/songs/{slug}/song_14.m4a', audio_off=round(s0, 3), accent=ACCENT[slug],
                   hook=[l1, big], payoff=PAY[pk], punch_words=sorted(PUNCH), out=f'{OUT}/{name}_raw.mp4',
                   crop_cx=sz / 2, crop_cy=sz / 2, crop_h=sz, hide_top=int(sz * top))
        cp = f'{P}/shorts/new6/cfg/{name}.json'; json.dump(cfg, open(cp, 'w'), indent=1)
        subprocess.run(['python3', f'{P}/scripts/make_quick_hook.py', cp], check=True)
        subprocess.run(['bash', f'{P}/scripts/norm_short.sh', f'{OUT}/{name}_raw.mp4', out], check=True); os.remove(f'{OUT}/{name}_raw.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-frames:v', '1', '-q:v', '2', f'{OUT}/{name}_cover.jpg'], check=True)
        print('done', name, round(s1 - s0, 1), flush=True)
print('ALL DONE', mode)
