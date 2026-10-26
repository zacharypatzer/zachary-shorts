#!/usr/bin/env python3
"""Render every quick-hook Short in plan.py (skips ones already rendered) and write posts.json for scheduling.
usage: batch.py [--only N]"""
import sys, json, os, subprocess, colorsys, time
sys.path.insert(0, os.path.dirname(__file__))
from plan import PLAN, PAYOFF, PUNCH
from PIL import Image, ImageColor

P = '/home/claude/zachary-shorts/pipeline'
OUT = '/home/claude/zachary-shorts/shorts/qh'
os.makedirs(OUT, exist_ok=True); os.makedirs(f'{P}/qh/cfg', exist_ok=True)
jobs = {}
for l in open(f'{P}/shorts/round2/jobs.txt'):
    if l.strip():
        slug, a, b, f, acc, h1, h2 = l.rstrip('\n').split('\t')
        jobs[(slug, f[:2])] = (float(a), float(b), f, acc)
titles = {l.split('\t')[1]: l.rstrip('\n').split('\t')[3] for l in open(f'{P}/songs/list.tsv')}


def windows(slug, a, b):
    L = [x for x in json.load(open(f'{P}/songs/{slug}/lyrics_final.json')) if 'words' in x]
    lines = [(x['words'][0]['s'], x['words'][-1]['e']) for x in L if x['words'][0]['s'] >= a + 0.3 and x['words'][-1]['e'] <= b - 0.6]
    i, wins = 0, []
    while i < len(lines):
        j = i
        while j + 1 < len(lines) and lines[j + 1][1] - lines[i][0] <= 15.5: j += 1
        if lines[j][1] - lines[i][0] >= 8: wins.append((lines[i][0] - 0.15, lines[j][1] + 0.25))
        i = j + 1
    return wins


def vivid(h):
    r, g, b = [c / 255 for c in ImageColor.getrgb(h)]
    hh, s, v = colorsys.rgb_to_hsv(r, g, b)
    if s < 0.5: s, v = 0.78, 1.0
    r, g, b = colorsys.hsv_to_rgb(hh, s, max(v, 0.9))
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))


def natural(l1, big):
    s = big.lower()
    s = s[0].upper() + s[1:] if l1.rstrip().endswith(('.', ':', '?', '."')) else s
    for a, b in ((" i ", " I "), ("i'm", "I'm"), ("i'd", "I'd"), ("stage 4", "Stage 4")):
        s = (' ' + s).replace(a, b)[1:] if a == " i " else s.replace(a, b)
    if s.startswith('i '): s = 'I ' + s[2:]
    return f'{l1} {s}'


posts = []
only = int(sys.argv[sys.argv.index('--only') + 1]) if '--only' in sys.argv else None
for n, (slug, var, sec, wi, l1, big, pk) in enumerate(PLAN):
    a, b, f, acc = jobs[(slug, sec)]
    s0, s1 = windows(slug, a, b)[wi]
    name = f'QH_{slug}_{var}'
    out = f'{OUT}/{name}.mp4'
    payoff = PAYOFF[pk] if isinstance(pk, str) else pk
    hook_txt = natural(l1, big)
    title = titles[slug]
    posts.append(dict(n=n, slug=slug, var=var, file=f'{name}.mp4', cover=f'{name}_cover.jpg', title=title, hook=hook_txt,
                      dur=round(s1 - s0, 2), payoff=' '.join(payoff)))
    if only is not None and n != only: continue
    if os.path.exists(out) and os.path.exists(f'{OUT}/{name}_cover.jpg'): continue
    if slug == 'we_die_before_we_quit':
        cover, extra = f'{P}/songs/we_die_before_we_quit/cover_full.jpg', dict(crop_cx=966, crop_cy=966, crop_h=1932, hide_top=470)
    else:
        cover = f'{P}/qh/covers4x/{slug}.png'
        while not os.path.exists(cover): time.sleep(20)
        time.sleep(2)
        sz = Image.open(cover).size[1]
        extra = dict(crop_cx=sz / 2, crop_cy=sz / 2, crop_h=sz, hide_top=int(sz * 0.245))
        if slug == 'remember_me_when_im_gone': extra.update(hide_top=int(sz * 0.29), hide_mode='blur')
    cfg = dict(lyrics=f'{P}/songs/{slug}/lyrics_final.json', cover=cover, song_start=round(s0, 3), song_end=round(s1, 3),
               audio_src=f'/home/claude/zachary-shorts/shorts/{f}', audio_off=round(s0 - a, 3), accent=vivid(acc),
               hook=[l1, big], payoff=payoff, punch_words=sorted(PUNCH), out=out, **extra)
    cp = f'{P}/qh/cfg/{name}.json'; json.dump(cfg, open(cp, 'w'), indent=1)
    subprocess.run(['python3', f'{P}/scripts/make_quick_hook.py', cp], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-frames:v', '1', '-q:v', '2', f'{OUT}/{name}_cover.jpg'], check=True)
    print('done', n, name, flush=True)
json.dump(posts, open(f'{P}/qh/posts.json', 'w'), indent=1)
print('ALL DONE', len(posts))
