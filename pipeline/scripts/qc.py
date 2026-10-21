#!/usr/bin/env python3
"""QC for a finished lyric video: specs, loudness, and a sheet of mid-word frames.

usage: qc.py SLUG
"""
import sys, json, subprocess, re, random
import numpy as np, cv2

slug = sys.argv[1]
D = f'/home/claude/songs/{slug}'
title = json.load(open(f'{D}/cfg.json'))['title']
fn = re.sub(r'[^A-Za-z0-9]+', '_', title.replace("'", '')).strip('_')
mp4 = f'/home/claude/out/{fn}_Lyric_Video.mp4'
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout + subprocess.run(c, shell=True, capture_output=True, text=True).stderr
info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', mp4], capture_output=True, text=True).stdout)
v = [s for s in info['streams'] if s['codec_type'] == 'video'][0]
a = [s for s in info['streams'] if s['codec_type'] == 'audio'][0]
size = int(info['format']['size'])
r = subprocess.run(f'ffmpeg -nostdin -hide_banner -i "{mp4}" -vn -af ebur128=peak=true -f null - 2>&1 | tail -14', shell=True, capture_output=True, text=True).stdout
I = re.search(r'I:\s+(-?[\d.]+) LUFS', r).group(1)
TP = re.search(r'Peak:\s+(-?[\d.]+) dBFS', r).group(1)
print(f'{fn}: {v["width"]}x{v["height"]} {v["codec_name"]} {eval(v["avg_frame_rate"]):.2f}fps, audio {a["codec_name"]} {int(a["bit_rate"])//1000}k, '
      f'dur {float(info["format"]["duration"]):.1f}s, size {size/1048576:.2f} MiB, loudness {I} LUFS / {TP} dBTP')
assert size < 30 * 1048576, 'too big'
# mid-word frames
lyr = json.load(open(f'{D}/lyrics_final.json'))
words = [w for it in lyr if 'words' in it for w in it['words']]
random.seed(1)
pick = sorted(random.sample(range(len(words)), 12))
tiles = []
for k in pick:
    w = words[k]
    t = w['s'] + min(0.12, (w['e'] - w['s']) / 2)
    png = f'/tmp/claude-0/-home-claude/7e2b6de3-c1a2-50ff-9aa8-ba533aa956e4/scratchpad/qc_{k}.png'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', mp4, '-frames:v', '1', png], check=True)
    im = cv2.imread(png)[1110:1440]
    im = cv2.resize(im, (540, 165))
    cv2.putText(im, f'{t:.2f} "{w["w"]}"', (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    tiles.append(im)
rows = [np.hstack(tiles[i:i + 3]) for i in range(0, 12, 3)]
cv2.imwrite(f'/tmp/claude-0/-home-claude/7e2b6de3-c1a2-50ff-9aa8-ba533aa956e4/scratchpad/qc_{slug}.jpg', np.vstack(rows))
print('sheet written')
