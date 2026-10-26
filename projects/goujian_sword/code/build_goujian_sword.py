# -*- coding: utf-8 -*-
"""Build the Sword of Goujian procedurally in Blender (no external services).

Run inside Blender (scripting tab or via MCP execute_blender_code).
Requires the KaiTi font at C:/Windows/Fonts/STKAITI.TTF for the inscription.

Spec (Hubei Provincial Museum):
- total ~55.6 cm, blade 47.3 cm, grip+pommel ~8.4 cm, guard width 5 cm
- disc pommel, 11 concentric circles (both faces)
- black diamond lattice over the blade (procedural node pattern)
- guard with blue-glass / turquoise inlays (10 gems, front+back) + 4 gold studs
- two-line inscription "越王鸠浅 / 自作用剑" as real extruded text geometry
- grip with knot texture (voronoi bump), two gold bands
Layout: built lying along +X, faces up (+Z), then parented to an empty lifted to z=0.02.
Renders: two EEVEE stills (full sword, hilt closeup) into research/outputs.
"""

import bpy, math

# ---------- helpers ----------
col = bpy.data.collections.new("goujian_sword")
bpy.context.scene.collection.children.link(col)

def tocol(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
    return o

def new_mat(name, base, metallic, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    return m

def sel(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o

def smooth(o, angle=None):
    sel(o)
    try:
        if angle is not None:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        else:
            bpy.ops.object.shade_smooth()
    except Exception:
        for p in o.data.polygons:
            p.use_smooth = True

# ---------- dimensions (metres) ----------
XB, XT = 0.083, 0.556
W0, TH0 = 0.0232, 0.0026

def wfun(t):
    if t <= 0.8:
        return W0 * (1 - 0.18 * t)
    return W0 * 0.856 * (((1 - t) / 0.2) ** 0.55)

def thfun(t):
    return TH0 * (max(wfun(t), 1e-6) / W0) ** 0.8

# ---------- blade ----------
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
me = bpy.data.meshes.new("Blade"); me.from_pydata(verts, [], faces); me.validate()
blade = tocol(bpy.data.objects.new("Blade", me))
sel(blade)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT')
smooth(blade, angle=40)

# blade material: gold + diamond lattice via pure math nodes (object coords)
mb = new_mat('blade_gold', (0.66, 0.53, 0.24), 1.0, 0.34)
nt = mb.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
tc = nt.nodes.new('ShaderNodeTexCoord')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])

def mnode(op, b=None):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op
    if b is not None: n.inputs[1].default_value = b
    return n

p, wl = 0.0086, 0.085
def fam(sign):
    add = mnode('ADD') if sign > 0 else mnode('SUBTRACT')
    nt.links.new(sep.outputs['X'], add.inputs[0]); nt.links.new(sep.outputs['Y'], add.inputs[1])
    mul = mnode('MULTIPLY', b=1/p); nt.links.new(add.outputs[0], mul.inputs[0])
    fr = mnode('FRACT'); nt.links.new(mul.outputs[0], fr.inputs[0])
    sub = mnode('SUBTRACT', b=0.5); nt.links.new(fr.outputs[0], sub.inputs[0])
    ab = mnode('ABSOLUTE'); nt.links.new(sub.outputs[0], ab.inputs[0])
    lt = mnode('LESS_THAN', b=wl); nt.links.new(ab.outputs[0], lt.inputs[0])
    return lt
lt1, lt2 = fam(+1), fam(-1)
mx = mnode('MAXIMUM'); nt.links.new(lt1.outputs[0], mx.inputs[0]); nt.links.new(lt2.outputs[0], mx.inputs[1])
gt = mnode('GREATER_THAN', b=0.147); nt.links.new(sep.outputs['X'], gt.inputs[0])
reg = mnode('MULTIPLY'); nt.links.new(mx.outputs[0], reg.inputs[0]); nt.links.new(gt.outputs[0], reg.inputs[1])
mixn = nt.nodes.new('ShaderNodeMix'); mixn.data_type = 'RGBA'
mixn.inputs[6].default_value = (0.66, 0.53, 0.24, 1)
mixn.inputs[7].default_value = (0.035, 0.03, 0.02, 1)
nt.links.new(reg.outputs[0], mixn.inputs[0])
nt.links.new(mixn.outputs[2], bsdf.inputs['Base Color'])
blade.data.materials.append(mb)

# ---------- collar ----------
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0855, 0, 0))
collar = tocol(bpy.context.active_object); collar.name = "Collar"
collar.scale = (0.0048, 0.047, 0.0058)
collar.data.materials.append(new_mat('collar_dark', (0.04, 0.03, 0.02), 0.8, 0.6))

# ---------- guard + gems + studs ----------
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.0765, 0, 0))
guard = tocol(bpy.context.active_object); guard.name = "Guard"
guard.scale = (0.013, 0.050, 0.016)
mg_guard = new_mat('guard_gold', (0.55, 0.42, 0.19), 1.0, 0.33)
guard.data.materials.append(mg_guard)
bv = guard.modifiers.new('Bevel', 'BEVEL'); bv.width = 0.0018; bv.segments = 3

mat_turq = new_mat('stone_turquoise', (0.10, 0.72, 0.60), 0.0, 0.14)
mat_blue = new_mat('stone_blue', (0.06, 0.32, 0.85), 0.0, 0.14)
mat_cyan = new_mat('stone_cyan', (0.10, 0.62, 0.92), 0.0, 0.12)
extras = []
for side in (1, -1):
    for k, yy in enumerate((-0.015, -0.0075, 0, 0.0075, 0.015)):
        bpy.ops.mesh.primitive_cube_add(size=0.0037, location=(0.0765, yy, side * 0.0088))
        g = tocol(bpy.context.active_object); g.name = f"Gem_{side}_{k}"
        g.scale = (1, 1, 0.55)
        bv2 = g.modifiers.new('Bevel', 'BEVEL'); bv2.width = 0.0007; bv2.segments = 3
        g.data.materials.append(mat_turq if k in (0, 4) else (mat_cyan if k == 2 else mat_blue))
        extras.append(g)
for side in (1, -1):
    for yy in (-0.021, 0.021):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0016, segments=16, ring_count=8, location=(0.0765, yy, side * 0.0085))
        st = tocol(bpy.context.active_object); st.name = f"Stud_{side}_{yy}"
        st.data.materials.append(mg_guard)
        extras.append(st)

# ---------- grip + bands ----------
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.006, radius2=0.0076, depth=0.054,
                                location=(0.043, 0, 0), rotation=(0, math.pi/2, 0))
grip = tocol(bpy.context.active_object); grip.name = "Grip"
mg_grip = new_mat('grip_bronze', (0.17, 0.125, 0.075), 0.85, 0.5)
gnt = mg_grip.node_tree
gb = next(n for n in gnt.nodes if n.type == 'BSDF_PRINCIPLED')
gtc = gnt.nodes.new('ShaderNodeTexCoord')
vor = gnt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 520
gnt.links.new(gtc.outputs['Object'], vor.inputs['Vector'])
bump = gnt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.35
gnt.links.new(vor.outputs['Distance'], bump.inputs['Height'])
gnt.links.new(bump.outputs['Normal'], gb.inputs['Normal'])
grip.data.materials.append(mg_grip)
smooth(grip)

bands = []
for bx in (0.030, 0.050):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0083, minor_radius=0.0015, major_segments=48,
                                     minor_segments=12, location=(bx, 0, 0), rotation=(0, math.pi/2, 0))
    b = tocol(bpy.context.active_object); b.name = f"GripBand_{bx}"
    b.data.materials.append(mg_guard); smooth(b)
    bands.append(b)

# ---------- pommel + 11 ring pairs + domes ----------
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.019, depth=0.011,
                                    location=(0.008, 0, 0), rotation=(0, math.pi/2, 0))
pom = tocol(bpy.context.active_object); pom.name = "Pommel"
pom.data.materials.append(mg_guard)
bv3 = pom.modifiers.new('Bevel', 'BEVEL'); bv3.width = 0.0008; bv3.segments = 2
smooth(pom)

mr_ring = new_mat('ring_gold', (0.42, 0.32, 0.15), 1.0, 0.4)
rings = []
for side in (1, -1):
    for i in range(11):
        r = 0.0028 + i * (0.016 - 0.0028) / 10
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.00055, major_segments=48,
                                         minor_segments=8, location=(0.008 + side * 0.0055, 0, 0),
                                         rotation=(0, math.pi/2, 0))
        rg = tocol(bpy.context.active_object); rg.name = f"Ring_{side}_{i}"
        rg.data.materials.append(mr_ring); smooth(rg)
        rings.append(rg)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0022, segments=16, ring_count=8,
                                         location=(0.008 + side * 0.0055, 0, 0))
    c = tocol(bpy.context.active_object); c.name = f"PommelDome_{side}"
    c.data.materials.append(mr_ring); rings.append(c)

# ---------- inscription (real text geometry) ----------
mtext = new_mat('gold_text', (0.78, 0.64, 0.28), 1.0, 0.22)
inscr = []
for body, yy in (("越王鸠浅", 0.0070), ("自作用剑", -0.0070)):
    cu = bpy.data.curves.new("txt", type='FONT')
    cu.body = body
    cu.font = bpy.data.fonts.load("C:/Windows/Fonts/STKAITI.TTF")
    cu.size = 0.0106
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    cu.extrude = 0.0006
    ob = tocol(bpy.data.objects.new(f"Inscription_{body}", cu))
    ob.location = (0.1115, yy, 0.0020)
    sel(ob)
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.active_object
    ob.data.materials.append(mtext)
    inscr.append(ob)

# ---------- parent to empty (raise whole sword to z=0.02) ----------
emp = bpy.data.objects.new("Goujian_Sword", None)
col.objects.link(emp)
for o in [blade, collar, guard, grip, pom] + extras + bands + rings + inscr:
    o.parent = emp
emp.location = (0, 0, 0.02)

print("BUILD OK, objects:", len(col.objects))
