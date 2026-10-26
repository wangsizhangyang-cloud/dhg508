# -*- coding: utf-8 -*-
"""Iteration 5: refine the model against the RAW museum photos
(sources/raw/goujian_sword/images/goujian_sword_2018_leiem.jpg and
 _2023_01.jpg).

What the raw photos show (vs the model):
- The dark diamond lattice covers the ENTIRE blade, from the collar to the
  tip, not just x > 0.147. The two inscription columns sit ON the patterned
  face right ahead of the guard.
- The lattice is confined to the central ~60% of the blade width; along both
  cutting edges the blade stays bright polished gold (wide margins), and the
  margins narrow toward the tip until the pattern covers the whole tip.
- The pommel reads as darker olive-bronze (not bright gold) with its ring
  grooves.
- Lattice lines are finer than in the model.

Changes:
1. blade_gold: pattern region now starts at x=0.0855 (guard) and is capped to
   |y| < 0.0163 (0.0145 at first run; widened after comparing renders with the
   raw closeup, where the bright edge margins are narrower); inside the band
   the base is tinted olive, with the dark diamond lines on top; outside stays
   bright gold.
2. lattice line width 0.078 -> 0.068 (finer).
3. edge polish ramp widened (0.55/0.82 -> 0.50/0.76).
4. pommel + center domes -> new darker 'pommel_bronze' material.
5. renders + blend copy.
"""
import bpy, math

mb = bpy.data.materials['blade_gold']
nt = mb.node_tree

sep = next(n for n in nt.nodes if n.type == 'SEPXYZ'
           and n.inputs['Vector'].links
           and n.inputs['Vector'].links[0].from_node.type == 'TEX_COORD')
gt = next(n for n in nt.nodes if n.type == 'MATH' and n.operation == 'GREATER_THAN')
mx = next(n for n in nt.nodes if n.type == 'MATH' and n.operation == 'MAXIMUM')
lt_nodes = [n for n in nt.nodes if n.type == 'MATH' and n.operation == 'LESS_THAN']
mixn = next(n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'RGBA'
            and n.inputs[7].default_value[0] < 0.1)
ramp = next(n for n in nt.nodes if n.type == 'VALTORGB')

# 1) pattern region: whole blade from the collar, central band only
gt.inputs[1].default_value = 0.0855
absY = nt.nodes.new('ShaderNodeMath'); absY.operation = 'ABSOLUTE'
nt.links.new(sep.outputs['Y'], absY.inputs[0])
ltY = nt.nodes.new('ShaderNodeMath'); ltY.operation = 'LESS_THAN'
ltY.inputs[1].default_value = 0.0163
nt.links.new(absY.outputs[0], ltY.inputs[0])
regB = nt.nodes.new('ShaderNodeMath'); regB.operation = 'MULTIPLY'
nt.links.new(gt.outputs[0], regB.inputs[0])
nt.links.new(ltY.outputs[0], regB.inputs[1])

# olive tint inside the band, bright gold outside
mixO = nt.nodes.new('ShaderNodeMix'); mixO.data_type = 'RGBA'
mixO.inputs[6].default_value = (0.66, 0.53, 0.24, 1)
mixO.inputs[7].default_value = (0.38, 0.35, 0.19, 1)
nt.links.new(regB.outputs[0], mixO.inputs[0])
nt.links.new(mixO.outputs[2], mixn.inputs[6])

# 2) finer lattice lines
for l in lt_nodes:
    l.inputs[1].default_value = 0.068

# dark lines only inside the band
lineFac = nt.nodes.new('ShaderNodeMath'); lineFac.operation = 'MULTIPLY'
nt.links.new(regB.outputs[0], lineFac.inputs[0])
nt.links.new(mx.outputs[0], lineFac.inputs[1])
for l in list(mixn.inputs[0].links):
    nt.links.remove(l)
nt.links.new(lineFac.outputs[0], mixn.inputs[0])

# 3) wider polished edge margins
ramp.color_ramp.elements[0].position = 0.50
ramp.color_ramp.elements[1].position = 0.76

# 4) pommel darker bronze (per raw photos)
mp = bpy.data.materials.new('pommel_bronze')
mp.use_nodes = True
pb = next(n for n in mp.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
pb.inputs['Base Color'].default_value = (0.42, 0.33, 0.16, 1)
pb.inputs['Metallic'].default_value = 1.0
pb.inputs['Roughness'].default_value = 0.38
pom = bpy.data.objects['Pommel']
pom.data.materials.clear(); pom.data.materials.append(mp)
for s in (1, -1):
    d = bpy.data.objects.get(f'PommelDome_{s}')
    if d:
        d.data.materials.clear(); d.data.materials.append(mp)

# 5) renders + save
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
print("ITERATION 5 done")
