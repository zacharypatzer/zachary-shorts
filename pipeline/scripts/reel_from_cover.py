#!/usr/bin/env python3
"""9:16 Facebook Reel cover from a finished square cover: removes the baked-in title/artist text,
places the cover low in the frame, extends the top with a blurred copy, redraws artist + title to fit.
usage: reel_from_cover.py cover.jpg out.jpg  (env: TITLE, FONT, FILL_TOP, FILL_BOT, OUTLINE, ART_BOX, TITLE_BOX as x0,y0,x1,y1 fractions)"""
import os, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1:3]
W, H = 1080, 1920
C = cv2.imread(src); n = C.shape[0]
def box(env, d):
    return [float(v) for v in os.environ.get(env, d).split(',')]
hsv = cv2.cvtColor(C, cv2.COLOR_BGR2HSV)
txt = ((hsv[..., 1] > 110) & (hsv[..., 2] > 90) & ((hsv[..., 0] < 12) | (hsv[..., 0] > 165))) | (hsv[..., 2] > 150)
m = np.zeros(C.shape[:2], np.uint8)
for b in (box('ART_BOX', '0.26,0.04,0.74,0.09'), box('TITLE_BOX', '0.06,0.105,0.94,0.205')):
    x0, y0, x1, y1 = [int(v * n) for v in b]
    m[y0:y1, x0:x1] = 255  # whole band: letters plus their dark shadows
clean = cv2.inpaint(C, m, 15, cv2.INPAINT_TELEA)
clean = np.where(m[..., None] > 0, cv2.GaussianBlur(clean, (0, 0), 6), clean)
# take the colour out of the patched band (old letter glow bleeds in) and match the surrounding tone
mf = cv2.GaussianBlur((m > 0).astype(np.float32), (0, 0), 12)[..., None]
ring = cv2.dilate(m, np.ones((61, 61), np.uint8)) & ~cv2.dilate(m, np.ones((15, 15), np.uint8))
tone = C[ring > 0].reshape(-1, 3).astype(np.float32).mean(0)
lum = cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
patched = lum / max(tone.mean(), 1) * tone * 0.85
clean = np.clip(clean * (1 - mf) + patched * mf, 0, 255).astype(np.uint8)
# background: only the strip of scene between the old title and the head, stretched and blurred (no face in it)
tb = box('TITLE_BOX', '0.06,0.105,0.94,0.205')[3]
strip = clean[int((tb + 0.01) * n):int(float(os.environ.get('HEAD_TOP', 0.27)) * n), int(0.1 * n):int(0.9 * n)]
bg = cv2.resize(strip, (W, H), interpolation=cv2.INTER_CUBIC)
bg = cv2.GaussianBlur(bg, (0, 0), 24).astype(np.float32) * 0.6
# sharp cover, scaled up, bottom aligned
S = int(W * 1.25); fg = cv2.resize(clean, (S, S), interpolation=cv2.INTER_AREA).astype(np.float32)
fx = (S - W) // 2; fy = H - S
fg = fg[:, fx:fx + W]
a = np.clip((np.arange(S) - (tb + 0.03) * S) / (0.14 * S), 0, 1)[:, None, None]
img = bg.copy(); img[fy:] = img[fy:] * (1 - a) + fg * a
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
img *= (1 - 0.25 * np.clip((0.40 * H - yy) / (0.40 * H), 0, 1))[..., None]
def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)
def mask(fn):
    mm = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(mm)); return np.asarray(mm, np.float32) / 255
def styled(img, A, ft, fb, outline, ow, top, bot, shadow=0.7):
    Ao = cv2.GaussianBlur(cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))), (0, 0), 0.8)
    sh = cv2.GaussianBlur(np.roll(np.roll(Ao, 10, 0), 6, 1), (0, 0), 9) * shadow
    img = img * (1 - sh[..., None]); img = img * (1 - Ao[..., None]) + hexc(outline) * Ao[..., None]
    t = np.clip((yy - top) / max(1, bot - top), 0, 1)[..., None]
    col = hexc(ft) * (1 - t) + hexc(fb) * t
    gy, gx = np.gradient(cv2.GaussianBlur(A, (0, 0), 3)); col = col + np.clip(-(gx * 0.6 + gy * 0.8) * 9, -1, 1)[..., None] * 80
    return img * (1 - A[..., None]) + np.clip(col, 0, 255) * A[..., None]
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
FONT = os.environ.get('FONT'); lines = os.environ.get('TITLE').split('|')
for sz in range(400, 60, -4):
    f = ImageFont.truetype(FONT, sz)
    if max(d0.textlength(l, font=f) for l in lines) <= W * 0.86: break
y = 0.20 * H + f.size * 0.75
for l in lines:
    w = d0.textlength(l, font=f)
    A = mask(lambda d: d.text(((W - w) / 2, y), l, font=f, fill=255, anchor='ls'))
    img = styled(img, A, os.environ.get('FILL_TOP', '#ff8a8a'), os.environ.get('FILL_BOT', '#c8101c'), os.environ.get('OUTLINE', '#2a0004'), 7, y - f.size * 0.75, y)
    y += f.size * 0.98
fa = ImageFont.truetype(os.environ.get('ART_FONT', FONT), int(os.environ.get('ART_SIZE', 58))); art, sp = 'ZACHARY PATZER', 22
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1); ay = 0.20 * H - 50
def draw_art(d):
    x = (W - wid) / 2
    for c in art: d.text((x, ay), c, font=fa, fill=255, anchor='ls'); x += d.textlength(c, font=fa) + sp
img = styled(img, mask(draw_art), os.environ.get('ART_TOP', '#ffffff'), os.environ.get('ART_BOT', '#b9bec6'), os.environ.get('ART_OUT', '#111111'), 3, ay - 45, ay, 0.5)
cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95]); print(out, f.size)
