# -*- coding: utf-8 -*-
"""Probe v3: auto-locate the 8 character crops in Deciphering_the_sword.jpg
via interval-based connected components of the dark regions, then build one
binary mask per character (bright gold strokes inside each dark box).

Outputs (artifacts/trace_probe/):
- chars_rgb.png / chars_masks.png montages
- prints each char bbox + fill
"""
import bpy, os, traceback, sys
import numpy as np
from collections import deque

OUT = r"E:\508\dhg508-workspace\projects\goujian_sword\artifacts\trace_probe"
JPG = r"E:\508\dhg508-workspace\projects\goujian_sword\sources\raw\goujian_sword\images\inscription\Deciphering_the_sword.jpg"

def save_png(name, arr01):
    h, w = arr01.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = arr01[..., None]
    rgba = rgba[::-1]
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = os.path.join(OUT, name)
    img.file_format = 'PNG'
    img.save()

def erode(m):
    r = m.copy()
    r[1:, :] &= m[:-1, :]; r[:-1, :] &= m[1:, :]
    r[:, 1:] &= m[:, :-1]; r[:, :-1] &= m[:, 1:]
    return r

def dilate(m):
    r = m.copy()
    r[1:, :] |= m[:-1, :]; r[:-1, :] |= m[1:, :]
    r[:, 1:] |= m[:, :-1]; r[:, :-1] |= m[:, 1:]
    return r

def label_components(mask):
    """interval-based 8-connected components; returns lab array + info dict."""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    parent = {}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[rb] = ra
    info = {}
    prev = []  # list of (x0, x1, id)
    nid = 0
    for y in range(h):
        row = mask[y]
        idx = np.flatnonzero(np.diff(np.r_[False, row, False].astype(np.int8)))
        cur = []
        for k in range(0, len(idx), 2):
            x0, x1 = int(idx[k]), int(idx[k+1] - 1)
            nid += 1; parent[nid] = nid
            myid = nid
            for (p0, p1, pid) in prev:
                if p0 <= x1 + 1 and p1 >= x0 - 1:
                    union(pid, myid)
            lab[y, x0:x1+1] = myid
            cur.append((x0, x1, myid))
        prev = cur
    # flatten labels
    flat = np.zeros(nid + 1, dtype=np.int32)
    for i in range(1, nid + 1):
        flat[i] = find(i)
    lab = flat[lab]
    for y in range(h):
        for x0, x1, myid in []:
            pass
    # bboxes
    ys, xs = np.where(lab > 0)
    for lid in np.unique(lab[lab > 0]):
        sel = (lab == lid)
        yy, xx = np.where(sel)
        if len(yy) == 0: continue
        info[int(lid)] = (int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max()), int(sel.sum()))
    return lab, info

try:
    os.makedirs(OUT, exist_ok=True)
    img = bpy.data.images.load(JPG)
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    px = buf.reshape(h, w, 4)[::-1, :, :3]
    lum = 0.2126 * px[..., 0] + 0.7152 * px[..., 1] + 0.0722 * px[..., 2]

    dark = lum < 0.35
    dark[:, :440] = False  # exclude the big blade panel on the left
    # lighten the load: process at half resolution for detection
    dh, dw = dark.shape
    dark2 = dark[:dh//2*2, :dw//2*2].reshape(dh//2, 2, dw//2, 2).any(axis=(1, 3))
    lab, info = label_components(dark2)
    boxes = []
    allbig = []
    for lid, (x0, y0, x1, y1, area) in info.items():
        bw, bh = x1-x0+1, y1-y0+1
        if area > 800:
            allbig.append((2*x0, 2*y0, 2*x1+1, 2*y1+1, area*4))
        if area > 800 and 20 < bw < 80 and 50 < bh < 170:
            boxes.append((2*x0, 2*y0, 2*x1+1, 2*y1+1))
    print("all large comps (fullres coords):", len(allbig), flush=True)
    for b in sorted(allbig, key=lambda t: (t[1], t[0]))[:24]:
        print("  comp", b, "size", b[2]-b[0], b[3]-b[1], flush=True)
    print("candidate boxes:", len(boxes), flush=True)
    for b in sorted(boxes, key=lambda t: (t[1], t[0])):
        print("  box", b, "size", b[2]-b[0], b[3]-b[1], flush=True)

    # organize into 2 rows x 4 cols
    boxes.sort(key=lambda t: (t[1], t[0]))
    if len(boxes) >= 8:
        row1 = sorted(boxes[:4] if boxes[3][1] < boxes[4][1] else boxes, key=lambda t: (t[1] > 200, t[0]))
        mid = np.median([b[1] for b in boxes])
        row1 = sorted([b for b in boxes if b[1] < mid], key=lambda t: t[0])[:4]
        row2 = sorted([b for b in boxes if b[1] >= mid], key=lambda t: t[0])[:4]
        order = row1 + row2
    else:
        order = boxes

    def otsu(vals, rng=0.8):
        hist, _ = np.histogram(vals, bins=256, range=(0.0, rng))
        best_t, best_v = 0.2, -1.0
        for t in range(1, 255):
            w0 = hist[:t].sum(); w1 = hist[t:].sum()
            if w0 == 0 or w1 == 0:
                continue
            m0 = (hist[:t] * np.arange(t)).sum() / w0
            m1 = (hist[t:] * np.arange(t, 256)).sum() / w1
            v = float(w0) * float(w1) * (m0 - m1) ** 2
            if v > best_v:
                best_v, best_t = v, (t / 256.0) * rng
        return best_t

    masks = []
    rgbs = []
    for k, (x0, y0, x1, y1) in enumerate(order):
        win = lum[y0:y1, x0:x1]
        # gold strokes = strongly red-dominant; pale glare and dark blade are not
        diff = (px[y0:y1, x0:x1, 0] - px[y0:y1, x0:x1, 2]).astype(np.float32)

        def erode_sq(a, r):
            h, w = a.shape
            p = np.pad(a, ((r, r), (r, r)), constant_values=np.inf)
            acc = np.full_like(a, np.inf)
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    np.minimum(acc, p[r+dy:r+dy+h, r+dx:r+dx+w], out=acc)
            return acc

        def dilate_sq(a, r):
            h, w = a.shape
            p = np.pad(a, ((r, r), (r, r)), constant_values=-np.inf)
            acc = np.full_like(a, -np.inf)
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    np.maximum(acc, p[r+dy:r+dy+h, r+dx:r+dx+w], out=acc)
            return acc

        opening = dilate_sq(erode_sq(diff, 6), 6)
        top = diff - opening
        mx = float(top.max())
        t = max(0.05, 0.25 * mx)
        m = top > t
        print(f"  char {k+1} tophat max={mx:.3f} t={t:.3f}", flush=True)
        # drop small specks
        lab3, info3 = label_components(m)
        keep = np.zeros_like(m)
        for lid, (bx0, by0, bx1, by1, area) in info3.items():
            if area >= 25:
                keep |= (lab3 == lid)
        m = keep
        masks.append(m)
        ys_, xs_ = np.where(m)
        bb = f"({xs_.min()},{ys_.min()})-({xs_.max()},{ys_.max()})" if len(xs_) else "EMPTY"
        print(f"char {k+1}: box=({x0},{y0},{x1},{y1}) otsu={t:.3f} fill={m.mean():.3f} bbox={bb}", flush=True)
        g = win / 0.8
        rgbs.append(np.clip(g, 0, 1))

    cellw, cellh = 240, 240
    mont_rgb = np.ones((cellh * 2 + 30, cellw * 4 + 60), dtype=np.float32)
    mont_msk = np.ones_like(mont_rgb)
    for k in range(len(masks)):
        def place(dst, k, src, invert=False):
            hh, ww = src.shape
            s = min((cellw - 12) / ww, (cellh - 12) / hh)
            oh, ow = max(1, int(hh * s)), max(1, int(ww * s))
            yy = (np.arange(oh) / s).astype(int).clip(0, hh - 1)
            xx = (np.arange(ow) / s).astype(int).clip(0, ww - 1)
            small = src[yy][:, xx].astype(np.float32)
            r, c = divmod(k, 4)
            y0m = r * (cellh + 20) + 10
            x0m = c * (cellw + 12) + 10
            sub = dst[y0m:y0m+oh, x0m:x0m+ow]
            if invert:
                sub[:] = np.minimum(sub, 1 - small * 0.9)
            else:
                sub[:] = np.minimum(sub, small)
        place(mont_rgb, k, rgbs[k])
        place(mont_msk, k, masks[k], invert=True)
    save_png('chars_rgb.png', mont_rgb)
    save_png('chars_masks.png', mont_msk)
    print("PROBE3 DONE")
except Exception:
    traceback.print_exc(file=sys.stdout)
