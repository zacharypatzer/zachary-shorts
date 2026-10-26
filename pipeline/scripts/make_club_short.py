#!/usr/bin/env python3
"""Club-style quick Short: black stage, beat-synced club lights, mirrored EQ, karaoke words in loud display fonts.
Works for any song (no footage needed). Reads the same config as make_quick_hook.py.
usage: make_club_short.py CFG.json"""
import sys, json, subprocess, tempfile, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageColor

C = json.load(open(sys.argv[1]))
W, H, FPS = 1080, 1920, 30
s0, s1 = C['song_start'], C['song_end']; T = s1 - s0; N = int(T * FPS)
ACC = C.get('accent', '#ff3640')
GF = '/home/claude/zachary-shorts/pipeline/fonts/gfonts/'
FONTS = [GF + 'ofl/anton/Anton-Regular.ttf', GF + 'apache/permanentmarker/PermanentMarker-Regular.ttf',
         GF + 'ofl/shrikhand/Shrikhand-Regular.ttf', GF + 'ofl/alfaslabone/AlfaSlabOne-Regular.ttf']
HOOKF = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
NEON = [ACC, '#00e5ff', '#ff2bd6', '#ffe14d']
_fc = {}
def font(p, sz):
    k = (p, sz)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, sz)
    return _fc[k]

# ---------- audio analysis ----------
tmp = tempfile.mkdtemp(dir=os.path.dirname(C['out']))
wav = f'{tmp}/a.wav'
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f"{C['audio_off']:.3f}", '-t', f'{T:.3f}', '-i', C['audio_src'],
                '-ac', '1', '-ar', '22050', '-f', 'wav', wav], check=True)
import wave
with wave.open(wav) as wf:
    sr = wf.getframerate(); x = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
hop, nfft = sr // FPS, 2048
win = np.hanning(nfft); xp = np.pad(x, (nfft // 2, nfft))
spec = np.array([np.abs(np.fft.rfft(xp[i * hop:i * hop + nfft] * win)) for i in range(N)])
freqs = np.fft.rfftfreq(nfft, 1 / sr)
NB = 28
edges = np.geomspace(45, 9000, NB + 1)
bands = np.stack([spec[:, (freqs >= edges[b]) & (freqs < edges[b + 1])].mean(1) for b in range(NB)], 1)
bands = np.log1p(bands * 40); bands /= np.percentile(bands, 97, axis=0) + 1e-6; bands = np.clip(bands, 0, 1.2)
bass = np.log1p(spec[:, (freqs > 40) & (freqs < 160)].mean(1) * 40); bass = (bass - np.percentile(bass, 10)) / (np.percentile(bass, 98) - np.percentile(bass, 10) + 1e-6)
bass = np.clip(bass, 0, 1)
flux = np.maximum(0, np.diff(np.log1p(spec[:, freqs < 200].sum(1)), prepend=0))
flux = flux / (np.percentile(flux, 98) + 1e-6)
beats = []
for i in range(N):   # onset picking with a 0.22 s refractory gap
    if flux[i] > 0.55 and flux[i] == flux[max(0, i - 3):i + 4].max() and (not beats or i - beats[-1] > 0.22 * FPS):
        beats.append(i)
pulse = np.zeros(N)
for b in beats:
    for j in range(b, min(N, b + 12)):
        pulse[j] = max(pulse[j], np.exp(-(j - b) / 3.2))
# smooth EQ: fast attack, slow release
eq = np.zeros_like(bands); cur = np.zeros(NB)
for i in range(N):
    cur = np.where(bands[i] > cur, bands[i], cur * 0.82 + bands[i] * 0.18); eq[i] = cur

# ---------- lyrics ----------
lines = []
for item in json.load(open(C['lyrics'])):
    if 'words' not in item: continue
    ws = [(w['w'], w['s'] - s0, w['e'] - s0) for w in item['words'] if s0 - 0.05 <= w['s'] < s1]
    if ws: lines.append(ws)
punch = set(C.get('punch_words', []))

# ---------- static layers ----------
Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
haze = np.exp(-((Y - 1500) / 520) ** 2) * 0.5 + np.exp(-((Y - 300) / 400) ** 2) * 0.25
rng = np.random.default_rng(3)
def rgb(h): return np.array(ImageColor.getrgb(h), np.float32)
BEAMS = [  # origin x, origin y, colour, sweep speed, phase, base angle
    (60, -40, rgb(NEON[1]), 0.55, 0.0, 0.55), (W - 60, -40, rgb(NEON[2]), 0.62, 1.7, -0.55),
    (W / 2, -60, rgb(ACC), 0.4, 3.1, 0.0), (300, -40, rgb(NEON[3]), 0.7, 4.4, 0.25), (W - 300, -40, rgb(NEON[1]), 0.5, 2.2, -0.25)]

def beams(i):
    t = i / FPS; img = np.zeros((H, W, 3), np.float32)
    for k, (ox, oy, col, sp, ph, ba) in enumerate(BEAMS):
        ang = ba + 0.42 * np.sin(t * sp * 2 + ph + 0.8 * len(beats) * 0)
        dx, dy = np.sin(ang), np.cos(ang)
        vx, vy = X - ox, Y - oy
        along = vx * dx + vy * dy; perp = np.abs(-vx * dy + vy * dx)
        width = 26 + along * 0.11
        m = np.clip(1 - perp / width, 0, 1) ** 2 * (along > 0) * np.exp(-along / 2300)
        on = 0.35 + 0.65 * (pulse[i] if k % 2 == 0 else bass[i])
        img += m[..., None] * col * on * 0.55
    img += haze[..., None] * (rgb(ACC) * 0.25 + 40) * (0.3 + 0.7 * bass[i])
    return img

def eq_layer(i, d):
    cy, half, x0, x1 = 1390, 140, 90, 930
    bw = (x1 - x0) / NB
    col = ImageColor.getrgb(ACC)
    for b in range(NB):
        v = float(eq[i, b]); h = max(6, v * half)
        x = x0 + b * bw
        c = tuple(int(c * (0.35 + 0.45 * v)) for c in (col if b % 2 == 0 else ImageColor.getrgb(NEON[1])))
        d.rounded_rectangle([x + 4, cy - h, x + bw - 4, cy + h * 0.55], 6, fill=c)

def hook(d, t):
    rows = C['hook'] if t < C['payoff_at'] else C['payoff']
    y = C.get('hook_y', 230)
    f = font(HOOKF, 70)
    for r in rows[:-1]:
        d.text((W / 2, y), r, font=f, fill='white', anchor='mt', stroke_width=8, stroke_fill='black'); y += 84
    sz = 150
    while d.textlength(rows[-1], font=font(HOOKF, sz)) > 940: sz -= 4
    return rows[-1], y + 4, sz

def wrap(words, fnt, d, maxw):
    rows, cur = [], []
    for w in words:
        if cur and d.textlength(' '.join(cur + [w]), font=fnt) > maxw: rows.append(cur); cur = [w]
        else: cur.append(w)
    rows.append(cur); return rows

ff = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-ss', f"{C['audio_off']:.3f}", '-t', f'{T:.3f}', '-i', C['audio_src'], '-map', '0:v', '-map', '1:a',
                       '-af', f'afade=t=in:d=0.04,afade=t=out:st={T - 0.12:.3f}:d=0.12',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                       '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', C['out']], stdin=subprocess.PIPE)

for i in range(N):
    t = i / FPS
    base = beams(i)
    glow = Image.new('RGB', (W, H)); gd = ImageDraw.Draw(glow)    # things that glow
    top = Image.new('RGBA', (W, H)); td = ImageDraw.Draw(top)     # crisp text on top
    eq_layer(i, gd); eq_layer(i, td)

    # hook / payoff
    big, by, bsz = hook(td, t)
    s = 1 + 0.05 * pulse[i]
    f = font(HOOKF, int(bsz * s))
    for dd, fill in ((gd, ACC), (td, ACC)):
        dd.text((W / 2, by - (s - 1) * 40), big, font=f, fill=fill, anchor='mt', **({'stroke_width': 12, 'stroke_fill': 'black'} if dd is td else {}))

    # karaoke line: font + neon colour change per line, words slam in as sung
    li = None
    for k, ln in enumerate(lines):
        if ln[0][1] - 0.12 <= t: li = k
    if li is not None:
        ln = lines[li]; fp = FONTS[li % len(FONTS)]; neon = NEON[li % len(NEON)]
        base_sz = {'Anton': 156, 'Permanent': 138, 'Shrikhand': 120, 'Alfa': 124}[next(k for k in ('Anton', 'Permanent', 'Shrikhand', 'Alfa') if k in fp)]
        fnt = font(fp, base_sz)
        rows = wrap([w for w, _, _ in ln], fnt, td, 820)
        lh = int(base_sz * 1.18); yy = 850 - (len(rows) - 1) * lh // 2; k = 0
        for r in rows:
            full = sum(td.textlength(w, font=fnt) for w in r) + base_sz * 0.32 * (len(r) - 1); x = W / 2 - full / 2
            for w in r:
                _, ws, we = ln[k]; k += 1
                wl = td.textlength(w, font=fnt) + base_sz * 0.32
                if t >= ws - 0.05:
                    age = t - (ws - 0.05)
                    pop = 1 + 0.22 * max(0, 1 - age / 0.12) ** 2            # slam-in
                    hot = ws - 0.05 <= t < we + 0.1
                    pw = w.lower().strip('.,!?') in punch
                    sz = int(base_sz * pop * (1.06 if pw and hot else 1) * (1 + 0.04 * bass[i]))
                    fw = font(fp, sz)
                    cx, cy = x + td.textlength(w, font=fnt) / 2, yy + base_sz * 0.55
                    fill = neon if hot else '#ffffff'
                    if hot: gd.text((cx, cy), w, font=fw, fill=neon, anchor='mm')
                    td.text((cx, cy), w, font=fw, fill=fill, anchor='mm', stroke_width=7, stroke_fill='black')
                x += wl
            yy += lh

    g = np.asarray(glow, np.float32)
    g = cv2.GaussianBlur(g, (0, 0), 18) * 1.0 + cv2.GaussianBlur(g, (0, 0), 4) * 0.35
    img = base + g
    img *= 1 + 0.18 * pulse[i]
    fr = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    fr.paste(top, (0, 0), top)
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait()
subprocess.run(['rm', '-rf', tmp])
print(C['out'], f'{T:.2f}s', f'{len(beats)} beats')
