import json, subprocess, sys
sys.path.insert(0, '/home/claude/zachary-shorts/pipeline/qh')
from plan import PUNCH
P = '/home/claude/zachary-shorts/pipeline'
L = f'/home/claude/songs/say_it_like_a_kid_would/lyrics_final.json'
cover = f'{P}/out/Say_It_Like_a_Kid_Would_DistroKid_3000.jpg'; sz = 3000
JOBS = [('QK1', 62.45, 72.75, ['Three little words', 'YOU KEEP SAVING.']),
        ('QK2', 20.3, 30.85, ['At the wake, a kid asked', 'ONE QUESTION.']),
        ('QK3', 179.15, 189.25, ['Ask the hard question.', 'IF IT COMES FROM LOVE.'])]
LYR = [x for x in json.load(open(L)) if 'words' in x]
for name, s0, s1, hook in JOBS:
    LL = [x for x in LYR if x['words'][0]['s'] >= s0 - 0.01 and x['words'][-1]['e'] <= s1 + 0.01]
    print(name, [' '.join(w['w'] for w in x['words']) for x in LL])
    out = f'/home/claude/shorts/kid/raw_{name}.mp4'
    cfg = dict(lyrics=L, cover=cover, song_start=s0, song_end=s1,
               audio_src='/home/claude/songs/say_it_like_a_kid_would/song_14.m4a', audio_off=s0, accent='#ffb547',
               hook=hook, payoff=['Send this to someone', 'WHO NEEDS IT.'], punch_words=sorted(PUNCH | {'sorry', 'cry'}),
               out=out, crop_cx=sz / 2, crop_cy=sz / 2, crop_h=sz, hide_top=int(sz * 0.245))
    cfg['payoff_at'] = round(min(max((s1 - s0) * 0.6, LL[-1]['words'][0]['s'] - s0 - 0.1), (s1 - s0) - 2.5), 2)
    cp = f'/home/claude/kidwork/{name}.json'; json.dump(cfg, open(cp, 'w'), indent=1)
    subprocess.run(['python3', f'{P}/scripts/make_quick_hook.py', cp], check=True)
