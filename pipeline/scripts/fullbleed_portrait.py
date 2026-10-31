#!/usr/bin/env python3
"""Story/R Shorts full-frame using his REAL portrait (assets/face_src.jpg), not the upscaled cover.
Fixes the waxy face (cover was blown up ~10x) and the 'phantom' cover-title letters at the top.
Lyric text is lifted from the ORIGINAL card-style Short (git 6b25d7e) by brightness, as in fullbleed.py.

usage: fullbleed_portrait.py ORIG_CARD.mp4 OUT.mp4 STYLE(story|r) "Song Title"
Slow push-in on the photo; song title + name in small caps under the lyrics."""
import subprocess, sys, os, tempfile
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

inp, out = sys.argv[1:3]
style = sys.argv[3] if len(sys.argv) > 3 else 'story'
title = sys.argv[4] if len(sys.argv) > 4 else ''
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

# song title card: small caps, letter-spaced, under the lyrics (static, not zoomed)
ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
if title:
    def spaced(d, y, txt, font, fill, sp):
        ws = [d.textlength(c, font=font) for c in txt]; tw = sum(ws) + sp * (len(txt) - 1)
        x = (W - tw) / 2
        for c, w in zip(txt, ws):
            d.text((x, y), c, font=font, fill=fill); x += w + sp
    f1 = ImageFont.truetype(f'{R}/sysfonts/Inter-SemiBold.otf', 40)
    f2 = ImageFont.truetype(f'{R}/sysfonts/Inter-Medium.otf', 27)
    t1s = title.upper(); sp1 = 5
    while sum(ImageDraw.Draw(ov).textlength(c, font=f1) for c in t1s) + sp1 * len(t1s) > 940:
        f1 = ImageFont.truetype(f'{R}/sysfonts/Inter-SemiBold.otf', f1.size - 2)
    TY = d1 + 30
    sh_ = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for layer_, c1, c2 in ((sh_, (0, 0, 0, 255), (0, 0, 0, 255)), (ov, (232, 190, 120, 255), (225, 215, 200, 235))):
        dd = ImageDraw.Draw(layer_)
        spaced(dd, TY, t1s, f1, c1, sp1)
        spaced(dd, TY + f1.size + 16, 'ZACHARY PATZER', f2, c2, 6)
    sh_ = sh_.filter(ImageFilter.GaussianBlur(7))
    ov = Image.alpha_composite(Image.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 0)), sh_), ov)
ovp = os.path.join(tmp, 'ov.png'); ov.save(ovp)

pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
    'stream=r_frame_rate:format=duration', '-of', 'default=nw=1:nk=1', inp], capture_output=True, text=True).stdout.split()
fps, dur = pr[0], pr[1]
h = t1 - t0
lay = (f"[1:v]setsar=1,crop=iw:{h}:0:{t0},split[f][mm];"
       f"[mm]format=gray,lut=y='clip((val-74)*4,0,255)'[a];"
       f"[f][a]alphamerge,format=rgba,split[t][s];"
       f"[s]lutrgb=r=0:g=0:b=0:a='clip((val-40)*3,0,255)',scale=iw/4:-2,boxblur=luma_radius=4:alpha_radius=4,scale=1080:{h}[sh];")
N = round(float(dur) * eval(fps))
# slow push-in 1.00 -> 1.07, centred a little below middle (on his eyes); 2x source keeps it smooth
zoom = (f"[0]scale=2160:3840:flags=lanczos,zoompan=z='1+0.07*on/{N}':d=1:s={W}x{H}:fps={fps}"
        f":x='iw/2-iw/zoom/2':y='(ih*0.56)-(ih*0.56)/zoom',setsar=1,format=yuv420p[bg];")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', fps, '-t', dur, '-i', bgp, '-i', inp, '-i', ovp,
    '-filter_complex', lay + zoom +
    f"[bg][sh]overlay=0:{d0}:format=auto[b1];[b1][t]overlay=0:{d0}:format=auto[b2];"
    f"[b2][2]overlay=0:0:format=auto,trim=end_frame={N},format=yuv420p[v]",
    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-maxrate', '8M', '-bufsize', '16M', '-c:a', 'copy', '-movflags', '+faststart', out], check=True)
