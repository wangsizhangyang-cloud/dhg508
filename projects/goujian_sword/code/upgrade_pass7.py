# -*- coding: utf-8 -*-
"""Iteration 7: aged / matte color grade to match the real sword (user feedback:
"整体贴近实物" + "金属太反光").

- all metals: muted, desaturated bronze/olive palette; roughness raised so the
  surfaces read as aged patinated bronze rather than shiny plastic gold.
- blade: margins -> pale desaturated bronze; band olive -> deeper gray-green;
  edge polish -> muted pale (no blow-out).
- stones: muted, less glassy.
"""
import bpy, math

def principled(mat_name):
    m = bpy.data.materials[mat_name]
    return m, next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

# --- blade_gold node palette ---
nt = bpy.data.materials['blade_gold'].node_tree
mixO = next(n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'RGBA'
            and abs(n.inputs[7].default_value[0] - 0.31) < 0.02
            and abs(n.inputs[7].default_value[1] - 0.29) < 0.02)
mixO.inputs[6].default_value = (0.50, 0.45, 0.28, 1)   # margin: pale bronze
mixO.inputs[7].default_value = (0.24, 0.26, 0.16, 1)   # band: gray-green olive
edgeMix = next(n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'RGBA'
               and abs(n.inputs[7].default_value[0] - 1.0) < 0.01
               and abs(n.inputs[7].default_value[2] - 0.72) < 0.02)
edgeMix.inputs[7].default_value = (0.80, 0.76, 0.62, 1)  # muted polish line
roughMix = next(n for n in nt.nodes if n.type == 'MIX' and n.data_type == 'FLOAT'
                and abs(n.inputs[2].default_value - 0.42) < 0.01)
roughMix.inputs[2].default_value = 0.55
roughMix.inputs[3].default_value = 0.30

# --- simple materials ---
for name, col, rough in (
        ('guard_gold',     (0.46, 0.37, 0.20), 0.48),
        ('pommel_bronze',  (0.30, 0.27, 0.15), 0.52),
        ('grip_bronze',    (0.13, 0.12, 0.075), 0.62),
        ('ring_gold',      (0.34, 0.29, 0.16), 0.55),
        ('gold_text',      (0.82, 0.70, 0.38), 0.32),
        ('stone_turquoise',(0.09, 0.50, 0.42), 0.28),
        ('stone_blue',     (0.07, 0.24, 0.55), 0.28),
        ('stone_cyan',     (0.10, 0.45, 0.66), 0.28)):
    m, b = principled(name)
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough

# --- renders + save ---
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
print("ITERATION 7 done")
