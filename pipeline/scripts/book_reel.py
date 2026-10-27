#!/usr/bin/env python3
"""Vertical 1080x1920 slideshow reel for one Real Life Series book (same content as its carousel).
No page counters, no 'Swipe', no bars. Cuts land on the music's beats.
usage: book_reel.py BOOK(1|2|3) AUDIO_SRC OUT.mp4 [audio_start_s]
"""
import sys, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

book = int(sys.argv[1]); src, out = sys.argv[2:4]
A0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
R = os.path.dirname(os.path.abspath(__file__)) + '/..'
LORA = f'{R}/sysfonts/Lora-Variable.ttf'; INTER = f'{R}/sysfonts/Inter-SemiBold.otf'; INTER_M = f'{R}/sysfonts/Inter-Medium.otf'
GOLD = (232, 190, 120); CREAM = (246, 238, 225); MUTED = (205, 192, 172)
W, H, FPS = 1080, 1920, 30

BOOKS = {
 1: dict(title='Real Life Happens. Real People Don’t.',
   s1=('When real life calls, pick up.', 'I wrote a book for the nights everything feels too loud.'),
   s3=('Life rarely waits until you feel ready.', 'A bad night. A hard conversation. A plan that falls apart.'),
   s4=('Twenty phone calls.', 'With the guy people call when everything feels too loud.'),
   s5=('Every call ends with a Steady Card.', 'What’s in your control. Your next move. One thing to remember.')),
 2: dict(title='Things Break. People Rebuild.',
   s1=('What’s still standing?', 'The one question every rebuild starts with.'),
   s3=('Sooner or later, something comes apart.', 'A job. A marriage. A body. A plan you built your whole life around.'),
   s4=('Twenty conversations at a picnic table.', 'Strangers sit down across from a guy with a buggie and end up telling him the truth.'),
   s5=('No fake masks.', 'Just honest talk, and the kind of company that makes the next step feel possible.')),
 3: dict(title='Figuring Things Out. Walk With Me.',
   s1=('Who’s worth going through hell for?', 'I’m still figuring it out. Walk with me.'),
   s3=('Surviving is supposed to be the end of the story.', 'It isn’t. It’s just a different middle.'),
   s4=('Twenty walks at buggie speed.', 'With whoever falls into step.'),
   s5=('No gurus. No slogans.', 'Just a guy who walks slow enough for you to keep up with your own thoughts.')),
}
B = BOOKS[book]
ACCENT = {1: (190, 40, 36), 2: (70, 105, 185), 3: (130, 165, 215)}
COVER = Image.open(f'{R}/assets/book_covers/book{book}.jpg').convert('RGB')


def lora(sz, wght=700):
    f = ImageFont.truetype(LORA, sz)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f


def ctext(d, y, s, f, fill, spacing=0):
    if spacing:
        w = sum(d.textlength(c, font=f) for c in s) + spacing * (len(s) - 1); x = (W - w) / 2
        for c in s: d.text((x, y), c, font=f, fill=fill, anchor='ls'); x += d.textlength(c, font=f) + spacing
    else:
        d.text((W / 2, y), s, font=f, fill=fill, anchor='ms')


def wrap(d, text, f, maxw):
    words, lines, line = text.split(), [], ''
    for w in words:
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else: lines.append(line); line = w
    lines.append(line)
    # balance: shrink width while line count stays the same
    n = len(lines); mw = maxw
    while mw > 400:
        test, line = [], ''
        for w in words:
            t = (line + ' ' + w).strip()
            if d.textlength(t, font=f) <= mw - 20: line = t
            else: test.append(line); line = w
        test.append(line)
        if len(test) != n or '' in test: break
        lines, mw = test, mw - 20
    return lines


def para(d, y, text, f, fill, maxw=900, lh=1.22):
    for ln in wrap(d, text, f, maxw):
        ctext(d, y + f.size, ln, f, fill); y += f.size * lh
    return y


def height(d, text, f, maxw=900, lh=1.22): return len(wrap(d, text, f, maxw)) * f.size * lh


def bg():
    s = COVER.resize((H, int(H * COVER.height / COVER.width)))
    s = s.crop(((s.width - W) // 2, (s.height - H) // 2, (s.width - W) // 2 + W, (s.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(70))
    a = np.asarray(s, np.float32) * 0.34 + np.array((14, 11, 8), np.float32) * 0.5
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (1 - 0.12 * np.abs(yy - H / 2) / (H / 2))[..., None]
    # soft glows in the book's accent color, reaching every edge, so the frame never reads as a bordered video
    acc = np.array(ACCENT[book], np.float32)
    for gx, gy, r, k in [(0.12, 0.03, 420, 0.20), (0.88, 0.10, 380, 0.14), (0.20, 0.97, 440, 0.20), (0.85, 0.92, 400, 0.15), (0.55, 1.0, 260, 0.16),
                         (0.02, 0.5, 320, 0.10), (0.98, 0.55, 320, 0.10)]:
        a += (k * np.exp(-((xx - gx * W) ** 2 + (yy - gy * H) ** 2) / (2 * r * r)))[..., None] * acc
    a += np.random.default_rng(7).normal(0, 2.5, (H, W, 1))  # light film grain
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


HDR = ImageFont.truetype(INTER, 30)


def header(d): ctext(d, 250, 'ZACHARY PATZER', HDR, GOLD, 10)


def rule(d, y): d.line((W / 2 - 60, y, W / 2 + 60, y), fill=GOLD, width=4)


def intro():
    img = bg()
    P = cv2.imread(f'{R}/assets/face_src.jpg').astype(np.float32)
    a = cv2.imread(f'{R}/assets/face_matte.png', 0).astype(np.float32) / 255
    FS = 760
    P = cv2.resize(P, (FS, FS), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (FS, FS), interpolation=cv2.INTER_AREA)
    a = a * np.clip((FS - 20 - np.arange(FS, dtype=np.float32)[:, None]) / 200, 0, 1)
    base = np.asarray(img, np.float32).copy(); fx, fy = (W - FS) // 2, 310
    base[fy:fy + FS, fx:fx + FS] = base[fy:fy + FS, fx:fx + FS] * (1 - a[..., None]) + P[..., ::-1] * a[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    header(d)
    y = fy + FS + 20
    ctext(d, y + 30, 'STAGE 4 SURVIVOR. AUTHOR.', ImageFont.truetype(INTER, 32), GOLD, 6); y += 80
    y = para(d, y, B['s1'][0], lora(76), CREAM, 920) + 20
    rule(d, y); y += 30
    para(d, y, B['s1'][1], lora(46, 400), MUTED, 880)
    return img


CW = 700; CH = round(CW * COVER.height / COVER.width); CX, CY = (W - CW) // 2, 330


def cover_layer(caption, small=None):
    img = bg(); x0, y0 = CX, CY
    sh = Image.new('L', img.size, 0); ImageDraw.Draw(sh).rectangle((x0 + 10, y0 + 26, x0 + CW + 10, y0 + CH + 26), fill=200)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(34)))
    d = ImageDraw.Draw(img); header(d)
    y = CY + CH + 70
    y = para(d, y, caption, lora(58), CREAM, 940) + 18
    if small:
        rule(d, y); y += 26
        para(d, y, small, lora(44, 400), GOLD if small.startswith('Link') else MUTED, 900)
    return img


def text_slide(big, small):
    img = bg(); d = ImageDraw.Draw(img); header(d)
    th = COVER.resize((150, round(150 * COVER.height / COVER.width)), Image.LANCZOS)
    fb, fs = lora(80), lora(48, 400)
    hb, hs = height(d, big, fb, 920), height(d, small, fs, 880)
    y = (H - (hb + 60 + hs)) / 2 - 60
    y = para(d, y, big, fb, CREAM, 920) + 22
    rule(d, y); y += 34
    para(d, y, small, fs, MUTED, 880)
    sh = Image.new('L', img.size, 0); ImageDraw.Draw(sh).rectangle((W // 2 - 75 + 4, 1440 + 10, W // 2 + 75 + 4, 1440 + th.height + 10), fill=160)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    img.paste(th, (W // 2 - 75, 1440))
    return img


# ---- beats (spectral-flux onsets + autocorrelation tempo; no librosa needed)
SR = 22050
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(A0), '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
x = np.frombuffer(pcm, np.float32); HOP = 512
S = np.abs(np.array([np.fft.rfft(x[i:i + 2048] * np.hanning(2048)) for i in range(0, len(x) - 2048, HOP)]))
flux = np.maximum(np.diff(np.log1p(S), axis=0), 0).sum(1); flux = (flux - flux.mean()) / (flux.std() + 1e-9)
fr = SR / HOP
ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
lo, hi = int(fr * 60 / 160), int(fr * 60 / 60)
per = (lo + np.argmax(ac[lo:hi])) / fr
ph = max(range(int(per * fr)), key=lambda o: flux[o::int(round(per * fr))].sum()) / fr
beats = ph + per * np.arange(200)
print(f'tempo {60 / per:.1f} bpm, first beat {ph:.2f}s')

# slide durations (seconds wanted), snapped to beats
want = [3.6, 3.2, 3.6, 3.4, 3.8, 4.2]
cuts, t = [0.0], 0.0
for w in want[:-1]:
    t += w; cuts.append(float(beats[np.argmin(np.abs(beats - t))]))
end = cuts[-1] + want[-1]
cuts.append(end)
print('cuts', [round(c, 2) for c in cuts])

L = [np.asarray(intro(), np.float32), None,
     np.asarray(text_slide(*B['s3']), np.float32), np.asarray(text_slide(*B['s4']), np.float32),
     np.asarray(text_slide(*B['s5']), np.float32), None]
cov2 = cover_layer('Book ' + str(book) + ' of The Real Life Series')
cov6 = cover_layer('Paperback, hardcover, and Kindle.', 'Link in the comments.')


def cover_frame(base, u):
    s = 1.0 + 0.04 * u; cw, ch = int(CW * s) // 2 * 2, int(CH * s) // 2 * 2
    im = base.copy(); im.paste(COVER.resize((cw, ch), Image.LANCZOS), ((W - cw) // 2, CY + (CH - ch) // 2))
    return np.asarray(im, np.float32)


def zoom(arr, z):
    M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def frame(k, t):
    u = (t - cuts[k]) / (cuts[k + 1] - cuts[k])
    if k == 1: return cover_frame(cov2, u)
    if k == 5: return cover_frame(cov6, u)
    return zoom(L[k], 1 + 0.035 * u)


XF = 0.25
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-ss', str(A0), '-i', src, '-map', '0:v', '-map', '1:a', '-t', f'{end:.3f}',
                       '-af', f'afade=t=in:st=0:d=0.15,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={end - 1.2:.2f}:d=1.2',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                       '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
for n in range(int(round(end * FPS))):
    t = n / FPS; k = min(np.searchsorted(cuts, t, 'right') - 1, 5)
    f = frame(k, t)
    if k > 0 and t - cuts[k] < XF:   # short dissolve from the previous slide
        a = (t - cuts[k]) / XF; f = f * a + frame(k - 1, t) * (1 - a)
    ff.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
print('wrote', out, ff.returncode)
