#!/usr/bin/env python3
"""9:16 vertical cover (1080x1920) for Remember Me When I'm Gone: a quiet old room, afternoon light through a
window, picture frames on the wall, dust in the light. Portrait centred low, artist line on top, title in
Playfair Display SC, ivory to soft gold. Key content stays inside the centre 4:5 band for Facebook's feed crop.
usage: cover_remember_me_vertical.py face_src.jpg face_matte.png out.jpg"""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

face_p, matte_p, out = sys.argv[1:4]
R = os.path.dirname(os.path.abspath(__file__)) + '/..'
FONT = f'{R}/fonts/gfonts/ofl/playfairdisplaysc/PlayfairDisplaySC-Black.ttf'
INTER = f'{R}/sysfonts/Inter-SemiBold.otf'
W, H = 1080, 1920
FLOOR = 1500
rng = np.random.default_rng(11)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def bgr(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)


# ---- back wall: warm plaster, lit from the right
t = np.clip(yy / FLOOR, 0, 1)[..., None]
img = bgr('#1e1812') * (1 - t) + bgr('#54442f') * t
img = img * (0.55 + 0.6 * np.clip(xx / W, 0, 1) ** 1.3)[..., None]
noise = cv2.GaussianBlur(rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32), (0, 0), 3)
noise = cv2.resize(noise, (W, H)) * 9 + cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1) * 3
img += noise[..., None]
# wainscot line
cv2.line(img, (0, 1260), (W, 1260), (bgr('#16110c')).tolist(), 6, cv2.LINE_AA)

# ---- window (right), bright, with mullions and a sheer curtain edge
wx0, wy0, wx1, wy1 = 700, 240, 1080, 1060
win = np.zeros((H, W), np.float32)
cv2.rectangle(win, (wx0, wy0), (wx1, wy1), 1.0, -1)
lightcol = bgr('#fff1d2')
glowwin = cv2.GaussianBlur(win, (0, 0), 60)
img = img + bgr('#ffcf8a')[None, None] * glowwin[..., None] * 0.55
img = img * (1 - win[..., None]) + lightcol * 0.95 * win[..., None]
for x in (wx0, 890, wx1 - 4):
    cv2.line(img, (x, wy0), (x, wy1), bgr('#2b2016').tolist(), 16, cv2.LINE_AA)
for y in (wy0, 520, 800, wy1):
    cv2.line(img, (wx0, y), (wx1, y), bgr('#2b2016').tolist(), 16, cv2.LINE_AA)
# curtain: soft vertical folds over the left part of the window
cur = np.zeros((H, W), np.float32)
pts = np.array([(wx0 - 40, wy0 - 60), (wx0 + 120, wy0 - 60), (wx0 + 90, wy1 + 40), (wx0 - 60, wy1 + 60)], np.int32)
cv2.fillPoly(cur, [pts], 1.0)
cur = cv2.GaussianBlur(cur, (0, 0), 6)
fold = (0.75 + 0.25 * np.sin(xx * 0.09))[..., None]
img = img * (1 - cur[..., None] * 0.8) + bgr('#e6d6bc') * fold * cur[..., None] * 0.8

# ---- picture frames on the left wall
for (x0, y0, w, h) in ((60, 120, 210, 260), (310, 170, 150, 190)):
    cv2.rectangle(img, (x0, y0), (x0 + w, y0 + h), bgr('#2a1f15').tolist(), -1)
    cv2.rectangle(img, (x0 + 16, y0 + 16), (x0 + w - 16, y0 + h - 16), bgr('#6f5c45').tolist(), -1)
    cv2.rectangle(img, (x0 + 28, y0 + 28), (x0 + w - 28, y0 + h - 28), bgr('#3d3226').tolist(), -1)

# ---- floor: planks in perspective, light patch from the window
fl = np.zeros((H, W, 3), np.float32)
ft = np.clip((yy - FLOOR) / (H - FLOOR), 0, 1)
fl[:] = (bgr('#2c2014')[None, None] * (1 - ft[..., None]) + bgr('#3e2d1b')[None, None] * ft[..., None])
vx = W * 0.55
for k in range(-14, 15):
    xb = vx + k * 140
    cv2.line(fl, (int(vx + k * 22), FLOOR), (int(xb), H), bgr('#22180f').tolist(), 2, cv2.LINE_AA)
img = np.where((yy >= FLOOR)[..., None], fl, img)
cv2.line(img, (0, FLOOR), (W, FLOOR), bgr('#120d08').tolist(), 10, cv2.LINE_AA)
patch = np.zeros((H, W), np.float32)
cv2.fillPoly(patch, [np.array([(560, FLOOR + 30), (980, FLOOR + 30), (1080, H), (380, H)], np.int32)], 1.0)
img += bgr('#ffcf8a')[None, None] * cv2.GaussianBlur(patch, (0, 0), 30)[..., None] * 0.35

# ---- light shafts from the window down-left, with dust
shaft = np.zeros((H, W), np.float32)
for (a0, a1) in ((0, 0.6), (0.7, 1.0)):
    p = np.array([(wx0 + (wx1 - wx0) * a0, wy0), (wx0 + (wx1 - wx0) * a1, wy0),
                  (wx0 + (wx1 - wx0) * a1 - 720, FLOOR + 200), (wx0 + (wx1 - wx0) * a0 - 720, FLOOR + 200)], np.int32)
    cv2.fillPoly(shaft, [p], 1.0)
shaft = cv2.GaussianBlur(shaft, (0, 0), 40) * (1 - win)
img += bgr('#ffd9a0')[None, None] * shaft[..., None] * 0.28
dust = np.zeros((H, W), np.float32)
for _ in range(260):
    x, y = rng.uniform(0, W), rng.uniform(150, FLOOR)
    cv2.circle(dust, (int(x), int(y)), int(rng.choice([1, 1, 2])), rng.uniform(0.2, 0.7), -1, cv2.LINE_AA)
dust = cv2.GaussianBlur(dust, (0, 0), 0.9) * shaft * 2.2
img += bgr('#fff1d6')[None, None] * np.clip(dust, 0, 1)[..., None] * 90

# soft focus on the room so he stands out
img = cv2.GaussianBlur(img, (0, 0), 3.5)

# ---- portrait, centred low, warm window light from the right
P = cv2.imread(face_p).astype(np.float32)
a = cv2.imread(matte_p, 0).astype(np.float32) / 255
core = cv2.erode((a > 0.95).astype(np.float32), np.ones((5, 5), np.uint8))
F = cv2.GaussianBlur(P * core[..., None], (0, 0), 4) / np.maximum(cv2.GaussianBlur(core, (0, 0), 4), 1e-4)[..., None]
band = cv2.GaussianBlur(cv2.dilate(((a > 0.02) & (a < 0.98)).astype(np.float32), np.ones((7, 7), np.uint8)), (0, 0), 2)[..., None]
P = P * (1 - band) + F * band
FS = 860
P = cv2.resize(P, (FS, FS), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (FS, FS), interpolation=cv2.INTER_AREA)
fx, fy = (W - FS) // 2, 735
P = P * np.array([0.92, 1.0, 1.06], np.float32)
ry, rx = np.mgrid[0:FS, 0:FS].astype(np.float32)
P += (bgr('#ffcf8a') * 0.10)[None, None] * np.clip(rx / FS, 0, 1)[..., None]
a = a * np.clip((FS - 30 - ry) / 170, 0, 1) ** 1.3 * np.clip(np.minimum(rx - 20, FS - 20 - rx) / 90, 0, 1)
reg = img[fy:fy + FS, fx:fx + FS]
sh = cv2.GaussianBlur(a, (0, 0), 30) * 0.55
reg = reg * (1 - sh[..., None])
img[fy:fy + FS, fx:fx + FS] = reg * (1 - a[..., None]) + P * a[..., None]

# ---- vignette, darker top band for type, darker bottom
vig = 1 - 0.38 * np.clip(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H * 0.55) / (H * 0.75)) ** 2, 0, 1)
top = 1 - 0.35 * np.clip((780 - yy) / 780, 0, 1)
bot = 1 - 0.65 * np.clip((yy - 1560) / 360, 0, 1) ** 0.8
img *= (vig * top * bot)[..., None]


def mask(fn):
    m = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(m)); return np.asarray(m, np.float32) / 255


def styled(img, A, ft, fb, outline, ow, t0, t1, shadow=0.7, bevel=60):
    Ao = cv2.GaussianBlur(cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))), (0, 0), 0.8)
    s = cv2.GaussianBlur(np.roll(np.roll(Ao, 9, 0), 5, 1), (0, 0), 9) * shadow
    img = img * (1 - s[..., None]); img = img * (1 - Ao[..., None]) + bgr(outline) * Ao[..., None]
    tt = np.clip((yy - t0) / max(1, t1 - t0), 0, 1)[..., None]
    col = bgr(ft) * (1 - tt) + bgr(fb) * tt
    gy, gx = np.gradient(cv2.GaussianBlur(A, (0, 0), 3))
    col = col + np.clip(-(gx * 0.6 + gy * 0.8) * 9, -1, 1)[..., None] * bevel
    return img * (1 - A[..., None]) + np.clip(col, 0, 255) * A[..., None]


d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
lines = ['REMEMBER ME', "WHEN I’M GONE"]
for sz in range(240, 60, -2):
    f = ImageFont.truetype(FONT, sz)
    if max(d0.textlength(l, font=f) for l in lines) <= W * 0.88: break
asc = -d0.textbbox((0, 0), 'REMEMBER', font=f, anchor='ls')[1]
gap = int(asc * 1.38)
base1 = 485 + asc; base2 = base1 + gap


def draw_title(d):
    for l, b in zip(lines, (base1, base2)):
        w = d0.textlength(l, font=f); d.text(((W - w) / 2, b), l, font=f, fill=255, anchor='ls')


A = mask(draw_title)
img = styled(img, A, '#fffaf0', '#e6c387', '#22160c', 6, base1 - asc, base2, 0.8)

fa = ImageFont.truetype(INTER, 44)
art, sp = 'ZACHARY PATZER', 16
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)


def draw_art(d):
    x = (W - wid) / 2
    for c in art:
        d.text((x, 430), c, font=fa, fill=255, anchor='ls'); x += d0.textlength(c, font=fa) + sp


img = styled(img, mask(draw_art), '#fff7ea', '#ecdcc4', '#140d07', 3, 398, 430, 0.55, 30)
cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
print(out, 'title size', sz)
