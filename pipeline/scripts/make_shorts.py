#!/usr/bin/env python3
"""Cut YouTube Shorts from a finished 1080x1920 lyric video, with a hook card over the title area for the first seconds.
usage: make_shorts.py SPEC.json"""
import sys, json, subprocess, os
from PIL import Image, ImageDraw, ImageFont

spec = json.load(open(sys.argv[1]))
src, outdir, accent = spec['video'], spec['outdir'], spec.get('accent', '#5ec0ff')
os.makedirs(outdir, exist_ok=True)
FB = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
W, H = 1080, 1920
HOOK_T = 4.5


def hook_png(lines, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size = 84
    while size > 52:
        f = ImageFont.truetype(FB, size)
        if max(d.textlength(l, font=f) for l in lines) <= W - 170:
            break
        size -= 2
    lh = int(size * 1.18)
    block = lh * len(lines)
    cy = 262
    top = cy - block // 2 - 34
    bot = cy + block // 2 + 30
    top = min(top, 150)
    bot = max(bot, 372)
    d.rounded_rectangle([44, top, W - 44, bot], 34, fill=(8, 14, 26, 255), outline=accent, width=5)
    y = (top + bot) / 2 - block / 2 + size * 0.86
    for i, l in enumerate(lines):
        col = accent if (i == len(lines) - 1 and len(lines) > 1) else '#ffffff'
        d.text((W / 2 + 3, y + 4), l, font=f, fill=(0, 0, 0, 170), anchor='ms')
        d.text((W / 2, y), l, font=f, fill=col, anchor='ms')
        y += lh
    im.save(path)


for c in spec['clips']:
    png = f"{outdir}/hook_{c['id']}.png"
    hook_png(c['hook'], png)
    dur = c['end'] - c['start']
    out = f"{outdir}/{c['file']}"
    fc = (f"[1:v]format=rgba,fade=t=in:st=0:d=0.2:alpha=1,fade=t=out:st={HOOK_T - 0.4}:d=0.4:alpha=1[h];"
          f"[0:v][h]overlay=0:0:enable='lte(t,{HOOK_T})',fade=t=out:st={dur - 0.45:.2f}:d=0.45[v];"
          f"[0:a]afade=t=in:st=0:d=0.15,afade=t=out:st={dur - 0.9:.2f}:d=0.9[a]")
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f"{c['start']:.2f}", '-t', f'{dur:.2f}', '-i', src,
           '-loop', '1', '-t', f'{HOOK_T + 0.1}', '-i', png, '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '30',
           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', out]
    subprocess.run(cmd, check=True)
    print(out, f'{dur:.1f}s', f'{os.path.getsize(out) / 1048576:.1f} MiB')
