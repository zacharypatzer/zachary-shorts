#!/usr/bin/env python3
"""Story/R Shorts full-frame using his REAL portrait (assets/face_src.jpg), not the upscaled cover.
Fixes the waxy face (cover was blown up ~10x) and the 'phantom' cover-title letters at the top.
Lyric text is lifted from the ORIGINAL card-style Short (git 6b25d7e) by brightness, as in fullbleed.py.

usage: fullbleed_portrait.py ORIG_CARD.mp4 OUT.mp4 [STYLE=story|r]"""
import subprocess, sys, os, tempfile
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

inp, out = sys.argv[1:3]
style = sys.argv[3] if len(sys.argv) > 3 else 'story'
TEXT = {'r': (870, 1330), 'story': (830, 1260)}[style]
W, H = 1080, 1920
DEST = 190                      # lyrics sit above his head, clear of his eyes
R = os.path.dirname(os.path.abspath(__file__)) + '/..'

# ---- background: sharp portrait (1.45x, whole head in frame) over a blurred fill of itself ----
p = Image.open(f'{R}/assets/face_src.jpg').convert('RGB')
# fill from the photo's empty corner only (smoke/embers), so no blurred copy of his head shows above him
corner = p.crop((0, 0, 240, 240))
fill = corner.resize((W, W), Image.LANCZOS).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(10))
fill = ImageEnhance.Brightness(fill).enhance(0.8)
s = 1.45
sw, sh = int(p.width * s), int(p.height * s)
sharp = p.resize((sw, sh), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
x0 = (sw - W) // 2
sharp = sharp.crop((x0, 0, x0 + W, sh))
y0 = H - sh                      # bottom-aligned: hoodie meets the bottom edge
m = Image.new('L', (W, sh), 255); md = ImageDraw.Draw(m)
for y in range(60):             # short feather: stops above the top of his head
    md.line([(0, y), (W, y)], fill=int(255 * y / 60))
bg = fill.copy(); bg.paste(sharp, (0, y0), m)
# soft dark band behind the lyrics so text stays readable
t0, t1 = TEXT; d0, d1 = DEST, DEST + (t1 - t0)
shade = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(shade)
for y in range(H):
    a = min((y - d0 + 170) / 170, (d1 + 170 - y) / 200)
    sd.line([(0, y), (W, y)], fill=int(150 * max(0, min(1, a))))
bg = Image.composite(Image.new('RGB', (W, H), (0, 0, 0)), bg, shade)
tmp = tempfile.mkdtemp(); bgp = os.path.join(tmp, 'bg.png'); bg.save(bgp)

pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
    'stream=r_frame_rate:format=duration', '-of', 'default=nw=1:nk=1', inp], capture_output=True, text=True).stdout.split()
fps, dur = pr[0], pr[1]
h = t1 - t0
lay = (f"[1:v]setsar=1,crop=iw:{h}:0:{t0},split[f][mm];"
       f"[mm]format=gray,lut=y='clip((val-74)*4,0,255)'[a];"
       f"[f][a]alphamerge,format=rgba,split[t][s];"
       f"[s]lutrgb=r=0:g=0:b=0:a='clip((val-40)*3,0,255)',scale=iw/4:-2,boxblur=luma_radius=4:alpha_radius=4,scale=1080:{h}[sh];")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', fps, '-t', dur, '-i', bgp, '-i', inp,
    '-filter_complex', lay + "[0]setsar=1,format=yuv420p[bg];"
    f"[bg][sh]overlay=0:{d0}:format=auto[b1];[b1][t]overlay=0:{d0}:format=auto,format=yuv420p[v]",
    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-maxrate', '8M', '-bufsize', '16M', '-c:a', 'copy', '-movflags', '+faststart', out], check=True)
