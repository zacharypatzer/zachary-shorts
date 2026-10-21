#!/usr/bin/env python3
"""Cover for Unfinished in the series system: Zachary's portrait (same placement as every cover) on the
sunrise-journal scene, artist line on top, title in its own font and colour.
usage: cover_unfinished.py FONTKEY out.png"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

D = '/home/claude/songs/unfinished'
GF = '/home/claude/fonts/gfonts'
FONTS = {'dafoe': f'{GF}/ofl/mrdafoe/MrDafoe-Regular.ttf', 'meddon': f'{GF}/ofl/meddon/Meddon.ttf'}
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
S = 1668
key, out = sys.argv[1], sys.argv[2]


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)


# ---- scene: scaled 1.2x so the pen and ink blot sit beside his shoulder and a flying page beside his head
sc = cv2.imread(f'{D}/scene_x4.png')
n2 = int(round(1.2 * S))
sc = cv2.resize(sc, (n2, n2), interpolation=cv2.INTER_AREA).astype(np.float32)
x0, y0 = int(0.67 * n2 - 0.80 * S), int(0.68 * n2 - 0.70 * S)
img = sc[y0:y0 + S, x0:x0 + S].copy()
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)

# ---- portrait at the series position (same transform the other covers use)
P = cv2.imread(f'{D}/face_src.jpg').astype(np.float32)
mP = cv2.imread(f'{D}/matte.png', 0).astype(np.float32) / 255
M = np.load(f'{D}/M_face.npy')
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
# warm morning light on him, to sit in the sunrise
Pw = Pw * np.array([0.97, 1.0, 1.04], np.float32)
img = img * (1 - a[..., None]) + Pw * a[..., None]

# ---- bottom fade + soft vignette like the rest of the series
fade = 1 - 0.5 * np.clip((yy - 0.80 * S) / (0.20 * S), 0, 1) ** 1.4
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


if 'clean' in sys.argv[3:]:
    cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8)); print(out, 'clean'); sys.exit()

# ---- title
title = 'Unfinished'
fp = FONTS[key]
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
for sz in range(400, 100, -4):
    f = ImageFont.truetype(fp, sz)
    l, t, r, b = d0.textbbox((0, 0), title, font=f, anchor='ls')
    if r - l <= S * 0.78 and (-t) <= 270:
        break
l, t, r, b = d0.textbbox((0, 0), title, font=f, anchor='ls')
base = 362 if key == 'dafoe' else 350
tx = (S - (r - l)) / 2 - l
A = mask(lambda d: d.text((tx, base), title, font=f, fill=255, anchor='ls', stroke_width=(2 if key == 'meddon' else 0), stroke_fill=255))
img = styled(img, A, '#fffaf1', '#ffbf9c', '#1a2647', 7, base + t, base + 20)

# ---- artist line
fa = ImageFont.truetype(INTER_SB, 54)
art, sp = 'ZACHARY PATZER', 20
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)


def draw_art(d):
    x = (S - wid) / 2
    for c in art:
        d.text((x, 112), c, font=fa, fill=255, anchor='ls')
        x += d.textlength(c, font=fa) + sp


img = styled(img, mask(draw_art), '#fffaf1', '#ffe2cf', '#1a2647', 4, 70, 112, 0.5)
img = np.clip(img, 0, 255).astype(np.uint8)
cv2.imwrite(out, img)
print(out, key, sz)
