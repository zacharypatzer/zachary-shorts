#!/usr/bin/env python3
"""9:16 Facebook vertical for What I'm Livin': clean square cover low in the frame, scene sky above, title + artist redrawn."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
L = '/home/claude/songs/what_im_livin'
FONT = '/home/claude/fonts/gfonts/ofl/rubikdirt/RubikDirt-Regular.ttf'
INTER = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
W, H = 1080, 1920
sq = cv2.resize(cv2.imread(f'/home/claude/covers/x4_what_im_livin_clean.png').astype(np.float32), (W, W), interpolation=cv2.INTER_AREA)
y0 = H - W
# top: dark porch-ceiling tone stretched from the cover's top rows and blurred (no mirrored shapes),
# blending into the cover over the last 220 px
B = 140
sky = cv2.GaussianBlur(cv2.resize(sq[:B], (W, y0), interpolation=cv2.INTER_AREA), (0, 0), 40) * 0.8
edge = np.repeat(cv2.GaussianBlur(sq[:12].mean(0, keepdims=True), (0, 0), 40), y0, 0)
d = (y0 - 1 - np.arange(y0)).astype(np.float32)
k = np.clip(d / 120, 0, 1)[:, None, None]
img = np.zeros((H, W, 3), np.float32)
img[:y0] = edge * (1 - k) + sky * k
img[y0:] = sq
# soften the join itself
jb = cv2.GaussianBlur(img[y0 - 40:y0 + 40], (0, 0), 6)
t = (1 - np.abs(np.arange(80) - 40) / 40)[:, None, None]
img[y0 - 40:y0 + 40] = img[y0 - 40:y0 + 40] * (1 - t) + jb * t
yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)
def mask(fn):
    m = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(m)); return np.asarray(m, np.float32) / 255
def styled(img, A, ft, fb, oc, ow, tp, bt, shadow=0.7):
    Ao = cv2.GaussianBlur(cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*ow+1, 2*ow+1))), (0, 0), 0.8)
    sh = cv2.GaussianBlur(np.roll(np.roll(Ao, 8, 0), 5, 1), (0, 0), 7) * shadow
    img = img * (1 - sh[..., None]); img = img * (1 - Ao[..., None]) + hexc(oc) * Ao[..., None]
    k = np.clip((yy - tp) / max(1, bt - tp), 0, 1)[..., None]
    col = hexc(ft) * (1 - k) + hexc(fb) * k
    gy, gx = np.gradient(cv2.GaussianBlur(A, (0, 0), 2.5))
    col = col + np.clip(-(gx*0.6 + gy*0.8)*9, -1, 1)[..., None] * 70
    return img * (1 - A[..., None]) + np.clip(col, 0, 255) * A[..., None]
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
f = ImageFont.truetype(FONT, 170)
y = 560
for line in ['WHAT I\u2019M', 'LIVIN\u2019']:
    l, tt, r, b = d0.textbbox((0, 0), line, font=f, anchor='ls')
    x = (W - (r - l)) / 2 - l
    img = styled(img, mask(lambda d: d.text((x, y), line, font=f, fill=255, anchor='ls')), '#ffeec4', '#e08f2c', '#1e0f05', 7, y + tt, y + 6)
    y += 190
fa = ImageFont.truetype(INTER, 46); art, sp = 'ZACHARY PATZER', 16
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)
def da(d):
    x = (W - wid) / 2
    for c in art: d.text((x, 320), c, font=fa, fill=255, anchor='ls'); x += d.textlength(c, font=fa) + sp
img = styled(img, mask(da), '#fffaf1', '#ffe9c8', '#1e0f05', 4, 285, 320, 0.55)
cv2.imwrite(f'{L}/vertical.jpg', np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 93])
print('ok')
