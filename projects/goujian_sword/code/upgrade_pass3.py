# -*- coding: utf-8 -*-
"""Iteration 3 upgrade for the Goujian sword model (run after upgrade_pass2.py).

Changes:
- inscription font: KaiTi -> LiSu (simli.ttf) for a more antique look
  (still not a true bird-seal glyph set; noted as a known simplification)
- guard: raised spiral volutes (Scroll_*) on the step faces (front & back), tube geometry
- blade: tip taper sharpened (power 0.55 -> 0.48), mesh rebuilt in place
- lighting: cool rim area light (RimArea) for the hero view
- renders: hilt/full in lying pose, then standing hero; blend copy saved
Note: render order matters - the sword is parented to the 'Goujian_Sword' empty,
so set the empty to lying (rot 0, z 0.02) for the flat views, standing
(rot (0, 90deg, 0), z 0.578) for the hero view.
"""
import bpy, math, os

emp = bpy.data.objects['Goujian_Sword']
col = bpy.data.collections['goujian_sword']
scn = bpy.context.scene
outdir = r"E:\508\dhg508-workspace\projects\goujian_sword\research\outputs"
mg_guard = bpy.data.materials['guard_gold']

def tocol(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); return o

def sel(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o

# ---- inscription: LiSu font ----
fonts_try = ["C:/Windows/Fonts/simli.ttf", "C:/Windows/Fonts/STLITI.TTF", "C:/Windows/Fonts/STKAITI.TTF"]
font_path = next(p for p in fonts_try if os.path.exists(p))
for body in ("越王鸠浅", "自作用剑"):
    o = bpy.data.objects.get(f"Inscription_{body}")
    if o: bpy.data.objects.remove(o, do_unlink=True)
mtext = bpy.data.materials['gold_text']
for body, yy in (("越王鸠浅", 0.0070), ("自作用剑", -0.0070)):
    cu = bpy.data.curves.new("txt", type='FONT')
    cu.body = body
    cu.font = bpy.data.fonts.load(font_path)
    cu.size = 0.0108
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    cu.extrude = 0.0009
    ob = tocol(bpy.data.objects.new(f"Inscription_{body}", cu))
    ob.location = (0.1115, yy, 0.0023)
    sel(ob)
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.active_object
    ob.data.materials.append(mtext)
    ob.parent = emp

# ---- guard scrolls ----
def spiral(name, cy, face_z, r0, r1, turns, cw, tube):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); n = 72
    sp.points.add(n)
    for i in range(n + 1):
        t = i / n
        ang = turns * 2 * math.pi * t * (-1 if cw else 1)
        r = r0 + (r1 - r0) * t
        sp.points[i].co = (0.0765 + r * math.cos(ang), cy + r * math.sin(ang), face_z, 1)
    cu.bevel_depth = tube; cu.bevel_resolution = 4
    ob = bpy.data.objects.new(name, cu); col.objects.link(ob)
    ob.data.materials.append(mg_guard)
    sel(ob); bpy.ops.object.convert(target='MESH')
    ob = bpy.context.active_object
    ob.parent = emp

for side in (1, -1):
    spiral(f"Scroll_up_{side}",  0.0195, side * 0.0097, 0.0004, 0.0017, 1.7, side > 0, 0.0004)
    spiral(f"Scroll_dn_{side}", -0.0195, side * 0.0097, 0.0004, 0.0017, 1.7, side < 0, 0.0004)

# ---- blade retip (taper power 0.48) ----
XB, XT, W0, TH0, N = 0.083, 0.556, 0.0232, 0.0026, 56
def wfun(t):
    if t <= 0.8: return W0 * (1 - 0.18 * t)
    return W0 * 0.856 * (((1 - t) / 0.2) ** 0.48)
def thfun(t):
    return TH0 * (max(wfun(t), 1e-6) / W0) ** 0.8
ring = [(1,0),(0.35,0.8),(0,1),(-0.35,0.8),(-1,0),(-0.35,-0.8),(0,-1),(0.35,-0.8)]
verts, faces = [], []
for i in range(N + 1):
    t = i / N; x = XB + t * (XT - XB); w, th = wfun(t), thfun(t)
    for a, b in ring: verts.append((x, a * w, b * th))
for i in range(N):
    for j in range(8): faces.append((i*8+j, i*8+(j+1) % 8, (i+1)*8+(j+1) % 8, (i+1)*8+j))
faces.append(tuple(range(7, -1, -1)))
tip = len(verts); verts.append((XT, 0, 0)); last = N*8
for j in range(8): faces.append((last+j, last+(j+1) % 8, tip))
blade = bpy.data.objects['Blade']
me = blade.data
me.clear_geometry()
me.from_pydata(verts, [], faces); me.validate()
sel(blade)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
except Exception: pass

# ---- cool rim light ----
rl = bpy.data.lights.new('RimArea', 'AREA'); rl.energy = 26; rl.size = 1.2
rl.color = (0.85, 0.92, 1.0)
ro = bpy.data.objects.new('RimArea', rl); scn.collection.objects.link(ro)
ro.location = (-0.55, 0.30, 0.50)
con = ro.constraints.new('TRACK_TO'); con.target = bpy.data.objects['Target_stand']
con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'

# ---- renders (mind the sword pose!) ----
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
print("ITERATION 3 done")
