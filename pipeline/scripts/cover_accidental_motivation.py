#!/usr/bin/env python3
"""Cover for Accidental Motivation: series portrait in the 3 a.m. bedroom scene, Abril Fatface two-line title, moonlight blue.
usage: cover_how_you_come_back.py out.png [clean]"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

D = '/home/claude/zachary-shorts/pipeline'
L = '/home/claude/songs/accidental_motivation'
GF = '/home/claude/zachary-shorts/pipeline/fonts/gfonts'
FONT = f'{GF}/ofl/abrilfatface/AbrilFatface-Regular.ttf'
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
S = 1668
out = sys.argv[1]
SCALE = float(__import__('os').environ.get('SCALE', '1.0'))


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)


# ---- scene: full frame (no zoom) keeps the lion right of his ear and the cape bow left of his head
sc = cv2.imread(__import__('os').environ.get('SRC', f'{L}/scene_src.webp'))
n2 = int(round(SCALE * S))
sc = cv2.resize(sc, (n2, n2), interpolation=cv2.INTER_AREA).astype(np.float32)
x0, y0 = (n2 - S) // 2, (n2 - S) // 2
img = sc[y0:y0 + S, x0:x0 + S].copy()
img = 255 * (img / 255) ** 0.78
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)

# ---- portrait at the series position (same transform the other covers use)
P = cv2.imread(f'{D}/assets/face_src.jpg').astype(np.float32)
mP = cv2.imread(f'{D}/songs/say_thank_you_for_me/matte.png', 0).astype(np.float32) / 255
M = np.load(f'{D}/songs/say_thank_you_for_me/M_face.npy')
# defringe: pull edge colours from inside the matte so the dark original backdrop doesn't halo on the sky
core = cv2.erode((mP > 0.95).astype(np.float32), np.ones((5, 5), np.uint8))
num = cv2.GaussianBlur(P * core[..., None], (0, 0), 4)
den = cv2.GaussianBlur(core, (0, 0), 4)[..., None]
F = num / np.maximum(den, 1e-4)
band = ((mP > 0.02) & (mP < 0.98)).astype(np.float32)
band = cv2.GaussianBlur(cv2.dilate(band, np.ones((7, 7), np.uint8)), (0, 0), 2)[..., None]
P = P * (1 - band) + F * band
Pw = cv2.warpAffine(P, M, (S, S), flags=cv2.INTER_LANCZOS4)
a = cv2.warpAffine(mP, M, (S, S), flags=cv2.INTER_LINEAR)
a = np.clip((a - 0.08) / 0.84, 0, 1)
a = cv2.GaussianBlur(a, (0, 0), 0.8)
# fade the portrait's right frame edge (the hoodie is cut there in the source)
right = M[0, 0] * P.shape[1] + M[0, 2]
a *= np.clip((right - 4 - xx) / 110, 0, 1)
# night light on him: slightly cool overall, with a soft warm phone glow rising from below his chin
Pw = Pw * np.array([1.03, 0.98, 0.93], np.float32)
glow = np.clip((yy - 0.55 * S) / (0.45 * S), 0, 1)[..., None]
Pw = Pw * (1 - 0.10 * glow) + Pw * np.array([0.92, 1.0, 1.10], np.float32) * 0.10 * glow
Pw = Pw * 0.94
img = img * (1 - a[..., None]) + Pw * a[..., None]

# ---- bottom fade + soft vignette like the rest of the series
fade = 1 - 0.5 * np.clip((yy - 0.80 * S) / (0.20 * S), 0, 1) ** 1.4
# the window glare is bright: deepen the top band a touch so the artist line and title hold
fade *= 1 - 0.10 * np.clip((0.36 * S - yy) / (0.36 * S), 0, 1) ** 1.2
vig = 1 - 0.22 * np.clip(((xx - S / 2) / (S * 0.75)) ** 2 + ((yy - S * 0.55) / (S * 0.8)) ** 2, 0, 1)
img *= (fade * vig)[..., None]


def mask(fn):
    m = Image.new('L', (S, S), 0)
    fn(ImageDraw.Draw(m))
    return np.asarray(m, np.float32) / 255.0


def styled(img, A, fill_top, fill_bot, outline, ow, top, bot, shadow=0.65):
    """bevelled title: drop shadow, outline, vertical gradient fill, top-left bevel light."""
    A_out = cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1)))
    A_out = cv2.GaussianBlur(A_out, (0, 0), 0.8)
    sh = cv2.GaussianBlur(np.roll(np.roll(A_out, 10, 0), 6, 1), (0, 0), 9) * shadow
    img = img * (1 - sh[..., None])
    img = img * (1 - A_out[..., None]) + hexc(outline) * A_out[..., None]
    t = np.clip((yy - top) / max(1, bot - top), 0, 1)[..., None]
    col = hexc(fill_top) * (1 - t) + hexc(fill_bot) * t
    hb = cv2.GaussianBlur(A, (0, 0), 3)
    gy, gx = np.gradient(hb)
    bev = np.clip(-(gx * 0.6 + gy * 0.8) * 9, -1, 1)
    col = col + (bev[..., None] * 70)
    return img * (1 - A[..., None]) + np.clip(col, 0, 255) * A[..., None]


if 'clean' in sys.argv[2:]:
    cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8))
    cv2.imwrite(out.replace('_clean.png', '_alpha.png'), np.clip(a * 255, 0, 255).astype(np.uint8))
    print(out, 'clean + alpha'); sys.exit()

# ---- title: two stacked lines
lines = ["ACCIDENTAL", "MOTIVATION"]
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
for sz in range(300, 80, -4):
    f = ImageFont.truetype(FONT, sz)
    ws = [d0.textbbox((0, 0), t, font=f, anchor='ls') for t in lines]
    if max(r - l for l, t, r, b in ws) <= S * 0.74 and max(-t for l, t, r, b in ws) <= 150:
        break
cap = max(-t for l, t, r, b in ws)
bases = [290, 290 + int(cap * 1.22)]
def draw_title(d):
    for t, (l, tt, r, b), y in zip(lines, ws, bases):
        d.text(((S - (r - l)) / 2 - l, y), t, font=f, fill=255, anchor='ls')
A = mask(draw_title)
img = styled(img, A, '#f4f8ff', '#8fb6ff', '#070c1f', 8, bases[0] - cap, bases[1] + 10, 0.8)
# ---- artist line
fa = ImageFont.truetype(INTER_SB, 54)
art, sp = 'ZACHARY PATZER', 20
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)


def draw_art(d):
    x = (S - wid) / 2
    for c in art:
        d.text((x, 112), c, font=fa, fill=255, anchor='ls')
        x += d.textlength(c, font=fa) + sp


img = styled(img, mask(draw_art), '#fffaf1', '#ffe9c8', '#0d1630', 4, 70, 112, 0.55)
img = np.clip(img, 0, 255).astype(np.uint8)
cv2.imwrite(out, img)
print(out, sz, bases)
