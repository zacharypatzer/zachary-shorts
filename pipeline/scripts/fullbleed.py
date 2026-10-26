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
# soft dark band behind the (moved) lyrics so text stays readable; no bottom darkening
band = f"(1-0.32*clip(min((Y-{d0}+160)/160,({d1}+150-Y)/200),0,1))"
dim = f"(0.97*{band})"
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', cover, '-vf',
    # cover big enough that the frame stops above its dark bottom edge;
    # mirror rows 70-150 over the top edge to hide any leftover cover-title shadow
    "scale=2600:2600:flags=lanczos,crop=1080:1920:760:520,split[m][t];"
    "[t]crop=1080:80:0:70,vflip,gblur=sigma=6[tp];[m][tp]overlay=0:0,"
    "gblur=sigma=1.2,format=gbrp,"
    f"geq=r='r(X,Y)*{dim}':g='g(X,Y)*{dim}':b='b(X,Y)*{dim}',"
    # lift the shadows so no edge sits at flat black
    "curves=all='0/0.07 0.25/0.29 1/1',eq=contrast=1.04:saturation=1.08,vignette=PI/10",
    '-frames:v', '1', bg], check=True)

a, b = CARD
pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries',
    'stream=r_frame_rate:format=duration', '-of', 'default=nw=1:nk=1', inp], capture_output=True, text=True).stdout.split()
fps, dur = pr[0], pr[1]

def layer(src, h, y, tag):
    # cut one band of the original, keep only its bright text (alpha from brightness), plus a soft shadow
    return (f"[{src}]crop=iw:{h}:0:{y},split[{tag}f][{tag}m];"
            f"[{tag}m]format=gray,lut=y='clip((val-74)*4,0,255)'[{tag}a];"
            f"[{tag}f][{tag}a]alphamerge,format=rgba,split[{tag}t][{tag}s];"
            f"[{tag}s]lutrgb=r=0:g=0:b=0:a='clip((val-40)*3,0,255)',scale=iw/4:-2,boxblur=luma_radius=4:alpha_radius=4,scale=1080:{h}[{tag}sh];")

# backdrop runs at the source frame rate and exact length, so nothing gets dropped or cut
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', fps, '-t', dur, '-i', bg, '-i', inp,
    '-filter_complex',
    "[1:v]setsar=1,split[s1][s2];" + layer('s1', a, 0, 'T') + layer('s2', t1 - t0, t0, 'L') +
    "[0]setsar=1,format=yuv420p[bg];"
    "[bg][Tsh]overlay=0:0:format=auto[b0];"
    f"[b0][Lsh]overlay=0:{d0}:format=auto[b1];"
    "[b1][Tt]overlay=0:0:format=auto[b2];"
    f"[b2][Lt]overlay=0:{d0}:format=auto,format=yuv420p[v]",
    '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast',
    '-crf', '20', '-maxrate', '8M', '-bufsize', '16M',
    '-c:a', 'copy', '-movflags', '+faststart', out], check=True)
