#!/usr/bin/env python3
"""One YouTube Short in the Shorts layout (title, art and lyrics in the top 60%, clear of the app's overlays).
usage: make_short_v2.py SLUG START END OUT.mp4 "hook line 1" ["hook line 2"] [--accent #hex]"""
import sys, os, json, subprocess, tempfile
sys.path.insert(0, '/home/claude/scripts')
from PIL import Image, ImageDraw, ImageFont

args = sys.argv[1:]
accent = '#5ec0ff'
if '--accent' in args:
    k = args.index('--accent'); accent = args[k + 1]; del args[k:k + 2]
slug, start, end, out = args[0], float(args[1]), float(args[2]), args[3]
hook = args[4:]
D = f'/home/claude/songs/{slug}'
W, H, HOOK_T, CY = 1080, 1920, 4.5, 222
tmp = tempfile.mkdtemp(dir='/tmp/claude-0/-home-claude/7e2b6de3-c1a2-50ff-9aa8-ba533aa956e4/scratchpad')

# hook card
FB = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
size = 80
while size > 52:
    f = ImageFont.truetype(FB, size)
    if max(d.textlength(l, font=f) for l in hook) <= W - 170:
        break
    size -= 2
lh = int(size * 1.18); block = lh * len(hook)
top, bot = min(CY - block // 2 - 30, 120), max(CY + block // 2 + 24, 322)
d.rounded_rectangle([44, top, W - 44, bot], 34, fill=(8, 14, 26, 255), outline=accent, width=5)
y = (top + bot) / 2 - block / 2 + size * 0.86
for i, l in enumerate(hook):
    col = accent if (i == len(hook) - 1 and len(hook) > 1) else '#ffffff'
    d.text((W / 2 + 3, y + 4), l, font=f, fill=(0, 0, 0, 170), anchor='ms')
    d.text((W / 2, y), l, font=f, fill=col, anchor='ms')
    y += lh
png = f'{tmp}/hook.png'; im.save(png)

# base video in the Shorts layout
env = dict(os.environ, RENDER_SHORTS='1', SONG_CFG=f'{D}/cfg.json', RENDER_PRESET='faster', RENDER_CRF='17')
v = f'{tmp}/v.mp4'
subprocess.run(['python3', '/home/claude/scripts/render.py', f'{D}/lyrics_final.json', v, '--range', f'{start:.3f}', f'{end:.3f}'],
               env=env, check=True, stdout=subprocess.DEVNULL)
dur = end - start
fc = (f"[2:v]format=rgba,fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st={HOOK_T - 0.4}:d=0.4:alpha=1[h];"
      f"[0:v][h]overlay=0:0:enable='lte(t,{HOOK_T})',fade=t=out:st={dur - 0.45:.2f}:d=0.45[v];"
      f"[1:a]afade=t=in:st=0:d=0.15,afade=t=out:st={dur - 0.9:.2f}:d=0.9[a]")
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', v, '-ss', f'{start:.3f}', '-t', f'{dur:.3f}', '-i', f'{D}/song_14.m4a',
                '-loop', '1', '-t', f'{HOOK_T + 0.1}', '-i', png, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], check=True)
subprocess.run(['rm', '-rf', tmp])
print(out, f'{dur:.1f}s', f'{os.path.getsize(out) / 1048576:.1f} MiB')
