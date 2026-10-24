#!/usr/bin/env python3
"""Per-song prep: cfg.json, cover.png, mono44.wav, vocals16.wav, -14 LUFS audio (song_14.m4a).

usage: prep_song.py SLUG
"""
import sys, os, json, re, subprocess, shutil

SLUG = sys.argv[1]
D = f'/home/claude/songs/{SLUG}'
U = os.environ.get('UPL', '/root/.claude/uploads/7e2b6de3-c1a2-50ff-9aa8-ba533aa956e4')
rows = [l.rstrip('\n').split('\t') for l in open('/home/claude/songs/list.tsv')]
row = [r for r in rows if r[1] == SLUG][0]
TITLE = row[3]

# glow, particles, subtitle tint (hex), particle speed, particle gain
PAL = {
    'island_time':            ('#ff8a50', '#ffd9a0', '#9ff3f0', 0.8, 0.9),
    'im_a_witness':           ('#8a4dff', '#ffd27a', '#ffb3dc', 1.0, 1.0),
    'a_seat_at_the_table':    ('#d98a2b', '#ffcf7a', '#9df0c0', 0.9, 0.9),
    'no_complaints':          ('#c8823c', '#ffc070', '#a8bfff', 1.0, 0.9),
    'embrace_every_scar':     ('#9a7cff', '#d9c2ff', '#e6dcff', 0.9, 0.8),
    'footprints_of_gold':     ('#c99a2e', '#ffd257', '#f4d58a', 0.8, 1.1),
    'shout_yes':              ('#b03cff', '#4fe3ff', '#f2a8ff', 1.4, 1.0),
    'even_if_we_stumble':     ('#b03ca8', '#ffb0f0', '#a8ffe0', 0.8, 0.9),
    'from_where_i_stand':     ('#b08a3c', '#ffe08a', '#f0e6c8', 0.6, 1.0),
    'remember_me_when_im_gone': ('#c8a070', '#fff0d0', '#f0dcc0', 0.5, 0.7),
    'dying_to_live':          ('#3c9a5a', '#c8ff7a', '#d0ffa0', 0.7, 1.0),
    'living_in_the_echo':     ('#2a6ab0', '#9ad8ff', '#ffcf8a', 0.6, 0.8),
    'only_the_strong_survive': ('#c03030', '#ffffff', '#e0e8f0', 1.2, 0.9),
    'make_your_time_count':   ('#c8903c', '#ffd890', '#f6c6b0', 0.9, 0.9),
    'live_now_die_later':     ('#2fae8a', '#e8f6ff', '#c4ebff', 0.6, 0.9),
    'my_word_wont_die':       ('#c87838', '#ffd8a0', '#f6e3bc', 0.9, 0.9),
    'quiet_fire':             ('#ff7c34', '#ff9646', '#ffc890', 1.0, 1.0),
    'floor_of_shadows':       ('#6a7a8a', '#e8f0ff', '#fff6a0', 0.5, 0.6),
    'i_live_on_through_you':  ('#e08a30', '#ffd890', '#ffe2b0', 0.8, 0.9),
    'we_die_before_we_quit':  ('#b02020', '#ffffff', '#ffb0b0', 1.1, 0.9),
    'take_a_number':          ('#b8743a', '#ffd9a0', '#f1d9ad', 0.7, 0.8),
    'light_one_let_it_go':    ('#d9822b', '#ffb85c', '#ffd9a0', 0.7, 1.1),
    'beautiful_anyway':       ('#c06a3a', '#ffc890', '#f2b48a', 0.5, 0.8),
    'a_mile_an_hour':         ('#2f6fb0', '#cfe6ff', '#9fd2ff', 0.4, 0.9),
    'unfinished':             ('#e07a64', '#c8f5e6', '#ffd0c2', 0.5, 0.8),
    'lions_heart':            ('#e0862a', '#ffd27a', '#ffe0a8', 0.6, 0.9),
    'the_seventh_day':        ('#d9a441', '#fff1c4', '#fff4d6', 0.35, 0.8),
}


def bgr(h, top=None):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    c = [b, g, r]
    if top:
        m = max(c)
        c = [round(x * top / m, 1) for x in c]
    return c


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def loudness(path):
    r = sh(f'ffmpeg -nostdin -hide_banner -i "{path}" -af ebur128=peak=true -f null - 2>&1 | tail -14')
    I = float(re.search(r'I:\s+(-?[\d.]+) LUFS', r.stdout).group(1))
    TP = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', r.stdout).group(1))
    return I, TP


os.chdir(D)
mp3 = f'{U}/{row[2]}'
dur = float(sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{mp3}"').stdout)
open('dur.txt', 'w').write(f'{dur:.3f}\n')
if not os.path.exists('mono44.wav'):
    sh('ffmpeg -nostdin -v error -y -i stereo44.wav -ac 1 mono44.wav')
if not os.path.exists('vocals16.wav') and os.path.exists('vocals.wav'):
    sh('ffmpeg -nostdin -v error -y -i vocals.wav -ac 1 -ar 16000 vocals16.wav')
if not os.path.exists('cover.png'):
    shutil.copy(f'/home/claude/covers/x4_{SLUG}.png', 'cover.png')

g, e, s, sp, gain = PAL[SLUG]
cfg = dict(work=D, dur=round(dur, 3), art_path=f'{D}/cover.png', title=TITLE,
           glow_col=bgr(g, 120), ember_col=bgr(e, 255), sub_tint=bgr(s), ember_speed=sp, ember_gain=gain,
           bg_tint=[1.0, 1.0, 1.0], bg_gain=0.40)
json.dump(cfg, open('cfg.json', 'w'), indent=1)

# ---- audio at -14 LUFS integrated, true peak <= -1 dBTP, AAC 160k
if not os.path.exists('song_14.m4a'):
    I0, TP0 = loudness('stereo44.wav')
    gain_db = -14.0 - I0
    lim = 0.89
    best, cands = None, []
    for it in range(10):
        sh(f'ffmpeg -nostdin -v error -y -i stereo44.wav -af "aformat=sample_fmts=flt,highpass=f=12,volume={gain_db:.2f}dB,'
           f'alimiter=limit={lim:.3f}:attack=5:release=60:level=disabled:latency=1" -c:a aac -aac_coder fast -b:a 160k -cutoff 17000 -ar 48000 song_14.m4a')
        I, TP = loudness('song_14.m4a')
        bad = max(0, abs(I + 14.0) - 0.2) + max(0, TP + 1.0)
        cands.append((bad, gain_db, lim, I, TP))
        if bad == 0:
            break
        if TP > -1.0:
            lim *= 10 ** ((-1.2 - TP) / 20)
        gain_db += (-14.0 - I)
    bad, gain_db, lim, I, TP = min(cands)
    if (I, TP) != cands[-1][3:]:
        sh(f'ffmpeg -nostdin -v error -y -i stereo44.wav -af "aformat=sample_fmts=flt,highpass=f=12,volume={gain_db:.2f}dB,'
           f'alimiter=limit={lim:.3f}:attack=5:release=60:level=disabled:latency=1" -c:a aac -aac_coder fast -b:a 160k -cutoff 17000 -ar 48000 song_14.m4a')
        I, TP = loudness('song_14.m4a')
    best = (I, TP)
    open('loudness.txt', 'w').write(f'source {I0:.1f} LUFS / {TP0:.1f} dBTP -> {best[0]:.1f} LUFS / {best[1]:.1f} dBTP\n')
print(open('loudness.txt').read().strip())
print(json.dumps(cfg))
