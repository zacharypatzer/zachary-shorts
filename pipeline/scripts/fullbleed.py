#!/usr/bin/env python3
"""Make a Short fill the whole 9:16 frame (fixes Facebook "Your video has a border").

The R2/R3 and Story Shorts show a small cover card on a flat dark background,
which Facebook/Instagram read as a bordered video. This puts the song's cover
full-bleed behind everything (title band pushed off-frame, dimmed, with a
darker band behind the lyrics), removes the small card, and keeps the original
title + lyric text on top (text is cut out of the original by brightness).

usage: fullbleed.py IN.mp4 COVER.jpg OUT.mp4 STYLE   (STYLE = r | story)
"""
import subprocess, sys, os, tempfile

inp, cover, out, style = sys.argv[1:5]
# rows (full-res) of the original small card (dropped) and the lyric band
CARD, TEXT = {'r': ((325, 865), (870, 1330)),
              'story': ((190, 775), (830, 1260))}[style]
# lyrics are lifted to forehead level so his eyes stay clear, looking back
DEST = 350

tmp = tempfile.mkdtemp()
bg = os.path.join(tmp, 'bg.png')
t0, t1 = TEXT
d0, d1 = DEST, DEST + (t1 - t0)
# base dim + a soft dark band behind the (moved) lyrics so text stays readable
band = f"(1-0.32*clip(min((Y-{d0}+160)/160,({d1}+150-Y)/200),0,1))"
dim = f"((0.98-0.20*clip((Y-900)/1000,0,1))*{band})"
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cover, '-vf',
    # mirror rows 70-150 over the top edge to hide any leftover cover-title shadow
    "scale=2320:2320:flags=lanczos,crop=1080:1920:620:495,split[m][t];"
    "[t]crop=1080:80:0:70,vflip,gblur=sigma=6[tp];[m][tp]overlay=0:0,"
    "gblur=sigma=1.2,format=gbrp,"
    f"geq=r='r(X,Y)*{dim}':g='g(X,Y)*{dim}':b='b(X,Y)*{dim}',"
    "eq=contrast=1.05:saturation=1.08,vignette=PI/8", '-frames:v', '1', bg], check=True)

a, b = CARD
# alpha from brightness: flat bg/glow (luma < ~70) -> clear, text -> solid
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', bg, '-i', inp,
    '-filter_complex',
    "[1:v]setsar=1,split[fg][m];"
    "[m]format=gray,lut=y='clip((val-60)*3.5,0,255)',"
    f"drawbox=x=0:y={a}:w=iw:h={b-a}:color=black:t=fill[a];"
    "[fg][a]alphamerge,format=rgba,split[tx][sh];"
    # soft dark shadow under all text so it reads on a bright face
    "[sh]lutrgb=r=0:g=0:b=0:a='min(255,val*3)',boxblur=luma_radius=14:alpha_radius=14[shb];"
    "[tx]split[t1][t2];[shb]split[s1][s2];"
    f"[t1]crop=iw:{a}:0:0[title];[s1]crop=iw:{a}:0:0[stitle];"
    f"[t2]crop=iw:{t1-t0}:0:{t0}[lyr];[s2]crop=iw:{t1-t0}:0:{t0}[slyr];"
    "[0]setsar=1,format=yuv420p[bg];"
    "[bg][stitle]overlay=0:0:shortest=1:format=auto[b0];"
    f"[b0][slyr]overlay=0:{d0}:format=auto[b1];"
    "[b1][title]overlay=0:0:format=auto[b2];"
    f"[b2][lyr]overlay=0:{d0}:format=auto,format=yuv420p[v]",
    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast',
    '-crf', '20', '-maxrate', '8M', '-bufsize', '16M',
    '-c:a', 'copy', '-movflags', '+faststart', out], check=True)
