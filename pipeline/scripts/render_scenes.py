#!/usr/bin/env python3
"""Scene-reel lyric video: Meta AI stills matched to lyric lines, slow push-in, crossfades,
word-by-word lyrics placed mid-screen (clear of Facebook/Reels buttons and caption).

usage: render_scenes.py PLAN.json OUT_video_only.mp4
PLAN.json: {"lyrics": ".../lyrics_final.json", "dur": 252.0, "title": "...",
            "images": [paths in prompt order], "cuts": [[t, img_index_1based], ...]}
"""
import sys, json, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, XF = 1080, 1920, 30, 0.8
plan = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
DUR = float(plan['dur'])
LINES = json.load(open(plan['lyrics']))
FONT = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 62)
F_NAME = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 40)
F_TITLE = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Black.otf', 104)
TEXT_Y = 860          # centre of lyric block (mid-screen, above Reels caption/buttons)
ACCENT = (255, 196, 120)


def load(p):
    im = cv2.imread(p, cv2.IMREAD_COLOR)
    if im is None:
        im = cv2.cvtColor(np.array(Image.open(p).convert('RGB')), cv2.COLOR_RGB2BGR)
    h, w = im.shape[:2]
    s = max(W * 1.12 / w, H * 1.12 / h)          # room for the push-in and drift
    return cv2.resize(im, (round(w * s), round(h * s)), interpolation=cv2.INTER_LANCZOS4)


imgs = [load(p) for p in plan['images']]
cuts = [(float(t), int(i) - 1) for t, i in plan['cuts']]


def kb(k, t0, t1, t):
    """slow push-in, alternate drift direction per scene"""
    src = imgs[cuts[k][1]]
    u = (t - t0) / max(t1 - t0, 1e-3)
    z = 1.0 + 0.07 * u
    sh, sw = src.shape[:2]
    f = min(sw / W, sh / H)               # src px per output px at full view
    cw, ch = W * f / z, H * f / z
    d = 1 if k % 2 == 0 else -1
    cx = sw / 2 + d * (sw - cw) * 0.35 * (u - 0.5)
    cy = sh / 2 - (sh - ch) * 0.2 * (u - 0.5)
    sx, sy = W / cw, H / ch
    M = np.float32([[sx, 0, -(cx - cw / 2) * sx], [0, sy, -(cy - ch / 2) * sy]])
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def scene(t):
    def span(k):
        return cuts[k][0] - XF, (cuts[k + 1][0] if k + 1 < len(cuts) else DUR) + XF
    k = max([0] + [i for i, (c, _) in enumerate(cuts) if c - XF / 2 <= t])
    a = kb(k, *span(k), t)
    c = cuts[k][0]
    if k > 0 and t < c + XF / 2:
        b = kb(k - 1, *span(k - 1), t)
        m = (t - (c - XF / 2)) / XF
        m = m * m * (3 - 2 * m)
        a = cv2.addWeighted(b, 1 - m, a, m, 0)
    return a


# readability band: soft darkening behind the lyric area only
yy = np.arange(H, dtype=np.float32)[:, None]
band = np.exp(-((yy - TEXT_Y) / 330.0) ** 2) * 0.55
SHADE = (1 - band).astype(np.float32)[:, :, None]

# ---- lyrics: pre-layout every line into <=2 rows
dr = ImageDraw.Draw(Image.new('L', (8, 8)))
SP = dr.textlength(' ', font=FONT)


def layout(words):
    ws = [w['w'] for w in words]
    L = [dr.textlength(w, font=FONT) for w in ws]
    MAXW = 900

    def wid(a, b):
        return sum(L[a:b]) + SP * (b - a - 1)
    n = len(ws)
    if wid(0, n) <= MAXW:
        rows = [list(range(n))]
    else:
        best2 = min(range(1, n), key=lambda b: max(wid(0, b), wid(b, n)))
        if max(wid(0, best2), wid(best2, n)) <= MAXW or n < 3:
            rows = [list(range(best2)), list(range(best2, n))]
        else:
            b1, b2 = min(((a, b) for a in range(1, n - 1) for b in range(a + 1, n)),
                         key=lambda ab: max(wid(0, ab[0]), wid(ab[0], ab[1]), wid(ab[1], n)))
            rows = [list(range(b1)), list(range(b1, b2)), list(range(b2, n))]
    pos = []
    RH = 86
    y0 = TEXT_Y - RH * (len(rows) - 1) / 2
    for r, row in enumerate(rows):
        rw = sum(L[i] for i in row) + SP * (len(row) - 1)
        x = (W - rw) / 2
        for i in row:
            pos.append((i, x, y0 + r * RH)); x += L[i] + SP
    pos.sort()
    return ws, [(x, y) for _, x, y in pos]


LAY = []
for n, l in enumerate(LINES):
    w = l['words']
    s, e = w[0]['s'], w[-1]['e']
    nxt = LINES[n + 1]['words'][0]['s'] if n + 1 < len(LINES) else DUR
    end = min(e + 1.2, nxt - 0.3 - 0.3)
    ws, ps = layout(w)
    LAY.append(dict(s=s - 0.3, e=end, words=w, ws=ws, ps=ps))


def draw_text(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh)
    for ln in LAY:
        if not (ln['s'] <= t <= ln['e'] + 0.25):
            continue
        fa = min(1, (t - ln['s']) / 0.25) * min(1, max(0, (ln['e'] + 0.25 - t) / 0.25))
        for w, txt, (x, y) in zip(ln['words'], ln['ws'], ln['ps']):
            if t >= w['e']:
                col, a = (255, 255, 255), 1.0
            elif t >= w['s']:
                col, a = ACCENT, 1.0
            else:
                col, a = (255, 255, 255), 0.5
            A = int(255 * a * fa)
            d.text((x, y), txt, font=FONT, fill=col + (A,), anchor='lm')
            ds.text((x, y + 3), txt, font=FONT, fill=(0, 0, 0, int(200 * fa)), anchor='lm')
    # title card at the start and end card at the finish
    for ta, tb in ((0.0, 3.5), (245.0, DUR)):
        if ta <= t <= tb:
            fa = min(1, (t - ta) / 0.6, (tb - t) / 0.6) if tb < DUR else min(1, (t - ta) / 0.8)
            fa = max(0.0, fa)
            for dd, f, txt, y, c in ((d, F_NAME, 'ZACHARY PATZER', TEXT_Y - 110, (255, 255, 255)),
                                     (d, F_TITLE, "THAT'D BE EASY", TEXT_Y + 10, ACCENT)):
                ds.text((W / 2, y + 4), txt, font=f, fill=(0, 0, 0, int(210 * fa)), anchor='mm')
                dd.text((W / 2, y), txt, font=f, fill=c + (int(255 * fa),), anchor='mm')
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(sh, im)


def main():
    N = int(DUR * FPS)
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                           '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
    for f in range(N):
        t = f / FPS
        bg = (scene(t).astype(np.float32) * SHADE)
        if t < 1.0:
            bg *= t
        tx = np.array(draw_text(t))
        a = tx[:, :, 3:4].astype(np.float32) / 255
        rgb = tx[:, :, 2::-1].astype(np.float32)
        out = bg * (1 - a) + rgb * a
        ff.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
        if f % 900 == 0:
            print(f'{t:.0f}s', flush=True)
    ff.stdin.close(); ff.wait()


if __name__ == '__main__':
    if len(sys.argv) > 3 and sys.argv[3] == '--stills':
        for ts in sys.argv[4:]:
            t = float(ts)
            bg = scene(t).astype(np.float32) * SHADE
            tx = np.array(draw_text(t)); a = tx[:, :, 3:4] / 255
            out = bg * (1 - a) + tx[:, :, 2::-1] * a
            cv2.imwrite(OUT.replace('.mp4', f'_{ts}.jpg'), np.clip(out, 0, 255).astype(np.uint8))
    else:
        main()
