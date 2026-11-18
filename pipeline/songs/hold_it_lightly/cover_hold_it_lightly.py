#!/usr/bin/env python3
"""Cover for Hold It Lightly, Love It Hard: series portrait on the sunset-window coffee scene, Yeseva One title, cream to rose-gold.
usage: cover_hold_it_lightly.py out.png [clean]"""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

D = '/home/claude/zachary-shorts/pipeline'
L = '/home/claude/songs/hold_it_lightly'
GF = '/home/claude/zachary-shorts/pipeline/fonts/gfonts'
FONT = '/home/claude/fonts/gfonts/ofl/yesevaone/YesevaOne-Regular.ttf'
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
S = 1668
out = sys.argv[1]
SCALE = float(__import__('os').environ.get('SCALE', '1.15'))


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)


# ---- scene: full frame (no zoom) keeps the lion right of his ear and the cape bow left of his head
sc = cv2.imread(__import__('os').environ.get('SRC', f'{L}/scene_src.jpg'))
n2 = int(round(SCALE * S))
sc = cv2.resize(sc, (n2, n2), interpolation=cv2.INTER_AREA).astype(np.float32)
x0, y0 = n2 - S, (n2 - S) // 2  # crop from the right edge: slides the mug left, clear of his beard
img = sc[y0:y0 + S, x0:x0 + S].copy()
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)

# ---- portrait at the series position (same transform the other covers use)
P = cv2.imread(f'{L}/face_hi.jpg').astype(np.float32)  # his full-res portrait (1932px) for a sharper, truer face
mP = cv2.imread(f'{D}/songs/say_thank_you_for_me/matte.png', 0).astype(np.float32) / 255
M = np.load(f'{D}/songs/say_thank_you_for_me/M_face.npy').copy()
k = 1079 / P.shape[1]
M[:, :2] *= k  # same placement, mapped from the hi-res photo
mP = cv2.resize(mP, (P.shape[1], P.shape[0]), interpolation=cv2.INTER_LINEAR)
# the stock matte shaved a notch out of the left jaw beard; add the beard back out to its real edge (hi-res photo coords)
_pts = np.array([[440, 1120], [425, 1160], [432, 1210], [440, 1250], [446, 1300], [450, 1350], [465, 1400], [480, 1430], [620, 1430], [620, 1120]], np.int32)
_fill = np.zeros_like(mP); cv2.fillPoly(_fill, [_pts], 1.0)
mP = np.maximum(mP, cv2.GaussianBlur(_fill, (0, 0), 5))
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
# warm morning light on him, to sit in the sunrise coming through the window
Pw = Pw * np.array([0.98, 1.0, 1.03], np.float32)  # lighter warm touch so skin stays true to his photo
# warm sunset rim light on his outline (the sun is behind him): makes the beard edge read against the dark window/plant
rim = np.clip(a * (1 - cv2.GaussianBlur(a, (0, 0), 14)) * 2.4, 0, 1)
rim = cv2.GaussianBlur(rim, (0, 0), 2) * np.clip((yy - 0.40 * S) / (0.12 * S), 0, 1)  # jaw/beard down, not the scalp
Pw = Pw + rim[..., None] * np.array([50, 90, 145], np.float32)
img = img * (1 - a[..., None]) + Pw * a[..., None]

# ---- bottom fade + soft vignette like the rest of the series
fade = 1 - 0.5 * np.clip((yy - 0.80 * S) / (0.20 * S), 0, 1) ** 1.4
# the window glare is bright: deepen the top band a touch so the artist line and title hold
fade *= 1 - 0.28 * np.clip((0.36 * S - yy) / (0.36 * S), 0, 1) ** 1.2
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

# ---- title: two lines, the song's full name; second line sits above the top of his head
d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
def fit(txt, maxw, maxh):
    for sz in range(400, 60, -2):
        f = ImageFont.truetype(FONT, sz)
        l, t, r, b = d0.textbbox((0, 0), txt, font=f, anchor='ls')
        if r - l <= maxw and (-t) <= maxh:
            return f, (l, t, r, b)
f1, (l1, t1, r1, b1) = fit("HOLD IT LIGHTLY", S * 0.86, 150)
f2, (l2, t2, r2, b2) = fit("LOVE IT HARD", S * 0.62, 118)
base1, base2 = 300, 440
A1 = mask(lambda d: d.text(((S - (r1 - l1)) / 2 - l1, base1), "HOLD IT LIGHTLY", font=f1, fill=255, anchor='ls'))
img = styled(img, A1, '#fff5ea', '#f0a07e', '#2b1210', 8, base1 + t1, base1 + 10, 0.75)
A2 = mask(lambda d: d.text(((S - (r2 - l2)) / 2 - l2, base2), "LOVE IT HARD", font=f2, fill=255, anchor='ls'))
img = styled(img, A2, '#fff5ea', '#f0a07e', '#2b1210', 7, base2 + t2, base2 + 10, 0.75)
sz = (f1.size, f2.size)
# ---- artist line
fa = ImageFont.truetype(INTER_SB, 54)
art, sp = 'ZACHARY PATZER', 20
wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)


def draw_art(d):
    x = (S - wid) / 2
    for c in art:
        d.text((x, 112), c, font=fa, fill=255, anchor='ls')
        x += d.textlength(c, font=fa) + sp


img = styled(img, mask(draw_art), '#fffaf1', '#ffe6c4', '#2a1406', 4, 70, 112, 0.55)
img = np.clip(img, 0, 255).astype(np.uint8)
cv2.imwrite(out, img)
print(out, sz)
