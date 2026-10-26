# -*- coding: utf-8 -*-
"""Iteration 12: "as-new" colors (user choice) — the sword as it was cast
2500 years ago: bright polished golden bronze blade, crisp black diamond
pattern, vivid blue glass / turquoise inlays, rich gold fittings.

Replaces the aged/matte grade of iteration 7 (geometry and inscription
untouched).
"""
import bpy, math

# ---------- blade_gold node palette ----------
nt = bpy.data.materials['blade_gold'].node_tree
def mix_by_b(test):
    for n in nt.nodes:
        if n.type == 'MIX' and n.data_type == 'RGBA':
            b = n.inputs[7].default_value
            if test(b):
                return n
    raise RuntimeError('mix node not found')

mixO = mix_by_b(lambda b: abs(b[0]-0.62) < 0.02 and abs(b[1]-0.49) < 0.02)
mixO.inputs[6].default_value = (0.80, 0.62, 0.24, 1)   # margins: rich bronze-gold
mixO.inputs[7].default_value = (0.72, 0.55, 0.20, 1)   # band: deeper gold
edgeMix = mix_by_b(lambda b: abs(b[0]-0.98) < 0.02 and abs(b[2]-0.72) < 0.02)
edgeMix.inputs[7].default_value = (1.0, 0.95, 0.75, 1)  # polished edges
mixn = mix_by_b(lambda b: abs(b[0]-0.015) < 0.01 and abs(b[1]-0.012) < 0.01)
mixn.inputs[7].default_value = (0.010, 0.008, 0.006, 1)  # crisp black lattice
roughMix = next(n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'FLOAT'
                and abs(n.inputs[2].default_value - 0.28) < 0.03)
roughMix.inputs[2].default_value = 0.24   # polished blade
roughMix.inputs[3].default_value = 0.12   # mirror-ish edges

# ---------- fittings ----------
for name, col, rough in (
        ('guard_gold',      (0.80, 0.62, 0.20), 0.26),
        ('pommel_bronze',   (0.75, 0.59, 0.22), 0.28),
        ('grip_bronze',     (0.22, 0.10, 0.06), 0.55),
        ('gold_text',       (0.92, 0.78, 0.40), 0.20),
        ('stone_turquoise', (0.03, 0.68, 0.50), 0.12),
        ('stone_blue',      (0.04, 0.20, 0.85), 0.08),
        ('stone_cyan',      (0.06, 0.52, 0.82), 0.10)):
    m = bpy.data.materials[name]
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    print(name, "->", col, "rough", rough)

# ---------- renders + save ----------
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
print("ITERATION 12 (as-new colors) done")
