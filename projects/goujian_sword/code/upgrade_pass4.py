# -*- coding: utf-8 -*-
"""Iteration 4 upgrade for the Goujian sword model (run after upgrade_pass3.py).

Changes:
- blade: bright polished edge lines via shading-normal ramp (|n.y| high near the
  cutting edges -> lighter color, lower roughness). No extra geometry.
- pommel: rebuilt as a surface of revolution (lathe) with 11 real engraved
  grooves on each face; replaces the old raised tori + rims.
  NOTE: bpy.ops.mesh.spin dropped its `dvec` argument in Blender 5.x, so the
  revolution is generated manually (verts rings + quads + center fans).
- renders: lying hilt/full + standing hero; blend copy saved.

(Inscription font was already changed KaiTi -> LiSu in upgrade_pass3.py.)
"""
import bpy, math

emp = bpy.data.objects['Goujian_Sword']
col = bpy.data.collections['goujian_sword']
scn = bpy.context.scene
outdir = r"E:\508\dhg508-workspace\projects\goujian_sword\research\outputs"

def tocol(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); return o

def sel(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o

# ============ 1. blade edge lines (shader) ============
mb = bpy.data.materials['blade_gold']
nt = mb.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
mixn = next(n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'RGBA')
for l in list(bsdf.inputs['Base Color'].links):
    nt.links.remove(l)
geo = nt.nodes.new('ShaderNodeNewGeometry')
sepN = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(geo.outputs['Normal'], sepN.inputs['Vector'])
absN = nt.nodes.new('ShaderNodeMath'); absN.operation = 'ABSOLUTE'
nt.links.new(sepN.outputs['Y'], absN.inputs[0])
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.55
ramp.color_ramp.elements[1].position = 0.82
nt.links.new(absN.outputs[0], ramp.inputs['Fac'])
mixE = nt.nodes.new('ShaderNodeMix'); mixE.data_type = 'RGBA'
nt.links.new(ramp.outputs['Color'], mixE.inputs[0])
nt.links.new(mixn.outputs[2], mixE.inputs[6])
mixE.inputs[7].default_value = (1.0, 0.92, 0.72, 1)
nt.links.new(mixE.outputs[2], bsdf.inputs['Base Color'])
mixR = nt.nodes.new('ShaderNodeMix'); mixR.data_type = 'FLOAT'
nt.links.new(ramp.outputs['Color'], mixR.inputs[0])
mixR.inputs[2].default_value = 0.42
mixR.inputs[3].default_value = 0.16
nt.links.new(mixR.outputs[0], bsdf.inputs['Roughness'])

# ============ 2. pommel lathe with real grooves ============
for i in range(11):
    for s in (1, -1):
        o = bpy.data.objects.get(f"Ring_{s}_{i}")
        if o: bpy.data.objects.remove(o, do_unlink=True)
for s in (1, -1):
    o = bpy.data.objects.get(f"PommelRim_{s}")
    if o: bpy.data.objects.remove(o, do_unlink=True)
old = bpy.data.objects.get("Pommel")
if old: bpy.data.objects.remove(old, do_unlink=True)

fx_hi, fx_lo = 0.0135, 0.0025
ring_r = [0.0028 + i * (0.016 - 0.0028) / 10 for i in range(11)]
def face_path(fx, s):
    pts = [(fx, 0.0019)]
    for r in ring_r:
        pts += [(fx, r - 0.00055), (fx - s * 0.0006, r - 0.00028),
                (fx - s * 0.0006, r + 0.00028), (fx, r + 0.00055)]
    pts.append((fx, 0.0182))
    return pts
prof = face_path(fx_hi, 1) + [(0.0138, 0.0190), (0.0128, 0.0193), (0.0032, 0.0193), (0.0022, 0.0190)] + face_path(fx_lo, -1)[::-1]

STEPS = 72
n = len(prof)
verts = []
for j in range(STEPS):
    a = 2 * math.pi * j / STEPS
    ca, sa = math.cos(a), math.sin(a)
    for (x, r) in prof:
        verts.append((x, r * ca, r * sa))
faces = []
for j in range(STEPS):
    j2 = (j + 1) % STEPS
    for i in range(n - 1):
        faces.append((j * n + i, j * n + i + 1, j2 * n + i + 1, j2 * n + i))
c_hi = len(verts); verts.append((fx_hi, 0, 0))
c_lo = len(verts); verts.append((fx_lo, 0, 0))
for j in range(STEPS):
    j2 = (j + 1) % STEPS
    faces.append((j * n, j2 * n, c_hi))
    faces.append((j2 * n + n - 1, j * n + n - 1, c_lo))

me = bpy.data.meshes.new('Pommel')
me.from_pydata(verts, [], faces); me.validate()
pom = tocol(bpy.data.objects.new("Pommel", me))
sel(pom)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
pom.data.materials.append(bpy.data.materials['guard_gold'])
try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
except Exception: pass
pom.parent = emp

# ============ 3. renders + save ============
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
print("ITERATION 4 done")
