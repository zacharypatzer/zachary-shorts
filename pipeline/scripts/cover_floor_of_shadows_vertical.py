#!/usr/bin/env python3
"""9:16 vertical cover (1080x1920) for Floor of Shadows: dim hospital corridor in one-point perspective,
cold fluorescent panels, doors with lit blinds, glossy floor, a "4" floor plaque. Portrait centred low,
artist line on top, title in Limelight yellow (matches the thumbnail). Key content inside the centre 4:5 band.
usage: cover_floor_of_shadows_vertical.py face_src.jpg face_matte.png out.jpg"""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

face_p, matte_p, out = sys.argv[1:4]
R = os.path.dirname(os.path.abspath(__file__)) + '/..'
FONT = f'{R}/fonts/gfonts/ofl/limelight/Limelight-Regular.ttf'
INTER = f'{R}/sysfonts/Inter-SemiBold.otf'
W, H = 1080, 1920
rng = np.random.default_rng(11)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def bgr(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)


VX, VY = 540, 700
NX0, NX1, NY0, NY1 = -260, 1340, -420, 2060   # near cross-section (beyond frame)
ZF = 9.0


def P3(x, y, z):  # world (near-plane px) at depth z -> screen
    return (VX + (x - VX) / z, VY + (y - VY) / z)


def quad(pts):
    return np.array([[int(round(a)), int(round(b))] for a, b in pts], np.int32)


img = np.zeros((H, W, 3), np.float32)
# surfaces
far = [P3(NX0, NY0, ZF), P3(NX1, NY0, ZF), P3(NX1, NY1, ZF), P3(NX0, NY1, ZF)]
def surf(poly, col):
    cv2.fillPoly(img, [quad(poly)], col.tolist(), cv2.LINE_AA)
surf([(NX0, NY0), (NX1, NY0), far[1], far[0]], bgr('#1f272d'))   # ceiling
surf([(NX0, NY1), (NX1, NY1), far[2], far[3]], bgr('#252b30'))   # floor
surf([(NX0, NY0), far[0], far[3], (NX0, NY1)], bgr('#2c363c'))   # left wall
surf([(NX1, NY0), far[1], far[2], (NX1, NY1)], bgr('#2a3439'))   # right wall
surf(far, bgr('#4a5862'))                                         # end wall (lit)
# depth falloff: darker near the camera edges, brighter toward the end
dist = np.sqrt(((xx - VX) / 540) ** 2 + ((yy - VY) / 900) ** 2)
img *= np.clip(1.25 - 0.55 * dist, 0.35, 1.3)[..., None]

glow = np.zeros((H, W, 3), np.float32)
# ceiling light panels
for z in (1.25, 1.75, 2.4, 3.2, 4.3, 5.8, 7.6):
    dz = 0.16 * z
    pts = [P3(VX - 260, NY0, z), P3(VX + 260, NY0, z), P3(VX + 260, NY0, z + dz), P3(VX - 260, NY0, z + dz)]
    cv2.fillPoly(glow, [quad(pts)], (bgr('#e6f2ff') * 1.0).tolist(), cv2.LINE_AA)
    # floor reflection
    pts = [P3(VX - 260, NY1, z), P3(VX + 260, NY1, z), P3(VX + 260, NY1, z + dz), P3(VX - 260, NY1, z + dz)]
    cv2.fillPoly(glow, [quad(pts)], (bgr('#bcd4ea') * 0.35).tolist(), cv2.LINE_AA)
# doors with lit blinds on both walls
for side, wx in ((0, NX0), (1, NX1)):
    for z in (1.5, 2.6, 3.9, 5.6):
        z2 = z + 0.45 * z
        top, bot = NY1 - 1500, NY1
        door = [P3(wx, top, z), P3(wx, top, z2), P3(wx, bot, z2), P3(wx, bot, z)]
        cv2.fillPoly(img, [quad(door)], bgr('#161c20').tolist(), cv2.LINE_AA)
        cv2.polylines(img, [quad(door)], True, bgr('#56636c').tolist(), max(1, int(6 / z)), cv2.LINE_AA)
        # window with blinds in upper half
        wt, wb = top + 180, top + 700
        za, zb = z + 0.1 * (z2 - z), z2 - 0.1 * (z2 - z)
        for k in range(14):
            y0 = wt + (wb - wt) * k / 14; y1 = y0 + (wb - wt) / 14 * 0.55
            sl = [P3(wx, y0, za), P3(wx, y0, zb), P3(wx, y1, zb), P3(wx, y1, za)]
            cv2.fillPoly(glow, [quad(sl)], (bgr('#d9e8f5') * (0.75 if side else 0.6)).tolist(), cv2.LINE_AA)
# "4" floor plaque on the right wall
pz0, pz1 = 1.95, 2.15
pl = [P3(NX1, 760, pz0), P3(NX1, 760, pz1), P3(NX1, 1040, pz1), P3(NX1, 1040, pz0)]
cv2.fillPoly(img, [quad(pl)], bgr('#2e3a42').tolist(), cv2.LINE_AA)
cv2.polylines(img, [quad(pl)], True, bgr('#8d9aa3').tolist(), 2, cv2.LINE_AA)
c = np.mean(quad(pl), 0)
_m = Image.new('L', (W, H), 0); ImageDraw.Draw(_m).text((c[0], c[1]), '4', font=ImageFont.truetype(INTER, 52), fill=255, anchor='mm')
_m = np.asarray(_m, np.float32)[..., None] / 255
img = img * (1 - _m) + bgr('#d7dee4') * _m

bloom = cv2.GaussianBlur(glow, (0, 0), 6) + cv2.GaussianBlur(glow, (0, 0), 28) * 0.9 + cv2.GaussianBlur(glow, (0, 0), 90) * 0.6
img = img + glow * 0.9 + bloom * 0.55
# haze at the far end
img += bgr('#9fb4c4')[None, None] * (np.exp(-(((xx - VX) / 220) ** 2 + ((yy - VY) / 260) ** 2)) * 0.25)[..., None] * 0.6
# film grain + dust motes
img += rng.normal(0, 3.0, (H, W, 1)).astype(np.float32)
img = cv2.GaussianBlur(img, (0, 0), 3.0)
img = img * np.array([1.04, 0.98, 0.9], np.float32)   # cold teal grade

# ---- portrait, centred low, warm window light from the right
P = cv2.imread(face_p).astype(np.float32)
a = cv2.imread(matte_p, 0).astype(np.float32) / 255
core = cv2.erode((a > 0.95).astype(np.float32), np.ones((5, 5), np.uint8))
F = cv2.GaussianBlur(P * core[..., None], (0, 0), 4) / np.maximum(cv2.GaussianBlur(core, (0, 0), 4), 1e-4)[..., None]
band = cv2.GaussianBlur(cv2.dilate(((a > 0.02) & (a < 0.98)).astype(np.float32), np.ones((7, 7), np.uint8)), (0, 0), 2)[..., None]
P = P * (1 - band) + F * band
FS = 1080
P = cv2.resize(P, (FS, FS), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (FS, FS), interpolation=cv2.INTER_AREA)
fx, fy = (W - FS) // 2, 840
P = P * np.array([1.04, 1.0, 0.97], np.float32)
ry, rx = np.mgrid[0:FS, 0:FS].astype(np.float32)
P += (bgr('#cfe6ff') * 0.08)[None, None] * np.clip(1 - ry / FS, 0, 1)[..., None]
a = cv2.GaussianBlur(a, (0, 0), 1.2)  # soft edge; bust runs off the bottom and sides so nothing is cut mid-body
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
lines = ['FLOOR OF', 'SHADOWS']
for sz in range(240, 60, -2):
    f = ImageFont.truetype(FONT, sz)
    if max(d0.textlength(l, font=f) for l in lines) <= W * 0.86: break
asc = -d0.textbbox((0, 0), 'FLOOR', font=f, anchor='ls')[1]
gap = int(asc * 1.38)
base1 = 485 + asc; base2 = base1 + gap


def draw_title(d):
    for l, b in zip(lines, (base1, base2)):
        w = d0.textlength(l, font=f); d.text(((W - w) / 2, b), l, font=f, fill=255, anchor='ls')


A = mask(draw_title)
img = styled(img, A, '#fff7a0', '#f2c41a', '#1e1c00', 7, base1 - asc, base2, 0.85)

fa = ImageFont.truetype(INTER, 44)
art, sp = 'ZACHARY PATZER', 16
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)


def draw_art(d):
    x = (W - wid) / 2
    for c in art:
        d.text((x, 430), c, font=fa, fill=255, anchor='ls'); x += d0.textlength(c, font=fa) + sp


img = styled(img, mask(draw_art), '#f4f8ff', '#cfd8e4', '#05070a', 3, 398, 430, 0.55, 30)
cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
print(out, 'title size', sz)
