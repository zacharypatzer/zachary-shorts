#!/usr/bin/env python3
"""Thumbnail for Unfinished (1280x720): the pen laid level across the watercolor paper, title written below in ink."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
D = '/home/claude/songs/unfinished'
MEDDON = '/home/claude/fonts/gfonts/ofl/meddon/Meddon.ttf'
INTER_B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
INK = np.array([0x47, 0x26, 0x1a], np.float32)       # #1a2647 (BGR)
CORAL = np.array([0x5c, 0x74, 0xe0], np.float32)     # #e0745c (BGR)

src = cv2.imread(f'{D}/cover_x4.png').astype(np.float32)
S = src.shape[0]
nib, cap = np.array([0.24, 0.68]) * S, np.array([0.85, 0.26]) * S
ang = np.degrees(np.arctan2(-(cap[1] - nib[1]), cap[0] - nib[0]))   # pen angle above horizontal
k = 0.86
mid = (nib + cap) / 2
# rotate so the pen is level, then place its centre at (640, 200)
M = cv2.getRotationMatrix2D((float(mid[0]), float(mid[1])), -ang, k)
M[0, 2] += 655 - mid[0]
M[1, 2] += 215 - mid[1]
bg = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
bg = bg + 0.45 * (bg - cv2.GaussianBlur(bg, (0, 0), 2.0))
bg = np.clip(bg * 1.02 + 2, 0, 255)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = 1 - 0.16 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2, 0, 1)
img = bg * vig[..., None]


def mask(fn):
    m = Image.new('L', (W, H), 0)
    fn(ImageDraw.Draw(m))
    return np.asarray(m, np.float32) / 255.0


def ink(img, a, col, strength, seed):
    rng = np.random.default_rng(seed)
    n = cv2.GaussianBlur(rng.random(a.shape).astype(np.float32), (0, 0), 5)
    n = (n - n.min()) / (n.max() - n.min())
    a2 = np.maximum(a, cv2.GaussianBlur(a, (0, 0), 1.3) * 0.5) * strength * (0.88 + 0.12 * n)
    return img * (1 - a2[..., None] * (1 - col / 255.0))


# title
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
title = 'Unfinished'
for sz in range(240, 100, -4):
    f = ImageFont.truetype(MEDDON, sz)
    l, t, r, b = d0.textbbox((0, 0), title, font=f, anchor='ls')
    if r - l <= W - 110:
        break
tx = (W - (r - l)) / 2 - l
ty = 560
a_t = mask(lambda d: d.text((tx, ty), title, font=f, fill=255, anchor='ls', stroke_width=4, stroke_fill=255))
# soft paper glow under the title so the ink sits on clean paper
glow = cv2.GaussianBlur(a_t, (0, 0), 26)
glow = glow / glow.max()
img = img * (1 - 0.35 * glow[..., None]) + 250 * 0.35 * glow[..., None]
img = ink(img, a_t, INK, 0.97, 1)


def spaced(d, x, y, text, f_, sp, center=False):
    if center:
        w = sum(d.textlength(c, font=f_) for c in text) + sp * (len(text) - 1)
        x = (W - w) / 2
    for ch in text:
        d.text((x, y), ch, font=f_, fill=255, anchor='ls')
        x += d.textlength(ch, font=f_) + sp
    return x


fa = ImageFont.truetype(INTER_B, 40)
a_a = mask(lambda d: spaced(d, 0, 668, 'ZACHARY PATZER', fa, 9, center=True))
img = ink(img, a_a, INK, 0.92, 2)
# pill, top-left like the rest of the series
fp = ImageFont.truetype(INTER_SB, 26)
ptxt = 'LYRIC VIDEO  ·  REMASTERED'
tw = sum(d0.textlength(c, font=fp) + 4 for c in ptxt) - 4
X, py = 48, 40
pill = mask(lambda d: d.rounded_rectangle([X, py, X + tw + 44, py + 50], 25, fill=255))
sh = cv2.GaussianBlur(np.roll(pill, 4, 0), (0, 0), 6) * 0.35
img *= (1 - sh[..., None])
img = img * (1 - pill[..., None]) + INK * pill[..., None]
a_p = mask(lambda d: spaced(d, X + 22, py + 35, ptxt, fp, 4))
img = img * (1 - a_p[..., None]) + np.array([248, 248, 252], np.float32) * a_p[..., None]
out = np.clip(img, 0, 255).astype(np.uint8)
cv2.imwrite('/home/claude/out/Unfinished_Thumbnail.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 92])
print('ok', sz, round(ang, 1))
