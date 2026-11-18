#!/usr/bin/env python3
"""Book 'scene' Short (round 2, Nov 2026): one true moment from a Real Life Series book, told in 3 beats,
then the cover. Hook on screen from frame 1, words pop in, cuts land on the music's beats.
usage: book_scene.py CFG.json OUT.mp4
CFG: {"book":1-3, "audio":path, "a0":sec, "beats":[[big,small],[big,small],[big,small]], "end":[line, small]}
"""
import sys, os, json, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

C = json.load(open(sys.argv[1])); out = sys.argv[2]
book, src, A0 = C['book'], C['audio'], float(C.get('a0', 0))
R = os.path.dirname(os.path.abspath(__file__)) + '/..'
LORA = f'{R}/sysfonts/Lora-Variable.ttf'; INTER = f'{R}/sysfonts/Inter-SemiBold.otf'
GOLD = (232, 190, 120); CREAM = (246, 238, 225); MUTED = (214, 202, 184)
W, H, FPS = 1080, 1920, 30
ACCENT = {1: (190, 40, 36), 2: (70, 105, 185), 3: (130, 165, 215)}
HL = {1: (236, 92, 80), 2: (232, 190, 120), 3: (150, 196, 242)}  # highlight color for the last word of each big line
COVER = Image.open(f'{R}/assets/book_covers/book{book}.jpg').convert('RGB')
TITLES = {1: 'Real Life Happens. Real People Don’t.', 2: 'Things Break. People Rebuild.', 3: 'Figuring Things Out. Walk With Me.'}


def lora(sz, wght=700):
    f = ImageFont.truetype(LORA, sz)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f


def spaced(d, y, s, f, fill, sp):
    w = sum(d.textlength(c, font=f) for c in s) + sp * (len(s) - 1); x = (W - w) / 2
    for c in s: d.text((x, y), c, font=f, fill=fill, anchor='ls'); x += d.textlength(c, font=f) + sp


def wrap(d, words, f, maxw):
    lines, line = [], []
    for w in words:
        if line and d.textlength(' '.join(line + [w]), font=f) > maxw: lines.append(line); line = [w]
        else: line.append(w)
    lines.append(line)
    n = len(lines); mw = maxw   # balance line lengths
    while mw > 420:
        test, line = [], []
        for w in words:
            if line and d.textlength(' '.join(line + [w]), font=f) > mw - 20: test.append(line); line = [w]
            else: line.append(w)
        test.append(line)
        if len(test) != n: break
        lines, mw = test, mw - 20
    return lines


def bg():
    s = COVER.resize((H, int(H * COVER.height / COVER.width)))
    s = s.crop(((s.width - W) // 2, (s.height - H) // 2, (s.width - W) // 2 + W, (s.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(70))
    a = np.asarray(s, np.float32) * 0.36 + np.array((14, 11, 8), np.float32) * 0.5
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (1 - 0.10 * np.abs(yy - H / 2) / (H / 2))[..., None]
    acc = np.array(ACCENT[book], np.float32)   # glows reach every edge so it never reads as a border
    for gx, gy, r, k in [(0.12, 0.03, 420, 0.22), (0.88, 0.10, 380, 0.16), (0.20, 0.97, 440, 0.22), (0.85, 0.92, 400, 0.17),
                         (0.02, 0.5, 320, 0.12), (0.98, 0.55, 320, 0.12), (0.5, 1.02, 300, 0.18)]:
        if book == 1: k *= 1.5   # near-black cover: lift the glows so the bottom never reads as a flat band
        a += (k * np.exp(-((xx - gx * W) ** 2 + (yy - gy * H) ** 2) / (2 * r * r)))[..., None] * acc
    a += np.random.default_rng(7).normal(0, 2.5, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


BG = bg()
LBL = ImageFont.truetype(INTER, 30)
SM_FONT = lora(50, 400)


def beat_card(big, small, nshow, top_label):
    """nshow = how many words of the big line are visible (word pop)."""
    img = BG.copy(); d = ImageDraw.Draw(img)
    spaced(d, 300, top_label, LBL, GOLD, 8)
    fb = lora(92 if len(big) < 40 else 80)
    words = big.split(); lines = wrap(d, words, fb, 940)
    lh = fb.size * 1.18
    sl = wrap(d, small.split(), SM_FONT, 880) if small else []
    total = len(lines) * lh + (40 + 26 + len(sl) * SM_FONT.size * 1.25 if sl else 0)
    y = 820 - total / 2 + fb.size   # block centred a bit above middle, clear of app buttons
    i = 0
    for ln in lines:
        x = (W - d.textlength(' '.join(ln), font=fb)) / 2
        for w in ln:
            if i < nshow:
                col = HL[book] if i == len(words) - 1 else CREAM
                d.text((x + 3, y + 4), w, font=fb, fill=(0, 0, 0), anchor='ls')
                d.text((x, y), w, font=fb, fill=col, anchor='ls')
            x += d.textlength(w + ' ', font=fb); i += 1
        y += lh
    if sl and nshow >= len(words):
        y += 10; d.line((W / 2 - 60, y, W / 2 + 60, y), fill=GOLD, width=4); y += 40
        for ln in sl:
            d.text((W / 2, y + SM_FONT.size * 0.8), ' '.join(ln), font=SM_FONT, fill=MUTED, anchor='ms'); y += SM_FONT.size * 1.25
    return np.asarray(img, np.float32), len(words)


CW = 640; CH = round(CW * COVER.height / COVER.width); CY = 300


def end_card():
    img = BG.copy(); x0 = (W - CW) // 2
    sh = Image.new('L', img.size, 0); ImageDraw.Draw(sh).rectangle((x0 + 10, CY + 26, x0 + CW + 10, CY + CH + 26), fill=200)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(34)))
    d = ImageDraw.Draw(img)
    spaced(d, 240, 'ZACHARY PATZER', LBL, GOLD, 10)
    y = CY + CH + 100
    f1 = lora(58); d.text((W / 2, y), C['end'][0], font=f1, fill=CREAM, anchor='ms'); y += 40
    d.line((W / 2 - 60, y, W / 2 + 60, y), fill=GOLD, width=4); y += 62
    for ln in C['end'][1].split('\n'):
        d.text((W / 2, y), ln, font=lora(42, 400), fill=GOLD, anchor='ms'); y += 56
    return img


# ---- beats from the music (spectral flux + autocorrelation)
SR = 22050
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(A0), '-i', src, '-t', '30', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
x = np.frombuffer(pcm, np.float32); HOP = 512
S = np.abs(np.array([np.fft.rfft(x[i:i + 2048] * np.hanning(2048)) for i in range(0, len(x) - 2048, HOP)]))
flux = np.maximum(np.diff(np.log1p(S), axis=0), 0).sum(1); flux = (flux - flux.mean()) / (flux.std() + 1e-9)
fr = SR / HOP; ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
lo, hi = int(fr * 60 / 160), int(fr * 60 / 60)
per = (lo + np.argmax(ac[lo:hi])) / fr
ph = max(range(int(per * fr)), key=lambda o: flux[o::int(round(per * fr))].sum()) / fr
beats = ph + per * np.arange(200)

want = [3.4, 3.8, 3.8, 4.6]   # hook, beat 2, payoff, cover
cuts, t = [0.0], 0.0
for w in want[:-1]:
    t += w; cuts.append(float(beats[np.argmin(np.abs(beats - t))]))
end = cuts[-1] + want[-1]; cuts.append(end)
print(f'tempo {60 / per:.0f} bpm, cuts', [round(c, 2) for c in cuts])

LABEL = f'BOOK {book}  ·  THE REAL LIFE SERIES'
cache = {}


def card(k, n):
    key = (k, n)
    if key not in cache: cache[key] = beat_card(*C['beats'][k], n, LABEL)
    return cache[key]


NW = [len(b[0].split()) for b in C['beats']]
END = end_card()


def frame(k, t):
    u = (t - cuts[k]) / (cuts[k + 1] - cuts[k]); el = t - cuts[k]
    if k == 3:
        s = 1.0 + 0.04 * u; cw, ch = int(CW * s) // 2 * 2, int(CH * s) // 2 * 2
        im = END.copy(); im.paste(COVER.resize((cw, ch), Image.LANCZOS), ((W - cw) // 2, CY + (CH - ch) // 2))
        return np.asarray(im, np.float32)
    # hook (k=0) is fully on screen from frame 1; later beats pop word by word over ~0.9 s
    n = NW[k] if k == 0 else min(NW[k], 1 + int(el / (0.9 / NW[k])))
    arr, _ = card(k, n)
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 + 0.035 * u)
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


XF = 0.2
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-ss', str(A0), '-i', src, '-map', '0:v', '-map', '1:a', '-t', f'{end:.3f}',
                       '-af', f'afade=t=in:st=0:d=0.1,afade=t=out:st={end - 1.2:.2f}:d=1.2',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                       '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
for n in range(int(round(end * FPS))):
    t = n / FPS; k = min(np.searchsorted(cuts, t, 'right') - 1, 3)
    f = frame(k, t)
    if k > 0 and t - cuts[k] < XF:
        a = (t - cuts[k]) / XF; f = f * a + frame(k - 1, t) * (1 - a)
    ff.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
Image.fromarray(np.clip(frame(0, 0.5), 0, 255).astype(np.uint8)).save(out.replace('.mp4', '_cover.jpg'), quality=92)
print('wrote', out, ff.returncode)
