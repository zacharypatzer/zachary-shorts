#!/usr/bin/env python3
"""Real-ESRGAN realesr-general-x4v3 (SRVGGNetCompact) in pure numpy.

usage: esrgan.py in.png out.png
"""
import sys, zipfile, pickle, collections
import numpy as np, cv2

PTH = '/home/claude/models/esr/realesr-general-x4v3.pth'


def load_pth(path):
    z = zipfile.ZipFile(path)
    prefix = z.namelist()[0].split('/')[0]
    dtmap = {'FloatStorage': np.float32, 'HalfStorage': np.float16, 'LongStorage': np.int64,
             'IntStorage': np.int32, 'DoubleStorage': np.float64}

    def rebuild(storage, offset, size, stride, *a):
        size, stride = tuple(size), tuple(stride)
        if len(size) == 0:
            return storage[offset].copy()
        return np.lib.stride_tricks.as_strided(storage[offset:], shape=size,
                                               strides=[s * storage.itemsize for s in stride]).copy()

    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if mod == 'torch._utils' and name == '_rebuild_tensor_v2':
                return rebuild
            if mod == 'torch' and name.endswith('Storage'):
                return name
            if mod == 'collections' and name == 'OrderedDict':
                return collections.OrderedDict
            return super().find_class(mod, name)

        def persistent_load(self, pid):
            typ, stype, key, loc, numel = pid
            stype = stype if isinstance(stype, str) else getattr(stype, '__name__', str(stype))
            return np.frombuffer(z.read(f'{prefix}/data/{key}'), dtmap[stype])

    return U(z.open(f'{prefix}/data.pkl')).load()


sd = load_pth(PTH)
sd = sd.get('params', sd.get('params_ema', sd))
keys = sorted({int(k.split('.')[1]) for k in sd}, key=int)
LAYERS = []
for k in keys:
    w = sd[f'body.{k}.weight']
    if w.ndim == 4:
        cout, cin = w.shape[:2]
        # im2col weight: (9*cin, cout), ordered (dy, dx, cin)
        wm = np.ascontiguousarray(w.transpose(2, 3, 1, 0).reshape(9 * cin, cout)).astype(np.float32)
        LAYERS.append(('conv', wm, sd[f'body.{k}.bias'].astype(np.float32)))
    else:
        LAYERS.append(('prelu', w.astype(np.float32).reshape(1, 1, -1)))


def conv3(x, wm, b):
    h, w, c = x.shape
    p = np.pad(x, ((1, 1), (1, 1), (0, 0)))
    cols = np.empty((h, w, 9 * c), np.float32)
    i = 0
    for dy in range(3):
        for dx in range(3):
            cols[:, :, i * c:(i + 1) * c] = p[dy:dy + h, dx:dx + w]
            i += 1
    return (cols.reshape(-1, 9 * c) @ wm + b).reshape(h, w, -1)


def net(x):
    inp = x
    for L in LAYERS:
        if L[0] == 'conv':
            x = conv3(x, L[1], L[2])
        else:
            x = np.where(x >= 0, x, x * L[1])
    h, w, _ = x.shape
    # pixel shuffle (C = 3*16, CRD order: c, r1, r2)
    x = x.reshape(h, w, 3, 4, 4).transpose(0, 3, 1, 4, 2).reshape(h * 4, w * 4, 3)
    up = np.repeat(np.repeat(inp, 4, 0), 4, 1)
    return x + up


def upscale(img_bgr, tile=160, pad=16):
    x = img_bgr[..., ::-1].astype(np.float32) / 255.0
    h, w, _ = x.shape
    out = np.zeros((h * 4, w * 4, 3), np.float32)
    for y0 in range(0, h, tile):
        for x0 in range(0, w, tile):
            y1, x1 = min(y0 + tile, h), min(x0 + tile, w)
            py0, px0 = max(y0 - pad, 0), max(x0 - pad, 0)
            py1, px1 = min(y1 + pad, h), min(x1 + pad, w)
            r = net(x[py0:py1, px0:px1])
            out[y0 * 4:y1 * 4, x0 * 4:x1 * 4] = r[(y0 - py0) * 4:(y0 - py0 + y1 - y0) * 4,
                                                 (x0 - px0) * 4:(x0 - px0 + x1 - x0) * 4]
    return (np.clip(out, 0, 1)[..., ::-1] * 255 + 0.5).astype(np.uint8)


if __name__ == '__main__':
    import time
    t = time.time()
    im = cv2.imread(sys.argv[1])
    cv2.imwrite(sys.argv[2], upscale(im))
    print('upscaled', im.shape, 'in', round(time.time() - t, 1), 's')
