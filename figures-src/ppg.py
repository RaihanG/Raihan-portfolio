"""Concept figure: tracheal photoplethysmography (PPG).

Cut-away trachea with an endotracheal tube; an optode on the cuff shines red
(650 nm) and infrared (870 nm, drawn violet) light into the tracheal wall and a
fibre carries the returning light out. Illustration only, no measured data.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import common as C  # noqa: E402

out, preview = C.args()
C.reset()
C.setup_render(out or "//ppg.webp", preview)

R_IN, WALL, HALF = 1.05, 0.16, 3.75
CUT_Y = -0.12   # keep y > CUT_Y: the front of the trachea is cut away

# ---------------------------------------------------------------- trachea wall
wall = C.principled("Mucosa", (0.82, 0.42, 0.42), rough=0.38, sss=1.0,
                    sss_radius=(1.0, 0.3, 0.16), sss_scale=0.22, coat=0.35)
bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=R_IN, depth=2 * HALF,
                                    end_fill_type="NOTHING", rotation=(0, math.pi / 2, 0))
tr = bpy.context.active_object
tr.name = "Trachea"
bpy.ops.object.transform_apply(rotation=True)
C.delete_verts(tr, lambda co: co.y > CUT_Y)
sol = tr.modifiers.new("Wall", "SOLIDIFY")
sol.thickness = WALL
sol.offset = 1.0
C.bevel(tr, 0.03, 3)
C.smooth(C.assign(tr, wall))

cart = C.principled("Cartilage", (0.93, 0.80, 0.76), rough=0.35, sss=1.0,
                    sss_radius=(1.0, 0.6, 0.45), sss_scale=0.1, coat=0.3)
x = -HALF + 0.3
while x < HALF - 0.2:
    bpy.ops.mesh.primitive_torus_add(major_radius=R_IN + WALL + 0.01, minor_radius=0.075,
                                     major_segments=160, minor_segments=20,
                                     location=(x, 0, 0), rotation=(0, math.pi / 2, 0))
    ring = bpy.context.active_object
    bpy.ops.object.transform_apply(location=False, rotation=True)
    C.delete_verts(ring, lambda co: co.y > CUT_Y + 0.02)
    C.smooth(C.assign(ring, cart))
    x += 0.52

# small vessels over the top of the wall
vessel = C.principled("Vessel", (0.55, 0.07, 0.09), rough=0.3, sss=0.4, sss_scale=0.05)
R_OUT = R_IN + WALL + 0.05
for k, (x0, x1, ph0, ph1, wob) in enumerate([(-2.8, 1.6, 40, 88, 0.25), (-0.6, 3.2, 30, 85, 0.18),
                                             (-3.3, -0.4, 55, 30, 0.2)]):
    pts = []
    for i in range(9):
        t = i / 8
        xx = x0 + (x1 - x0) * t
        ph = math.radians(ph0 + (ph1 - ph0) * t + 9 * math.sin(7 * t + k))
        pts.append((xx, R_OUT * math.cos(ph), R_OUT * math.sin(ph) + wob * 0.0))
    C.curve_tube(f"Vessel{k}", pts, 0.028 - 0.006 * k, vessel)

# ------------------------------------------------------- endotracheal tube
pvc = C.principled("PVC", (0.93, 0.97, 1.0), rough=0.05, transmission=1.0, ior=1.46)
path = [(2.6, 0, 0), (-1.5, 0, 0), (-3.6, 0, 0.12), (-4.8, 0, 0.9), (-5.5, 0, 2.2), (-5.75, 0, 3.6)]
tube = C.curve_tube("ETTube", path, 0.38, pvc, hollow=True, resolution=32)
s = tube.modifiers.new("Wall", "SOLIDIFY")
s.thickness = 0.05
line_mat = C.principled("Line", (0.10, 0.35, 0.95), rough=0.3)
# radiopaque line along the tube's far side (offset in +y so it reads through the clear PVC)
C.curve_tube("BlueLine", [(p[0], 0.365, p[2]) for p in path], 0.022, line_mat)

# cuff: a frosted balloon around the tube, almost touching the wall
cuff_mat = C.principled("Cuff", (0.96, 0.98, 1.0), rough=0.32, transmission=1.0, ior=1.4)
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=1.0, location=(0.9, 0, 0))
cuff = bpy.context.active_object
cuff.scale = (1.3, 0.94, 0.94)
C.smooth(C.assign(cuff, cuff_mat))

# ----------------------------------------------------------------- optode
pcb = C.principled("PCB", (0.06, 0.07, 0.08), rough=0.4, coat=0.5)
OP = (0.9, 0.955, 0.0)
chip = C.rounded_box("Optode", (0.42, 0.07, 0.26), OP, width=0.02, mat=pcb)
red_led = C.emissive("RedLED", (1.0, 0.16, 0.20), 25)
ir_led = C.emissive("IRLED", (0.62, 0.30, 1.0), 25)
for dx, mat in ((-0.1, red_led), (0.1, ir_led)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(OP[0] + dx, OP[1] + 0.035, OP[2]))
    C.smooth(C.assign(bpy.context.active_object, mat))
C.spot("Red650", (OP[0] - 0.1, OP[1] + 0.05, OP[2]), (OP[0] - 0.1, 2.0, OP[2]), 70,
       (1.0, 0.12, 0.15), angle_deg=70, blend=0.9)
C.spot("IR870", (OP[0] + 0.1, OP[1] + 0.05, OP[2]), (OP[0] + 0.1, 2.0, OP[2]), 55,
       (0.6, 0.28, 1.0), angle_deg=70, blend=0.9)

# receiving fibre from the optode, along the tube and out
fibre = C.principled("Fibre", (0.10, 0.36, 0.98), rough=0.25, coat=0.6)
C.curve_tube("Fibre", [(0.9, 0.97, 0.14), (0.3, 0.78, 0.42), (-0.8, 0.43, 0.30),
                       (-3.0, 0.43, 0.22), (-4.55, 0.43, 0.75), (-5.35, 0.43, 2.1),
                       (-5.6, 0.43, 3.6)], 0.035, fibre)

# ----------------------------------------------------------------- lighting
C.area_light("Key", (-2, -7, 7), (0, 0, 0), 800, 7)
C.area_light("Rim", (3, 6, 4), (0, 0, 0.3), 650, 5, color=(0.75, 0.95, 1.0))
C.area_light("Fill", (7, -3, 1), (0, 0, 0), 160, 4)
C.shadow_catcher(z=-1.45)

C.camera((-0.6, -9.4, 3.9), (-0.9, 0.25, 0.55), lens=34)
C.render()
