# -*- coding: utf-8 -*-
"""Iteration 6: small color corrections against the raw closeup photo
(sources/raw/goujian_sword/images/goujian_sword_2019_06_detail.jpg).

- inscription gold brighter (real inlay reads light gold over the pattern):
  base (0.78,0.64,0.28) -> (0.92,0.78,0.40), roughness 0.22 -> 0.16
- pattern band olive deeper: mixO B (0.38,0.35,0.19) -> (0.31,0.29,0.16)
- renders + blend copy.
"""
import bpy, math

mt = bpy.data.materials['gold_text']
tb = next(n for n in mt.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
tb.inputs['Base Color'].default_value = (0.92, 0.78, 0.40, 1)
tb.inputs['Roughness'].default_value = 0.16

nt = bpy.data.materials['blade_gold'].node_tree
mixO = None
for n in nt.nodes:
    if n.type == 'MIX' and n.data_type == 'RGBA':
        b = n.inputs[7].default_value
        if abs(b[0]-0.38) < 0.01 and abs(b[1]-0.35) < 0.01:
            mixO = n
    if mixO: break
if mixO is None:
    raise RuntimeError('mixO (olive) not found')
mixO.inputs[7].default_value = (0.31, 0.29, 0.16, 1)

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
print("ITERATION 6 done")
