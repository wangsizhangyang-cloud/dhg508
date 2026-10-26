# -*- coding: utf-8 -*-
"""Iteration 13: guard refinement against the hi-res photo
(goujian_sword_2019_06_full.jpg guard crop):
- the real guard's ends flare outward and curl (hooked tips);
- the inlays are fewer, larger OVAL stones: two blue-glass ovals on the front
  (+Z, 正面), two turquoise ovals on the back (-Z, 背面) — not 5 small squares.

Replaces the 10 small gems with 4 oval inlays and adds the curled end horns.
"""
import bpy, math
from mathutils import Vector

# 1. remove the old square gems + pass3 scroll tubes (clutter vs the real
#    guard's clean openwork silhouette)
n = 0
for o in list(bpy.data.objects):
    if o.name.startswith('Gem_') or o.name.startswith('Scroll_'):
        bpy.data.objects.remove(o, do_unlink=True)
        n += 1
print("old gems/scrolls removed:", n, flush=True)

col = bpy.data.collections['goujian_sword']
emp = bpy.data.objects['Goujian_Sword']
GUARD_X = 0.0765

# 2. oval inlays: front = blue glass, back = turquoise
def oval(name, x, y, z, mat, ry=0.75, rz=0.35):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12,
                                         radius=0.0046, location=(x, y, z))
    o = bpy.context.active_object
    o.name = name
    o.scale = (1.0, ry, rz)
    o.data.materials.clear()
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    o.parent = emp
    return o

mb = bpy.data.materials['stone_blue']
mt = bpy.data.materials['stone_turquoise']
for s in (1, -1):
    for k, yy in enumerate((-0.011, 0.011)):
        if s > 0:
            oval(f"Inlay_blue_{k}", GUARD_X, yy, s * 0.0086, mb)
        else:
            oval(f"Inlay_turq_{k}", GUARD_X, yy, s * 0.0086, mt)
print("oval inlays placed (2 blue front, 2 turquoise back)", flush=True)

# 3. (卷钩端饰尝试过两版，均在此建模精度下读感不佳，已移除——保留干净轮廓；
#    如需可参照实物照片另做透雕端饰)

# 4. renders + save
scn = bpy.context.scene
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
print("ITERATION 13 (guard refinement) done")
