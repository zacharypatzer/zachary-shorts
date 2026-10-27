"""Facebook carousels for The Real Life Series (one per book, 1080x1350).
usage: python3 books.py [COVER_DIR]   covers named book1.jpg, book2.jpg, book3.jpg (flat front covers)
Text comes from each book's back cover, so nothing is quoted that isn't in the final book.
"""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import lib
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)
OUT = os.path.join(os.path.dirname(R), 'carousels', 'books'); os.makedirs(OUT, exist_ok=True)
COVERS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'assets', 'book_covers')
W, H = lib.W, lib.H

def portrait_slide(big, small, i, n, kicker=None):
    im = lib.bg()
    P = cv2.cvtColor(cv2.imread(f'{R}/assets/face_src.jpg'), cv2.COLOR_BGR2RGB).astype(np.float32)
    m = cv2.imread(f'{R}/assets/face_matte.png', 0).astype(np.float32) / 255
    s = 0.6; P = cv2.resize(P, None, fx=s, fy=s, interpolation=cv2.INTER_AREA); m = cv2.resize(m, (P.shape[1], P.shape[0]))
    ph, pw = P.shape[:2]; x0 = (W - pw) // 2; y0 = 120
    yy = np.linspace(0, 1, ph)[:, None]; m = m * np.clip((1 - yy) / 0.18, 0, 1)
    base = np.asarray(im).astype(np.float32)
    reg = base[y0:y0+ph, x0:x0+pw]; base[y0:y0+ph, x0:x0+pw] = reg*(1-m[..., None]) + P*m[..., None]
    im = Image.fromarray(base.astype(np.uint8)); d = ImageDraw.Draw(im)
    y = y0 + ph + 10
    if kicker:
        fk = ImageFont.truetype(lib.INTER, 30); sp = ' '.join(kicker.upper())
        d.text(((W - d.textlength(sp, font=fk)) / 2, y), sp, font=fk, fill=lib.GOLD); y += 70
    y = lib.block(d, y, big, lib.lora(64), lib.CREAM); y += 10
    d.line([(W/2-70, y), (W/2+70, y)], fill=lib.GOLD, width=3); y += 30
    lib.block(d, y, small, lib.lora(42, False), lib.DIM)
    f = ImageFont.truetype(lib.INTERM, 34); t = 'Swipe  →'; d.text(((W - d.textlength(t, font=f)) / 2, H - 180), t, font=f, fill=lib.GOLD)
    lib.footer(d, i, n); return im

def cover_slide(path, caption, i, n):
    im = lib.bg(); d = ImageDraw.Draw(im)
    c = Image.open(path).convert('RGB')
    ch = 900; cw = round(c.width * ch / c.height)
    if cw > 760: cw = 760; ch = round(c.height * cw / c.width)
    c = c.resize((cw, ch), Image.LANCZOS)
    x0, y0 = (W - cw) // 2, 110
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rectangle([x0+14, y0+22, x0+cw+14, y0+ch+22], fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(26)); im.paste((0, 0, 0), (0, 0), sh)
    im.paste(c, (x0, y0)); d = ImageDraw.Draw(im)
    lib.block(d, y0 + ch + 50, caption, lib.lora(44, False), lib.DIM)
    lib.footer(d, i, n); return im

BOOKS = {
 1: dict(slug='real_life_happens', title='Real Life Happens. Real People Don’t.',
   s1=('When real life calls, pick up.', 'I wrote a book for the nights everything feels too loud.'),
   cover='Book 1 of The Real Life Series',
   s3=('Life rarely waits until you feel ready.', 'A bad night. A hard conversation. A plan that falls apart.'),
   s4=('Twenty phone calls.', 'With the guy people call when everything feels too loud.'),
   s5=('Every call ends with a Steady Card.', 'What’s in your control. Your next move. One thing to remember.')),
 2: dict(slug='things_break', title='Things Break. People Rebuild.',
   s1=('What’s still standing?', 'The one question every rebuild starts with.'),
   cover='Book 2 of The Real Life Series',
   s3=('Sooner or later, something comes apart.', 'A job. A marriage. A body. A plan you built your whole life around.'),
   s4=('Twenty conversations at a picnic table.', 'Strangers sit down across from a guy with a buggie and end up telling him the truth.'),
   s5=('No fake masks.', 'Just honest talk, and the kind of company that makes the next step feel possible.')),
 3: dict(slug='walk_with_me', title='Figuring Things Out. Walk With Me.',
   s1=('Who’s worth going through hell for?', 'I’m still figuring it out. Walk with me.'),
   cover='Book 3 of The Real Life Series',
   s3=('Surviving is supposed to be the end of the story.', 'It isn’t. It’s just a different middle.'),
   s4=('Twenty walks at buggie speed.', 'With whoever falls into step.'),
   s5=('No gurus. No slogans.', 'Just a guy who walks slow enough for you to keep up with your own thoughts.')),
}

def build(b):
    B = BOOKS[b]; n = 6; cov = os.path.join(COVERS, f'book{b}.jpg')
    slides = [portrait_slide(*B['s1'], 1, n, kicker='Stage 4 survivor. Author.')]
    if os.path.exists(cov): slides.append(cover_slide(cov, B['cover'], 2, n))
    else: slides.append(lib.slide(B['title'], B['cover'] + '\n[cover goes here]', 2, n))
    slides.append(lib.slide(*B['s3'], 3, n))
    slides.append(lib.slide(*B['s4'], 4, n))
    slides.append(lib.slide(*B['s5'], 5, n))
    slides.append(lib.slide('Paperback, hardcover, and Kindle.', 'Link in the comments.', 6, n, kicker='The Real Life Series'))
    for i, im in enumerate(slides, 1):
        im.save(os.path.join(OUT, f'book{b}_{B["slug"]}_{i}.jpg'), quality=93)

for b in BOOKS: build(b)
print('ok', OUT)
