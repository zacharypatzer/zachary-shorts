"""Square song cover + 'EARLY TAKE' badge (bottom-left). usage: take_cover.py SRC.jpg OUT.png "EARLY TAKE B" """
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
src, out, label = sys.argv[1:4]
S = 1668
im = Image.open(src).convert('RGB').resize((S, S), Image.LANCZOS)
im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
F = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Black.otf', 64)
d = ImageDraw.Draw(im)
sp = 6
w = sum(d.textlength(c, font=F) for c in label) + sp * (len(label) - 1)
padx, pady, h = 46, 30, 64
x0, y0 = 56, S - 56 - (h + 2 * pady)
x1, y1 = x0 + w + 2 * padx, S - 56
sh = Image.new('L', (S, S), 0); ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 10, x1, y1 + 10), 999, fill=150)
im.paste((0, 0, 0), mask=sh.filter(ImageFilter.GaussianBlur(18)))
ov = Image.new('RGBA', (S, S), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
od.rounded_rectangle((x0, y0, x1, y1), 999, fill=(16, 16, 18, 215), outline=(255, 214, 120, 255), width=6)
im = Image.alpha_composite(im.convert('RGBA'), ov)
d = ImageDraw.Draw(im)
x = x0 + padx
for c in label:
    d.text((x, (y0 + y1) / 2), c, font=F, fill=(255, 236, 190), anchor='lm'); x += d.textlength(c, font=F) + sp
im.convert('RGB').save(out)
