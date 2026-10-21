#!/usr/bin/env python3
"""YouTube thumbnail (1280x720) per song: cover scene background, big face panel on the right,
title on the left in the cover's own font and colour.

usage: thumbs.py SLUG [SLUG ...]
"""
import sys, json, colorsys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
GF = '/home/claude/fonts/gfonts'
U = '/root/.claude/uploads/7e2b6de3-c1a2-50ff-9aa8-ba533aa956e4'
INTER_SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
INTER_B = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'

# slug: (bg image, font file, variation weight, fill, stroke, mode, upper)
S = {
    'island_time':            ('210d3d2e-7890.jpg', 'ofl/pacifico/Pacifico-Regular.ttf', None, '#46e8e4', '#06302f', 'flat', False),
    'im_a_witness':           ('29c93216-7912.webp', 'ofl/playfairdisplaysc/PlayfairDisplaySC-Black.ttf', None, '#ff4fae', '#2a0018', 'flat', True),
    'a_seat_at_the_table':    ('5b8c1aa4-7892.jpg', 'ofl/uncialantiqua/UncialAntiqua-Regular.ttf', None, '#35d47d', '#03200f', 'flat', True),
    'no_complaints':          ('75d506ed-7895.webp', 'apache/ultra/Ultra-Regular.ttf', None, '#5f8bff', '#050d2e', 'flat', True),
    'embrace_every_scar':     ('6c0ab0bf-7897.webp', 'apache/permanentmarker/PermanentMarker-Regular.ttf', None, None, '#111111', 'rainbow', True),
    'footprints_of_gold':     ('2a92e72f-7898.webp', 'ofl/abrilfatface/AbrilFatface-Regular.ttf', None, '#f4c23c', '#2a1800', 'gold', True),
    'shout_yes':              ('4888c2b6-7900.webp', 'ofl/orbitron/Orbitron[wght].ttf', 900, None, '#12002a', 'neon', True),
    'even_if_we_stumble':     ('464d0686-7902.webp', 'ofl/righteous/Righteous-Regular.ttf', None, '#92f7cf', '#06281c', 'flat', True),
    'from_where_i_stand':     ('e499a516-7903.webp', 'ofl/holtwoodonesc/HoltwoodOneSC-Regular.ttf', None, '#ffffff', '#1a1408', 'flat', True),
    'remember_me_when_im_gone': ('663a14d5-7905.jpg', 'ofl/cormorantgaramond/CormorantGaramond-Italic[wght].ttf', 700, '#f6dcef', '#3a0f33', 'flat', False),
    'dying_to_live':          ('9e6c582c-7906.webp', 'ofl/amaticsc/AmaticSC-Bold.ttf', None, '#b4f24c', '#0d2004', 'flat', True),
    'living_in_the_echo':     ('7b42f79b-7913.webp', 'apache/syncopate/Syncopate-Bold.ttf', None, '#ffa31a', '#2a1400', 'flat', True),
    'only_the_strong_survive': ('efdd3f07-7872.jpg', 'ofl/anton/Anton-Regular.ttf', None, None, '#5a0606', 'chrome', True),
    'make_your_time_count':   ('1fa4db46-7873.jpg', 'ofl/poiretone/PoiretOne-Regular.ttf', None, '#f2a88a', '#2a120a', 'flat', True),
    'live_now_die_later':     ('422c1f9f-7870.jpg', 'ofl/cinzel/Cinzel[wght].ttf', 800, '#c4ebff', '#06202e', 'flat', True),
    'my_word_wont_die':       ('677937e0-7869.jpg', 'ofl/shrikhand/Shrikhand-Regular.ttf', None, '#f6e3bc', '#5a1408', 'flat', True),
    'quiet_fire':             ('ce6493ac-7878.jpg', 'ofl/alfaslabone/AlfaSlabOne-Regular.ttf', None, '#ff6a14', '#2a0c00', 'fire', True),
    'floor_of_shadows':       ('272fe216-7877.jpg', 'ofl/limelight/Limelight-Regular.ttf', None, '#fff03a', '#1e1c00', 'flat', True),
    'i_live_on_through_you':  ('99c87944-7914.webp', 'ofl/arvo/Arvo-Bold.ttf', None, '#fff1d6', '#1c3a7a', 'flat', True),
    'we_die_before_we_quit':  ('9eabd123-7879.jpg', 'ofl/oswald/Oswald[wght].ttf', 700, '#ff3640', '#1a0002', 'flat', True),
    'take_a_number':          ('149c9fd2-7889.jpg', 'ofl/rye/Rye-Regular.ttf', None, '#f1d9ad', '#6e1a16', 'flat', True),
    'light_one_let_it_go':    ('e9767445-7887.jpg', 'ofl/josefinslab/JosefinSlab[wght].ttf', 700, '#c7a6ff', '#140a2a', 'flat', True),
    'beautiful_anyway':       ('eda2c795-7882.jpg', 'ofl/bebasneue/BebasNeue-Regular.ttf', None, '#e3874f', '#2a1206', 'flat', True),
    'a_mile_an_hour':         ('bfef81be-7867.jpg', 'ofl/bevan/Bevan-Regular.ttf', None, '#5ec0ff', '#03182a', 'flat', True),
    'unfinished':             ('/home/claude/songs/unfinished/scene_crop.png', 'ofl/mrdafoe/MrDafoe-Regular.ttf', None, '#fff3e6', '#1a2647', 'sunrise', False),
    'lions_heart':            ('/home/claude/songs/lions_heart/scene_crop.png', 'ofl/sansita/Sansita-BlackItalic.ttf', None, '#ffd27a', '#3d0f08', 'lion', False),
}
# per-song face-panel crop (fraction of cover width): Lion's Heart shifts right to keep the lion and drop the IV cape
PANEL_X = {}
# per-song: hide the cover's scene left of the portrait (Lion's Heart: IV pole + cape would double up with the background)
HIDE_LEFT_SCENE = {'lions_heart'}
EXTRA_TITLES = {'take_a_number': 'Take a Number', 'light_one_let_it_go': 'Light One, Let It Go',
                'beautiful_anyway': 'Beautiful Anyway', 'a_mile_an_hour': 'A Mile An Hour',
                'lions_heart': 'Lion\u2019s Heart'}


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)  # BGR


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def font(path, size, wght=None):
    f = ImageFont.truetype(path, size)
    if wght:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


def mask(draw_fn, size=(W, H)):
    m = Image.new('L', size, 0)
    draw_fn(ImageDraw.Draw(m))
    return np.asarray(m, np.float32) / 255.0


def wrap_title(title, fpath, wght, maxw, maxlines=3, start=150, minsize=56):
    words = title.split()
    d = ImageDraw.Draw(Image.new('L', (8, 8)))
    if ', ' in title:
        # break at the comma when the two halves fit at a decent size
        rows = [title.split(', ', 1)[0] + ',', title.split(', ', 1)[1]]
        for size in range(start, 89, -4):
            f = font(fpath, size, wght)
            if max(d.textlength(r, font=f) for r in rows) <= maxw:
                return f, rows, size
    for size in range(start, minsize - 1, -4):
        f = font(fpath, size, wght)
        for nl in range(1, maxlines + 1):
            # balanced split into nl lines
            import itertools
            best = None
            for cuts in itertools.combinations(range(1, len(words)), nl - 1):
                b = (0,) + cuts + (len(words),)
                rows = [' '.join(words[b[i]:b[i + 1]]) for i in range(nl)]
                wid = max(d.textlength(r, font=f) for r in rows)
                if wid <= maxw and (best is None or wid < best[0]):
                    best = (wid, rows)
            if best:
                return f, best[1], size
    return f, [title], minsize


def thumb(slug):
    rows_ = [l.rstrip('\n').split('\t') for l in open('/home/claude/songs/list.tsv') if l.split('\t')[1] == slug]
    title = rows_[0][3] if rows_ else EXTRA_TITLES[slug]
    bgf, fpath, wght, fill, stroke, mode, upper = S[slug]
    # ---- background scene
    bgp = bgf if bgf.startswith('/') else f'{U}/{bgf}'
    bg = cv2.imread(bgp) if not bgf.endswith('.webp') else cv2.cvtColor(np.asarray(Image.open(bgp).convert('RGB')), cv2.COLOR_RGB2BGR)
    if slug == 'we_die_before_we_quit':
        # keep the burning rock out of the thumbnail
        mk = np.zeros(bg.shape[:2], np.uint8)
        k_ = bg.shape[0] / 1024
        cv2.ellipse(mk, (int(505 * k_), int(600 * k_)), (int(125 * k_), int(115 * k_)), 0, 0, 360, 255, -1)
        bg = cv2.inpaint(bg, mk, 25, cv2.INPAINT_TELEA)
        bg = cv2.GaussianBlur(bg, (0, 0), 1)
    s = bg.shape[0]
    hh = int(s * 9 / 16)
    y0 = int((s - hh) * 0.45)
    bg = cv2.resize(bg[y0:y0 + hh], (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    bg = cv2.GaussianBlur(bg, (0, 0), 2.2)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = bg * 0.78
    # ---- face panel from the cover (below its title)
    import os
    cp_ = f'/home/claude/covers/x4_{slug}_clean.png'
    cov = cv2.imread(cp_ if os.path.exists(cp_) else f'/home/claude/covers/x4_{slug}.png')
    C = cov.shape[0]
    cx0, cx1 = PANEL_X.get(slug, (0.14, 0.86))
    crop = cov[int(C * 0.275):C, int(C * cx0):int(C * cx1)]
    ph = H
    pw = int(crop.shape[1] * ph / crop.shape[0])
    face = cv2.resize(crop, (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32)
    x0 = W - pw + 30
    xs = np.arange(pw, dtype=np.float32)
    a = smooth(xs / 230.0)[None, :, None] * np.ones((ph, 1, 1), np.float32)
    x1 = min(W, x0 + pw)
    ap_ = f'/home/claude/covers/x4_{slug}_alpha.png'
    if slug in HIDE_LEFT_SCENE and os.path.exists(ap_):
        # same panel crop and fade as every other thumbnail; only the scene part left of him is dropped
        pa = cv2.imread(ap_, 0)[int(C * 0.275):C, int(C * cx0):int(C * cx1)]
        pa = cv2.resize(pa, (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255
        a = a * np.maximum(pa, smooth((xs - 230) / 110.0)[None, :, None])
    a = a[:, :x1 - x0]
    img[:, x0:x1] = img[:, x0:x1] * (1 - a) + face[:, :x1 - x0] * a
    # ---- darken the left for the title, vignette
    dark = 1 - 0.62 * smooth((780 - xx) / 640)
    img *= dark[..., None]
    vig = 1 - 0.38 * smooth(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.78)) ** 2)
    img *= vig[..., None]

    # ---- title
    X = 64
    t = title.upper() if upper else title
    start = 150 if len(t) < 14 else 128
    if 'amatic' in fpath:
        start = 230
    while True:
        f, rows, size = wrap_title(t, f'{GF}/{fpath}', wght, 590, 3, start)
        asc, desc = f.getmetrics()
        lh = int((asc + desc) * (0.92 if not upper else 0.98))
        if 'amatic' in fpath or 'anton' in fpath or 'oswald' in fpath or 'bebas' in fpath:
            lh = int(size * 1.05)
        if 92 + lh * len(rows) + 80 <= 610 or start <= 60:
            break
        start = size - 6
    d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
    block = lh * len(rows)
    total = 50 + 42 + block + 70 + 10
    top = int(H / 2 - total / 2) + 50 + 42
    base = [top + asc + i * lh for i in range(len(rows))]

    def draw_rows(d, stroke_w=0):
        for r, b in zip(rows, base):
            d.text((X, b), r, font=f, fill=255, anchor='ls', stroke_width=stroke_w, stroke_fill=255)
    a_fill = mask(lambda d: draw_rows(d, 3 if 'poiret' in fpath else 0))
    a_strk = mask(lambda d: draw_rows(d, max(5, size // 22)))
    # drop shadow
    sh = cv2.GaussianBlur(np.roll(np.roll(a_strk, 8, 0), 5, 1), (0, 0), 12) * 0.85
    img *= (1 - sh[..., None])
    # stroke
    img = img * (1 - a_strk[..., None]) + hexc(stroke) * a_strk[..., None]
    # fill colour field
    if mode == 'rainbow':
        hue = ((xx - X) / 560.0 + (yy - top) / 900.0) % 1.0
        col = np.zeros((H, W, 3), np.float32)
        for c in range(1):
            pass
        hsv = np.stack([hue * 179, np.full_like(hue, 200), np.full_like(hue, 255)], -1).astype(np.uint8)
        col = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32)
    elif mode == 'neon':
        tt = smooth((xx - X) / 560.0)[..., None]
        col = hexc('#4fe3ff') * (1 - tt) + hexc('#ff5cf4') * tt
    elif mode == 'chrome':
        ty = np.zeros_like(yy)
        for b in base:
            ty = np.where((yy > b - asc) & (yy <= b + desc), (yy - (b - asc)) / (asc * 0.95), ty)
        ty = np.clip(ty, 0, 1)[..., None]
        top_c, mid_c, low_c = hexc('#ffffff'), hexc('#8d9aaa'), hexc('#e6ecf3')
        col = np.where(ty < 0.55, top_c * (1 - ty / 0.55) + mid_c * (ty / 0.55), mid_c * (1 - (ty - 0.55) / 0.45) + low_c * ((ty - 0.55) / 0.45))
    elif mode in ('gold', 'fire', 'sunrise', 'lion'):
        ty = np.zeros_like(yy)
        for b in base:
            ty = np.where((yy > b - asc) & (yy <= b + desc), (yy - (b - asc)) / (asc * 0.95), ty)
        ty = np.clip(ty, 0, 1)[..., None]
        if mode == 'gold':
            c0, c1 = hexc('#fff0a8'), hexc('#d99a1e')
        elif mode == 'sunrise':
            c0, c1 = hexc('#fffaf1'), hexc('#ffbf9c')
        elif mode == 'lion':
            c0, c1 = hexc('#ffe9a3'), hexc('#ec7a26')
        else:
            c0, c1 = hexc('#ffd24a'), hexc('#ff4a0c')
        col = c0 * (1 - ty) + c1 * ty
    else:
        col = np.broadcast_to(hexc(fill), (H, W, 3))
    img = img * (1 - a_fill[..., None]) + col * a_fill[..., None]
    # soft glow behind the title for punch
    accent = col if mode == 'flat' else (hexc('#ffb02e') if mode in ('gold', 'fire') else hexc('#c8a0ff'))
    if mode == 'flat':
        accent = hexc(fill)
    elif mode == 'rainbow':
        accent = hexc('#d0b8ff')
    elif mode == 'neon':
        accent = hexc('#b36bff')
    elif mode == 'chrome':
        accent = hexc('#ff3a3a')
    elif mode == 'sunrise':
        accent = hexc('#ffbf9c')
    elif mode == 'lion':
        accent = hexc('#ffc160')

    # ---- artist + tags
    fa = font(INTER_B, 38)

    def spaced(d, x, y, text, f_, sp):
        for ch in text:
            d.text((x, y), ch, font=f_, fill=255, anchor='ls')
            x += d.textlength(ch, font=f_) + sp
        return x
    ya = base[-1] + min(desc, 30) + 62
    a_art = mask(lambda d: spaced(d, X + 2, ya, 'ZACHARY PATZER', fa, 6))
    sh2 = cv2.GaussianBlur(np.roll(a_art, 3, 0), (0, 0), 6) * 0.8
    img *= (1 - sh2[..., None])
    img = img * (1 - a_art[..., None]) + hexc('#f4f6f8') * a_art[..., None]
    # pill
    fp = font(INTER_SB, 26)
    ptxt = 'LYRIC VIDEO  ·  REMASTERED'
    tw = sum(d0.textlength(c, font=fp) + 4 for c in ptxt) - 4
    py = top - 92
    pill = mask(lambda d: d.rounded_rectangle([X, py, X + tw + 44, py + 50], 25, fill=255))
    pc = accent * 0.85
    lum = float(pc @ np.array([0.114, 0.587, 0.299], np.float32))
    img = img * (1 - pill[..., None] * 0.92) + pc * pill[..., None] * 0.92
    a_p = mask(lambda d: spaced(d, X + 22, py + 35, ptxt, fp, 4))
    txtc = hexc('#101010') if lum > 150 else hexc('#ffffff')
    img = img * (1 - a_p[..., None]) + txtc * a_p[..., None]
    out = np.clip(img, 0, 255).astype(np.uint8)
    fn = title.replace("'", '').replace('\u2019', '').replace(',', '')
    fn = '_'.join(fn.split())
    path = f'/home/claude/out/{fn}_Thumbnail.jpg'
    cv2.imwrite(path, out, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(path)


if __name__ == '__main__':
    for s_ in sys.argv[1:]:
        thumb(s_)
