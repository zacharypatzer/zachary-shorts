#!/usr/bin/env python3
"""Music-video style renderer (test style, Oct 2026).

Dusk desert road that slowly rolls toward the viewer (walking pace), Zachary's portrait in a circle
with a radial beat visualizer, and kinetic word-by-word lyrics.

usage:
  render_mv.py SLUG --stills t1 t2 ...          # PNG stills into songs/SLUG/mv_still_*.png
  render_mv.py SLUG out.mp4 [--range a b]       # video only (mux audio afterwards)
"""
import sys, os, json, math, subprocess, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import scipy.io.wavfile as wavfile

W, H, FPS = 1080, 1920, 30
SLUG = sys.argv[1]
D = f'/home/claude/songs/{SLUG}'
CFG = json.load(open(f'{D}/cfg.json'))
DUR = float(CFG['dur'])
TITLE = CFG['title']

F_SLAB = '/home/claude/fonts/gfonts/ofl/alfaslabone/AlfaSlabOne-Regular.ttf'
INTER_B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
INTER_M = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
FACE = '/home/claude/zachary-shorts/pipeline/assets/face_src.jpg'


def bgr(rgb):
    return np.array(rgb[::-1], np.float32)


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


# ---------------------------------------------------------------- scene geometry
HZ = 1075            # horizon line
VX = 540             # vanishing point x
FOC = 700.0          # focal length (px)
CAMH = 1.7           # eye height (m)
CAMX = 1.6           # walking in the right lane
SPEED = 1.8          # m/s: a slow walk, so the road just rolls by
ROAD = 3.4           # road half width
POLE_X, POLE_GAP, POLE_H = 6.5, 50.0, 8.5
POST_X, POST_GAP = 3.95, 25.0

# UI layout
PCX, PCY, PR = 540, 640, 188     # portrait circle
NB = 40                           # visualizer bands per side
LY = 1452                         # lyric block centre
LZ0, LZ1 = LY - 300, LY + 300     # lyric compositing window
FS, ROW_H, MAXW = 74, 92, 950
BAR_Y, BAR_X0, BAR_X1 = 1806, 170, 910

ACCENT = (255, 200, 103)          # warm gold (RGB)
PROFK = (1 - 0.72 * np.exp(-((np.arange(H) - LY) / 230.0) ** 2)).astype(np.float32)   # keep road paint quiet under the lyrics
TITLE_COL = (92, 186, 255)        # series light blue (matches the thumbnail)


def proj(x, h, z):
    return VX + FOC * (x - CAMX) / z, HZ + FOC * (CAMH - h) / z


def poly(pts):
    return np.round(np.array(pts, np.float64) * 16).astype(np.int32).reshape(-1, 1, 2)


def fill(mask, pts, v=255):
    cv2.fillPoly(mask, [poly(pts)], int(v), lineType=cv2.LINE_AA, shift=4)


# ---------------------------------------------------------------- audio analysis
def analyse_audio():
    sr, d = wavfile.read(f'{D}/mono44.wav')
    d = d.astype(np.float32) / 32768.0
    N = 4096
    n = int(math.ceil(DUR * FPS)) + 2
    hop = sr / FPS
    pad = np.concatenate([np.zeros(N), d, np.zeros(N * 2)]).astype(np.float32)
    win = np.hanning(N).astype(np.float32)
    freqs = np.fft.rfftfreq(N, 1 / sr)
    edges = np.geomspace(55, 11000, NB + 1)
    samp = np.array([np.geomspace(edges[j], edges[j + 1], 6) for j in range(NB)])  # NB x 6
    bands = np.zeros((n, NB), np.float32)
    rms = np.zeros(n, np.float32)
    for c0 in range(0, n, 600):
        idx = (np.arange(c0, min(c0 + 600, n)) * hop).astype(np.int64) + N // 2
        seg = np.stack([pad[i:i + N] for i in idx])
        rms[c0:c0 + len(idx)] = np.sqrt(np.mean(seg[:, N // 2 - 735:N // 2 + 735] ** 2, axis=1))
        p = np.abs(np.fft.rfft(seg * win, axis=1)) ** 2
        for j in range(NB):
            lo, hi = np.searchsorted(freqs, edges[j]), np.searchsorted(freqs, edges[j + 1])
            hi = max(hi, lo + 1)
            bands[c0:c0 + len(idx), j] = p[:, lo:hi].mean(axis=1) if hi - lo > 1 else \
                np.array([np.interp(samp[j], freqs, row).mean() for row in p])
    db = 10 * np.log10(bands + 1e-10)
    lo = np.percentile(db, 30, axis=0)
    hi = np.percentile(db, 99.7, axis=0)
    g = np.clip((db - lo) / (hi - lo + 1e-6), 0, 1) ** 1.8
    # local contrast: how far each band sits above its own last ~1.5 s, so the bars keep dancing in loud choruses
    from scipy.ndimage import uniform_filter1d
    mm = uniform_filter1d(db, 45, axis=0, mode='nearest')
    loc = np.clip((db - mm + 1.5) / 9.0, 0, 1)
    v = np.clip(0.35 * g + 0.8 * loc * (0.25 + 0.75 * g), 0, 1)
    # spread across neighbouring bands a little
    v = np.apply_along_axis(lambda r: np.convolve(r, [0.2, 0.6, 0.2], 'same'), 1, v)
    out = np.zeros_like(v)
    cur = np.zeros(NB, np.float32)
    for i in range(n):
        k = np.where(v[i] > cur, 0.65, 0.16)
        cur = cur + k * (v[i] - cur)
        out[i] = cur
    bass_raw = v[:, :5].mean(axis=1)
    bass = np.zeros(n, np.float32)
    b = 0
    for i in range(n):
        b = b + (0.7 if bass_raw[i] > b else 0.10) * (bass_raw[i] - b)
        bass[i] = b
    e = np.zeros(n, np.float32)
    x = 0
    for i in range(n):
        x = x + (0.4 if rms[i] > x else 0.05) * (rms[i] - x)
        e[i] = x
    e = np.clip((e - np.percentile(e, 5)) / (np.percentile(e, 98) - np.percentile(e, 5) + 1e-9), 0, 1)
    return out, bass, e


# ---------------------------------------------------------------- static background
def build_background():
    rng = np.random.default_rng(11)
    img = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    # sky
    stops = [(0.00, (5, 9, 24)), (0.40, (12, 26, 60)), (0.70, (28, 56, 104)), (0.86, (58, 82, 128)),
             (0.94, (130, 104, 112)), (0.985, (214, 132, 78)), (1.0, (240, 150, 74))]
    ts = np.array([s[0] for s in stops]) * HZ
    for c in range(3):
        col = np.interp(np.arange(HZ), ts, [s[1][2 - c] for s in stops]).astype(np.float32)
        img[:HZ, :, c] = col[:, None]
    # afterglow off to the right of the road
    g = np.exp(-((xx[:HZ] - 760) / 520) ** 2 - ((yy[:HZ] - HZ) / 190) ** 2)
    img[:HZ] += g[..., None] * bgr((120, 62, 20))
    g2 = np.exp(-((xx[:HZ] - 760) / 900) ** 2 - ((yy[:HZ] - HZ) / 520) ** 2)
    img[:HZ] += g2[..., None] * bgr((30, 26, 40))

    # milky way: faint diagonal band, upper right to mid left
    nz = rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32)
    nz = cv2.GaussianBlur(nz, (0, 0), 2.2) * 0.6 + cv2.GaussianBlur(rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32), (0, 0), 6) * 1.6
    nz = cv2.resize(nz, (W, H), interpolation=cv2.INTER_CUBIC)
    # line through (1080, 80) and (0, 760)
    dx, dy = -1080.0, 680.0
    L = math.hypot(dx, dy)
    dist = np.abs((xx - 1080) * dy - (yy - 80) * dx) / L
    band = np.exp(-(dist / 150) ** 2) * smooth((HZ - 220 - yy) / 300)
    mw = np.clip(0.55 + 0.45 * nz, 0, 1.6) * band
    img += mw[..., None] * bgr((70, 72, 100))

    # stars (static part)
    N = 900
    sy = (HZ - 120) * rng.uniform(0, 1, N) ** 1.35
    sx = rng.uniform(0, W, N)
    # extra stars inside the milky way
    k = 500
    t = rng.uniform(0.05, 0.95, k)
    mx, my = 1080 + dx * t, 80 + dy * t
    off = rng.normal(0, 90, k)
    sx = np.concatenate([sx, mx + off * dy / L])
    sy = np.concatenate([sy, my - off * dx / L])
    keep = (sy > 0) & (sy < HZ - 110) & (sx > 0) & (sx < W)
    sx, sy = sx[keep], sy[keep]
    br = rng.uniform(0.15, 1.0, len(sx)) ** 2.2 * (1 - sy / HZ) ** 0.6
    rr = rng.choice([0.55, 0.8, 1.2], len(sx), p=[0.6, 0.3, 0.1])
    star = np.zeros((H, W), np.float32)
    for x, y, b, r in zip(sx, sy, br, rr):
        x0, y0 = int(x) - 3, int(y) - 3
        gy, gx = np.mgrid[y0:y0 + 7, x0:x0 + 7].astype(np.float32)
        spr = np.exp(-((gx - x) ** 2 + (gy - y) ** 2) / (2 * r * r))
        y1, x1 = min(y0 + 7, H), min(x0 + 7, W)
        if x0 < 0 or y0 < 0:
            continue
        star[y0:y1, x0:x1] += spr[:y1 - y0, :x1 - x0] * b
    img += np.clip(star, 0, 1.2)[..., None] * bgr((235, 240, 255))

    # mountains
    x = np.arange(W, dtype=np.float32)
    walk = np.cumsum(rng.normal(0, 1, W + 400)).astype(np.float32)
    walk = cv2.GaussianBlur(walk[None, :], (0, 0), 18)[0][200:200 + W]
    walk = (walk - walk.mean()) / (walk.std() + 1e-6)
    far = 40 + 18 * np.sin(x / 120 + 0.7) + 10 * np.sin(x / 47 + 2.1) + 9 * walk
    far = np.clip(far + 26 * np.exp(-((x - 230) / 140) ** 2) + 14 * np.exp(-((x - 930) / 110) ** 2), 10, 95)
    near = np.clip(14 + 7 * np.sin(x / 63 + 1.4) + 5 * np.sin(x / 19) + 3 * walk, 3, 34)
    rows = np.arange(H, dtype=np.float32)[:, None]
    m_far = smooth((rows - (HZ - far[None, :])) + 0.5) * (rows < HZ)
    m_near = smooth((rows - (HZ - near[None, :])) + 0.5) * (rows < HZ)
    far_col = bgr((62, 54, 82)) * 1.0
    img = img * (1 - m_far[..., None]) + m_far[..., None] * far_col
    # a little rim light on the far range from the afterglow
    rim = np.clip(m_far - np.roll(m_far, 3, axis=0), 0, 1) * np.exp(-((x - 760) / 420) ** 2)[None, :]
    img += rim[..., None] * bgr((140, 80, 40))
    img = img * (1 - m_near[..., None]) + m_near[..., None] * bgr((24, 20, 32))

    # ground
    t = np.clip((rows[HZ:, 0] - HZ) / (H - HZ), 0, 1)
    gcol = np.stack([np.interp(t, [0, 0.06, 0.35, 1], [c0, c1, c2, c3]) for c0, c1, c2, c3 in
                     zip((44, 38, 52), (30, 26, 34), (16, 15, 20), (8, 8, 11))], axis=1)[:, ::-1].astype(np.float32)
    img[HZ:] = gcol[:, None, :]
    gn = cv2.GaussianBlur(rng.normal(0, 1, (H - HZ, W)).astype(np.float32), (0, 0), 1.2)
    img[HZ:] *= (1 + 0.06 * gn)[..., None]

    # road surface
    rm = np.zeros((H, W), np.uint8)
    fill(rm, [proj(-ROAD, 0, 0.7), proj(ROAD, 0, 0.7), proj(ROAD, 0, 4000), proj(-ROAD, 0, 4000)])
    rmf = rm.astype(np.float32) / 255
    rc = np.stack([np.interp(t, [0, 0.03, 0.25, 1], [c0, c1, c2, c3]) for c0, c1, c2, c3 in
                   zip((96, 74, 74), (56, 48, 58), (30, 30, 37), (20, 20, 25))], axis=1)[:, ::-1].astype(np.float32)
    road = np.zeros((H, W, 3), np.float32)
    road[HZ:] = rc[:, None, :]
    road[HZ:] *= (1 + 0.05 * gn)[..., None]
    img = img * (1 - rmf[..., None]) + road * rmf[..., None]
    # solid edge lines
    lm = np.zeros((H, W), np.uint8)
    for e in (-ROAD + 0.25, ROAD - 0.25):
        fill(lm, [proj(e - 0.07, 0, 0.7), proj(e + 0.07, 0, 0.7), proj(e + 0.07, 0, 4000), proj(e - 0.07, 0, 4000)])
    lmf = lm.astype(np.float32) / 255 * (0.55 + 0.25 * smooth((rows - HZ) / 300))
    img = img * (1 - lmf[..., None]) + lmf[..., None] * bgr((205, 200, 196))

    # horizon haze
    hz = np.exp(-((yy - HZ) / 26) ** 2) * np.exp(-((xx - 700) / 700) ** 2)
    img += hz[..., None] * bgr((90, 52, 30))

    # darken behind the lyrics so they always read
    prof = np.exp(-((rows[:, 0] - LY) / 240) ** 2)
    img *= (1 - 0.58 * prof)[:, None, None]
    # gentle overall vignette
    vig = 1 - 0.38 * smooth((((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2) - 0.25)
    img *= vig[..., None]
    # bottom fade so the progress bar has room
    img *= (1 - 0.35 * smooth((rows[:, 0] - 1700) / 220))[:, None, None]

    # twinkling subset (drawn per frame)
    tw = dict(x=sx[br > 0.35], y=sy[br > 0.35], b=br[br > 0.35])
    m = len(tw['x'])
    tw['f'] = rng.uniform(0.3, 1.4, m)
    tw['p'] = rng.uniform(0, 2 * np.pi, m)
    # bushes: world positions tiled every 140 m
    nb = 70
    side = rng.choice([-1, 1], nb, p=[0.35, 0.65])
    bx = np.where(side > 0, rng.uniform(ROAD + 1.4, 26, nb), -rng.uniform(ROAD + 1.4, 30, nb))
    bush = dict(x=bx, z=rng.uniform(0, 140, nb), w=rng.uniform(0.35, 1.1, nb), h=rng.uniform(0.25, 0.7, nb))
    # static dither to stop banding in the sky
    img += rng.uniform(-1.2, 1.2, (H, W, 1)).astype(np.float32)
    return img.astype(np.float32), tw, bush


# ---------------------------------------------------------------- moving scenery
def draw_scenery(img, t, tw, bush, env):
    P = SPEED * t
    # twinkles
    a = 0.5 + 0.5 * np.sin(tw['p'] + t * tw['f'] * 2 * np.pi)
    for x, y, b, k in zip(tw['x'], tw['y'], tw['b'], a):
        if k < 0.75:
            continue
        xi, yi = int(x), int(y)
        img[yi, xi] += (k - 0.75) * 4 * b * 70
    # horizon breathes with the music
    hr0, hr1 = HZ - 160, HZ + 60
    img[hr0:hr1] += GLOW_H * (0.15 + 0.85 * env)

    mask = np.zeros((H, W), np.uint8)       # dark silhouettes (poles, wires, bushes)
    paint = np.zeros((H, W), np.uint8)      # centre dashes
    posts = np.zeros((H, W), np.uint8)      # white posts
    zmin = 0.75
    # centre dashes: 3 m dash every 12 m
    k0 = math.floor((P + zmin) / 12)
    for k in range(k0, k0 + 30):
        z0 = k * 12 - P
        z1 = z0 + 3
        z0 = max(z0, zmin)
        if z1 <= zmin:
            continue
        fade = 1 - smooth((z0 - 60) / 200)
        fill(paint, [proj(-0.07, 0, z0), proj(0.07, 0, z0), proj(0.07, 0, z1), proj(-0.07, 0, z1)], 255 * fade)
    # bushes
    for x, z, w, h in zip(bush['x'], bush['z'], bush['w'], bush['h']):
        zz = (z - P) % 140
        if zz < 14:
            continue
        cx, cy = proj(x, 0, zz)
        rx, ry = FOC * w / zz / 2, FOC * h / zz
        if rx < 0.4 or cx + rx < 0 or cx - rx > W:
            continue
        av = 230 * sm((zz - 14) / 22)
        cv2.ellipse(mask, (int(cx * 16), int((cy - ry * 0.45) * 16)), (max(int(rx * 16), 8), max(int(ry * 0.55 * 16), 6)),
                    0, 0, 360, int(av), -1, cv2.LINE_AA, 4)
    # delineator posts with amber reflectors
    refl = []
    k0 = math.floor((P + 1.5) / POST_GAP)
    for k in range(k0, k0 + 12):
        z = k * POST_GAP - P + 7
        if z < 1.5:
            continue
        x0, yb = proj(POST_X - 0.05, 0, z)
        x1, yt = proj(POST_X + 0.05, 1.0, z)
        if x0 > W:
            continue
        fade = (1 - sm((z - 40) / 160)) * sm((z - 3) / 9)
        fill(posts, [(x0, yb), (x1, yb), (x1, yt), (x0, yt)], 120 * fade)
        refl.append(((x0 + x1) / 2, yt + (yb - yt) * 0.12, FOC * 0.06 / z, fade))
    # power poles + wires
    k0 = math.floor((P + 1.0) / POLE_GAP)
    tops = []
    for k in range(k0, k0 + 9):
        z = k * POLE_GAP - P + 20
        if z < 1.0:
            continue
        xl, yb = proj(POLE_X - 0.13, 0, z)
        xr, yt = proj(POLE_X + 0.13, POLE_H, z)
        if xl < W + 50:
            fill(mask, [(xl, yb), (xr, yb), (xr, yt), (xl, yt)], 255)
            a0, ay = proj(POLE_X - 1.1, POLE_H - 0.5, z)
            a1, ay2 = proj(POLE_X + 1.1, POLE_H - 0.35, z)
            th = FOC * 0.12 / z
            fill(mask, [(a0, ay), (a1, ay), (a1, ay - th), (a0, ay - th)], 255)
        tops.append(z)
    for z0, z1 in zip(tops[:-1], tops[1:]):
        for wx in (POLE_X - 0.95, POLE_X + 0.95):
            zs = np.linspace(z0, z1, 40)
            u = (zs - z0) / (z1 - z0)
            hgt = POLE_H - 0.45 - 1.0 * 4 * u * (1 - u)
            pts = [proj(wx, h_, z_) for h_, z_ in zip(hgt, zs)]
            arr = np.round(np.array(pts) * 16).astype(np.int32).reshape(-1, 1, 2)
            cv2.polylines(mask, [arr], False, 200, 2 if z0 < 30 else 1, cv2.LINE_AA, 4)

    # composite: paint lines, posts, then silhouettes on top
    for m, col, kk in ((paint, bgr((222, 198, 120)), 0.75), (posts, bgr((200, 200, 205)), 0.8)):
        x, y, w, h = cv2.boundingRect(m)
        if w and h:
            a_ = m[y:y + h, x:x + w].astype(np.float32)[..., None] * (kk / 255) * PROFK[y:y + h, None, None]
            reg = img[y:y + h, x:x + w]
            reg *= (1 - a_)
            reg += a_ * col
    x, y, w, h = cv2.boundingRect(mask)
    if w and h:
        a_ = mask[y:y + h, x:x + w].astype(np.float32)[..., None] / 255
        reg = img[y:y + h, x:x + w]
        reg *= (1 - a_)
        reg += a_ * bgr((10, 10, 16))
    for (cx, cy, r, fade) in refl:
        r = max(r, 0.7)
        s = int(r * 6) + 3
        x0, y0 = int(cx) - s, int(cy) - s
        if x0 < 0 or y0 < 0 or x0 + 2 * s >= W or y0 + 2 * s >= H:
            continue
        gy, gx = np.mgrid[y0:y0 + 2 * s, x0:x0 + 2 * s].astype(np.float32)
        spr = np.exp(-((gx - cx) ** 2 + (gy - cy) ** 2) / (2 * (r * 1.6) ** 2))
        img[y0:y0 + 2 * s, x0:x0 + 2 * s] += spr[..., None] * bgr((255, 170, 60)) * fade * 1.1


def shooting_star(img, t):
    rng = np.random.default_rng(int(t // 23) + 5)
    t0 = (t // 23) * 23 + rng.uniform(3, 17)
    u = (t - t0) / 0.8
    if not 0 <= u <= 1:
        return
    x0, y0 = rng.uniform(150, 1000), rng.uniform(60, 420)
    ang = rng.uniform(2.3, 2.7)
    Ls = 420
    hx, hy = x0 + math.cos(ang) * Ls * u, y0 + math.sin(ang) * Ls * u
    lay = np.zeros((H // 2, W), np.uint8)
    for k in range(12):
        f = k / 12
        a = (1 - f) * math.sin(math.pi * u)
        p0 = (hx - math.cos(ang) * 150 * f, hy - math.sin(ang) * 150 * f)
        p1 = (hx - math.cos(ang) * 150 * (f + 1 / 12), hy - math.sin(ang) * 150 * (f + 1 / 12))
        cv2.line(lay, (int(p0[0] * 16), int(p0[1] * 16)), (int(p1[0] * 16), int(p1[1] * 16)), int(255 * a), 2, cv2.LINE_AA, 4)
    img[:H // 2] += lay.astype(np.float32)[..., None] / 255 * bgr((220, 232, 255))


# ---------------------------------------------------------------- portrait + visualizer
def build_portrait():
    face = cv2.imread(FACE)
    cx, cy, s = 540, 510, 820
    crop = face[cy - s // 2:cy + s // 2, cx - s // 2:cx + s // 2]
    d = 2 * PR
    crop = cv2.resize(crop, (d, d), interpolation=cv2.INTER_AREA).astype(np.float32)
    yy, xx = np.mgrid[0:d, 0:d].astype(np.float32)
    r = np.sqrt((xx - PR + 0.5) ** 2 + (yy - PR + 0.5) ** 2)
    m = np.clip(PR - r + 0.5, 0, 1)
    crop *= (1 - 0.35 * smooth((r / PR - 0.72) / 0.28))[..., None]
    ring = np.clip(1.6 - np.abs(r - (PR - 0.5)), 0, 1)
    # shadow disk behind
    P = 120
    sh = np.zeros((d + 2 * P, d + 2 * P), np.float32)
    sh[P:P + d, P:P + d] = m
    sh = cv2.GaussianBlur(sh, (0, 0), 34) * 0.75
    return dict(face=crop, m=m[..., None], ring=ring[..., None], sh=sh[..., None], P=P)


def draw_portrait(img, PT, bass):
    d = 2 * PR
    P = PT['P']
    x0, y0 = PCX - PR - P, PCY - PR - P
    reg = img[y0:y0 + d + 2 * P, x0:x0 + d + 2 * P]
    reg *= (1 - PT['sh'])
    x0, y0 = PCX - PR, PCY - PR
    reg = img[y0:y0 + d, x0:x0 + d]
    m = PT['m']
    reg *= (1 - m)
    reg += PT['face'] * m
    ra = PT['ring'] * (0.55 + 0.45 * bass)
    reg *= (1 - ra)
    reg += ra * bgr((235, 240, 255))


VS = 2 * (PR + 150)
ANG = np.pi * (np.arange(NB) + 0.5) / NB      # 0 = top, pi = bottom
COL_TOP, COL_BOT = bgr((120, 196, 255)), bgr(ACCENT)


def draw_visualizer(img, vals, bass):
    lay = np.zeros((VS, VS, 3), np.uint8)
    c = VS / 2
    r0 = PR + 13
    for side in (1, -1):
        for j in range(NB):
            v = float(vals[j])
            L = 5 + 120 * v
            a = ANG[j]
            sx, sy = math.sin(a) * side, -math.cos(a)
            p0 = (c + sx * r0, c + sy * r0)
            p1 = (c + sx * (r0 + L), c + sy * (r0 + L))
            mix = j / (NB - 1)
            col = (COL_TOP * (1 - mix) + COL_BOT * mix) * (0.45 + 0.55 * min(1, 0.3 + v))
            cv2.line(lay, (int(p0[0] * 16), int(p0[1] * 16)), (int(p1[0] * 16), int(p1[1] * 16)),
                     tuple(int(q) for q in col), 7, cv2.LINE_AA, 4)
    f = lay.astype(np.float32)
    small = cv2.resize(f, (VS // 2, VS // 2), interpolation=cv2.INTER_AREA)
    glow = cv2.resize(cv2.GaussianBlur(small, (0, 0), 6), (VS, VS), interpolation=cv2.INTER_LINEAR)
    x0, y0 = PCX - VS // 2, PCY - VS // 2
    reg = img[y0:y0 + VS, x0:x0 + VS]
    # soft halo behind the circle that swells on the kick
    reg += HALO * (0.25 + 0.75 * bass)
    reg += glow * (0.9 + 0.6 * bass)
    a = (f.max(axis=2, keepdims=True) / 255)
    reg *= (1 - 0.85 * a)
    reg += f * 1.0


# ---------------------------------------------------------------- title
def build_title():
    hgt = 300
    rgba = Image.new('RGBA', (W, hgt), (0, 0, 0, 0))
    d = ImageDraw.Draw(rgba)
    f_name = ImageFont.truetype(INTER_SB, 33)
    name = 'ZACHARY PATZER'
    sp = 9
    ws = [d.textlength(ch, font=f_name) for ch in name]
    x = (W - (sum(ws) + sp * (len(name) - 1))) / 2
    for ch, w in zip(name, ws):
        d.text((x, 118), ch, font=f_name, fill=(255, 255, 255, 225), anchor='ls')
        x += w + sp
    s = 96
    while True:
        ft = ImageFont.truetype(F_SLAB, s)
        if d.textlength(TITLE.upper(), font=ft) <= 900 or s < 50:
            break
        s -= 2
    tw = d.textlength(TITLE.upper(), font=ft)
    glow = Image.new('L', (W, hgt), 0)
    ImageDraw.Draw(glow).text(((W - tw) / 2, 232), TITLE.upper(), font=ft, fill=255, anchor='ls', stroke_width=6)
    d.text(((W - tw) / 2, 232), TITLE.upper(), font=ft, fill=TITLE_COL + (255,), anchor='ls',
           stroke_width=3, stroke_fill=(8, 18, 40, 255))
    a = np.asarray(rgba, np.float32) / 255
    al = a[..., 3:4]
    col = a[..., :3][..., ::-1] * 255
    sh = cv2.GaussianBlur(np.asarray(glow, np.float32) / 255, (0, 0), 12)[..., None]
    return dict(K=(1 - 0.6 * sh) * (1 - al), C=col * al, hgt=hgt)


# ---------------------------------------------------------------- kinetic lyrics
WEAK = {'and', 'a', 'an', 'the', 'to', 'at', 'of', 'i', 'but', 'so', 'like', 'for', 'when', 'that', 'who',
        'this', 'my', "i'm", "i'll", 'as', 'with', 'even', 'has', 'some', 'in', 'on', 'me', "they'd"}
EMPH = {'mile', 'hour', 'power', 'walk', 'walkin', 'stand', 'stage', 'four', 'bell', 'blessin', 'gold', 'alone',
        'time', 'love', 'promise', 'light', 'tomorrow', 'fight'}
PAD = 36


def key(w):
    return w.lower().strip(' ".,!?()…;:').rstrip('.').strip("'\"").replace('’', "'")


def wrap(words, f):
    import itertools
    dr = ImageDraw.Draw(Image.new('L', (8, 8)))
    sw = dr.textlength(' ', font=f)
    ww = [dr.textlength(w, font=f) for w in words]

    def width(a, b):
        return sum(ww[a:b]) + sw * (b - a - 1)
    n = len(words)
    if width(0, n) <= MAXW:
        return [list(range(n))]
    for k in (2, 3, 4):
        best = None
        for cuts in itertools.combinations(range(1, n), k - 1):
            b = (0,) + cuts + (n,)
            wid = [width(b[j], b[j + 1]) for j in range(k)]
            if max(wid) > MAXW:
                continue
            score = max(wid) - min(wid) * 0.5 + (400 if any(b[j + 1] - b[j] == 1 for j in range(k)) else 0)
            for j in range(k - 1):
                last = words[b[j + 1] - 1]
                if key(last) in WEAK:
                    score += 260
                if last[-1] in ',.!?;"' or last.endswith('...'):
                    score -= 140
            if best is None or score < best[0]:
                best = (score, b)
        if best:
            b = best[1]
            return [list(range(b[j], b[j + 1])) for j in range(len(b) - 1)]
    raise ValueError(' '.join(words))


class Word:
    pass


def build_lyrics(lyr):
    f = ImageFont.truetype(INTER_B, FS)
    dr = ImageDraw.Draw(Image.new('L', (8, 8)))
    sw = dr.textlength(' ', font=f)
    items = []
    for it in lyr:
        if it.get('kind') == 'dots':
            items.append(dict(kind='dots', s=it['start'], e=it['end'], last=it['start']))
            continue
        words = [w['w'] for w in it['words']]
        rows = wrap(words, f)
        bh = ROW_H * len(rows)
        ws = []
        for ri, row in enumerate(rows):
            lens = [dr.textlength(words[i], font=f) for i in row]
            x = (W - (sum(lens) + sw * (len(row) - 1))) / 2
            for i, wl in zip(row, lens):
                o = Word()
                o.text, o.s, o.e = words[i], it['words'][i]['s'], it['words'][i]['e']
                o.emph = key(o.text) in EMPH
                cw, ch = int(math.ceil(wl)) + 2 * PAD, ROW_H + 2 * PAD
                im = Image.new('L', (cw, ch), 0)
                ImageDraw.Draw(im).text((PAD, PAD + int(ROW_H * 0.74)), o.text, font=f, fill=255, anchor='ls')
                o.a = np.asarray(im, np.float32) / 255
                o.g = cv2.GaussianBlur(o.a, (0, 0), 11)
                o.cx = x + wl / 2
                o.cy = -bh / 2 + ri * ROW_H + ROW_H / 2          # relative to block centre
                ws.append(o)
                x += wl + sw
        items.append(dict(kind='line', s=ws[0].s, e=ws[-1].e, last=ws[-1].s, words=ws))
    # enter / exit times
    for k, it in enumerate(items):
        prev = items[k - 1] if k else None
        lead = 0.0 if it['kind'] == 'dots' else 0.32
        it['in'] = it['s'] - lead
        if prev is not None:
            it['in'] = max(it['in'], prev['last'] + 0.28)
    for k, it in enumerate(items):
        nxt = items[k + 1]['in'] if k + 1 < len(items) else 1e9
        linger = it['e'] + 1.3
        it['out'] = nxt if nxt - it['e'] < 1.3 or it['kind'] == 'dots' else linger
        if it['kind'] == 'dots':
            it['out'] = min(nxt, it['e'] + 0.2)
    return items


def paste(acc, src, x0, y0):
    h, w = src.shape[:2]
    H_, W_ = acc.shape[:2]
    ax0, ay0 = max(x0, 0), max(y0, 0)
    ax1, ay1 = min(x0 + w, W_), min(y0 + h, H_)
    if ax1 <= ax0 or ay1 <= ay0:
        return
    acc[ay0:ay1, ax0:ax1] += src[ay0 - y0:ay1 - y0, ax0 - x0:ax1 - x0]


def draw_lyrics(img, items, t):
    RH = LZ1 - LZ0
    A = np.zeros((RH, W), np.float32)
    C = np.zeros((RH, W, 3), np.float32)
    G = np.zeros((RH, W, 3), np.float32)
    gold, white = bgr(ACCENT), bgr((255, 255, 255))
    for it in items:
        if t < it['in'] - 0.01 or t > it['out'] + 0.01:
            continue
        pin = ease_out((t - it['in']) / 0.32)
        q = sm((t - (it['out'] - 0.24)) / 0.24)
        la = pin * (1 - q)
        if la <= 0.002:
            continue
        dy = 64 * (1 - pin) - 64 * q
        cyb = LY - LZ0 + dy
        if it['kind'] == 'dots':
            prog = (t - it['s']) / max(it['e'] - it['s'], 0.1)
            br = 1 + 0.12 * math.sin(2 * math.pi * t / 2.4)
            for k in range(3):
                fl = float(np.clip(prog * 3 - k, 0, 1))
                lvl = (0.35 + 0.65 * fl) * la
                r = 11 * br
                cx, cy = W / 2 + (k - 1) * 42 * br, cyb
                x0, y0 = int(cx - r - 3), int(cy - r - 3)
                yy, xx = np.mgrid[y0:y0 + int(2 * r) + 8, x0:x0 + int(2 * r) + 8].astype(np.float32)
                dd = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
                a = np.clip(r - dd + 0.5, 0, 1) * lvl
                paste(A, a, x0, y0)
                paste(C, a[..., None] * white, x0, y0)
            continue
        for o in it['words']:
            lit = sm((t - o.s) / 0.09 + 0.5)
            u = (t - o.s) / 0.42
            amp = 0.11 if o.emph else 0.045
            pop = 0.0
            if 0 <= u <= 1:
                kk = u / 0.22 if u < 0.22 else 1 - (u - 0.22) / 0.78
                pop = sm(kk)
            sc = 1 + amp * pop
            lvl = (0.40 + 0.60 * lit) * la
            a, g = o.a, o.g
            if sc != 1:
                nw, nh = int(round(a.shape[1] * sc)), int(round(a.shape[0] * sc))
                a = cv2.resize(a, (nw, nh), interpolation=cv2.INTER_LINEAR)
                g = cv2.resize(g, (nw, nh), interpolation=cv2.INTER_LINEAR)
            x0 = int(round(o.cx - a.shape[1] / 2))
            y0 = int(round(cyb + o.cy - a.shape[0] / 2 - 8 * pop))
            col = gold if (o.emph and lit > 0.5) else white
            aa = a * lvl
            paste(A, aa, x0, y0)
            paste(C, aa[..., None] * col, x0, y0)
            # glow while being sung
            gs = (1 - sm((t - o.e) / 0.45)) * lit * la
            if gs > 0.01:
                gcol = gold if o.emph else bgr((255, 226, 170))
                paste(G, g[..., None] * gcol * (gs * (1.15 if o.emph else 0.55)), x0, y0)
    if not A.any():
        return
    A = np.clip(A, 0, 1)
    S = cv2.GaussianBlur(A, (0, 0), 9)
    S = np.roll(S, 4, axis=0) * 0.7
    reg = img[LZ0:LZ1]
    reg *= (1 - S)[..., None]
    reg *= (1 - A)[..., None]
    reg += C
    reg += G


# ---------------------------------------------------------------- progress bar
F_TIME = ImageFont.truetype(INTER_M, 23)
_tl = {}


def tlabel(s, right):
    if (s, right) not in _tl:
        im = Image.new('L', (150, 36), 0)
        ImageDraw.Draw(im).text((149 if right else 0, 28), s, font=F_TIME, fill=255, anchor='rs' if right else 'ls')
        _tl[(s, right)] = np.asarray(im, np.float32)[..., None] / 255
    return _tl[(s, right)]


def draw_bar(img, t, f):
    prog = min(max(t / DUR, 0), 1)
    y0, y1 = BAR_Y - 2, BAR_Y + 2
    img[y0:y1, BAR_X0:BAR_X1] = img[y0:y1, BAR_X0:BAR_X1] * (1 - 0.2 * f) + 255 * 0.2 * f
    xb = int(BAR_X0 + prog * (BAR_X1 - BAR_X0))
    img[y0:y1, BAR_X0:xb] = img[y0:y1, BAR_X0:xb] * (1 - 0.7 * f) + bgr(ACCENT) * 0.7 * f
    r = 7
    yy, xx = np.mgrid[BAR_Y - 10:BAR_Y + 11, xb - 10:xb + 11].astype(np.float32)
    k = np.clip(r - np.sqrt((xx - xb) ** 2 + (yy - BAR_Y) ** 2) + 0.5, 0, 1)[..., None] * f
    reg = img[BAR_Y - 10:BAR_Y + 11, xb - 10:xb + 11]
    reg[:] = reg * (1 - k) + 255 * k
    el, rem = int(t), int(math.ceil(DUR - t))
    for lab, x0 in ((tlabel(f'{el // 60}:{el % 60:02d}', False), BAR_X0), (tlabel(f'-{rem // 60}:{rem % 60:02d}', True), BAR_X1 - 150)):
        reg = img[BAR_Y + 12:BAR_Y + 48, x0:x0 + 150]
        a = lab * 0.55 * f
        reg[:] = reg * (1 - a) + 255 * a


# ---------------------------------------------------------------- frame
class Renderer:
    def __init__(self, lyr):
        global GLOW_H, HALO
        self.bg, self.tw, self.bush = build_background()
        self.PT = build_portrait()
        self.TT = build_title()
        self.items = build_lyrics(lyr)
        self.vals, self.bass, self.env = analyse_audio()
        yy, xx = np.mgrid[HZ - 160:HZ + 60, 0:W].astype(np.float32)
        GLOW_H = (np.exp(-((xx - 700) / 520) ** 2 - ((yy - HZ) / 70) ** 2)[..., None] * bgr((70, 36, 14))).astype(np.float32)
        yy, xx = np.mgrid[0:VS, 0:VS].astype(np.float32)
        r = np.sqrt((xx - VS / 2) ** 2 + (yy - VS / 2) ** 2)
        HALO = (np.exp(-((r - PR) / 60) ** 2)[..., None] * bgr((60, 90, 140)) * 0.6).astype(np.float32)
        self.fade_in, self.fade_out = 0.0, DUR

    def frame(self, t):
        fi = min(max(int(t * FPS), 0), len(self.env) - 1)
        img = self.bg.copy()
        draw_scenery(img, t, self.tw, self.bush, float(self.env[fi]))
        shooting_star(img, t)
        ui = sm((t - self.fade_in - 0.1) / 1.0)
        b = float(self.bass[fi])
        draw_visualizer(img, self.vals[fi] * ui, b * ui)
        draw_portrait(img, self.PT, b * ui)
        reg = img[:self.TT['hgt']]
        reg *= self.TT['K']
        reg += self.TT['C']
        draw_lyrics(img, self.items, t)
        draw_bar(img, t, ui)
        g = sm((t - self.fade_in) / 0.7) * sm((self.fade_out - t) / 1.4)
        if g < 1:
            img *= g
        return cv2.convertScaleAbs(img)


def main():
    lyr = json.load(open(f'{D}/lyrics_final.json'))
    R = Renderer(lyr)
    if sys.argv[2] == '--stills':
        for ts in sys.argv[3:]:
            t = float(ts)
            tic = time.time()
            cv2.imwrite(f'{D}/mv_still_{t:07.2f}.png', R.frame(t))
            print('still', t, f'{time.time() - tic:.2f}s')
        return
    out = sys.argv[2]
    t0, t1 = 0.0, DUR
    if '--range' in sys.argv:
        k = sys.argv.index('--range')
        t0, t1 = float(sys.argv[k + 1]), float(sys.argv[k + 2])
        R.fade_in, R.fade_out = t0, t1
    f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
           '-c:v', 'libx264', '-preset', os.environ.get('RENDER_PRESET', 'medium'), '-crf', os.environ.get('RENDER_CRF', '19'),
           '-x264-params', 'aq-mode=3']
    if os.environ.get('RENDER_MAXRATE'):
        mr = int(os.environ['RENDER_MAXRATE'])
        cmd += ['-maxrate', f'{mr}k', '-bufsize', f'{mr * 2}k']
    cmd += ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    tic = time.time()
    for f in range(f0, f1):
        p.stdin.write(R.frame(f / FPS).tobytes())
        if f % 150 == 0:
            print(f'frame {f - f0}/{f1 - f0}  {time.time() - tic:.0f}s', flush=True)
    p.stdin.close()
    p.wait()
    print('done', round(time.time() - tic))


if __name__ == '__main__':
    main()
