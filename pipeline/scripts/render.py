#!/usr/bin/env python3
"""Karaoke lyric video renderer (per-song settings from the SONG_CFG json).

usage:
  render.py lyrics.json out.mp4                 # full render
  render.py lyrics.json --stills t1 t2 ...      # PNG stills for review
  render.py lyrics.json out.mp4 --range a b     # partial render (seconds)
"""
import sys, os, json, math, subprocess, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import scipy.io.wavfile as wavfile

W, H, FPS = 1080, 1920, 30
CFG = json.load(open(os.environ['SONG_CFG']))
WORK = CFG['work']
DUR = float(CFG['dur'])

LORA = '/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf'
INTER_M = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
INTER_D_SB = '/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf'

# ---------------------------------------------------------------- layout
TITLE_Y = 262
SUB_Y = 336
ART = 560
ART_X = (W - ART) // 2
ART_Y = 394
FOCUS_Y = 1272              # centre of the active lyric line
LYR_TOP, LYR_BOT = 990, 1596
LYR_SIZE = 60
ROW_H = 76
LINE_GAP = 36
MAX_TEXT_W = 860
DIM = 0.38                  # alpha of unsung / inactive text
BAR_Y = 1652
BAR_X0, BAR_X1 = ART_X, ART_X + ART

# vertical Shorts/Reels layout: everything in the top ~60% so the app's caption, buttons and progress bar don't cover it
SHORTS = os.environ.get('RENDER_SHORTS') == '1'
if SHORTS:
    TITLE_Y, SUB_Y = 238, 300
    ART = 480
    ART_X = (W - ART) // 2
    ART_Y = 352
    FOCUS_Y = 1034
    LYR_TOP, LYR_BOT = 858, 1272
    MAX_TEXT_W = 760
FADE_T, FADE_B = (95.0, 100.0) if SHORTS else (175.0, 150.0)


def font(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var:
        f.set_variation_by_name(var)
    return f


def _fit_title():
    s = 82
    while s > 50:
        f = font(LORA, s, 'SemiBold')
        if ImageDraw.Draw(Image.new('L', (8, 8))).textlength(CFG['title'], font=f) <= 960:
            return f
        s -= 2
    return f


F_TITLE = _fit_title()
F_SUB = font(INTER_M, 29)
F_LYR = font(INTER_D_SB, LYR_SIZE)
F_TIME = font(INTER_M, 23)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- audio envelope
def audio_envelope():
    sr, d = wavfile.read(f'{WORK}/mono44.wav')
    d = d.astype(np.float32) / 32768.0
    hop = sr // FPS
    n = int(math.ceil(DUR * FPS)) + 2
    env = np.zeros(n, np.float32)
    for i in range(n):
        seg = d[i * hop:(i + 1) * hop]
        env[i] = np.sqrt(np.mean(seg * seg)) if len(seg) else 0
    # attack / release smoothing
    out = np.zeros_like(env)
    v = 0
    for i, e in enumerate(env):
        k = 0.45 if e > v else 0.06
        v = v + k * (e - v)
        out[i] = v
    lo, hi = np.percentile(out, 5), np.percentile(out, 98)
    return np.clip((out - lo) / (hi - lo + 1e-9), 0, 1)


# ---------------------------------------------------------------- static layers
def rounded_mask(w, h, r, ss=4):
    m = Image.new('L', (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], r * ss, fill=255)
    return np.asarray(m.resize((w, h), Image.LANCZOS), np.float32) / 255.0


def load_art():
    return cv2.imread(CFG['art_path'])


def build_static():
    art = load_art()
    st = {}
    # --- background source: heavily blurred, darkened art
    bg = cv2.resize(art, (720, 720), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg = cv2.GaussianBlur(bg, (0, 0), 26)
    bg = cv2.GaussianBlur(bg, (0, 0), 14)
    bg *= np.array(CFG.get('bg_tint', [0.86, 0.95, 1.06]), np.float32) * CFG.get('bg_gain', 0.40)
    st['bg'] = bg

    # --- vignette (multiplicative)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W / 2) / (W * 0.62)
    ny = (yy - H * 0.46) / (H * 0.58)
    r2 = nx * nx + ny * ny
    vig = np.clip(1.0 - 0.72 * smooth(r2 * 0.85), 0.18, 1.0)
    # extra darkening toward bottom/top edges
    vig *= (1 - 0.35 * smooth((yy / H - 0.78) / 0.22)) * (1 - 0.25 * smooth((0.12 - yy / H) / 0.12))
    st['vig'] = vig[..., None].astype(np.float32)

    # --- warm glow behind the art (additive, scaled by audio)
    cx, cy = W / 2, ART_Y + ART / 2
    d = np.sqrt(((xx - cx) / 1.0) ** 2 + ((yy - cy) / 1.15) ** 2)
    g = np.exp(-(d / 430.0) ** 2)
    st['glow'] = (g[..., None] * np.array(CFG.get('glow_col', [26, 62, 128]), np.float32)).astype(np.float32)

    # --- art card
    art_s = cv2.resize(art, (ART, ART), interpolation=cv2.INTER_AREA).astype(np.float32)
    # gentle local-contrast / clarity on the upscaled art
    blur = cv2.GaussianBlur(art_s, (0, 0), 2.0)
    art_s = np.clip(art_s + 0.18 * (art_s - blur), 0, 255)
    m = rounded_mask(ART, ART, 26)
    st['art'] = art_s
    st['art_m'] = m[..., None]
    # thin light edge
    edge = np.clip(m - cv2.erode(m, np.ones((3, 3), np.uint8)), 0, 1)
    st['art_edge'] = edge[..., None] * 0.18
    # drop shadow (pad region)
    P = 90
    sh = np.zeros((ART + 2 * P, ART + 2 * P), np.float32)
    sh[P + 18:P + 18 + ART, P:P + ART] = m
    sh = cv2.GaussianBlur(sh, (0, 0), 30) * 0.78
    st['shadow'] = sh[..., None]
    st['shadow_xy'] = (ART_X - P, ART_Y - P)

    # --- title + subtitle (RGBA layer, premultiplied as float)
    lay = Image.new('L', (W, 420), 0)
    dr = ImageDraw.Draw(lay)
    title = CFG['title']
    tw = dr.textlength(title, font=F_TITLE)
    dr.text(((W - tw) / 2, TITLE_Y), title, font=F_TITLE, fill=255, anchor='ls')
    sub = 'ZACHARY PATZER   ·   REMASTERED'
    spacing = 4.2
    widths = [dr.textlength(c, font=F_SUB) for c in sub]
    total = sum(widths) + spacing * (len(sub) - 1)
    x = (W - total) / 2
    sub_l = Image.new('L', (W, 420), 0)
    ds = ImageDraw.Draw(sub_l)
    for c, cw in zip(sub, widths):
        ds.text((x, SUB_Y), c, font=F_SUB, fill=255, anchor='ls')
        x += cw + spacing
    t_a = np.asarray(lay, np.float32) / 255.0
    s_a = np.asarray(sub_l, np.float32) / 255.0 * 0.66
    a = np.maximum(t_a, s_a)
    shadow = cv2.GaussianBlur(a, (0, 0), 7) * 0.55
    st['title_a'] = a[..., None]
    st['title_sh'] = shadow[..., None]
    # subtitle tinted warm, title white
    col = np.ones((420, W, 3), np.float32) * 255
    tint = np.array(CFG.get('sub_tint', [200, 222, 246]), np.float32)
    sub_only = (s_a > t_a)[..., None]
    st['title_col'] = np.where(sub_only, tint, col)


    # --- ember sprites
    st['ember'] = {}
    for r in (1.6, 2.2, 3.0, 4.0):
        s = int(r * 7) | 1
        k = cv2.getGaussianKernel(s, r * 0.9)
        spr = (k @ k.T).astype(np.float32)
        spr /= spr.max()
        st['ember'][r] = spr
    st['glow_h'] = cv2.resize(st['glow'], (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    st['vig_h'] = cv2.resize(st['vig'][..., 0], (W // 2, H // 2), interpolation=cv2.INTER_AREA)[..., None]
    nrng = np.random.default_rng(3)
    return st


# ---------------------------------------------------------------- embers
rng = np.random.default_rng(7)
N_EMB = 46
EMB = dict(
    x=rng.uniform(40, W - 40, N_EMB),
    speed=rng.uniform(22, 62, N_EMB),
    sway=rng.uniform(8, 36, N_EMB),
    swf=rng.uniform(0.05, 0.22, N_EMB),
    ph=rng.uniform(0, 1, N_EMB),
    r=rng.choice([1.6, 2.2, 3.0, 4.0], N_EMB, p=[0.35, 0.3, 0.22, 0.13]),
    b=rng.uniform(0.25, 0.75, N_EMB),
    fl=rng.uniform(1.5, 4.0, N_EMB),
    top=rng.uniform(0.15, 0.55, N_EMB),
)
EMB['speed'] *= CFG.get('ember_speed', 1.0)
EMB_COL = np.array(CFG.get('ember_col', [70, 150, 255]), np.float32)  # BGR


def draw_embers(img, t, st, gain):
    for i in range(N_EMB):
        span = H * (1 - EMB['top'][i]) + 60
        per = span / EMB['speed'][i]
        ph = (t / per + EMB['ph'][i]) % 1.0
        y = H + 30 - ph * span
        x = EMB['x'][i] + EMB['sway'][i] * math.sin(2 * math.pi * EMB['swf'][i] * t + i)
        life = math.sin(math.pi * ph) ** 0.8
        flick = 0.75 + 0.25 * math.sin(EMB['fl'][i] * t * 2 * math.pi + i * 1.7)
        a = EMB['b'][i] * life * flick * gain
        if a < 0.01:
            continue
        spr = st['ember'][EMB['r'][i]]
        s = spr.shape[0]
        x0, y0 = int(round(x - s / 2)), int(round(y - s / 2))
        x1, y1 = x0 + s, y0 + s
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            continue
        img[y0:y1, x0:x1] += spr[..., None] * (EMB_COL * a)


# ---------------------------------------------------------------- lyrics
class Line:
    pass


WEAK = {'and', 'a', 'an', 'the', 'to', 'at', 'of', 'i', 'but', 'so', 'like', 'for', 'when', 'that', 'who',
        'this', 'my', "i'm", "i'll", 'as', 'with', 'even', 'has', 'some'}


def wrap_words(words, f, forced=None):
    if forced:
        return forced
    """Return list of rows (list of word indices), balanced, each <= MAX_TEXT_W."""
    dr = ImageDraw.Draw(Image.new('L', (8, 8)))
    sw = dr.textlength(' ', font=f)
    ww = [dr.textlength(w, font=f) for w in words]

    def width(a, b):
        return sum(ww[a:b]) + sw * (b - a - 1)
    n = len(words)
    if width(0, n) <= MAX_TEXT_W:
        return [list(range(n))]
    best = None
    for k in ((2, 3, 4) if SHORTS else (2, 3)):
        # brute-force balanced split into k rows
        import itertools
        for cuts in itertools.combinations(range(1, n), k - 1):
            b = (0,) + cuts + (n,)
            wid = [width(b[j], b[j + 1]) for j in range(k)]
            if max(wid) > MAX_TEXT_W:
                continue
            # prefer balanced rows; avoid single-word rows; avoid ending a row on a weak word
            score = max(wid) - min(wid) * 0.5 + (400 if any(b[j + 1] - b[j] == 1 for j in range(k)) else 0)
            for j in range(k - 1):
                last = words[b[j + 1] - 1].lower().strip('",.!?()')
                if last in WEAK:
                    score += 260
                if words[b[j + 1] - 1][-1] in ',.!?;' or words[b[j + 1] - 1].endswith('...'):
                    score -= 120
            if best is None or score < best[0]:
                best = (score, b)
        if best:
            b = best[1]
            return [list(range(b[j], b[j + 1])) for j in range(len(b) - 1)]
    raise ValueError('line too long: ' + ' '.join(words))


def build_lines(lyrics):
    lines = []
    dr = ImageDraw.Draw(Image.new('L', (8, 8)))
    sw = dr.textlength(' ', font=F_LYR)
    ypos = 0.0
    for item in lyrics:
        L = Line()
        L.kind = item.get('kind', 'line')
        if L.kind == 'dots':
            L.start, L.end = item['start'], item['end']
            L.h = 60
            L.y = ypos
            ypos += L.h + LINE_GAP
            lines.append(L)
            continue
        words = [w['w'] for w in item['words']]
        forced = None
        if item.get('breaks'):
            forced, k = [], 0
            for n in item['breaks']:
                forced.append(list(range(k, k + n)))
                k += n
            assert k == len(words), item
        rows = wrap_words(words, F_LYR, forced)
        L.h = ROW_H * len(rows)
        img = Image.new('L', (W, L.h), 0)
        d = ImageDraw.Draw(img)
        # per-row column time maps
        L.tmap = np.full((L.h, W), 1e9, np.float32)
        for ri, row in enumerate(rows):
            ws = [words[i] for i in row]
            wl = [dr.textlength(w, font=F_LYR) for w in ws]
            total = sum(wl) + sw * (len(ws) - 1)
            x = (W - total) / 2
            base = ri * ROW_H + int(ROW_H * 0.74)
            tm = np.full(W, 1e9, np.float32)
            prev_end_x, prev_end_t = None, None
            for wi, w, wlen in zip(row, ws, wl):
                d.text((x, base), w, font=F_LYR, fill=255, anchor='ls')
                s = item['words'][wi]['s']
                e = item['words'][wi]['e']
                e = s + min(max(e - s, 0.14), 1.6)
                x0, x1 = int(math.floor(x)) - 2, int(math.ceil(x + wlen)) + 2
                cols = np.arange(max(x0, 0), min(x1, W))
                tm[cols] = s + (cols - x0) / max(x1 - x0, 1) * (e - s)
                if prev_end_x is not None:
                    gap = np.arange(prev_end_x, max(x0, prev_end_x))
                    tm[gap] = prev_end_t
                prev_end_x, prev_end_t = x1, e
                x += wlen + sw
            # columns left of the first word light with the first word; right of the last stay with last
            first = np.argmax(tm < 1e8)
            tm[:first] = tm[first]
            lastx = W - 1 - np.argmax(tm[::-1] < 1e8)
            tm[lastx:] = tm[lastx]
            L.tmap[ri * ROW_H:(ri + 1) * ROW_H] = tm[None, :]
        a = np.asarray(img, np.float32) / 255.0
        L.alpha = a
        sh = cv2.GaussianBlur(np.pad(a, ((20, 20), (0, 0))), (0, 0), 9)
        L.shadow = sh  # padded 20px top/bottom
        L.start = item['words'][0]['s']
        L.end = item['words'][-1]['e']
        L.y = ypos
        ypos += L.h + LINE_GAP
        lines.append(L)
    for L in lines:
        L.c = L.y + L.h / 2
    return lines


SCROLL_LEAD = 0.42
SCROLL_DUR = 0.60


def scroll_pos(lines, t):
    p = lines[0].c
    for i in range(1, len(lines)):
        s = lines[i].start - SCROLL_LEAD
        # never leave a line before it has finished being sung (unless the next line is already starting)
        s = max(s, min(lines[i - 1].end, lines[i].start - 0.12))
        if lines[i].kind == 'dots':
            s = lines[i].start
        if t <= s:
            break
        p += ease((t - s) / SCROLL_DUR) * (lines[i].c - lines[i - 1].c)
    return p


def render_lyrics(lines, t):
    """Returns (alpha, shadow) arrays for region LYR_TOP..LYR_BOT."""
    RH = LYR_BOT - LYR_TOP
    A = np.zeros((RH, W), np.float32)
    S = np.zeros((RH + 40, W), np.float32)
    P = scroll_pos(lines, t)
    for i, L in enumerate(lines):
        top = FOCUS_Y + (L.y - P) - LYR_TOP
        if top > RH or top + L.h < 0:
            continue
        d = (L.c - P)
        pitch = 140.0
        fw = max(0.0, 1.0 - abs(d) / pitch)      # 1 at focus
        if L.kind == 'dots':
            draw_dots(A, L, t, int(round(top)), fw)
            continue
        # karaoke reveal
        R = smooth((t - L.tmap) / 0.10 + 0.5)
        # after a line has been sung and a long gap follows, relax it back to dim
        nxt = lines[i + 1].start if i + 1 < len(lines) else 1e9
        if nxt - L.end > 3.5:
            relax = smooth((t - L.end - 1.4) / 1.0)
            R = R * (1 - relax)
        dim = DIM if d >= 0 else DIM - 0.08 * min(1.0, -d / pitch)
        # the line being sung lights on time even while the scroll is still settling
        fwl = max(fw, 0.85) if (L.start - 0.05 <= t <= L.end + 0.4) else fw
        level = dim + (1 - dim) * R * fwl
        a = L.alpha * level
        it = int(round(top))
        y0, y1 = max(it, 0), min(it + L.h, RH)
        A[y0:y1] += a[y0 - it:y1 - it]
        sy0, sy1 = max(it, 0), min(it + L.h + 40, RH + 40)
        S[sy0:sy1] += (L.shadow[sy0 - it:sy1 - it]) * (0.35 + 0.65 * fw)
    # vertical fade mask for the lyric window
    yy = np.arange(RH, dtype=np.float32)
    fade = smooth((yy - 10) / FADE_T) ** 1.6 * smooth((RH - yy) / FADE_B)
    A *= fade[:, None]
    S = S[20:RH + 20] * fade[:, None]
    return np.clip(A, 0, 1), np.clip(S, 0, 1) * 0.62


def draw_dots(A, L, t, top, fw):
    """Apple-Music style breathing dots that fill up across an instrumental gap."""
    RH = A.shape[0]
    cy = top + L.h // 2
    if cy < -30 or cy > RH + 30:
        return
    prog = (t - L.start) / max(L.end - L.start, 0.1)
    breathe = 1 + 0.10 * math.sin(2 * math.pi * t / 2.4)
    # shrink away at the end
    out = smooth((L.end - t) / 0.35) if t > L.end - 0.35 else 1.0
    inn = smooth((t - L.start) / 0.4)
    sc = breathe * out * inn
    if sc <= 0.01:
        return
    for k in range(3):
        fill = float(np.clip(prog * 3 - k, 0, 1))
        lvl = (DIM + (1 - DIM) * fill) * max(fw, 0.0)
        r = 11 * sc
        cx = W / 2 + (k - 1) * 40 * sc
        x0, x1 = int(cx - r - 3), int(cx + r + 4)
        y0, y1 = int(cy - r - 3), int(cy + r + 4)
        if y0 < 0 or y1 > RH:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        dd = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        A[y0:y1, x0:x1] += np.clip(r - dd + 0.5, 0, 1) * lvl


# ---------------------------------------------------------------- compositor
class Renderer:
    def __init__(self, lyrics):
        self.st = build_static()
        self.lines = build_lines(lyrics)
        self.env = audio_envelope()
        self.time_cache = {}
        self.ov_cache = {}

    def overlay(self, name, f):
        """K (multiplier) and C (additive) arrays for a static layer at fade f."""
        key = (name, round(f, 4))
        if f >= 1 and key in self.ov_cache:
            return self.ov_cache[key]
        st = self.st
        if name == 'art':
            sh = st['shadow'] * f
            P = (sh.shape[0] - ART) // 2
            m = np.zeros_like(sh); e = np.zeros_like(sh); art = np.zeros(sh.shape[:2] + (3,), np.float32)
            m[P:P + ART, P:P + ART] = st['art_m'] * f
            e[P:P + ART, P:P + ART] = st['art_edge'] * f
            art[P:P + ART, P:P + ART] = st['art']
            K = (1 - sh) * (1 - m) * (1 - e)
            C = art * m * (1 - e) + 255 * e
            xy = st['shadow_xy']
        elif name == 'title':
            a = st['title_a'] * f
            K = (1 - st['title_sh'] * f) * (1 - a)
            C = st['title_col'] * a
            xy = (0, 0)
        else:
            a = st['credit'] * f
            K = 1 - a
            C = 255 * a
            xy = (0, 1712)
        K = np.ascontiguousarray(np.broadcast_to(K, K.shape[:2] + (3,)), np.float32)
        C = np.ascontiguousarray(np.broadcast_to(C, C.shape[:2] + (3,)), np.float32)
        out = (K, C, xy)
        if f >= 1:
            self.ov_cache[key] = out
        return out

    def time_label(self, s, align):
        key = (s, align)
        if key not in self.time_cache:
            img = Image.new('L', (160, 40), 0)
            d = ImageDraw.Draw(img)
            if align == 'l':
                d.text((0, 30), s, font=F_TIME, fill=255, anchor='ls')
            else:
                d.text((159, 30), s, font=F_TIME, fill=255, anchor='rs')
            self.time_cache[key] = np.asarray(img, np.float32)[..., None] / 255.0
        return self.time_cache[key]

    def frame(self, t):
        st = self.st
        fi = min(int(t * FPS), len(self.env) - 1)
        env = float(self.env[fi])
        # ---- background (slow drift / zoom)
        # background drifts very slowly: rebuild it every other frame and reuse it in between
        bkey = fi // 2
        if getattr(self, '_bg_key', None) != bkey:
            bg = st['bg']
            bs = bg.shape[0]
            tb = bkey * 2 / FPS
            # computed at half resolution (it is all soft, low-frequency light) then upscaled
            hs = 0.5
            scale = (H / bs) * 1.18 * (1 + 0.035 * math.sin(2 * math.pi * tb / 71.0)) * hs
            cx = bs / 2 + 22 * math.sin(2 * math.pi * tb / 53.0)
            cy = bs / 2 + 28 * math.sin(2 * math.pi * tb / 67.0 + 1.3)
            M = np.array([[scale, 0, W * hs / 2 - scale * cx], [0, scale, H * hs / 2 - scale * cy]], np.float32)
            small = cv2.warpAffine(bg, M, (W // 2, H // 2), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            small += st['glow_h'] * (0.50 + 0.65 * env)
            small *= st['vig_h']
            self._bg = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
            self._bg_key = bkey
        img = self._bg.copy()
        draw_embers(img, t, st, (0.75 + 0.8 * env) * 0.8 * CFG.get('ember_gain', 1.0))

        intro = smooth((t - 0.15) / 1.3)
        ti = smooth((t - 0.35) / 1.2)
        bi = smooth((t - 0.8) / 1.0)
        # ---- static overlays (art card, title, credit) as  out = img*K + C
        for name, f in (('art', intro), ('title', ti)):
            if f <= 0:
                continue
            K, C, (x0, y0) = self.overlay(name, f)
            reg = img[y0:y0 + K.shape[0], x0:x0 + K.shape[1]]
            cv2.multiply(reg, K, dst=reg)
            cv2.add(reg, C, dst=reg)

        # ---- lyrics
        A, S = render_lyrics(self.lines, t)
        lyr_in = smooth((t - 0.5) / 1.0)
        if lyr_in > 0:
            A *= lyr_in
            S *= lyr_in
            K = (1 - S) * (1 - A)
            C = A * 255
            reg = img[LYR_TOP:LYR_BOT]
            cv2.multiply(reg, cv2.merge([K, K, K]), dst=reg)
            cv2.add(reg, cv2.merge([C, C, C]), dst=reg)

        # ---- progress bar + times (not in Shorts layout)
        if not SHORTS:
            prog = min(max(t / DUR, 0), 1)
            bx = BAR_X0 + prog * (BAR_X1 - BAR_X0)
            y0, y1 = BAR_Y - 2, BAR_Y + 2
            img[y0:y1, BAR_X0:BAR_X1] = img[y0:y1, BAR_X0:BAR_X1] * (1 - 0.20 * bi) + 255 * 0.20 * bi
            xb = int(bx)
            img[y0:y1, BAR_X0:xb] = img[y0:y1, BAR_X0:xb] * (1 - 0.65 * bi) + 255 * 0.65 * bi
            # knob
            r = 6
            kx0, ky0 = xb - r - 2, BAR_Y - r - 2
            yy, xx = np.mgrid[ky0:ky0 + 2 * r + 5, kx0:kx0 + 2 * r + 5].astype(np.float32)
            k = np.clip(r - np.sqrt((xx - bx) ** 2 + (yy - BAR_Y) ** 2) + 0.5, 0, 1)[..., None] * 0.9 * bi
            kreg = img[ky0:ky0 + 2 * r + 5, kx0:kx0 + 2 * r + 5]
            kreg[:] = kreg * (1 - k) + 255 * k
            el = int(t)
            rem = int(math.ceil(DUR - t))
            lab_l = self.time_label(f'{el // 60}:{el % 60:02d}', 'l')
            lab_r = self.time_label(f'-{rem // 60}:{rem % 60:02d}', 'r')
            for lab, x0 in ((lab_l, BAR_X0), (lab_r, BAR_X1 - 160)):
                reg = img[BAR_Y + 10:BAR_Y + 50, x0:x0 + 160]
                a = lab * 0.5 * bi
                reg[:] = reg * (1 - a) + 255 * a

        # ---- global fades
        g = smooth(t / 0.9) * smooth((DUR - t) / 2.2)
        if g < 1:
            img *= g
        # dither + quantise
        return cv2.convertScaleAbs(img)


def main():
    lyr = json.load(open(sys.argv[1]))
    R = Renderer(lyr)
    if sys.argv[2] == '--stills':
        for ts in sys.argv[3:]:
            t = float(ts)
            cv2.imwrite(f'{WORK}/still_{t:07.2f}.png', R.frame(t))
            print('still', t)
        return
    out = sys.argv[2]
    t0, t1 = 0.0, DUR
    if '--range' in sys.argv:
        k = sys.argv.index('--range')
        t0, t1 = float(sys.argv[k + 1]), float(sys.argv[k + 2])
    f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
           '-c:v', 'libx264', '-preset', os.environ.get('RENDER_PRESET', 'slow'), '-crf', os.environ.get('RENDER_CRF', '16'),
           '-tune', 'film', '-x264-params', 'aq-mode=3']
    if os.environ.get('RENDER_MAXRATE'):
        mr = int(os.environ['RENDER_MAXRATE'])
        cmd += ['-maxrate', f'{mr}k', '-bufsize', f'{mr * 2}k']
    cmd += [
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
           out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    tic = time.time()
    for f in range(f0, f1):
        p.stdin.write(R.frame(f / FPS).tobytes())
        if f % 300 == 0:
            el = time.time() - tic
            print(f'frame {f}/{f1}  {el:.0f}s', flush=True)
    p.stdin.close()
    p.wait()
    print('done', time.time() - tic)


if __name__ == '__main__':
    main()
