#!/usr/bin/env python3
"""Catalog pieces for Facebook from the 25 square covers:
  grid  -> one 2160x2700 (4:5) image, header + 5x5 cover grid + footer
  slides-> 27 carousel slides 1080x1350: intro (his photo), one per song (cover, title, hook), outro
usage: catalog_grid.py covers_dir out_dir
covers_dir holds <slug>.png (upscaled) and raw/<slug>.png (original) for each song."""
import sys, os, json, re
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

cov, outd = sys.argv[1:3]
R = os.path.dirname(os.path.abspath(__file__)) + '/..'
LORA = f'{R}/sysfonts/Lora-Variable.ttf'
INTER = f'{R}/sysfonts/Inter-SemiBold.otf'
INTER_M = f'{R}/sysfonts/Inter-Medium.otf'
os.makedirs(outd, exist_ok=True)

songs = [l.rstrip('\n').split('\t') for l in open(f'{R}/songs/list.tsv')]
songs = [(s[1], s[3].replace("'", '\u2019')) for s in songs if s[1] not in ('im_a_witness', 'the_seventh_day', 'its_your_birthday')]
assert len(songs) == 25, len(songs)
hooks = {e['slug']: e['info']['text'].split('\n')[0] for e in json.load(open(f'{R}/kit/posts.json'))}
EMO = re.compile('[\U0001F000-\U0001FFFF☀-➿️]')
hooks = {k: EMO.sub('', v).strip() for k, v in hooks.items()}

GOLD = (232, 190, 120); CREAM = (246, 238, 225); MUTED = (196, 182, 162)


def lora(sz, wght=700, italic=False):
    f = ImageFont.truetype(LORA, sz)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f


def load_cover(slug, size):
    up = Image.open(f'{cov}/{slug}.png').convert('RGB').resize((size, size), Image.LANCZOS)
    raw = Image.open(f'{cov}/raw/{slug}.png').convert('RGB').resize((size, size), Image.LANCZOS)
    return Image.blend(raw, up, 0.6)


def rounded(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), r, fill=255)
    return m


def paste_card(bg, im, xy, r, shadow=40):
    x, y = xy; w, h = im.size
    sh = Image.new('L', bg.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((x + 6, y + 16, x + w + 6, y + h + 16), r, fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(shadow))
    bg.paste((0, 0, 0), (0, 0), sh)
    bg.paste(im, (x, y), rounded(im, r))


def bg_grad(W, H, top=(22, 17, 13), bot=(44, 30, 18)):
    t = np.linspace(0, 1, H)[:, None, None]
    a = np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t
    a = np.broadcast_to(a, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (1 - 0.35 * np.clip(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2, 0, 1))[..., None] * 1.0
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def ctext(d, W, y, s, f, fill, spacing=0):
    if spacing:
        w = sum(d.textlength(c, font=f) for c in s) + spacing * (len(s) - 1); x = (W - w) / 2
        for c in s: d.text((x, y), c, font=f, fill=fill, anchor='ls'); x += d.textlength(c, font=f) + spacing
    else:
        d.text((W / 2, y), s, font=f, fill=fill, anchor='ms')


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines


# ---------------- grid
W, H = 2160, 2700
img = bg_grad(W, H); d = ImageDraw.Draw(img)
ctext(d, W, 170, 'ZACHARY PATZER', ImageFont.truetype(INTER, 54), GOLD, 22)
ctext(d, W, 330, '25 Songs. One Fight.', lora(150, 700), CREAM)
ctext(d, W, 430, 'Written through stage 4 cancer and the comeback after.', lora(58, 400), MUTED)
C, G = 396, 14
gx0 = (W - (5 * C + 4 * G)) // 2; gy0 = 500
for i, (slug, name) in enumerate(songs):
    x = gx0 + (i % 5) * (C + G); y = gy0 + (i // 5) * (C + G)
    paste_card(img, load_cover(slug, C), (x, y), 18, 14)
d = ImageDraw.Draw(img)
ctext(d, W, gy0 + 5 * C + 4 * G + 110, 'Full lyric videos on YouTube  ·  @zacharypatzer', ImageFont.truetype(INTER_M, 52), GOLD)
img.save(f'{outd}/Zachary_Patzer_25_Songs_Grid.jpg', quality=93)

# ---------------- carousel slides
W, H = 1080, 1350
N = len(songs) + 2


def slide_bg(slug=None):
    if slug is None:
        return bg_grad(W, H)
    c = load_cover(slug, 400).resize((W, W)).filter(ImageFilter.GaussianBlur(60))
    c = c.resize((W, H))
    a = np.asarray(c, np.float32) * 0.32 + np.array((18, 13, 9), np.float32) * 0.5
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def footer(d, k):
    d.text((60, H - 56), '@zacharypatzer', font=ImageFont.truetype(INTER_M, 30), fill=MUTED, anchor='ls')
    d.text((W - 60, H - 56), f'{k}/{N}', font=ImageFont.truetype(INTER_M, 30), fill=MUTED, anchor='rs')


# intro: his photo
img = bg_grad(W, H); d = ImageDraw.Draw(img)
P = cv2.imread(f'{R}/assets/face_src.jpg').astype(np.float32)
a = cv2.imread(f'{R}/assets/face_matte.png', 0).astype(np.float32) / 255
FS = 640
P = cv2.resize(P, (FS, FS), interpolation=cv2.INTER_AREA); a = cv2.resize(a, (FS, FS), interpolation=cv2.INTER_AREA)
ry = np.arange(FS, dtype=np.float32)[:, None]
a = a * np.clip((FS - 20 - ry) / 160, 0, 1)
base = np.asarray(img, np.float32).copy(); fx, fy = (W - FS) // 2, 90
reg = base[fy:fy + FS, fx:fx + FS]
base[fy:fy + FS, fx:fx + FS] = reg * (1 - a[..., None]) + P[..., ::-1] * a[..., None]
img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
ctext(d, W, 860, '25 Songs. One Fight.', lora(92, 700), CREAM)
d.line((W / 2 - 60, 905, W / 2 + 60, 905), fill=GOLD, width=4)
for j, l in enumerate(['Stage 4 Hodgkin’s lymphoma. Three bells rung.', 'Every song I wrote on the way back.']):
    ctext(d, W, 990 + j * 62, l, lora(44, 400), MUTED)
ctext(d, W, 1160, 'Swipe →', ImageFont.truetype(INTER, 40), GOLD)
footer(d, 1)
img.save(f'{outd}/slide_01.jpg', quality=93)

# one slide per song
CS = 820
for i, (slug, name) in enumerate(songs):
    img = slide_bg(slug); d = ImageDraw.Draw(img)
    ctext(d, W, 92, f'SONG {i + 1} OF 25', ImageFont.truetype(INTER, 30), GOLD, 8)
    paste_card(img, load_cover(slug, CS), ((W - CS) // 2, 130), 26, 30)
    d = ImageDraw.Draw(img)
    f = lora(64, 700)
    while d.textlength(name, font=f) > W - 120: f = lora(f.size - 2, 700)
    ctext(d, W, 1060, name, f, CREAM)
    hf = lora(42, 400)
    q = '“' + hooks[slug].replace("'", '’') + '”'
    if d.textlength(q, font=hf) <= W - 140:
        hl = [q]
    else:  # two balanced lines: split at the word break nearest the middle
        ws = q.split()
        k = min(range(1, len(ws)), key=lambda k: abs(d.textlength(' '.join(ws[:k]), font=hf) - d.textlength(' '.join(ws[k:]), font=hf)))
        hl = [' '.join(ws[:k]), ' '.join(ws[k:])]
    for j, l in enumerate(hl):
        ctext(d, W, 1135 + j * 56, l, hf, MUTED)
    footer(d, i + 2)
    img.save(f'{outd}/slide_{i + 2:02d}.jpg', quality=93)

# outro
img = bg_grad(W, H); d = ImageDraw.Draw(img)
mini = 150; g = 12; x0 = (W - (5 * mini + 4 * g)) // 2
for i, (slug, _) in enumerate(songs):
    paste_card(img, load_cover(slug, mini), (x0 + (i % 5) * (mini + g), 110 + (i // 5) * (mini + g)), 10, 6)
d = ImageDraw.Draw(img)
ctext(d, W, 1010, 'Which one is yours?', lora(84, 700), CREAM)
d.line((W / 2 - 60, 1055, W / 2 + 60, 1055), fill=GOLD, width=4)
ctext(d, W, 1135, 'Full lyric videos on YouTube', lora(44, 400), MUTED)
ctext(d, W, 1195, '@zacharypatzer', ImageFont.truetype(INTER, 44), GOLD)
footer(d, N)
img.save(f'{outd}/slide_{N:02d}.jpg', quality=93)
print('done', N, 'slides')
