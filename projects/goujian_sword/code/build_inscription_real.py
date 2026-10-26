# -*- coding: utf-8 -*-
"""Build the inscription as smooth gold-wire reliefs. v5: traced from the
authoritative epigraphic line drawing of the actual inscription
(wuyuescripts.com goujiansword3epigraphy.jpg, drawing by Benjamin Daniels 2018,
after Cao Jinyan 《鸟虫书通考》 illus. 46 / 《殷周金文集成》11621).

The drawing: black glyph strokes on white, green guide lines for the blade
edges and the centre ridge; drawn with the guard end UP, reading from the
guard outward (right column 越王鳩淺, left column 自作用劍), glyph tops toward
the guard — matching sources/.../goujian_sword_sources.md §7.4.
"""
import bpy, math
import numpy as np

JPG = r"E:\508\dhg508-workspace\projects\goujian_sword\sources\raw\goujian_sword\images\inscription\goujiansword3epigraphy.jpg"
WIRE_R = 0.00046
Z_BASE = 0.0021
X_NEAR = 0.108     # model X of the glyph-region edge nearest the guard
X_FAR = 0.1986     # model X of the far edge (span ~90 mm per measurement)

img = bpy.data.images.load(JPG)
w, h = img.size
print("drawing size:", w, h, flush=True)
buf = np.empty(w * h * 4, dtype=np.float32)
img.pixels.foreach_get(buf)
px = buf.reshape(h, w, 4)[::-1, :, :3]  # top-left origin, linear RGB
lum = (0.2126 * px[..., 0] + 0.7152 * px[..., 1] + 0.0722 * px[..., 2])

# green guide lines (blade edges + ridge)
green = (px[..., 1] > 0.10) & (px[..., 1] > 1.6 * px[..., 0]) & (px[..., 1] > 1.6 * px[..., 2])
gcol = green.sum(axis=0)
gth = max(20, int(0.05 * h))
gxs = np.where(gcol > gth)[0]
print("green line columns:", gxs[:5], "...", gxs[-5:] if len(gxs) > 5 else "", flush=True)
# cluster consecutive columns into lines
lines = []
if len(gxs):
    start = gxs[0]; prev = gxs[0]
    for x in gxs[1:]:
        if x - prev > 6:
            lines.append(int((start + prev) / 2)); start = x
        prev = x
    lines.append(int((start + prev) / 2))
print("green lines at x =", lines, flush=True)
x_left, x_right = lines[0], lines[-1]
x_ridge = lines[len(lines) // 2]
S = 0.046 / (x_right - x_left)   # m per px
U_RIDGE = float(x_ridge)
print(f"blade width {x_right-x_left}px = 46mm -> S={S*1000:.4f} mm/px, ridge at {x_ridge}", flush=True)

# dark glyph strokes
dark = (lum < 0.38) & (~green)
ys, xs = np.where(dark)
print("dark px:", len(xs), flush=True)

# connected components (8-conn BFS on sparse mask)
from collections import deque
lab = np.zeros(dark.shape, dtype=np.int32)
comps = []
cur = 0
for (yy, xx) in zip(ys, xs):
    if lab[yy, xx]:
        continue
    cur += 1
    q = deque([(yy, xx)]); lab[yy, xx] = cur
    pix = []
    while q:
        cy, cx = q.popleft(); pix.append((cy, cx))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < dark.shape[0] and 0 <= nx < dark.shape[1] and dark[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur; q.append((ny, nx))
    comps.append(pix)
comps.sort(key=len, reverse=True)
glyphs = comps[:8]
print("component sizes (top 8):", [len(c) for c in glyphs], flush=True)
# sort: two columns (left/right of ridge), each top->bottom
boxes = []
for pix in glyphs:
    vss = [p[0] for p in pix]; uss = [p[1] for p in pix]
    boxes.append((min(uss), min(vss), max(uss), max(vss), len(pix)))
right = sorted([b for b in boxes if (b[0]+b[2])/2 > x_ridge], key=lambda b: b[1])
left = sorted([b for b in boxes if (b[0]+b[2])/2 <= x_ridge], key=lambda b: b[1])
print("right col boxes:", len(right), "left col boxes:", len(left), flush=True)
order = [('yue', right[0]), ('wang', right[1]), ('jiu', right[2]), ('qian', right[3]),
         ('zi', left[0]), ('zha', left[1]), ('yong', left[2]), ('jian', left[3])]
vmin = min(b[1] for _, b in order)
vmax = max(b[3] for _, b in order)
Sv = (X_FAR - X_NEAR) / (vmax - vmin)
print(f"glyph span {vmax-vmin}px -> X {X_NEAR}..{X_FAR}", flush=True)

OFFS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def thin_zs(m):
    imgm = m.astype(np.uint8).copy()
    changed = True
    while changed:
        changed = False
        for step in (0, 1):
            P = np.pad(imgm, 1)
            N_ = P[:-2, 1:-1]; NE = P[:-2, 2:]; E_ = P[1:-1, 2:]; SE = P[2:, 2:]
            S_ = P[2:, 1:-1];  SW = P[2:, :-2]; W_ = P[1:-1, :-2]; NW = P[:-2, :-2]
            Nsum = N_ + NE + E_ + SE + S_ + SW + W_ + NW
            seq = [N_, NE, E_, SE, S_, SW, W_, NW]
            A = np.zeros(imgm.shape, dtype=np.int32)
            for k in range(8):
                A += ((seq[k] == 0) & (seq[(k + 1) % 8] == 1)).astype(np.int32)
            cond = (Nsum >= 2) & (Nsum <= 6) & (A == 1)
            if step == 0:
                dele = cond & (N_ * E_ * S_ == 0) & (E_ * S_ * W_ == 0)
            else:
                dele = cond & (N_ * E_ * W_ == 0) & (N_ * S_ * W_ == 0)
            dele = dele & (imgm == 1)
            if dele.any():
                imgm[dele] = 0
                changed = True
    return imgm.astype(bool)

def chains_of(mask):
    pts = set(map(tuple, np.argwhere(mask)))
    adj = {}
    for (y, x) in pts:
        for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            q = (y + dy, x + dx)
            if q in pts:
                adj.setdefault((y, x), []).append(q)
                adj.setdefault(q, []).append((y, x))
    used = set()
    chains = []

    def walk(a, b):
        chain = [a, b]
        used.add(frozenset((a, b)))
        prev, cur = a, b
        while True:
            nxt = [q for q in adj.get(cur, []) if q != prev and frozenset((cur, q)) not in used]
            if not nxt:
                break
            q = nxt[0]
            used.add(frozenset((cur, q)))
            chain.append(q)
            prev, cur = cur, q
        return chain

    for n in sorted(adj):
        if len(adj[n]) == 1:
            for q in adj[n]:
                if frozenset((n, q)) not in used:
                    chains.append(walk(n, q))
    for a, bs in sorted(adj.items()):
        for b in bs:
            if frozenset((a, b)) not in used:
                chains.append(walk(a, b))
    return chains

def chaikin(c):
    if len(c) < 3:
        return c
    out = [c[0]]
    for a, b in zip(c[:-1], c[1:]):
        out.append((0.72*a[0] + 0.28*b[0], 0.72*a[1] + 0.28*b[1]))
        out.append((0.28*a[0] + 0.72*b[0], 0.28*a[1] + 0.72*b[1]))
    out.append(c[-1])
    return out

for o in list(bpy.data.objects):
    n = o.name
    if n == 'Inscription_real' or n.startswith('Inscription_'):
        bpy.data.objects.remove(o, do_unlink=True)
        print("removed old", n, flush=True)

DS = 6          # block-mean downsample factor
H_MAX = 0.0005  # relief height

all_v = []
all_f = []
for (name, (bu0, bv0, bu1, bv1, npix)) in order:
    pad = 4
    u0 = max(0, bu0 - pad); u1 = min(w, bu1 + pad)
    v0 = max(0, bv0 - pad); v1 = min(h, bv1 + pad)
    sub = dark[v0:v1, u0:u1].astype(np.float32)
    hh, ww = sub.shape
    hh -= hh % DS; ww -= ww % DS
    sub = sub[:hh, :ww].reshape(hh // DS, DS, ww // DS, DS).mean(axis=(1, 3))
    # soft-edged height field from the clean binary mask
    p = np.pad(sub, 1)
    sm = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:] + 4 * sub) / 8.0
    hf = np.clip((sm - 0.12) / 0.6, 0.0, 1.0)
    ch, cw = hf.shape
    cell = hf[:-1, :-1] + hf[1:, :-1] + hf[:-1, 1:] + hf[1:, 1:]
    cmask = cell > 0.05
    idx = -np.ones((ch, cw), dtype=np.int64)
    vlist = []
    for j in range(ch):
        for i in range(cw):
            if cmask[max(0, j-1):j+1, max(0, i-1):i+1].any():
                idx[j, i] = len(vlist)
                U = u0 + i * DS
                V = v0 + j * DS
                X = X_NEAR + (V - vmin) * Sv
                Y = -(U - U_RIDGE) * S
                Z = Z_BASE + float(hf[j, i]) * H_MAX
                vlist.append((X, Y, Z))
    flist = []
    for j in range(ch - 1):
        for i in range(cw - 1):
            if cmask[j, i]:
                a, b = idx[j, i], idx[j, i+1]
                c, d = idx[j+1, i+1], idx[j+1, i]
                flist.append((a, b, c, d))
    off = len(all_v)
    all_v.extend(vlist)
    all_f.extend([(a+off, b+off, c+off, d+off) for (a, b, c, d) in flist])
    print(f"{name}: grid {cw}x{ch} verts={len(vlist)} faces={len(flist)}", flush=True)

print("total verts:", len(all_v), "faces:", len(all_f), flush=True)
me = bpy.data.meshes.new('Inscription_real')
me.from_pydata(all_v, [], all_f)
me.validate()
ob = bpy.data.objects.new('Inscription_real', me)
bpy.data.collections['goujian_sword'].objects.link(ob)
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True); bpy.context.view_layer.objects.active = ob
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
sol = ob.modifiers.new('Solidify', 'SOLIDIFY')
sol.thickness = 0.0004
sol.offset = -1.0
bpy.ops.object.modifier_apply(modifier='Solidify')
ob.data.materials.append(bpy.data.materials['gold_text'])
gt = bpy.data.materials['gold_text']
gtb = next(n for n in gt.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
gtb.inputs['Base Color'].default_value = (0.86, 0.74, 0.42, 1)
gtb.inputs['Roughness'].default_value = 0.33
ob.parent = bpy.data.objects['Goujian_Sword']
bpy.ops.object.shade_smooth()

scn = bpy.context.scene
emp = bpy.data.objects['Goujian_Sword']
outdir = r"E:\508\dhg508-workspace\projects\goujian_sword\research\outputs"
emp.rotation_euler = (0, 0, 0); emp.location = (0, 0, 0.02)
scn.camera = bpy.data.objects['Cam_hilt']
scn.render.resolution_x = 1600; scn.render.resolution_y = 1200
scn.render.filepath = outdir + r"\goujian_sword_model_hilt.png"
bpy.ops.render.render(write_still=True)
scn.camera = bpy.data.objects['Cam_full']
scn.render.resolution_x = 1800; scn.render.resolution_y = 1200
scn.render.filepath = outdir + r"\goujian_sword_model_full.png"
bpy.ops.render.render(write_still=True)
emp.rotation_euler = (0, math.radians(90), 0); emp.location = (0, 0, 0.578)
scn.camera = bpy.data.objects['Cam_stand']
scn.render.resolution_x = 1200; scn.render.resolution_y = 1800
scn.render.filepath = outdir + r"\goujian_sword_model_standing.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r"E:\508\dhg508-workspace\projects\goujian_sword\artifacts\goujian_sword.blend", copy=True)
print("INSCRIPTION v5 (authoritative line-drawing tracing) built")
