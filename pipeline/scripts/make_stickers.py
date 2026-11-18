#!/usr/bin/env python3
"""Transparent PNG call-to-action stickers (LIKE / COMMENT / SHARE / SAVE) in the gold-on-dark brand style.
Dark glass pill, thin gold rim, gold medallion with a dark icon, gold label. Drawn at 4x and downsampled.
usage: make_stickers.py OUTDIR"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = os.path.dirname(os.path.abspath(__file__)) + '/..'
FONT = f'{R}/sysfonts/Inter-Black.otf'
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
K = 4                                   # supersampling
H = 220                                 # final pill height
GOLD_T, GOLD_B = (255, 236, 170), (204, 146, 46)


def grad_img(w, h, top, bot):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top, np.float32) * (1 - t) + np.array(bot, np.float32) * t
    return Image.fromarray(np.broadcast_to(a, (h, w, 3)).astype(np.uint8))


def icon_mask(kind, s):
    """white-on-black icon mask, s x s"""
    m = Image.new('L', (s, s), 0); d = ImageDraw.Draw(m); c = s / 2
    if kind == 'like':      # heart
        pts = []
        for i in range(400):
            t = 2 * math.pi * i / 400
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((c + x * s / 40, c - y * s / 40 - s * 0.02))
        d.polygon(pts, fill=255)
    elif kind == 'comment':  # speech bubble with three dots
        d.rounded_rectangle((s * .14, s * .2, s * .86, s * .7), radius=s * .16, fill=255)
        d.polygon([(s * .3, s * .66), (s * .48, s * .66), (s * .26, s * .86)], fill=255)
        for k in (-1, 0, 1):
            x = c + k * s * .17
            d.ellipse((x - s * .055, s * .45 - s * .055, x + s * .055, s * .45 + s * .055), fill=0)
    elif kind == 'share':    # paper plane
        d.polygon([(s * .12, s * .46), (s * .88, s * .16), (s * .62, s * .86), (s * .47, s * .58)], fill=255)
        d.polygon([(s * .47, s * .58), (s * .88, s * .16), (s * .42, s * .76)], fill=0)   # fold line
        d.line([(s * .47, s * .58), (s * .88, s * .16)], fill=0, width=int(s * .045))
    elif kind == 'save':     # bookmark
        d.rounded_rectangle((s * .26, s * .12, s * .74, s * .5), radius=s * .06, fill=255)
        d.polygon([(s * .26, s * .4), (s * .74, s * .4), (s * .74, s * .88), (c, s * .68), (s * .26, s * .88)], fill=255)
    return m


def sticker(kind, label):
    h = H * K; pad = int(h * 0.11)
    f = ImageFont.truetype(FONT, int(h * 0.36))
    track = int(h * 0.025)
    tw = sum(f.getlength(ch) for ch in label) + track * (len(label) - 1)
    med = h - 2 * pad                                     # medallion diameter
    w = int(pad + med + h * 0.16 + tw + h * 0.30)
    shadow_pad = int(h * 0.10)
    W, HH = w + 2 * shadow_pad, h + 2 * shadow_pad
    img = Image.new('RGBA', (W, HH), (0, 0, 0, 0))
    ox, oy = shadow_pad, shadow_pad
    box = (ox, oy, ox + w, oy + h)
    # soft drop shadow
    sh = Image.new('L', (W, HH), 0); ImageDraw.Draw(sh).rounded_rectangle((ox, oy + h * .05, ox + w, oy + h * 1.05), radius=h / 2, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(h * .06))
    img.paste((0, 0, 0, 255), (0, 0), sh)
    # gold rim
    rim = Image.new('L', (W, HH), 0); ImageDraw.Draw(rim).rounded_rectangle(box, radius=h / 2, fill=255)
    img.paste(grad_img(W, HH, GOLD_T, GOLD_B), (0, 0), rim)
    # dark body
    rw = int(h * 0.035)
    body = Image.new('L', (W, HH), 0)
    ImageDraw.Draw(body).rounded_rectangle((ox + rw, oy + rw, ox + w - rw, oy + h - rw), radius=h / 2 - rw, fill=255)
    img.paste(grad_img(W, HH, (52, 34, 26), (16, 10, 8)), (0, 0), body)
    # glossy top highlight
    gl = Image.new('L', (W, HH), 0)
    ImageDraw.Draw(gl).rounded_rectangle((ox + rw * 2, oy + rw * 2, ox + w - rw * 2, oy + h * .48), radius=h * .3, fill=38)
    img.paste((255, 255, 255, 255), (0, 0), gl.filter(ImageFilter.GaussianBlur(h * .03)))
    # medallion
    mx, my = ox + pad, oy + pad
    mm = Image.new('L', (W, HH), 0); ImageDraw.Draw(mm).ellipse((mx, my, mx + med, my + med), fill=255)
    img.paste(grad_img(W, HH, GOLD_T, GOLD_B), (0, 0), mm)
    inner = Image.new('L', (W, HH), 0); ImageDraw.Draw(inner).ellipse((mx + rw, my + rw, mx + med - rw, my + med - rw), fill=60)
    img.paste((120, 70, 10, 255), (0, 0), inner.filter(ImageFilter.GaussianBlur(rw)))
    img.paste(grad_img(W, HH, (255, 244, 200), (226, 170, 64)), (0, 0),
              Image.composite(Image.new('L', (W, HH), 255), Image.new('L', (W, HH), 0),
                              (lambda m: (ImageDraw.Draw(m).ellipse((mx + rw * 1.6, my + rw * 1.6, mx + med - rw * 1.6, my + med - rw * 1.6), fill=255), m)[1])(Image.new('L', (W, HH), 0))))
    isz = int(med * 0.60)
    im = icon_mask(kind, isz)
    full = Image.new('L', (W, HH), 0); full.paste(im, (int(mx + (med - isz) / 2), int(my + (med - isz) / 2)))
    img.paste((34, 20, 6, 255), (0, 0), full)
    # label with gold gradient + subtle dark shadow
    tx = mx + med + h * 0.16; ty = oy + h / 2
    tm = Image.new('L', (W, HH), 0); dt = ImageDraw.Draw(tm); x = tx
    for ch in label:
        dt.text((x, ty), ch, font=f, fill=255, anchor='lm'); x += f.getlength(ch) + track
    ts = Image.new('L', (W, HH), 0); ts.paste(tm, (int(h * .012), int(h * .02)))
    img.paste((0, 0, 0, 255), (0, 0), ts.filter(ImageFilter.GaussianBlur(h * .012)).point(lambda v: v * 0.8))
    img.paste(grad_img(W, HH, GOLD_T, GOLD_B), (0, 0), tm)
    return img.resize((W // K, HH // K), Image.LANCZOS)


S = [('like', 'LIKE'), ('comment', 'COMMENT'), ('share', 'SHARE'), ('save', 'SAVE')]
ims = []
for k, lab in S:
    im = sticker(k, lab); im.save(f'{out}/Sticker_{lab.title()}.png'); ims.append(im); print(lab, im.size)
# combined stack (all four, left-aligned) for quick use
gap = 18; Wc = max(i.width for i in ims); Hc = sum(i.height for i in ims) + gap * 3
c = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0)); y = 0
for i in ims: c.alpha_composite(i, ((Wc - i.width) // 2, y)); y += i.height + gap
c.save(f'{out}/Stickers_All_Four.png'); print('stack', c.size)
