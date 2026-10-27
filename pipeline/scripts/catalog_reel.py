#!/usr/bin/env python3
"""Clean 1080x1920 catalog reel: intro (his face) -> 25 covers cut on the beat -> outro grid.
No black bars, no carousel page counters, no 'Swipe'.
usage: catalog_reel.py AUDIO_SRC OUT.mp4 [first_beat] [beat_period]"""
import sys, os, json, re, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

src, out = sys.argv[1:3]
B0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.244
BP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.4644
R = os.path.dirname(os.path.abspath(__file__)) + '/..'
LORA = f'{R}/sysfonts/Lora-Variable.ttf'; INTER = f'{R}/sysfonts/Inter-SemiBold.otf'; INTER_M = f'{R}/sysfonts/Inter-Medium.otf'
GOLD = (232, 190, 120); CREAM = (246, 238, 225); MUTED = (200, 186, 166)
W, H, FPS = 1080, 1920, 30

songs = [l.rstrip('\n').split('\t') for l in open(f'{R}/songs/list.tsv')]
songs = [(s[1], s[3].replace("'", '’')) for s in songs if s[1] not in ('im_a_witness', 'the_seventh_day', 'its_your_birthday', 'glad_youre_here')]
assert len(songs) == 25


def lora(sz, wght=700):
    f = ImageFont.truetype(LORA, sz)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f


def cover(slug):
    return Image.open(f'{R}/qh/covers/{slug}.jpg').convert('RGB')


def ctext(d, y, s, f, fill, spacing=0):
    if spacing:
        w = sum(d.textlength(c, font=f) for c in s) + spacing * (len(s) - 1); x = (W - w) / 2
        for c in s: d.text((x, y), c, font=f, fill=fill, anchor='ls'); x += d.textlength(c, font=f) + spacing
    else:
        d.text((W / 2, y), s, font=f, fill=fill, anchor='ms')


def grad_bg():
    t = np.linspace(0, 1, H)[:, None, None]
    a = np.array((20, 15, 11), np.float32) * (1 - t) + np.array((40, 28, 17), np.float32) * t
    a = np.broadcast_to(a, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (1 - 0.4 * np.clip(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2, 0, 1))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def blur_bg(c):
    s = c.resize((H, H)).crop(((H - W) // 2, 0, (H - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(70))
    a = np.asarray(s, np.float32) * 0.34 + np.array((16, 12, 8), np.float32) * 0.5
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    a *= 1 - 0.35 * np.abs(yy - H / 2) / (H / 2)  # darker top/bottom for UI overlays
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def round_mask(size, r):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255); return m


def shadow(bg, box, r, blur=34):
    x0, y0, x1, y1 = box
    sh = Image.new('L', bg.size, 0); ImageDraw.Draw(sh).rounded_rectangle((x0 + 4, y0 + 18, x1 + 4, y1 + 18), r, fill=210)
    bg.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)))


HDR = ImageFont.truetype(INTER, 30)

# ---- static layers per slide (background + text), card drawn per frame for the push-in
CS, CY = 880, 420          # card size / top
def song_layer(i, slug, name):
    c = cover(slug); bg = blur_bg(c); d = ImageDraw.Draw(bg)
    ctext(d, 250, 'ZACHARY PATZER', HDR, GOLD, 10)
    ctext(d, 330, f'SONG {i + 1} OF 25', ImageFont.truetype(INTER_M, 34), MUTED, 8)
    shadow(bg, ((W - CS) // 2, CY, (W + CS) // 2, CY + CS), 30)
    d = ImageDraw.Draw(bg)
    f = lora(82)
    while d.textlength(name, font=f) > W - 140: f = lora(f.size - 2)
    ctext(d, CY + CS + 140, name, f, CREAM)
    d.line((W / 2 - 50, CY + CS + 180, W / 2 + 50, CY + CS + 180), fill=GOLD, width=4)
    return bg, c


def intro_layer():
    img = grad_bg()
    P = cv2.imread(f'{R}/assets/face_src.jpg').astype(np.float32)
    a = cv2.imread(f'{R}/assets/face_matte.png', 0).astype(np.float32) / 255
    FS = 820
    P = cv2.resize(P, (FS, FS), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (FS, FS), interpolation=cv2.INTER_AREA)
    a = a * np.clip((FS - 20 - np.arange(FS, dtype=np.float32)[:, None]) / 200, 0, 1)
    base = np.asarray(img, np.float32).copy(); fx, fy = (W - FS) // 2, 330
    base[fy:fy + FS, fx:fx + FS] = base[fy:fy + FS, fx:fx + FS] * (1 - a[..., None]) + P[..., ::-1] * a[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    ctext(d, 250, 'ZACHARY PATZER', HDR, GOLD, 10)
    ctext(d, 1290, '25 Songs. One Fight.', lora(94), CREAM)
    d.line((W / 2 - 60, 1340, W / 2 + 60, 1340), fill=GOLD, width=4)
    for j, l in enumerate(['Stage 4 Hodgkin’s lymphoma. Three bells rung.', 'Every song I wrote on the way back.']):
        ctext(d, 1420 + j * 64, l, lora(46, 400), MUTED)
    return img


def outro_layer():
    img = grad_bg(); d = ImageDraw.Draw(img)
    ctext(d, 250, 'ZACHARY PATZER', HDR, GOLD, 10)
    mini, g = 176, 12; x0 = (W - (5 * mini + 4 * g)) // 2; y0 = 330
    for i, (slug, _) in enumerate(songs):
        x, y = x0 + (i % 5) * (mini + g), y0 + (i // 5) * (mini + g)
        c = cover(slug).resize((mini, mini), Image.LANCZOS)
        shadow(img, (x, y, x + mini, y + mini), 10, 8); img.paste(c, (x, y), round_mask(c.size, 12))
    d = ImageDraw.Draw(img); ty = y0 + 5 * mini + 4 * g
    ctext(d, ty + 170, 'Which one is yours?', lora(92), CREAM)
    d.line((W / 2 - 60, ty + 215, W / 2 + 60, ty + 215), fill=GOLD, width=4)
    ctext(d, ty + 295, 'Full lyric videos on YouTube', lora(48, 400), MUTED)
    ctext(d, ty + 365, '@zacharypatzer', ImageFont.truetype(INTER, 50), GOLD)
    return img


# ---- timeline (cuts on the beat)
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src]))
NF = int(round(dur * FPS))
beat = lambda k: B0 + k * BP
t_songs = beat(3); t_outro = beat(28)
print(f'dur {dur:.2f}  intro 0-{t_songs:.2f}  songs -{t_outro:.2f}  outro -{dur:.2f}')

intro, outro = np.asarray(intro_layer()), np.asarray(outro_layer())
layers = [song_layer(i, s, n) for i, (s, n) in enumerate(songs)]
mask_cache = {}


def zoom(arr, z):
    if z == 1: return arr
    M = cv2.getRotationMatrix2D((W / 2, H / 2 - 100), 0, z)
    return cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-i', src, '-map', '0:v', '-map', '1:a',
                       '-af', f'loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={dur - 0.6:.2f}:d=0.6',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                       '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', '-shortest', out], stdin=subprocess.PIPE)
for n in range(NF):
    t = n / FPS
    if t < t_songs:
        fr = zoom(intro, 1 + 0.04 * t / t_songs)
    elif t < t_outro:
        k = min(int((t - t_songs) / BP), 24); u = (t - t_songs - k * BP) / BP
        bg, c = layers[k]; s = int(CS * (1.0 + 0.035 * u)) // 2 * 2
        im = bg.copy(); cc = c.resize((s, s), Image.LANCZOS)
        if s not in mask_cache: mask_cache[s] = round_mask((s, s), 30)
        im.paste(cc, ((W - s) // 2, CY + (CS - s) // 2), mask_cache[s]); fr = np.asarray(im)
    else:
        u = (t - t_outro) / max(dur - t_outro, 0.1)
        fr = zoom(outro, 1 + 0.03 * u)
    ff.stdin.write(np.ascontiguousarray(fr).tobytes())
ff.stdin.close(); ff.wait()
print('wrote', out, ff.returncode)
