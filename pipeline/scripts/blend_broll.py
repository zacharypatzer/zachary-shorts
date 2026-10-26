#!/usr/bin/env python3
"""Cut the good parts of several AI studio clips into one silent, colour-matched 1080x1920 b-roll loop.
usage: blend_broll.py OUT.mp4 clip.mp4:start:end [clip.mp4:start:end ...]"""
import sys, subprocess, numpy as np, cv2

W, H, FPS, XF = 1080, 1920, 24, 0.4
out, segs = sys.argv[1], [s.rsplit(':', 2) for s in sys.argv[2:]]


def read(path, a, b):
    cap = cv2.VideoCapture(path); cap.set(cv2.CAP_PROP_POS_MSEC, a * 1000); fr = []
    while cap.get(cv2.CAP_PROP_POS_MSEC) < b * 1000:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    return fr


clips = [read(p, float(a), float(b)) for p, a, b in segs]

# colour match every segment to the shared average look (Reinhard transfer in Lab)
def stats(frames):
    lab = np.concatenate([cv2.cvtColor(f, cv2.COLOR_BGR2LAB).reshape(-1, 3)[::37].astype(np.float32) for f in frames[::6]])
    return lab.mean(0), lab.std(0)
st = [stats(c) for c in clips]
tm = np.mean([s[0] for s in st], 0); ts = np.mean([s[1] for s in st], 0)
tm[0] += 4  # a touch brighter overall


def grade(f, m, s):
    lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(np.float32)
    k = np.array([0.7, 0.85, 0.85])          # partial match keeps each shot natural
    lab = (lab - m) * (1 + k * (ts / s - 1)) + m + k * (tm - m)
    return cv2.cvtColor(lab.clip(0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)


def up(f):
    g = cv2.resize(f, (W, H), interpolation=cv2.INTER_LANCZOS4)
    bl = cv2.GaussianBlur(g, (0, 0), 1.4)
    return cv2.addWeighted(g, 1.35, bl, -0.35, 0)

ff = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out], stdin=subprocess.PIPE)
nx = int(XF * FPS); tail = None; n = 0
for ci, c in enumerate(clips):
    g = [up(grade(f, *st[ci])) for f in c]
    if tail is not None:
        for j in range(nx):
            a = (j + 1) / (nx + 1)
            ff.stdin.write(cv2.addWeighted(tail[j], 1 - a, g[j], a, 0).tobytes()); n += 1
        g = g[nx:]
    body = g if ci == len(clips) - 1 else g[:-nx]
    for f in body:
        ff.stdin.write(f.tobytes()); n += 1
    tail = g[-nx:]
ff.stdin.close(); ff.wait()
print(out, f'{n / FPS:.1f}s')
