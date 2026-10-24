#!/usr/bin/env python3
"""Shareable Facebook birthday card (1080x1350) for It's Your Birthday: club scene, no portrait, neon HAPPY BIRTHDAY."""
import numpy as np, cv2, sys
from PIL import Image, ImageDraw, ImageFont
D = '/home/claude/songs/its_your_birthday'; W, H = 1080, 1350
BLACK = '/usr/share/fonts/opentype/inter/Inter-Black.otf'; SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)
sc = cv2.imread(f'{D}/scene_x4.png'); sc = cv2.resize(sc, (H, H), interpolation=cv2.INTER_AREA).astype(np.float32)
x0 = int(0.52 * H - W / 2); img = sc[:, x0:x0 + W].copy()
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
# darken the middle band where the text sits
band = np.exp(-((yy - 0.42 * H) / (0.24 * H)) ** 2)
img *= (1 - 0.45 * band)[..., None]
img *= (1 - 0.35 * np.clip((yy - 0.85 * H) / (0.15 * H), 0, 1))[..., None]
def mask(fn):
    m = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(m)); return np.asarray(m, np.float32) / 255
def styled(img, A, ft, fb, outline, ow, top, bot, glow_col=None, glow=0.0, gs=26):
    A_out = cv2.GaussianBlur(cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))), (0, 0), 0.8)
    if glow:
        g = cv2.GaussianBlur(A_out, (0, 0), gs) * glow; img = img + g[..., None] * hexc(glow_col)
    sh = cv2.GaussianBlur(np.roll(np.roll(A_out, 8, 0), 5, 1), (0, 0), 8) * 0.6
    img = img * (1 - sh[..., None]); img = img * (1 - A_out[..., None]) + hexc(outline) * A_out[..., None]
    t = np.clip((yy - top) / max(1, bot - top), 0, 1)[..., None]
    col = hexc(ft) * (1 - t) + hexc(fb) * t
    gy, gx = np.gradient(cv2.GaussianBlur(A, (0, 0), 3)); col = col + np.clip(-(gx * 0.6 + gy * 0.8) * 9, -1, 1)[..., None] * 60
    return img * (1 - A[..., None]) + np.clip(col, 0, 255) * A[..., None]
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
def fit(text, font, maxw, start):
    for sz in range(start, 20, -2):
        f = ImageFont.truetype(font, sz)
        if d0.textlength(text, font=f) <= maxw: return f
def center(text, f, y):
    w = d0.textlength(text, font=f); return mask(lambda d: d.text(((W - w) / 2, y), text, font=f, fill=255, anchor='ls'))
f1 = fit('HAPPY', BLACK, W * 0.78, 300); f2 = fit('BIRTHDAY!', BLACK, W * 0.86, 300)
y1, y2 = 0.37 * H, 0.37 * H + f2.size * 0.98
img = styled(img, center('HAPPY', f1, y1), '#fff3c4', '#ffb21f', '#3a0640', 9, y1 - f1.size * 0.72, y1, '#ff3fc8', 1.0)
img = styled(img, center('BIRTHDAY!', f2, y2), '#fff3c4', '#ffb21f', '#3a0640', 9, y2 - f2.size * 0.72, y2, '#ff3fc8', 1.0)
f3 = ImageFont.truetype(SB, 46); y3 = y2 + 95
img = styled(img, center("Turn it up. It's your day.", f3, y3), '#ffffff', '#ffe3f6', '#3a0640', 4, y3 - 34, y3, '#5ad7ff', 0.5, 14)
f4 = ImageFont.truetype(SB, 34); y4 = 0.93 * H
img = styled(img, center("It's Your Birthday  ·  Zachary Patzer", f4, y4), '#ffffff', '#ffe3f6', '#1a0420', 3, y4 - 26, y4)
cv2.imwrite(sys.argv[1], np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95]); print(sys.argv[1])
