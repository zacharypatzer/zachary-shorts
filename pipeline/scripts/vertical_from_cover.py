#!/usr/bin/env python3
"""9:16 Facebook vertical cover (1080x1920) from a song's finished square cover.
Removes the baked-in artist/title band, places the (ESRGAN 4x) cover low in the frame, fills the top with a
blurred stretch of the cover's own scene (no face in it), and redraws "ZACHARY PATZER" + the title in the
song's own font and colours (same as thumbs.py). Only the removed title band is feathered, so the face stays sharp.
Key content sits inside the centre 4:5 band so Facebook's feed crop still shows it.
usage: vertical_from_cover.py SLUG [SLUG ...]   (reads qh/covers4x/SLUG.png, else qh/covers/SLUG.jpg;
       writes out/<Title>_Facebook_Vertical.jpg)"""
import os, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

R = os.path.dirname(os.path.abspath(__file__)) + '/..'
GF = f'{R}/fonts/gfonts/'
INTER = f'{R}/sysfonts/Inter-SemiBold.otf'
W, H = 1080, 1920

# slug: (file title, title lines, font, wght, fill top, fill bottom, outline)  'rainbow' = per-letter colours
S = {
    'a_mile_an_hour': ('A_Mile_An_Hour', ['A MILE', 'AN HOUR'], 'ofl/bevan/Bevan-Regular.ttf', None, '#c9ecff', '#3aa8f5', '#03182a'),
    'a_seat_at_the_table': ('A_Seat_at_the_Table', ['A SEAT AT', 'THE TABLE'], 'ofl/uncialantiqua/UncialAntiqua-Regular.ttf', None, '#b8f5d2', '#2fc471', '#03200f'),
    'beautiful_anyway': ('Beautiful_Anyway', ['BEAUTIFUL', 'ANYWAY'], 'ofl/bebasneue/BebasNeue-Regular.ttf', None, '#ffd7b8', '#e3874f', '#2a1206'),
    'dying_to_live': ('Dying_to_Live', ['DYING', 'TO LIVE'], 'ofl/amaticsc/AmaticSC-Bold.ttf', None, '#e6ffb8', '#9ee03a', '#0d2004'),
    'embrace_every_scar': ('Embrace_Every_Scar', ['EMBRACE', 'EVERY SCAR'], 'apache/permanentmarker/PermanentMarker-Regular.ttf', None, 'rainbow', None, '#111111'),
    'even_if_we_stumble': ('Even_If_We_Stumble', ['EVEN IF WE', 'STUMBLE'], 'ofl/righteous/Righteous-Regular.ttf', None, '#e0fff2', '#5fe8b4', '#06281c'),
    'footprints_of_gold': ('Footprints_of_Gold', ['FOOTPRINTS', 'OF GOLD'], 'ofl/abrilfatface/AbrilFatface-Regular.ttf', None, '#fff1a8', '#d99a1c', '#2a1800'),
    'from_where_i_stand': ('From_Where_I_Stand', ['FROM', 'WHERE I', 'STAND'], 'ofl/holtwoodonesc/HoltwoodOneSC-Regular.ttf', None, '#ffffff', '#d9dee6', '#1a1408'),
    'i_live_on_through_you': ('I_Live_On_Through_You', ['I LIVE ON', 'THROUGH', 'YOU'], 'ofl/arvo/Arvo-Bold.ttf', None, '#ffffff', '#ffe2b0', '#1c3a7a'),
    'island_time': ('Island_Time', ['Island Time'], 'ofl/pacifico/Pacifico-Regular.ttf', None, '#c8fffd', '#2fd6d2', '#06302f'),
    'lions_heart': ('Lions_Heart', ['Lion’s Heart'], 'ofl/sansita/Sansita-BlackItalic.ttf', None, '#ffe7a0', '#ff8a1e', '#3d0f08'),
    'live_now_die_later': ('Live_Now_Die_Later', ['LIVE NOW,', 'DIE LATER'], 'ofl/cinzel/Cinzel[wght].ttf', 800, '#eef9ff', '#8fd3f5', '#06202e'),
    'make_your_time_count': ('Make_Your_Time_Count', ['MAKE YOUR', 'TIME COUNT'], 'ofl/poiretone/PoiretOne-Regular.ttf', None, '#ffe1d4', '#f2a88a', '#2a120a'),
    'my_word_wont_die': ('My_Word_Wont_Die', ['MY WORD', 'WON’T DIE'], 'ofl/shrikhand/Shrikhand-Regular.ttf', None, '#fff6e2', '#f0d49c', '#5a1408'),
    'no_complaints': ('No_Complaints', ['NO', 'COMPLAINTS'], 'apache/ultra/Ultra-Regular.ttf', None, '#c4d4ff', '#4a78ff', '#050d2e'),
    'only_the_strong_survive': ('Only_The_Strong_Survive', ['ONLY THE', 'STRONG', 'SURVIVE'], 'ofl/anton/Anton-Regular.ttf', None, '#ffffff', '#a9b1bb', '#5a0606'),
    'quiet_fire': ('Quiet_Fire', ['QUIET', 'FIRE'], 'ofl/alfaslabone/AlfaSlabOne-Regular.ttf', None, '#ffd27a', '#ff4a0a', '#2a0c00'),
    'shout_yes': ('Shout_Yes', ['SHOUT', 'YES'], 'ofl/orbitron/Orbitron[wght].ttf', 900, '#ffffff', '#ff4fd8', '#12002a'),
    'take_a_number': ('Take_a_Number', ['TAKE A', 'NUMBER'], 'ofl/rye/Rye-Regular.ttf', None, '#fff4dc', '#f1d9ad', '#6e1a16'),
    'unfinished': ('Unfinished', ['Unfinished'], 'ofl/mrdafoe/MrDafoe-Regular.ttf', None, '#ffffff', '#ffe6cc', '#1a2647'),
}
BAND = {'unfinished': 0.238}   # covers whose old title sits lower
RAINBOW = ['#ff4a4a', '#ff9a2e', '#ffe14a', '#5be35b', '#3fd0ff', '#5a7dff', '#c06bff']
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)


def font(path, size, wght):
    f = ImageFont.truetype(path, size)
    if wght:
        f.set_variation_by_axes([wght])
    return f


def mask(fn):
    m = Image.new('L', (W, H), 0); fn(ImageDraw.Draw(m)); return np.asarray(m, np.float32) / 255


def styled(img, A, col, outline, ow, shadow=0.75, bevel=70):
    Ao = cv2.GaussianBlur(cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))), (0, 0), 0.8)
    sh = cv2.GaussianBlur(np.roll(np.roll(Ao, 10, 0), 6, 1), (0, 0), 10) * shadow
    img = img * (1 - sh[..., None]); img = img * (1 - Ao[..., None]) + hexc(outline) * Ao[..., None]
    gy, gx = np.gradient(cv2.GaussianBlur(A, (0, 0), 3))
    col = col + np.clip(-(gx * 0.6 + gy * 0.8) * 9, -1, 1)[..., None] * bevel
    return img * (1 - A[..., None]) + np.clip(col, 0, 255) * A[..., None]


def grad(top, bot, y0, y1):
    t = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)[..., None]
    return hexc(top) * (1 - t) + hexc(bot) * t


def build(slug):
    ftitle, lines, fpath, wght, ftop, fbot, outl = S[slug]
    src = f'{R}/qh/covers4x/{slug}.png'
    C = cv2.imread(src if os.path.exists(src) else f'{R}/qh/covers/{slug}.jpg')
    SZ = 1350
    C = cv2.resize(C, (SZ, SZ), interpolation=cv2.INTER_AREA)
    n = SZ
    # artist + title band = top ~21% of the cover; it is replaced by the extended background
    band = int(BAND.get(slug, 0.212) * n)
    # background: the scene strip between old title and head, stretched + blurred (no face), streaks smoothed
    strip = C[band + 4:int(0.262 * n), int(0.03 * n):int(0.97 * n)]
    bg = cv2.resize(strip, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    bg = cv2.GaussianBlur(bg, (0, 0), sigmaX=70, sigmaY=30)
    tv = np.clip(yy / (H - n + band), 0, 1)[..., None]
    bg = bg * (0.42 + 0.33 * tv)                              # darker toward the top
    bg += np.random.default_rng(1).normal(0, 2.2, (H, W, 1)).astype(np.float32)
    fx = (n - W) // 2; fy = H - n
    fg = C[:, fx:fx + W].astype(np.float32)
    a = np.clip((np.arange(n) - band) / (0.052 * n), 0, 1)
    a = (a * a * (3 - 2 * a))[:, None, None]
    img = bg.copy(); img[fy:] = img[fy:] * (1 - a) + fg * a
    # darken the top so type reads, gentle vignette
    img *= (1 - 0.30 * np.clip((0.45 * H - yy) / (0.45 * H), 0, 1))[..., None]
    img *= np.clip(1 - 0.30 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.55) / (H * 0.8)) ** 2), 0.6, 1)[..., None]

    # title
    d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
    fp = GF + fpath
    maxw = W * (0.88 if len(lines) > 1 else 0.82)
    for sz in range(196 if len(lines) < 3 else 150, 60, -2):
        f = font(fp, sz, wght)
        if max(d0.textlength(l, font=f) for l in lines) <= maxw: break
    bb = [d0.textbbox((0, 0), l, font=f, anchor='ls') for l in lines]
    asc = max(-b[1] for b in bb); desc = max(b[3] for b in bb)
    lh = int((asc + desc * 0.6) * 1.08)
    total = asc + lh * (len(lines) - 1)
    y_top = {1: 470, 2: 430, 3: 400}[len(lines)]          # cap top of the title block
    base = y_top + asc
    for i, l in enumerate(lines):
        b = base + i * lh
        w = d0.textlength(l, font=f)
        if ftop == 'rainbow':
            x = (W - w) / 2; k = 0
            for ch in l:
                cw = d0.textlength(ch, font=f)
                if ch.strip():
                    A = mask(lambda d: d.text((x, b), ch, font=f, fill=255, anchor='ls'))
                    c = hexc(RAINBOW[(k + 3 * i) % len(RAINBOW)])
                    img = styled(img, A, c * 0.75 + hexc('#ffffff') * 0.25 * 0 + c * 0.25, outl, 6)
                    k += 1
                x += cw
        else:
            A = mask(lambda d: d.text(((W - w) / 2, b), l, font=f, fill=255, anchor='ls'))
            img = styled(img, A, grad(ftop, fbot, b - asc, b), outl, 7)
    # artist line
    fa = ImageFont.truetype(INTER, 44); art, sp = 'ZACHARY PATZER', 16
    wid = sum(d0.textlength(c, font=fa) for c in art) + sp * (len(art) - 1)
    ay = y_top - 52

    def draw_art(d):
        x = (W - wid) / 2
        for c in art:
            d.text((x, ay), c, font=fa, fill=255, anchor='ls'); x += d0.textlength(c, font=fa) + sp
    img = styled(img, mask(draw_art), grad('#ffffff', '#d6dbe2', ay - 34, ay), '#0a0a0a', 3, 0.55, 30)
    out = f'{R}/out/{ftitle}_Facebook_Vertical.jpg'
    cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 94])
    print(out, 'title', f.size, 'lines', len(lines), 'block', y_top, '->', base + lh * (len(lines) - 1) + desc)


for s in (sys.argv[1:] or S):
    build(s)
