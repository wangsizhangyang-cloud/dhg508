# -*- coding: utf-8 -*-
"""Iteration 2 upgrade for the Goujian sword model (run after build_goujian_sword.py).

Changes:
- grip: 23 stacked chain-ring ribs (matches the woven texture of the reference)
- pommel: added outer rim tori on both faces (rings kept, slightly sunk)
- guard: stepped flanges top/bottom (beast-face silhouette) with bevel
- inscription: rebuilt thicker (extrude 0.0009) and raised (z=0.0023)
- blade: roughness 0.34 -> 0.42 (matte, so raised text pops), pattern line width 0.085 -> 0.078
- renders: re-render lying full/hilt; then stand the sword (rotation_euler=(0,90deg,0),
  z=0.578) and render the vertical hero view (dark studio), floor darkened
"""
import bpy, math

emp = bpy.data.objects['Goujian_Sword']
col = bpy.data.collections['goujian_sword']
outdir = r"E:\508\dhg508-workspace\projects\goujian_sword\research\outputs"
mg_guard = bpy.data.materials['guard_gold']

def tocol(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); return o

def smooth(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o
    try: bpy.ops.object.shade_smooth()
    except Exception: pass

# ---- grip chain rings ----
def grip_r(x):
    return 0.006 + 0.0016 * (x - 0.016) / 0.054
for k in range(23):
    x = 0.0185 + k * 0.0021
    bpy.ops.mesh.primitive_torus_add(major_radius=grip_r(x) + 0.0003, minor_radius=0.0006,
                                     major_segments=48, minor_segments=8,
                                     location=(x, 0, 0), rotation=(0, math.pi/2, 0))
    o = tocol(bpy.context.active_object); o.name = f"GripRib_{k}"
    o.data.materials.append(bpy.data.materials['grip_bronze']); smooth(o)
    o.parent = emp

# ---- pommel rims ----
mr_ring = bpy.data.materials['ring_gold']
for side in (1, -1):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0180, minor_radius=0.0010,
                                     major_segments=64, minor_segments=10,
                                     location=(0.008 + side * 0.0052, 0, 0), rotation=(0, math.pi/2, 0))
    rim = tocol(bpy.context.active_object); rim.name = f"PommelRim_{side}"
    rim.data.materials.append(mr_ring); smooth(rim); rim.parent = emp

# ---- guard stepped flanges ----
for yy in (-0.0195, 0.0195):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0765, yy, 0))
    st = tocol(bpy.context.active_object); st.name = f"GuardStep_{yy}"
    st.scale = (0.011, 0.013, 0.019)
    st.data.materials.append(mg_guard)
    bv = st.modifiers.new('Bevel', 'BEVEL'); bv.width = 0.0012; bv.segments = 3
    st.parent = emp

# ---- inscription rebuild (thicker, raised) ----
for o in [bpy.data.objects.get("Inscription_越王鸠浅"), bpy.data.objects.get("Inscription_自作用剑")]:
    if o: bpy.data.objects.remove(o, do_unlink=True)
mtext = bpy.data.materials['gold_text']
for body, yy in (("越王鸠浅", 0.0070), ("自作用剑", -0.0070)):
    cu = bpy.data.curves.new("txt", type='FONT')
    cu.body = body
    cu.font = bpy.data.fonts.load("C:/Windows/Fonts/STKAITI.TTF")
    cu.size = 0.0106
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    cu.extrude = 0.0009
    ob = tocol(bpy.data.objects.new(f"Inscription_{body}", cu))
    ob.location = (0.1115, yy, 0.0023)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.active_object
    ob.data.materials.append(mtext)
    ob.parent = emp

# ---- material tweaks ----
mb = bpy.data.materials['blade_gold']
bb = next(n for n in mb.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bb.inputs['Roughness'].default_value = 0.42
for n in mb.node_tree.nodes:
    if n.type == 'MATH':
        for inp in n.inputs:
            if not inp.is_linked and abs(inp.default_value - 0.085) < 1e-6:
                inp.default_value = 0.078

# ---- renders ----
scn = bpy.context.scene
scn.camera = bpy.data.objects['Cam_full']
scn.render.resolution_x = 1800; scn.render.resolution_y = 1200
scn.render.filepath = outdir + r"\goujian_sword_model_full.png"
bpy.ops.render.render(write_still=True)
scn.camera = bpy.data.objects['Cam_hilt']
scn.render.resolution_x = 1600; scn.render.resolution_y = 1200
scn.render.filepath = outdir + r"\goujian_sword_model_hilt.png"
bpy.ops.render.render(write_still=True)

# stand the sword (tip down, face to +X) + hero render
tgt_stand = bpy.data.objects.new("Target_stand", None)
scn.collection.objects.link(tgt_stand)
tgt_stand.location = (0, 0, 0.335)
for lname in ("KeyArea", "FillArea"):
    for c in bpy.data.objects[lname].constraints:
        if c.type == 'TRACK_TO': c.target = tgt_stand
emp.rotation_euler = (0, math.radians(90), 0)
emp.location = (0, 0, 0.578)
cam = bpy.data.cameras.new('Cam_stand'); cam.lens = 45
cs = bpy.data.objects.new('Cam_stand', cam); scn.collection.objects.link(cs)
cs.location = (0.76, -0.38, 0.46)
con = cs.constraints.new('TRACK_TO'); con.target = tgt_stand
con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
gm = bpy.data.materials['studio_floor']
gb = next(n for n in gm.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
gb.inputs['Base Color'].default_value = (0.022, 0.021, 0.02, 1)
bpy.data.lights['FillArea'].energy = 24
scn.camera = cs
scn.render.resolution_x = 1200; scn.render.resolution_y = 1800
scn.render.filepath = outdir + r"\goujian_sword_model_standing.png"
bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=r"E:\508\dhg508-workspace\projects\goujian_sword\artifacts\goujian_sword.blend", copy=True)
print("ITERATION 2 done")
