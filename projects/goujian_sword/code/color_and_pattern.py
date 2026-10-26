# -*- coding: utf-8 -*-
"""One-shot: as-new colors + museum-photo pattern (finer lattice, thinner
lines, 4-petal star at each crossing), then renders + save + verify print.

Reads the CURRENT (aged) node state:
  Mix.003 (band base): A=(0.54,0.45,0.25) B=(0.20,0.22,0.13)
  Mix (lines):         A=(0.66,0.53,0.24) B=(0.035,0.03,0.02)
  Mix.001 (edge):      B=(0.80,0.76,0.62)
  Mix.002 (roughness): A(2)=0.55 B(3)=0.30
  pitch MULTIPLY = 116.27907 (p=0.0086); line LESS_THAN = 0.068
"""
import bpy, math
import numpy as np

nt = bpy.data.materials['blade_gold'].node_tree

def mathnodes(op):
    return [n for n in nt.nodes if n.type == 'MATH' and n.operation == op]

def mix_by_b(test):
    for n in nt.nodes:
        if n.type == 'MIX' and n.data_type == 'RGBA':
            b = n.inputs[7].default_value
            if test(b):
                return n
    raise RuntimeError('mix node not found')

# ---- pattern: finer pitch + thinner lines ----
for n in mathnodes('MULTIPLY'):
    if abs(n.inputs[1].default_value - 116.27907) < 0.01:
        n.inputs[1].default_value = 1.0 / 0.0068
for n in mathnodes('LESS_THAN'):
    if abs(n.inputs[1].default_value - 0.068) < 0.001:
        n.inputs[1].default_value = 0.05
print("pitch/width set", flush=True)

# ---- as-new colors on the existing nodes ----
mixO = mix_by_b(lambda b: abs(b[0]-0.20) < 0.02 and abs(b[1]-0.22) < 0.02)
mixO.inputs[6].default_value = (0.80, 0.62, 0.24, 1)   # margins: rich bronze-gold
mixO.inputs[7].default_value = (0.72, 0.55, 0.20, 1)   # band: deeper gold
edgeMix = mix_by_b(lambda b: abs(b[0]-0.80) < 0.02 and abs(b[2]-0.62) < 0.02)
edgeMix.inputs[7].default_value = (1.0, 0.95, 0.75, 1)  # polished edges
mixn = mix_by_b(lambda b: abs(b[0]-0.035) < 0.01 and abs(b[1]-0.03) < 0.01)
mixn.inputs[7].default_value = (0.010, 0.008, 0.006, 1)  # crisp black lattice
roughMix = next(n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'FLOAT'
                and abs(n.inputs[2].default_value - 0.55) < 0.03)
roughMix.inputs[2].default_value = 0.24
roughMix.inputs[3].default_value = 0.12
print("as-new blade colors set", flush=True)

# ---- crossing flowers (star at each lattice crossing) ----
subs = []
for n in mathnodes('SUBTRACT'):
    if abs(n.inputs[1].default_value - 0.5) < 0.001 and n.inputs[0].links:
        src = n.inputs[0].links[0].from_node
        if src.type == 'MATH' and src.operation == 'FRACT':
            subs.append(n)
assert len(subs) == 2, "subs=%d" % len(subs)
abss = []
for n in mathnodes('ABSOLUTE'):
    if n.inputs[0].links:
        src = n.inputs[0].links[0].from_node
        if src.type == 'MATH' and src.operation == 'SUBTRACT':
            abss.append(n)
assert len(abss) == 2, "abss=%d" % len(abss)
a1, a2 = abss[0], abss[1]

def newmath(op, a=None, b=None):
    n = nt.nodes.new('ShaderNodeMath')
    n.operation = op
    if a is not None:
        nt.links.new(a, n.inputs[0])
    if b is not None:
        n.inputs[1].default_value = b
    return n

R, W2 = 0.17, 0.115

def lozenge(absN, absOther):
    inv = newmath('DIVIDE', a=absN.outputs[0], b=R)
    one = newmath('SUBTRACT', a=inv.outputs[0], b=1.0)     # |d|/R - 1  (<=0 inside)
    neg = newmath('MULTIPLY', a=one.outputs[0], b=-1.0)    # 1 - |d|/R
    wN = newmath('MULTIPLY', a=neg.outputs[0], b=W2)
    cond_w = newmath('LESS_THAN', a=absOther.outputs[0], b=0.0)
    nt.links.new(wN.outputs[0], cond_w.inputs[1])
    cond_r = newmath('LESS_THAN', a=absN.outputs[0], b=R)
    both = newmath('MULTIPLY', a=cond_r.outputs[0], b=0.0)
    nt.links.new(cond_w.outputs[0], both.inputs[1])
    return both

lz1 = lozenge(a1, a2)
lz2 = lozenge(a2, a1)
star = newmath('MAXIMUM', a=lz1.outputs[0], b=0.0)
nt.links.new(lz2.outputs[0], star.inputs[1])

line_link = mixn.inputs[0].links[0]
lineFac = line_link.from_node
fl_in = newmath('MULTIPLY', a=star.outputs[0], b=0.0)
nt.links.new(lineFac.outputs[0], fl_in.inputs[1])
nt.links.remove(line_link)
un = newmath('MAXIMUM', a=fl_in.outputs[0], b=0.0)
nt.links.new(lineFac.outputs[0], un.inputs[1])
nt.links.new(un.outputs[0], mixn.inputs[0])
print("crossing flowers wired", flush=True)

# ---- fittings: as-new ----
for name, col, rough in (
        ('guard_gold',      (0.80, 0.62, 0.20), 0.26),
        ('pommel_bronze',   (0.75, 0.59, 0.22), 0.28),
        ('grip_bronze',     (0.22, 0.10, 0.06), 0.55),
        ('gold_text',       (0.92, 0.78, 0.40), 0.20),
        ('stone_turquoise', (0.03, 0.68, 0.50), 0.12),
        ('stone_blue',      (0.04, 0.20, 0.85), 0.08),
        ('stone_cyan',      (0.06, 0.52, 0.82), 0.10)):
    m = bpy.data.materials.get(name)
    if m is None:
        print("skip (not present):", name, flush=True)
        continue
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
print("fittings colored", flush=True)

# ---- renders + save + verify ----
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

# verify from the saved copy
bpy.ops.wm.open_mainfile(filepath=r"E:\508\dhg508-workspace\projects\goujian_sword\artifacts\goujian_sword.blend")
nt2 = bpy.data.materials['blade_gold'].node_tree
for n in nt2.nodes:
    if n.name == 'Mix.003':
        print("VERIFY Mix.003 A=", tuple(round(float(v),3) for v in n.inputs[6].default_value),
              "B=", tuple(round(float(v),3) for v in n.inputs[7].default_value), flush=True)
g = bpy.data.materials['guard_gold']
gb = next(n for n in g.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
print("VERIFY guard_gold", tuple(round(float(v),3) for v in gb.inputs['Base Color'].default_value), flush=True)
print("ALL DONE (colors + flowers + renders + save)")
