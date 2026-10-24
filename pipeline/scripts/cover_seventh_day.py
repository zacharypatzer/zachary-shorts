#!/usr/bin/env python3
"""Cover for The Seventh Day: portrait in series position on Zachary's creation-light scene.
usage: cover_seventh_day.py out.png [square|vertical]   (square 1668x1668, vertical 1080x1350 for Facebook)"""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
D = '/home/claude/songs/the_seventh_day'
FONT = os.environ.get('FONT', '/home/claude/fonts/Lora-Variable.ttf')
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
out = sys.argv[1]; mode = sys.argv[2] if len(sys.argv) > 2 else 'square'
S0 = 1668
if mode == 'square':
    W, H, k, dy = S0, S0, 1.0, 0
else:
    W, H = 1080, 1350; k = W / S0; dy = H - W
def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)
sc = cv2.imread(f'{D}/scene_x4.png')
n = max(W, H); sc = cv2.resize(sc, (n, n), interpolation=cv2.INTER_AREA).astype(np.float32)
x0 = (n - W) // 2; img = sc[0:H, x0:x0 + W].copy()
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
P = cv2.imread('/home/claude/songs/unfinished/face_src.jpg').astype(np.float32)
mP = cv2.imread(f'{D}/matte.png', 0).astype(np.float32) / 255
M = np.load(f'{D}/M_face.npy') * k; M[1, 2] += dy
core = cv2.erode((mP > 0.95).astype(np.float32), np.ones((5, 5), np.uint8))
F = cv2.GaussianBlur(P * core[..., None], (0, 0), 4) / np.maximum(cv2.GaussianBlur(core, (0, 0), 4)[..., None], 1e-4)
band = cv2.GaussianBlur(cv2.dilate(((mP > 0.02) & (mP < 0.98)).astype(np.float32), np.ones((7, 7), np.uint8)), (0, 0), 2)[..., None]
P = P * (1 - band) + F * band
Pw = cv2.warpAffine(P, M, (W, H), flags=cv2.INTER_LANCZOS4)
a = cv2.warpAffine(mP, M, (W, H), flags=cv2.INTER_LINEAR)
a = cv2.GaussianBlur(np.clip((a - 0.08) / 0.84, 0, 1), (0, 0), 0.8)
# heavenly light from above: warm top of head, cool shadow lower
lt = np.clip(1 - (yy - (0.35 * H)) / (0.6 * H), 0, 1)[..., None]
Pw = Pw * (np.array([0.97, 1.0, 1.04], np.float32) * (0.92 + 0.12 * lt))
# soft golden rim light on head edge
edge = np.clip(cv2.GaussianBlur(a, (0, 0), 6) - cv2.erode(a, np.ones((9, 9), np.uint8)), 0, 1)
img = img * (1 - a[..., None]) + Pw * a[..., None]
img += (edge * lt[..., 0] * 0.9)[..., None] * hexc('#ffe2a8') * 0.55
fade = 1 - 0.5 * np.clip((yy - 0.80 * H) / (0.20 * H), 0, 1) ** 1.4
fade *= 1 - 0.30 * np.clip((0.30 * H - yy) / (0.30 * H), 0, 1) ** 1.2
vig = 1 - 0.22 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.55) / (H * 0.8)) ** 2, 0, 1)
img *= (fade * vig)[..., None]
def mask(fn):
    m = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(m)); return np.asarray(m, np.float32) / 255.0
def styled(img, A, ft, fb, outline, ow, top, bot, shadow=0.65, glow=0.0):
    A_out = cv2.GaussianBlur(cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))), (0, 0), 0.8)
    if glow:
        g = cv2.GaussianBlur(A_out, (0, 0), 22 * W / S0) * glow
        img = img + g[..., None] * hexc('#ffd88a') * 0.8
    sh = cv2.GaussianBlur(np.roll(np.roll(A_out, 10, 0), 6, 1), (0, 0), 9) * shadow
    img = img * (1 - sh[..., None])
    img = img * (1 - A_out[..., None]) + hexc(outline) * A_out[..., None]
    t = np.clip((yy - top) / max(1, bot - top), 0, 1)[..., None]
    col = hexc(ft) * (1 - t) + hexc(fb) * t
    gy, gx = np.gradient(cv2.GaussianBlur(A, (0, 0), 3))
    col = col + np.clip(-(gx * 0.6 + gy * 0.8) * 9, -1, 1)[..., None] * 70
    return img * (1 - A[..., None]) + np.clip(col, 0, 255) * A[..., None]
u = W / S0
title = 'The Seventh Day'
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
cap = float(os.environ.get('CAP', 200))
for sz in range(int(420 * u), 60, -4):
    f = ImageFont.truetype(FONT, sz)
    try: f.set_variation_by_axes([700])
    except Exception: pass
    l, t, r, b = d0.textbbox((0, 0), title, font=f, anchor='ls')
    if r - l <= W * 0.86 and (-t) <= cap * u: break
base = (int(os.environ.get('BASE', 370)) * u) + (dy * 0.35 if mode != 'square' else 0)
tx = (W - (r - l)) / 2 - l
A = mask(lambda d: d.text((tx, base), title, font=f, fill=255, anchor='ls'))
img = styled(img, A, '#fffdf4', '#f2c35a', '#14203f', max(3, int(7 * u)), base + t, base + b, 0.7, glow=0.9)
fa = ImageFont.truetype(INTER_SB, max(20, int(54 * u))); art, sp = 'ZACHARY PATZER', 20 * u
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)
ay = 112 * u + (dy * 0.12 if mode != 'square' else 0)
def draw_art(d):
    x = (W - wid) / 2
    for c in art:
        d.text((x, ay), c, font=fa, fill=255, anchor='ls'); x += d.textlength(c, font=fa) + sp
img = styled(img, mask(draw_art), '#ffffff', '#ffeccc', '#14203f', max(2, int(4 * u)), ay - 42 * u, ay, 0.55)
cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
print(out, sz)
