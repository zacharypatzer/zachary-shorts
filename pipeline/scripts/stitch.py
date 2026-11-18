import sys, numpy as np, scipy.io.wavfile as wf
# stitch chunked UVR vocal outputs: chunks.txt rows "i st s hop"
d = sys.argv[1]
rows = [l.split() for l in open(f'{d}/sep/chunks.txt') if l[0].isdigit()]
sr0, mix = wf.read(f'{d}/stereo44.wav'); N = len(mix)
acc = np.zeros((N, 2)); wsum = np.zeros(N)
for i, st, s, hop in rows:
    i, st, s, hop = int(i), float(st), float(s), float(hop)
    sr, v = wf.read(f'{d}/sep/v_{i}.wav')
    isf = v.dtype.kind == 'f'
    v = v.astype(np.float64) * (32767 if isf else 1)
    if v.ndim == 1: v = np.stack([v, v], 1)
    a = int(round(st * sr)); t = (np.arange(len(v)) + a) / sr
    w = np.clip((t - (s - 0.5)) / 1.0, 0, 1) if s > 0 else np.ones(len(v))
    w = np.minimum(w, np.clip(((s + hop + 0.5) - t) / 1.0, 0, 1))
    b = min(N, a + len(v)); acc[a:b] += v[:b-a] * w[:b-a, None]; wsum[a:b] += w[:b-a]
out = acc / np.maximum(wsum, 1e-6)[:, None]
wf.write(f'{d}/vocals.wav', sr0, np.clip(out, -32768, 32767).astype(np.int16))
print('stitched', d, len(rows), 'chunks')
