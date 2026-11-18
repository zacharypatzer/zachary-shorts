#!/usr/bin/env python3
"""Platform check for Shorts/Reels (Facebook quality checklist + YouTube/TikTok/IG limits).

usage: check_platform.py VIDEO.mp4 [ORIGINAL.mp4]   -> prints PASS/FAIL lines, exit 1 on any fail

Checks: 1080x1920 (9:16, >=720p), has audio, 10 s < duration <= 90 s, size < 250 MB,
no flat border (edge strips that are a single flat dark color across the video),
and if ORIGINAL is given: same duration (+-0.15 s) so the sound still lines up.
"""
import json, subprocess, sys, numpy as np

def probe(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
        'stream=codec_type,width,height:format=duration,size', '-of', 'json', f],
        capture_output=True, text=True)
    return json.loads(r.stdout)

def frames(f, n=8, w=270, h=480):
    d = float(probe(f)['format']['duration'])
    out = []
    for i in range(n):
        t = d * (i + 0.5) / n
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', f, '-frames:v', '1',
            '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True)
        if len(r.stdout) == w * h:
            out.append(np.frombuffer(r.stdout, np.uint8).reshape(h, w).astype(float))
    return np.array(out)

def main():
    f = sys.argv[1]; orig = sys.argv[2] if len(sys.argv) > 2 else None
    p = probe(f); fails = []
    v = [s for s in p['streams'] if s['codec_type'] == 'video'][0]
    a = [s for s in p['streams'] if s['codec_type'] == 'audio']
    dur = float(p['format']['duration']); size = int(p['format']['size'])
    if (v['width'], v['height']) != (1080, 1920): fails.append(f"size {v['width']}x{v['height']}")
    if not a: fails.append('no audio')
    if not 10 < dur <= 90: fails.append(f'duration {dur:.1f}s')
    if size > 250e6: fails.append(f'file {size/1e6:.0f} MB')
    fr = frames(f)
    # border = an edge strip (4% of frame) that is flat (tiny spread) in every sampled frame
    for name, sl in [('top', np.s_[:, :20, :]), ('bottom', np.s_[:, -20:, :]),
                     ('left', np.s_[:, :, :11]), ('right', np.s_[:, :, -11:])]:
        strip = fr[sl]
        flat = [s.std() < 3.0 for s in strip]
        if all(flat): fails.append(f'flat {name} border')
    if orig:
        od = float(probe(orig)['format']['duration'])
        if abs(od - dur) > 0.15: fails.append(f'duration changed {od:.2f}->{dur:.2f}')
    print(('PASS ' if not fails else 'FAIL ') + f + ('' if not fails else '  ' + '; '.join(fails)))
    sys.exit(1 if fails else 0)

main()
