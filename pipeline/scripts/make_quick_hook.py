#!/usr/bin/env python3
"""Quick 10-15 s scroll-stopper Short: full-bleed cover art, push-in + beat punches,
big word-by-word captions, a hook line on screen from frame 1 and a payoff line at the end.
Audio is cut from an existing finished Short (already -14 LUFS).
usage: make_quick_hook.py CFG.json"""
import sys, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor

C = json.load(open(sys.argv[1]))
W, H, FPS = 1080, 1920, 30
CAP_SZ, CAP_W = 86, 780
FB = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
s0, s1 = C['song_start'], C['song_end']          # song-time window
T = s1 - s0
ACC = C.get('accent', '#ff3640')

# words in window, shifted to clip time, grouped by line
lines = []
for x in json.load(open(C['lyrics'])):
    if 'words' not in x:
        continue
    ws = [(w['w'], w['s'] - s0, w['e'] - s0) for w in x['words'] if s0 - 0.05 <= w['s'] < s1]
    if ws:
        lines.append(ws)

# background crop of the square cover (face + ring, no title)
src = Image.open(C['cover']).convert('RGB')
if C.get('hide_top') and 'crop_cx' in C:   # replace the cover's own title band with stretched smoke from just below it
    k = C['hide_top']
    band = src.crop((0, k, src.width, k + 60)).resize((src.width, k), Image.BICUBIC).filter(ImageFilter.GaussianBlur(25))
    band = Image.blend(band, Image.new('RGB', band.size, (0, 0, 0)), 0.35)
    m = Image.new('L', (src.width, k), 255); md = ImageDraw.Draw(m)
    for y in range(k - 60, k):
        md.line([(0, y), (src.width, y)], fill=int(255 * (k - y) / 60))
    src.paste(band, (0, 0), m)
if 'crop_cx' in C:
  cx, cy, ch = C['crop_cx'], C['crop_cy'], C['crop_h']
  cw = ch * W / H
  base = src.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W * 2, H * 2), Image.LANCZOS)

# static overlays: vignette + dark bands top/bottom for text
shade = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(shade)
for y in range(H):
    a = 0
    if y < 620: a = int(200 * (1 - y / 620) ** 1.3)
    if y > 1040: a = max(a, int(215 * min(1, (y - 1040) / 420) ** 1.1))
    sd.line([(0, y), (W, y)], fill=a)
dark = Image.new('RGB', (W, H), (0, 0, 0))

# ---- 'studio' background: works for every song (his portrait over a living dark set) ----
STUDIO = C.get('bg') in ('studio', 'cover_blur')
COVERBG = C.get('bg') == 'cover_blur'
if STUDIO:
    import numpy as np, cv2
    rng = np.random.default_rng(7)
    P = '/home/claude/zachary-shorts/pipeline/assets/'
    fs = cv2.cvtColor(cv2.imread(P + 'face_src.jpg'), cv2.COLOR_BGR2RGB).astype(np.float32)
    fm = cv2.resize(cv2.imread(P + 'face_matte.png', 0), (fs.shape[1], fs.shape[0])).astype(np.float32) / 255
    fh, fw = fm.shape
    fm = cv2.GaussianBlur(cv2.erode(fm, np.ones((9, 9), np.uint8)), (0, 0), 6)
    hsv = cv2.cvtColor(fs.astype(np.uint8), cv2.COLOR_RGB2HSV)       # grey out the old cover's embers on the hoodie
    em = (((hsv[..., 0] < 25) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 90) & (hsv[..., 2] > 70)).astype(np.float32)
    reg = np.zeros((fh, fw), np.float32); reg[680:, :] = 1; reg[680:960, 360:780] = 0
    em = cv2.GaussianBlur(cv2.dilate(em * reg, np.ones((9, 9), np.uint8)), (0, 0), 3)
    g = cv2.cvtColor(cv2.cvtColor(fs.astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2RGB).astype(np.float32) * 0.55
    fs = fs * (1 - em[..., None]) + g * em[..., None]
    yy, xx = np.mgrid[0:fh, 0:fw]
    fade = np.clip((1.05 - np.sqrt(((xx - 540) / 560) ** 2 + ((yy - 430) / 640) ** 2)) / 0.30, 0, 1) * np.clip((fh - yy) / 220, 0, 1)
    fa = fm * fade
    PW = C.get('portrait_w', 1040); PY = C.get('portrait_top', 400)

    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    glow = np.exp(-(((X - W / 2) / 560) ** 2 + ((Y - 860) / 760) ** 2))             # soft light behind him
    beam = np.clip(1 - np.abs(X - W / 2) / (90 + Y * 0.42), 0, 1) ** 1.6 * np.clip(1 - Y / 1500, 0, 1)
    hz = cv2.resize(rng.random((24, 14)).astype(np.float32), (W * 2, H), interpolation=cv2.INTER_CUBIC)
    hz = cv2.GaussianBlur(hz, (0, 0), 40); hz = (hz - hz.min()) / (np.ptp(hz) + 1e-6)
    NP = 150
    px, py = rng.random(NP) * W, rng.random(NP) * H
    pv = 6 + rng.random(NP) * 18; pr = rng.choice([1, 2, 2, 3, 4], NP); ph = rng.random(NP) * 6.28
    cool, warm = np.array([0.55, 0.66, 0.85]), np.array([1.0, 0.72, 0.48])
    if COVERBG:   # the song's own cover, filled to 9:16, softly blurred and dimmed behind the sharp portrait
        cv_ = cv2.cvtColor(np.asarray(src), cv2.COLOR_RGB2BGR)[..., ::-1].astype(np.float32)
        sc = H * 1.12 / cv_.shape[0]
        cv_ = cv2.resize(cv_, (int(cv_.shape[1] * sc), int(cv_.shape[0] * sc)), interpolation=cv2.INTER_CUBIC)
        cv_ = cv2.GaussianBlur(cv_, (0, 0), C.get('bg_blur', 7)) * C.get('bg_gain', 0.62)
        CB = cv_

    def studio_frame(t, z, flash):
        k = t / T
        tint = cool * (1 - k) + warm * k
        if COVERBG:
            zb = 1 + (z - 1) * 0.5
            bh_, bw_ = CB.shape[:2]; vh, vw = H / zb * (bh_ / (H * 1.12)), W / zb * (bh_ / (H * 1.12))
            y0b, x0b = (bh_ - vh) / 2, (bw_ - vw) / 2
            img = cv2.resize(CB[int(y0b):int(y0b + vh), int(x0b):int(x0b + vw)], (W, H), interpolation=cv2.INTER_LINEAR)
            tint = np.array([1.0, 1.0, 1.0])
        else:
            lvl = 0.9 + 0.1 * np.sin(t * 1.3)
            h = np.roll(hz, int(t * 22), axis=1)[:, :W]
            lum = 10 + 70 * glow * (0.85 + 0.25 * k) + 46 * beam * lvl + 26 * h * glow
            img = lum[..., None] * tint[None, None, :]
        dots = np.zeros((H, W), np.float32)
        for j in range(NP):
            x = (px[j] + 14 * np.sin(t * 0.4 + ph[j])) % W; y = (py[j] - pv[j] * t) % H
            cv2.circle(dots, (int(x), int(y)), int(pr[j]), float(120 + 120 * (0.5 + 0.5 * np.sin(t * 2 + ph[j]))), -1, cv2.LINE_AA)
        dots = cv2.GaussianBlur(dots, (0, 0), 1.6) * (0.35 + 0.65 * glow)
        img += dots[..., None] * (tint * 0.6 + 0.4)[None, None, :]
        # portrait with push-in
        sw = int(PW * z); sh = int(fh * sw / fw)
        fr_ = cv2.resize(fs, (sw, sh), interpolation=cv2.INTER_AREA if z < 1 else cv2.INTER_LINEAR)
        fa_ = cv2.resize(fa, (sw, sh))
        x0 = (W - sw) // 2; y0 = int(PY - (sh - fh * PW / fw) * 0.35)
        ys, xs = max(0, y0), max(0, x0); ye, xe = min(H, y0 + sh), min(W, x0 + sw)
        sub = fr_[ys - y0:ye - y0, xs - x0:xe - x0]; a = fa_[ys - y0:ye - y0, xs - x0:xe - x0][..., None]
        img[ys:ye, xs:xe] = img[ys:ye, xs:xe] * (1 - a) + sub * (0.92 + 0.12 * k) * a
        img = np.clip(img + rng.normal(0, 3.0, (H // 4, W // 4)).repeat(4, 0).repeat(4, 1)[..., None], 0, 255)   # film grain
        out = Image.fromarray(img.astype(np.uint8))
        out = Image.composite(dark, out, shade)
        if flash:
            out = Image.blend(out, Image.new('RGB', (W, H), ImageColor.getrgb(ACC)), flash * (0.45 if COVERBG else 0.7))
        return out

_d = ImageDraw.Draw(Image.new('RGB', (10, 10))); _f = ImageFont.truetype(FB, CAP_SZ)
def _rows(ws):
    rows, cur = 1, ''
    for w in ws:
        t = (cur + ' ' + w).strip()
        if cur and _d.textlength(t, font=_f) > CAP_W: rows += 1; cur = w
        else: cur = t
    return rows
def _split(ln, k):   # k contiguous groups, balanced by character length
    tot = sum(len(w[0]) + 1 for w in ln); out, cur, acc = [], [], 0
    for i, w in enumerate(ln):
        cur.append(w); acc += len(w[0]) + 1
        left = len(ln) - i - 1
        if len(out) < k - 1 and acc >= tot * (len(out) + 1) / k and left >= k - 1 - len(out):
            out.append(cur); cur = []
    out.append(cur); return [g for g in out if g]
chunks = []
for ln in lines:
    k = 1
    while True:
        gs = _split(ln, k)
        if all(_rows([w[0] for w in g]) <= 2 for g in gs) or k >= len(ln): break
        k += 1
    chunks.extend(gs)
lines = chunks
if 'payoff_at' not in C:
    C['payoff_at'] = max(T * 0.6, lines[-1][0][1] - 0.1)
punches = [p for p in C.get('punch_words', [])]
hits = []
for ln in lines:
    for w, s, e in ln:
        if w.lower().strip('.,!?') in punches:
            hits.append(s)
hits.append(0.0)


def font(sz):
    return ImageFont.truetype(FB, sz)


def text_block(d, rows, y, sz, cols, stroke=10):
    f = font(sz); lh = int(sz * 1.12)
    for i, r in enumerate(rows):
        d.text((W / 2, y + i * lh), r, font=f, fill=cols[i], anchor='mt', stroke_width=stroke, stroke_fill=(0, 0, 0))
    return y + len(rows) * lh


def fit(d, rows, sz, maxw):
    while sz > 40 and max(d.textlength(r, font=font(sz)) for r in rows) > maxw:
        sz -= 2
    return sz


def wrap(words, f, d, maxw):
    rows, cur = [], []
    for w in words:
        t = ' '.join(cur + [w])
        if cur and d.textlength(t, font=f) > maxw:
            rows.append(cur); cur = [w]
        else:
            cur.append(w)
    rows.append(cur)
    return rows


ff = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-ss', f"{C['audio_off']:.3f}", '-t', f'{T:.3f}', '-i', C['audio_src'],
                       '-map', '0:v', '-map', '1:a', '-af', f'afade=t=in:d=0.04,afade=t=out:st={T - 0.12:.3f}:d=0.12',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', C['out']], stdin=subprocess.PIPE)

N = int(T * FPS)
for i in range(N):
    t = i / FPS
    # zoom: slow push + decaying punch on hit words
    z = 1.0 + 0.07 * t / T
    flash = 0.0
    for h in hits:
        if 0 <= t - h < 0.45:
            k = 1 - (t - h) / 0.45
            z += 0.06 * k * k
            flash = max(flash, 0.32 * k * k if h > 0 else 0)
    if STUDIO:
        fr = studio_frame(t, z, flash)
    else:
        bw, bh = base.size
        vw, vh = bw / 2 / z, bh / 2 / z
        ox, oy = (bw - vw * 2) / 2 / 1, (bh - vh * 2) / 2
        fr = base.crop((int(ox), int(oy), int(ox + vw * 2), int(oy + vh * 2))).resize((W, H), Image.BILINEAR)
        fr = Image.composite(dark, fr, shade)
        if flash:
            fr = Image.blend(fr, Image.new('RGB', (W, H), ImageColor.getrgb(C.get('flash_col', ACC))), flash * C.get('flash_gain', 0.6))
    d = ImageDraw.Draw(fr)

    # top hook (frame 1) -> payoff near the end
    if t < C['payoff_at']:
        rows, cols = C['hook'], ['#ffffff'] * (len(C['hook']) - 1) + [ACC]
    else:
        rows, cols = C['payoff'], ['#ffffff'] * (len(C['payoff']) - 1) + [ACC]
    sz = fit(d, rows[:-1], 78, 900) if len(rows) > 1 else 78
    y = C.get('hook_y', 230)
    y = text_block(d, rows[:-1], y, sz, cols[:-1], stroke=8)
    big = fit(d, rows[-1:], 150, 940)
    text_block(d, rows[-1:], y + 6, big, cols[-1:], stroke=12)

    # captions: current line, words appear as sung, current word in accent
    cur = None
    for ln in lines:
        if ln[0][1] - 0.15 <= t:
            cur = ln
    if cur:
        f = font(CAP_SZ)
        words = [w for w, s, e in cur]
        rws = wrap(words, f, d, CAP_W)
        k = 0; yy = 1200; lh = 104
        for r in rws:
            full = ' '.join(r); x = W / 2 - d.textlength(full, font=f) / 2
            for w in r:
                _, s, e = cur[k]; k += 1
                if t >= s - 0.04:
                    on = s - 0.04 <= t < e + 0.08
                    pop = 1.0
                    col = ACC if on else '#ffffff'
                    d.text((x, yy), w, font=f, fill=col, stroke_width=10, stroke_fill=(0, 0, 0))
                x += d.textlength(w + ' ', font=f)
            yy += lh
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait()
print(C['out'], f'{T:.2f}s')
