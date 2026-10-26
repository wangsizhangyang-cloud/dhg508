# -*- coding: utf-8 -*-
"""Iteration 8: detail fixes against records and the hi-res museum photo
(sources/raw/goujian_sword/images/inscription/goujian_sword_2019_06_full.jpg,
5794x3868 original).

1. Blade tip: official description "前锋曲弧内凹" (concave sweeping point).
   Rebuild the blade loft with tip profile power 0.48 -> 1.3 (concave).
2. Guard stones per official record: front (+Z, 正面) = blue glass (蓝色琉璃),
   back (-Z, 背面) = turquoise (绿松石).
3. Grip: the real grip is a smooth silk-cord wrap, not a coarse coil spring.
   Remove the 23 raised coil rings (GripRib_*) and put a fine spiral cord bump
   into the grip_bronze material instead. Keep the two raised bands.
4. Renders + blend copy.
"""
import bpy, math

# ---------- 1. blade rebuild with concave tip ----------
XB, XT = 0.083, 0.556
W0, TH0 = 0.0232, 0.0026

def wfun(t):
    if t <= 0.8:
        return W0 * (1 - 0.18 * t)
    return W0 * 0.856 * (((1 - t) / 0.2) ** 1.3)

def thfun(t):
    return TH0 * (max(wfun(t), 1e-6) / W0) ** 0.8

ring = [(1,0),(0.35,0.8),(0,1),(-0.35,0.8),(-1,0),(-0.35,-0.8),(0,-1),(0.35,-0.8)]
N = 56
verts, faces = [], []
for i in range(N + 1):
    t = i / N
    x = XB + t * (XT - XB)
    w, th = wfun(t), thfun(t)
    for a, b in ring:
        verts.append((x, a * w, b * th))
for i in range(N):
    for j in range(8):
        faces.append((i*8+j, i*8+(j+1) % 8, (i+1)*8+(j+1) % 8, (i+1)*8+j))
faces.append(tuple(range(7, -1, -1)))
tip = len(verts); verts.append((XT, 0, 0)); last = N*8
for j in range(8):
    faces.append((last+j, last+(j+1) % 8, tip))

blade = bpy.data.objects['Blade']
old = blade.data
me = bpy.data.meshes.new('Blade')
me.from_pydata(verts, [], faces)
me.validate()
me.materials.append(bpy.data.materials['blade_gold'])
blade.data = me
bpy.data.meshes.remove(old)
print("blade rebuilt, tip power 1.3 (concave)")
bpy.ops.object.select_all(action='DESELECT')
blade.select_set(True); bpy.context.view_layer.objects.active = blade
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
try:
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
except Exception:
    for p in blade.data.polygons:
        p.use_smooth = True

# ---------- 2. guard stones: front blue glass, back turquoise ----------
mt = bpy.data.materials['stone_turquoise']
mb = bpy.data.materials['stone_blue']
mc = bpy.data.materials['stone_cyan']
n_front = n_back = 0
for o in bpy.data.objects:
    if o.name.startswith('Gem_'):
        try:
            side = int(o.name.split('_')[1])
        except Exception:
            continue
        if side > 0:  # +Z face = 正面 -> 蓝色琉璃
            o.data.materials.clear()
            o.data.materials.append(mb if n_front % 2 == 0 else mc)
            n_front += 1
        else:        # -Z face = 背面 -> 绿松石
            o.data.materials.clear()
            o.data.materials.append(mt)
            n_back += 1
print(f"guard stones: front(blue glass)={n_front}, back(turquoise)={n_back}")

# ---------- 3. grip: remove coil rings, add fine spiral cord bump ----------
removed = 0
for o in list(bpy.data.objects):
    if o.name.startswith('GripRib'):
        bpy.data.objects.remove(o, do_unlink=True)
        removed += 1
print("removed grip ribs:", removed)

mg = bpy.data.materials['grip_bronze']
gnt = mg.node_tree
gb = next(n for n in gnt.nodes if n.type == 'BSDF_PRINCIPLED')
if 'CordBump' not in [n.name for n in gnt.nodes]:
    tc = next(n for n in gnt.nodes if n.type == 'TEX_COORD')
    sep = gnt.nodes.new('ShaderNodeSeparateXYZ'); sep.name = 'CordSep'
    gnt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    m1 = gnt.nodes.new('ShaderNodeMath'); m1.name = 'CordMulX'; m1.operation = 'MULTIPLY'
    m1.inputs[1].default_value = 1.0 / 0.0013
    gnt.links.new(sep.outputs['X'], m1.inputs[0])
    m2 = gnt.nodes.new('ShaderNodeMath'); m2.name = 'CordMulY'; m2.operation = 'MULTIPLY'
    m2.inputs[1].default_value = 1.0 / 0.03
    gnt.links.new(sep.outputs['Y'], m2.inputs[0])
    add = gnt.nodes.new('ShaderNodeMath'); add.name = 'CordAdd'; add.operation = 'ADD'
    gnt.links.new(m1.outputs[0], add.inputs[0])
    gnt.links.new(m2.outputs[0], add.inputs[1])
    mul = gnt.nodes.new('ShaderNodeMath'); mul.name = 'CordMulTau'; mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = 2 * math.pi
    gnt.links.new(add.outputs[0], mul.inputs[0])
    sn = gnt.nodes.new('ShaderNodeMath'); sn.name = 'CordSine'; sn.operation = 'SINE'
    gnt.links.new(mul.outputs[0], sn.inputs[0])
    bump2 = gnt.nodes.new('ShaderNodeBump'); bump2.name = 'CordBump'
    bump2.inputs['Strength'].default_value = 0.18
    gnt.links.new(sn.outputs[0], bump2.inputs['Height'])
    # chain: Voronoi bump -> cord bump -> BSDF
    vor_bump = next((n for n in gnt.nodes if n.type == 'BUMP'), None)
    if vor_bump:
        gnt.links.new(vor_bump.outputs['Normal'], bump2.inputs['Normal'])
    gnt.links.new(bump2.outputs['Normal'], gb.inputs['Normal'])
print("grip cord bump added")

# ---------- 4. renders + save ----------
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
print("ITERATION 8 done")
