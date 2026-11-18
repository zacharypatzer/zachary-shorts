#!/usr/bin/env python3
"""9:16 Facebook Reel cover that keeps the original square cover untouched: cover full-width, centred
(so Facebook's 4:5 feed crop still shows all of it), top/bottom filled with a soft mirrored extension of its own edges.
usage: reel_center_cover.py cover.jpg out.jpg"""
import sys, numpy as np, cv2
src, out = sys.argv[1:3]
W, H = 1080, 1920
C = cv2.resize(cv2.imread(src), (W, W), interpolation=cv2.INTER_AREA).astype(np.float32)
y0 = (H - W) // 2
# fill: each column continues the colour of the cover's edge rows (no mirrored content), fading to near-black
top = cv2.GaussianBlur(C[:24].mean(0, keepdims=True), (0, 0), 40)      # 1 x W x 3
bot = cv2.GaussianBlur(C[-24:].mean(0, keepdims=True), (0, 0), 40)
yy = np.arange(H, dtype=np.float32)[:, None, None]
dt = np.clip((y0 - yy) / y0, 0, 1); db = np.clip((yy - (y0 + W)) / y0, 0, 1)
img = np.where(yy < y0, top * (1 - 0.8 * dt ** 0.8), bot * (1 - 0.8 * db ** 0.8)).astype(np.float32)
img = np.broadcast_to(img, (H, W, 3)).copy()
img[y0:y0 + W] = C
# feather the cover into the extension over 50 px so there is no hard seam
# soften the seam: blur a thin band across each cover edge
for e in (y0, y0 + W):
    band = img[e - 30:e + 30].copy(); img[e - 30:e + 30] = cv2.GaussianBlur(band, (0, 0), 8)
cv2.imwrite(out, np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95]); print(out)
