#!/usr/bin/env python3
"""Put Zachary's REAL portrait (assets/face_src.jpg) back onto an upscaled song cover, so quick-hook
Shorts don't show the waxy / clay face that comes from blowing the small cover face up ~4x.

Finds where the portrait sits in the square cover (template match over scales), then pastes the
sharp portrait at the same spot on the 4x cover (qh/covers4x/SLUG.png), colour-matched to the cover.

usage: real_face_cover.py SLUG [SLUG ...]   -> qh/covers_real/SLUG.png"""
import sys, os
import numpy as np, cv2

R = os.path.dirname(os.path.abspath(__file__)) + '/..'
src = cv2.imread(f'{R}/assets/face_src.jpg').astype(np.float32)
mat = cv2.imread(f'{R}/assets/face_matte.png', 0)
mat = cv2.resize(mat, (src.shape[1], src.shape[0])).astype(np.float32) / 255
SH, SW = src.shape[:2]
FACE = (250, 120, 830, 820)          # x0, y0, x1, y1 of head+beard in face_src, used for matching
os.makedirs(f'{R}/qh/covers_real', exist_ok=True)


def locate(cover):
    g = cv2.cvtColor(cover, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sg = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    x0, y0, x1, y1 = FACE
    best = (-1, None)
    for s in np.arange(0.35, 0.95, 0.01):
        t = cv2.resize(sg[y0:y1, x0:x1], None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        if t.shape[0] >= g.shape[0] or t.shape[1] >= g.shape[1]:
            continue
        r = cv2.matchTemplate(g, t, cv2.TM_CCOEFF_NORMED)
        _, v, _, loc = cv2.minMaxLoc(r)
        if v > best[0]:
            best = (v, (s, loc[0] - s * x0, loc[1] - s * y0))
    # refine scale in 0.002 steps around the best
    v0, (s0, _, _) = best
    for s in np.arange(s0 - 0.012, s0 + 0.012, 0.002):
        t = cv2.resize(sg[y0:y1, x0:x1], None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        r = cv2.matchTemplate(g, t, cv2.TM_CCOEFF_NORMED)
        _, v, _, loc = cv2.minMaxLoc(r)
        if v > best[0]:
            best = (v, (s, loc[0] - s * x0, loc[1] - s * y0))
    return best


def lab_match(face, ref, w):
    """shift portrait colour (LAB mean/std inside the matte) toward the cover's version of the face"""
    fl = cv2.cvtColor(np.clip(face, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    rl = cv2.cvtColor(np.clip(ref, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    m = w > 0.9
    for c in range(3):
        fm, fs = fl[..., c][m].mean(), fl[..., c][m].std() + 1e-3
        rm, rs = rl[..., c][m].mean(), rl[..., c][m].std() + 1e-3
        k = rs / fs if c == 0 else 1.0       # match contrast on lightness only, keep skin texture
        fl[..., c] = (fl[..., c] - fm) * k + rm
    return cv2.cvtColor(np.clip(fl, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)


for slug in sys.argv[1:]:
    cov = cv2.imread(f'{R}/qh/covers/{slug}.jpg')
    big = cv2.imread(f'{R}/qh/covers4x/{slug}.png').astype(np.float32)
    score, (s, tx, ty) = locate(cov)
    k = big.shape[0] / cov.shape[0]
    M = np.float32([[s * k, 0, tx * k], [0, s * k, ty * k]])
    Wd, Hd = big.shape[1], big.shape[0]
    face = cv2.warpAffine(src, M, (Wd, Hd), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    a = cv2.warpAffine(mat, M, (Wd, Hd), flags=cv2.INTER_LINEAR, borderValue=0)
    a = cv2.erode(a, np.ones((int(6 * k), int(6 * k)), np.uint8))
    a = cv2.GaussianBlur(a, (0, 0), 3 * k)
    face = lab_match(face, big, a)
    blur = cv2.GaussianBlur(face, (0, 0), 1.6)
    face = np.clip(face * 1.35 - blur * 0.35, 0, 255)      # light sharpen
    out = big * (1 - a[..., None]) + face * a[..., None]
    cv2.imwrite(f'{R}/qh/covers_real/{slug}.png', np.clip(out, 0, 255).astype(np.uint8))
    print(f'{slug}: match {score:.3f}  scale {s:.3f}  portrait at {s * k * 1920 / Hd:.2f}x in the Short')
