# -*- coding: utf-8 -*-
"""Iteration 14: blade pattern per the museum photo (hi-res closeup):
- finer lattice: diamond pitch 8.6 mm -> 6.8 mm
- thinner lines: half-width 0.068 -> 0.05 (cell units)
- THE KEY MOTIF: at each lattice crossing the lines swell into a small
  4-petal star/flower (visible in every museum closeup).
Implemented as math nodes: two rhombi (one along each diagonal family)
unioned into a 4-point star, masked to the pattern band.
"""
import bpy, math

nt = bpy.data.materials['blade_gold'].node_tree

def mathnodes(op):
    return [n for n in nt.nodes if n.type == 'MATH' and n.operation == op]

# 1. finer pitch: the two MULTIPLY(1/p) nodes
for n in mathnodes('MULTIPLY'):
    if abs(n.inputs[1].default_value - 116.27907) < 0.01:
        n.inputs[1].default_value = 1.0 / 0.0068
        print("pitch node -> 1/0.0068", flush=True)

# 2. thinner lines: the two LESS_THAN(0.068)
for n in mathnodes('LESS_THAN'):
    if abs(n.inputs[1].default_value - 0.068) < 0.001:
        n.inputs[1].default_value = 0.05
        print("line width node -> 0.05", flush=True)

# 3. locate the family chains: SUBTRACT(0.5) after FRACT (signed distances),
#    and their ABSOLUTE outputs
subs = []
for n in mathnodes('SUBTRACT'):
    if abs(n.inputs[1].default_value - 0.5) < 0.001 and n.inputs[0].links:
        src = n.inputs[0].links[0].from_node
        if src.type == 'MATH' and src.operation == 'FRACT':
            subs.append(n)
assert len(subs) == 2, "expected 2 signed-distance nodes, got %d" % len(subs)
abss = []
for n in mathnodes('ABSOLUTE'):
    if n.inputs[0].links:
        src = n.inputs[0].links[0].from_node
        if src.type == 'MATH' and src.operation == 'SUBTRACT':
            abss.append(n)
assert len(abss) == 2, "expected 2 abs nodes, got %d" % len(abss)
a1, a2 = abss[0], abss[1]
print("family chains located", flush=True)

def newmath(op, a=None, b=None):
    n = nt.nodes.new('ShaderNodeMath')
    n.operation = op
    if a is not None:
        nt.links.new(a, n.inputs[0])
    if b is not None:
        n.inputs[1].default_value = b
    return n

R = 0.17        # star radius (cell units)
W2 = 0.115      # petal half-width (cell units)

def lozenge(absN, absOther):
    """rhombus elongated along this family's line direction"""
    inv = newmath('DIVIDE', a=absN.outputs[0], b=R)          # |d|/R
    one = nt.nodes.new('ShaderNodeMath'); one.operation = 'SUBTRACT'
    one.inputs[1].default_value = 1.0
    nt.links.new(inv.outputs[0], one.inputs[0])              # 1 - |d|/R
    wN = newmath('MULTIPLY', a=one.outputs[0], b=W2)         # taper * petal width
    cond_w = newmath('LESS_THAN', a=absOther.outputs[0], b=0.0)
    nt.links.new(wN.outputs[0], cond_w.inputs[1])
    cond_r = newmath('LESS_THAN', a=absN.outputs[0], b=R)
    both = newmath('MULTIPLY', a=cond_r.outputs[0], b=0.0)
    nt.links.new(cond_w.outputs[0], both.inputs[1])
    return both

lz1 = lozenge(a1, a2)   # along family-1 lines
lz2 = lozenge(a2, a1)   # along family-2 lines
star = newmath('MAXIMUM', a=lz1.outputs[0], b=0.0)
nt.links.new(lz2.outputs[0], star.inputs[1])
print("star network built", flush=True)

# 4. flower only inside the band; union with the line factor
mixn = next(n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'RGBA'
            and n.inputs[7].default_value[0] < 0.02)
line_link = mixn.inputs[0].links[0]
lineFac = line_link.from_node
fl_in = newmath('MULTIPLY', a=star.outputs[0], b=0.0)
nt.links.new(lineFac.outputs[0], fl_in.inputs[1])
nt.links.remove(line_link)
un = newmath('MAXIMUM', a=fl_in.outputs[0], b=0.0)
nt.links.new(lineFac.outputs[0], un.inputs[1])
nt.links.new(un.outputs[0], mixn.inputs[0])
print("flower unioned into the line factor", flush=True)

# 5. renders + save
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
print("ITERATION 14 (crossing flowers) done")
