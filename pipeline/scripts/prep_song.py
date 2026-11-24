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
    'its_your_birthday':      ('#d63cc8', '#ffcf4a', '#ffd9f4', 1.0, 1.1),
    'glad_youre_here':        ('#ff8a1f', '#ffe08a', '#fff0c8', 0.8, 1.0),
    'say_thank_you_for_me':   ('#2f55b8', '#ffcf5a', '#ffe6a8', 0.7, 1.0),
    'nobody_watches_a_draw':  ('#e0471b', '#ffb36b', '#e8ecef', 0.5, 0.9),
    'thats_up':               ('#e8a13f', '#ffd890', '#fff0d0', 0.5, 0.9),
    'im_fine':                ('#3a5fa8', '#ffc878', '#d6e4ff', 0.4, 0.8),
    'how_you_come_back':      ('#f2b552', '#ffe3a0', '#dbe6ff', 0.6, 0.9),
    'hold_it_lightly':        ('#f0a07e', '#ffd9b0', '#fff0e6', 0.4, 0.8),
    'what_im_livin':          ('#e08f2c', '#ffcf7a', '#ffeec4', 0.6, 0.9),
    'accidental_motivation':  ('#5b86e0', '#cfe0ff', '#e4ecff', 0.35, 0.8),
    'i_see_you':              ('#2fb8b0', '#d8fffb', '#e6fbf9', 0.35, 0.8),
    'we_die_v2':              ('#c0392b', '#ffd27a', '#ffe9c0', 0.9, 1.0),
    'thatd_be_easy':          ('#2f6fd0', '#bfe0ff', '#dbe9ff', 0.35, 0.8),
    'say_it_like_a_kid_would': ('#5aa8e0', '#fff1c8', '#e2f2ff', 0.35, 0.8),
    'who_you_stay_for':       ('#e8928c', '#ffe2c0', '#ffe9e4', 0.35, 0.8),
    'pray_for_somebody_else': ('#d9a441', '#fff1c4', '#fff2d6', 0.35, 0.8),
    'if_we_can_we_do': ('#e8b04a', '#ffe3a0', '#fff3d6', 0.5, 0.9),
    'just_a_nod': ('#b8a888', '#f0e8d8', '#f2ede4', 0.35, 0.7),
    'im_good_for_it': ('#e0862a', '#ffd27a', '#ffe9c8', 0.4, 0.8),
    'givin_time_more_life': ('#ff7fb0', '#ffe0ef', '#ffe6f2', 0.6, 0.9),
    'count_the_arms_you_hold': ('#7fbf4c', '#fff6c8', '#eaffd8', 0.5, 0.9),
    'put_it_together': ('#f2a64c', '#ffd890', '#fff0dc', 0.5, 0.9),
    'the_sunrise_kind': ('#ffb067', '#fff1d0', '#fff4e6', 0.5, 0.9),
    'd_keep_on_breathing': ('#f0a050', '#ffe0b0', '#fff0dc', 0.5, 0.9),
    'd_just_remember_my_name': ('#e0a040', '#ffe0a0', '#fff0d0', 0.5, 0.9),
    'd_light_the_way': ('#2fa86a', '#ffe680', '#e8ffd0', 0.9, 1.0),
    'd_words_unspoken': ('#c89048', '#ffd890', '#f4e2c0', 0.5, 0.8),
    'd_time_is_the_currency': ('#d4a04a', '#ffe2a0', '#f8e6c4', 0.5, 0.85),
    'd_cancer_fighters_blueprint': ('#4a8ad0', '#d8ecff', '#e0eeff', 0.5, 0.9),
    'd_bleeding_the_same': ('#c0392b', '#ffd0c0', '#ffe4dc', 0.6, 0.9),
    'd_bleeding_the_same_red': ('#b02040', '#ffc0c8', '#ffe0e6', 0.6, 0.9),
    'd_cancer_fighter': ('#2fae6a', '#d0ffd8', '#e6ffe8', 0.6, 0.9),
    'd_quality_over_quantity': ('#d08a3a', '#ffe0b0', '#fff0dc', 0.5, 0.85),
    'd_strangers_anchor': ('#5a8aa8', '#dceaf4', '#e6f0f6', 0.5, 0.85),
    'd_even_if_we_fall': ('#8a6a2a', '#ffd890', '#f4e2bc', 0.6, 0.9),
    'd_monsters_out_of_shadows': ('#d07a3a', '#ffd0a0', '#e8eeff', 0.6, 0.9),
    'd_empty_out_the_cup': ('#b07a4a', '#ffe0c0', '#f4e6d4', 0.4, 0.8),
    'd_true_strength': ('#c8a040', '#fff0c0', '#f2ead8', 0.4, 0.8),
    'd_lone_wolf_rising': ('#5a7ac8', '#e0ecff', '#e8f0ff', 0.5, 0.85),
    'd_bloodline_endures': ('#a8742a', '#ffe0a0', '#f6e6c8', 0.6, 0.9),
    'd_beacon_of_hope': ('#d8a030', '#ffe08a', '#dce8ff', 0.7, 1.0),
    'd_the_ink_is_setting': ('#c8a050', '#fff0c8', '#efe6d6', 0.4, 0.8),
    'd_man_behind_the_scenes': ('#6a6ab0', '#e0e0ff', '#ecebff', 0.4, 0.8),
    'd_patzer_pro_files': ('#b04a3a', '#ffd8c8', '#f2e4dc', 0.5, 0.85),
    'd_intertwined_motivational_minds': ('#e0902a', '#ffd890', '#fff0d4', 0.8, 1.0),
    'd_living_2_die': ('#d06a3a', '#ffd0a8', '#fde6d6', 0.5, 0.85),
    'd_maze_made_the_man': ('#c87a3a', '#ffd8a8', '#f2e6d8', 0.7, 1.0),
    'd_a_new_god_rises': ('#e07a2a', '#ffd080', '#ffe8c8', 0.8, 1.0),
    'o_beautiful_anyway': ('#c06a3a', '#ffc890', '#f2b48a', 0.5, 0.8),
    'o_embrace_every_scar': ('#9a7cff', '#d9c2ff', '#e6dcff', 0.9, 0.8),
    'o_even_if_we_stumble': ('#b03ca8', '#ffb0f0', '#a8ffe0', 0.8, 0.9),
    'o_floor_of_shadows': ('#6a7a8a', '#e8f0ff', '#fff6a0', 0.5, 0.6),
    'o_footprints_of_gold': ('#c99a2e', '#ffd257', '#f4d58a', 0.8, 1.1),
    'o_i_live_on_through_you_1': ('#e08a30', '#ffd890', '#ffe2b0', 0.8, 0.9),
    'o_i_live_on_through_you_2': ('#e08a30', '#ffd890', '#ffe2b0', 0.8, 0.9),
    'o_live_now_die_later_1': ('#2fae8a', '#e8f6ff', '#c4ebff', 0.6, 0.9),
    'o_live_now_die_later_2': ('#2fae8a', '#e8f6ff', '#c4ebff', 0.6, 0.9),
    'o_live_now_die_later_3': ('#2fae8a', '#e8f6ff', '#c4ebff', 0.6, 0.9),
    'o_only_the_strong_survive_1': ('#c03030', '#ffffff', '#e0e8f0', 1.2, 0.9),
    'o_only_the_strong_survive_2': ('#c03030', '#ffffff', '#e0e8f0', 1.2, 0.9),
    'o_only_the_strong_survive_3': ('#c03030', '#ffffff', '#e0e8f0', 1.2, 0.9),
    'o_remember_me_when_im_gone_1': ('#c8a070', '#fff0d0', '#f0dcc0', 0.5, 0.7),
    'o_remember_me_when_im_gone_2': ('#c8a070', '#fff0d0', '#f0dcc0', 0.5, 0.7),
    'o_shout_yes': ('#b03cff', '#4fe3ff', '#f2a8ff', 1.4, 1.0),
    'o_take_a_number': ('#b8743a', '#ffd9a0', '#f1d9ad', 0.7, 0.8),
    'o_we_die_before_we_quit': ('#b02020', '#ffffff', '#ffb0b0', 1.1, 0.9),
    'raise_one_for_jim': ('#c8962e', '#ffe6a8', '#ffe2a0', 0.3, 0.7),
    'things_break_people_rebuild': ('#f2c14e', '#fff1c8', '#fff6dc', 0.6, 1.0),
    'rearrange': ('#f0b445', '#ffe6a8', '#e0f4f4', 0.5, 0.9),
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
