#!/usr/bin/env python3
"""Quick 10-15 s scroll-stopper Short: full-bleed cover art, push-in + beat punches,
big word-by-word captions, a hook line on screen from frame 1 and a payoff line at the end.
Audio is cut from an existing finished Short (already -14 LUFS).
usage: make_quick_hook.py CFG.json"""
import sys, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

C = json.load(open(sys.argv[1]))
W, H, FPS = 1080, 1920, 30
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
if C.get('hide_top'):   # replace the cover's own title band with stretched smoke from just below it
    k = C['hide_top']
    band = src.crop((0, k, src.width, k + 60)).resize((src.width, k), Image.BICUBIC).filter(ImageFilter.GaussianBlur(25))
    band = Image.blend(band, Image.new('RGB', band.size, (0, 0, 0)), 0.35)
    m = Image.new('L', (src.width, k), 255); md = ImageDraw.Draw(m)
    for y in range(k - 60, k):
        md.line([(0, y), (src.width, y)], fill=int(255 * (k - y) / 60))
    src.paste(band, (0, 0), m)
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
    bw, bh = base.size
    vw, vh = bw / 2 / z, bh / 2 / z
    ox, oy = (bw - vw * 2) / 2 / 1, (bh - vh * 2) / 2
    fr = base.crop((int(ox), int(oy), int(ox + vw * 2), int(oy + vh * 2))).resize((W, H), Image.BILINEAR)
    fr = Image.composite(dark, fr, shade)
    if flash:
        fr = Image.blend(fr, Image.new('RGB', (W, H), (170, 0, 10)), flash)
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
        f = font(98)
        words = [w for w, s, e in cur]
        rws = wrap(words, f, d, 840)
        k = 0; yy = 1220; lh = 116
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
