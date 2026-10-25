#!/usr/bin/env python3
"""9:16 vertical cover (1080x1920) for Light One, Let It Go: night lake full of paper lanterns, Zachary's
portrait centred low, artist line on top, title in Limelight, warm gold to amber. All key content sits
inside the centre 4:5 band so Facebook's feed crop still shows it.
usage: cover_light_one_vertical.py face_src.jpg matte.png out.jpg"""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

face_p, matte_p, out = sys.argv[1:4]
R = os.path.dirname(os.path.abspath(__file__)) + '/..'
FONT = f'{R}/fonts/gfonts/ofl/limelight/Limelight-Regular.ttf'
INTER = f'{R}/sysfonts/Inter-SemiBold.otf'
W, H = 1080, 1920
HZ = 1190                      # horizon line
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def bgr(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)


# ---- sky: deep navy to a violet-blue glow at the horizon
t = np.clip(yy / HZ, 0, 1)[..., None]
img = bgr('#05081a') * (1 - t) ** 1.2 + bgr('#2a2f5e') * (1 - (1 - t) ** 1.2)
# warm haze low in the sky from all the lanterns
img += bgr('#3a2410') * np.exp(-((yy - HZ) / 260) ** 2)[..., None] * 0.9
# stars
for _ in range(500):
    x, y = rng.uniform(0, W), rng.uniform(0, HZ * 0.85)
    b = rng.uniform(40, 200) * (1 - y / HZ)
    cv2.circle(img, (int(x), int(y)), 1, (b, b, b * 1.1), -1, cv2.LINE_AA)

# ---- mountains: two silhouette layers
def ridge(base, amp, freq, seed, col):
    r = np.random.default_rng(seed); x = np.arange(W, dtype=np.float32)
    y = base + sum(amp / k * np.sin(x * freq * k + r.uniform(0, 6.28)) for k in (1, 2.3, 4.7, 9.1))
    m = (yy >= y[None, :]) & (yy < HZ)
    return m, col


for base, amp, freq, seed, col in ((HZ - 150, 90, 0.006, 3, '#141a36'), (HZ - 70, 60, 0.011, 5, '#0b0f22')):
    m, c = ridge(base, amp, freq, seed, col)
    img[m] = bgr(c)

# ---- lake: darker mirror of the sky, slightly blue
sky_ref = cv2.flip(img[2 * HZ - H:HZ], 0) if 2 * HZ - H >= 0 else None
lake = cv2.GaussianBlur(sky_ref, (0, 0), 6) * 0.40 + bgr('#04060f') * 0.60
img[HZ:] = lake

# ---- lanterns (glow layer drawn additively, reflections below the horizon)
glow = np.zeros((H, W, 3), np.float32)
body = np.zeros((H, W, 3), np.float32)
refl = np.zeros((H, W, 3), np.float32)
L = []
for _ in range(170):
    d = rng.uniform(0, 1) ** 1.7                 # 0 far, 1 near
    y = HZ - 20 - (1 - d) * rng.uniform(0, 120) - d * rng.uniform(80, HZ - 60)
    y = HZ - 20 - rng.uniform(0, 1) ** (0.6 + 1.6 * (1 - d)) * (HZ - 80)
    s = 4 + 34 * d ** 1.6
    L.append((rng.uniform(-20, W + 20), y, s, d))
# a few big near ones, kept off the face/title zone
for x, y, s in ((120, 1080, 52), (960, 980, 46), (70, 360, 40), (1000, 300, 34), (900, 1500, 0)):
    if s: L.append((x, y, s, 1.0))
L.sort(key=lambda v: v[3])
for x, y, s, d in L:
    w, h = s, s * 1.25
    pts = np.array([(x - w * 0.42, y - h / 2), (x + w * 0.42, y - h / 2), (x + w * 0.52, y + h / 2), (x - w * 0.52, y + h / 2)], np.int32)
    warm = bgr('#ffb347') * (0.55 + 0.45 * d)
    cv2.fillPoly(body, [pts], warm.tolist(), cv2.LINE_AA)
    cv2.ellipse(body, (int(x), int(y + h * 0.45)), (max(1, int(w * 0.28)), max(1, int(h * 0.08))), 0, 0, 360,
                (bgr('#fff1c8') * (0.6 + 0.4 * d)).tolist(), -1, cv2.LINE_AA)
    cv2.circle(glow, (int(x), int(y)), int(s * 1.6), (bgr('#ff8a2a') * (0.35 + 0.4 * d)).tolist(), -1, cv2.LINE_AA)
    # reflection: broken horizontal shimmer dashes straight below the lantern
    ry0 = 2 * HZ - y
    n_ = int(6 + 10 * d)
    for k in range(n_):
        yk = ry0 + (k - n_ / 2) * (3 + 5 * d) + rng.normal(0, 2)
        if HZ + 2 < yk < H:
            hw = w * rng.uniform(0.2, 0.7) * (1 + 0.3 * d)
            xk = x + rng.normal(0, w * 0.12)
            c = bgr('#ff9a3a') * (0.35 + 0.5 * d) * (1 - abs(k - n_ / 2) / n_)
            cv2.line(refl, (int(xk - hw), int(yk)), (int(xk + hw), int(yk)), c.tolist(), max(1, int(1 + 2 * d)), cv2.LINE_AA)
glow = cv2.GaussianBlur(glow, (0, 0), 14) + cv2.GaussianBlur(glow, (0, 0), 50) * 0.8
body = cv2.GaussianBlur(body, (0, 0), 0.7)
refl = (cv2.GaussianBlur(refl, (0, 0), sigmaX=2.2, sigmaY=1.3) + cv2.GaussianBlur(refl, (0, 0), 10) * 0.6) * 0.7
refl *= (yy > HZ)[..., None]
bm = np.clip(body.max(2, keepdims=True) / 255, 0, 1)
img = img + glow * 0.55 + refl * 0.8
img = img * (1 - bm) + body * bm * 1.05 + glow * 0.1

# ---- portrait, centred low, warm lantern light on him
P = cv2.imread(face_p).astype(np.float32)
a = cv2.imread(matte_p, 0).astype(np.float32) / 255
# defringe edges from inside the matte so the dark source backdrop doesn't halo
core = cv2.erode((a > 0.95).astype(np.float32), np.ones((5, 5), np.uint8))
F = cv2.GaussianBlur(P * core[..., None], (0, 0), 4) / np.maximum(cv2.GaussianBlur(core, (0, 0), 4), 1e-4)[..., None]
band = cv2.GaussianBlur(cv2.dilate(((a > 0.02) & (a < 0.98)).astype(np.float32), np.ones((7, 7), np.uint8)), (0, 0), 2)[..., None]
P = P * (1 - band) + F * band
FS = 860
P = cv2.resize(P, (FS, FS), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (FS, FS), interpolation=cv2.INTER_AREA)
fx, fy = (W - FS) // 2, 735
# warm grade + soft rim from below-left (lanterns)
P = P * np.array([0.93, 1.0, 1.07], np.float32)
ry, rx = np.mgrid[0:FS, 0:FS].astype(np.float32)
P += (bgr('#ff9a3a') * 0.10)[None, None] * np.clip(1 - rx / FS, 0, 1)[..., None]
# fade the hoodie into the lake
a = a * np.clip((FS - 30 - ry) / 170, 0, 1) ** 1.3 * np.clip(np.minimum(rx - 20, FS - 20 - rx) / 90, 0, 1)
reg = img[fy:fy + FS, fx:fx + FS]
# contact shadow behind him
sh = cv2.GaussianBlur(a, (0, 0), 30) * 0.55
reg = reg * (1 - sh[..., None])
img[fy:fy + FS, fx:fx + FS] = reg * (1 - a[..., None]) + P * a[..., None]

# ---- vignette, darker top band for type, darker bottom
vig = 1 - 0.35 * np.clip(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H * 0.55) / (H * 0.75)) ** 2, 0, 1)
top = 1 - 0.30 * np.clip((760 - yy) / 760, 0, 1)
bot = 1 - 0.55 * np.clip((yy - 1600) / 320, 0, 1)
img *= (vig * top * bot)[..., None]


def mask(fn):
    m = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(m)); return np.asarray(m, np.float32) / 255


def styled(img, A, ft, fb, outline, ow, t0, t1, shadow=0.7, bevel=70):
    Ao = cv2.GaussianBlur(cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))), (0, 0), 0.8)
    s = cv2.GaussianBlur(np.roll(np.roll(Ao, 9, 0), 5, 1), (0, 0), 9) * shadow
    img = img * (1 - s[..., None]); img = img * (1 - Ao[..., None]) + bgr(outline) * Ao[..., None]
    tt = np.clip((yy - t0) / max(1, t1 - t0), 0, 1)[..., None]
    col = bgr(ft) * (1 - tt) + bgr(fb) * tt
    gy, gx = np.gradient(cv2.GaussianBlur(A, (0, 0), 3))
    col = col + np.clip(-(gx * 0.6 + gy * 0.8) * 9, -1, 1)[..., None] * bevel
    return img * (1 - A[..., None]) + np.clip(col, 0, 255) * A[..., None]


# soft lantern glow behind the title so it reads warm
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
lines = ['LIGHT ONE,', 'LET IT GO']
for sz in range(240, 60, -2):
    f = ImageFont.truetype(FONT, sz)
    if max(d0.textlength(l, font=f) for l in lines) <= W * 0.86: break
asc = -d0.textbbox((0, 0), 'LIGHT', font=f, anchor='ls')[1]
gap = int(asc * 1.32)
base1 = 470 + asc; base2 = base1 + gap


def draw_title(d):
    for l, b in zip(lines, (base1, base2)):
        w = d0.textlength(l, font=f); d.text(((W - w) / 2, b), l, font=f, fill=255, anchor='ls')


A = mask(draw_title)
halo = cv2.GaussianBlur(A, (0, 0), 28)
img += bgr('#ff8a2a')[None, None] * halo[..., None] * 0.55
img = styled(img, A, '#fff0c2', '#f2952e', '#2a1206', 6, base1 - asc, base2, 0.75)

fa = ImageFont.truetype(INTER, 44)
art, sp = 'ZACHARY PATZER', 16
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)


def draw_art(d):
    x = (W - wid) / 2
    for c in art:
        d.text((x, 420), c, font=fa, fill=255, anchor='ls'); x += d0.textlength(c, font=fa) + sp


img = styled(img, mask(draw_art), '#fff7ea', '#ffe1b8', '#1a0c05', 3, 388, 420, 0.55, 30)
cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
print(out, 'title size', sz)
