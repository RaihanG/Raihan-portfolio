"""Concept figure: spatial frequency domain imaging (SFDI), photographic.

A projector above a skin sample casts sinusoidal fringes (a real projection through a patterned
slide, so the tissue blurs them by scattering); a camera near normal records the reflected light.
Crossed polarisers sit on both lenses. The cut face shows epidermis, vascular dermis and
subcutaneous fat. Illustration only, no measured data. Facts: brief.md.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
import common as C  # noqa: E402

out, preview = C.args()
S = C.start(preview)

# ------------------------------------------------------------------ skin block (top at z = 0)
BX, BY = 4.6, 3.0
Z_EPI, Z_DERM, Z_FAT = -0.08, -0.66, -1.30          # bottoms of each layer (schematic thicknesses)

epi = C.tissue("#d8a28c", sss_radius=(1.0, 0.45, 0.25), sss_scale=0.05, rough=0.5, coat=0.15,
               mottle="#c98b78", mottle_scale=9.0, bump=0.35, bump_scale=90.0, name="epidermis")
# fine skin creases on the top surface
co = epi.coord()
vor = epi.new("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE")
epi.put(vor.inputs["Vector"], co); vor.inputs["Scale"].default_value = 14.0
crease = epi.maprange(vor.outputs["Distance"], 0.0, 0.04, 0.0, 1.0)
epi.bump(epi.math("MULTIPLY", crease, epi.noise(co, 90.0, 8.0, 0.65)), 0.3, 0.008)

derm = C.tissue("#c66f6c", sss_radius=(1.0, 0.3, 0.15), sss_scale=0.05, rough=0.6,
                mottle="#b35a5c", mottle_scale=14.0, name="dermis")
# collagen: stretched fibrous noise on the cut face
mp = derm.new("ShaderNodeMapping"); derm.put(mp.inputs["Vector"], derm.coord())
mp.inputs["Scale"].default_value = (1.0, 1.0, 4.0)
fib = derm.noise(mp.outputs[0], 45.0, 6.0, 0.7)
derm.set(Base_Color=derm.mix(derm.maprange(fib, 0.4, 0.75), "#b9615f", "#cf8079"))
derm.bump(fib, 0.15, 0.01)

fat = C.tissue("#ead7a0", sss_radius=(1.0, 0.8, 0.35), sss_scale=0.08, rough=0.35, coat=0.2, name="fat")
fv = fat.new("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE")
fat.put(fv.inputs["Vector"], fat.coord()); fv.inputs["Scale"].default_value = 5.5
sept = fat.maprange(fv.outputs["Distance"], 0.0, 0.035)
fat.set(Base_Color=fat.mix(sept, "#d9a089", fat.mix(fat.noise(fat.coord(), 9.0), "#efdeaa", "#e2c787")))
fat.bump(sept, 0.5, 0.02)

C._box((BX, BY, -Z_EPI), (0, 0, Z_EPI / 2), epi.m, bevel=0.03, name="Epidermis")
C._box((BX, BY, Z_EPI - Z_DERM), (0, 0, (Z_EPI + Z_DERM) / 2), derm.m, name="Dermis")
C._box((BX, BY, Z_DERM - Z_FAT), (0, 0, (Z_DERM + Z_FAT) / 2), fat.m, name="Fat")

# dermal vessels: their cut ends show on the front (-y) and left (-x) faces
vessel = C._mat("vessel", **{"Base Color": C.hex_rgb("#7d1620"), "Roughness": 0.3, "Coat Weight": 0.6,
                              "Subsurface Weight": 0.4, "Subsurface Radius": (1.0, 0.2, 0.1),
                              "Subsurface Scale": 0.03})
for x, z, r in ((-1.6, -0.30, 0.045), (-0.7, -0.45, 0.06), (0.3, -0.27, 0.035), (1.2, -0.50, 0.055),
                (1.9, -0.33, 0.04)):
    C.cylinder((x, -BY / 2 - 0.004, z), (x + 0.15, BY / 2 - 0.3, z + 0.05), r, vessel, 32)
for y, z, r in ((-0.9, -0.38, 0.05), (0.4, -0.52, 0.04), (1.0, -0.29, 0.035)):
    C.cylinder((-BX / 2 - 0.004, y, z), (BX / 2 - 0.4, y - 0.1, z - 0.04), r, vessel, 32)

# optical table
C.breadboard((0, 0.6, Z_FAT - 0.14), (9.0, 6.2, 0.14), color="#9aa1a8")

# ------------------------------------------------------------------ devices
# Each device is built with its optical axis along local -x and turned about y by -(90 + tilt),
# so it looks down, tilted by `tilt` degrees from vertical towards +x.
steel = C.brushed_metal("#c8cdd2", 0.25, "z")
blk = C.anodized("#25282d")
RAIL_Z = 4.55


def place(objs, front_local, front_world, tilt):
    R = C.rot_y(-(90.0 + tilt))
    loc = Vector(front_world) - R @ Vector(front_local)
    C.group(objs, loc, R)
    D = R @ Vector((-1, 0, 0))
    return lambda p: Vector(loc) + R @ Vector(p), D


def projector():
    """DLP-style light engine, lens towards -x, optical axis on local z = 0. Front glass at x = -0.38."""
    objs = []
    house = C.painted("#cfd4d9", 0.45)
    objs.append(C._box((1.15, 0.95, 0.62), (0.62, 0, 0.12), house, 0.05))
    for k in range(7):                                    # heat-sink fins on the back
        objs.append(C._box((0.06, 0.8, 0.12), (0.3 + k * 0.1, 0, 0.49), C.anodized("#2a2d33"), 0.008))
    objs.append(C.cylinder((0.05, 0, 0), (-0.32, 0, 0), 0.19, C.anodized("#17191d", 0.5), 64))
    for k in range(2):
        xx = -0.06 - k * 0.12
        objs.append(C.cylinder((xx, 0, 0), (xx - 0.05, 0, 0), 0.205, C.anodized("#2d3036", 0.6), 64))
    objs.append(C.cylinder((-0.32, 0, 0), (-0.36, 0, 0), 0.2, C.brushed_metal("#b9bec4", 0.3, "radial"), 64))
    objs.append(C.cylinder((-0.36, 0, 0), (-0.38, 0, 0), 0.17, POL, 64))
    return objs


POL = C._mat("polariser", **{"Base Color": C.hex_rgb("#39404c"), "Roughness": 0.06, "Coat Weight": 1.0,
                             "Metallic": 0.3})

# projector: left, 30 deg off vertical
P_TILT = 30.0
P_FRONT = Vector((-2.2, 0.0, 3.4))
to_w, P_DIR = place(projector(), (-0.38, 0, 0), P_FRONT, P_TILT)
pb = to_w((0.62, 0, 0.12))
C.cylinder((pb.x, 0, RAIL_Z), tuple(pb), 0.05, steel, 32)
C._box((0.3, 0.3, 0.26), (pb.x, 0, RAIL_Z), blk, 0.02)

# camera: right, near normal (15 deg towards -x), with its own polariser
C_TILT = -15.0
CAM_SIZE = (0.62, 0.56, 0.56)
zc = CAM_SIZE[2] / 2 + 0.05
cam_objs, _ = C.camera_box((0, 0, -zc), CAM_SIZE, color="#24272c", lens_length=0.42)
xf = -CAM_SIZE[0] / 2 - 0.06 - 0.42
cam_objs.append(C.cylinder((xf - 0.005, 0, 0), (xf - 0.03, 0, 0), 0.12, POL, 64))
C_FRONT = Vector((0.95, 0.0, 3.05))
to_wc, C_DIR = place(cam_objs, (xf - 0.03, 0, 0), C_FRONT, C_TILT)
cb = to_wc((0, 0, 0))
C.cylinder((cb.x, 0, RAIL_Z), tuple(cb), 0.05, steel, 32)
C._box((0.3, 0.3, 0.26), (cb.x, 0, RAIL_Z), blk, 0.02)

# rail on a post at the back-left of the table
POST = (-4.1, 0.0)
C.cylinder((POST[0], 2.6, Z_FAT - 0.07), (POST[0], 2.6, RAIL_Z), 0.11, steel, 48)
C.cylinder((POST[0], 2.6, RAIL_Z), (POST[0], 0.0, RAIL_Z), 0.08, C.brushed_metal("#c8cdd2", 0.25, "y"), 48)
C._box((0.34, 0.34, 0.34), (POST[0], 2.6, RAIL_Z), blk, 0.02)
C._box((0.3, 0.3, 0.3), (POST[0], 0.0, RAIL_Z), blk, 0.02)
C.cylinder((POST[0], 0, RAIL_Z), (2.0, 0, RAIL_Z), 0.08, C.brushed_metal("#c8cdd2", 0.25, "x"), 48)

# ------------------------------------------------------------------ fringe projection
# A spot light just in front of the projector shines through a patterned slide (seen only by
# shadow rays): sinusoidal transmission inside a rectangle, opaque outside it.
L_POS = P_FRONT + P_DIR * 0.03
SLIDE = 0.10
Bm = C.basis(P_DIR, hint=(1, 0, 0))
u, v = Bm.col[0], Bm.col[1]
FIELD = [(-1.85, -1.25), (1.85, -1.25), (1.85, 1.25), (-1.85, 1.25)]   # field on the tissue (x, y)
X0 = 0.0
corners = [Vector((X0 + x, y, 0.0)) for x, y in FIELD]
ab = []
for q in corners:
    w = q - L_POS
    p = L_POS + w * (SLIDE / w.dot(P_DIR)) - (L_POS + P_DIR * SLIDE)
    ab.append((p.dot(u), p.dot(v)))
a0, a1 = min(a for a, b in ab), max(a for a, b in ab)
b0, b1 = min(b for a, b in ab), max(b for a, b in ab)
N_FRINGE = 7.0

bpy.ops.mesh.primitive_plane_add(size=1.0)
slide = bpy.context.object
slide.name = "Slide"
slide.matrix_world = (C.Matrix.Translation(L_POS + P_DIR * SLIDE) @ Bm.to_4x4())
g = C._N("slide")
g.nt.nodes.remove(g.bsdf)
sx, sy, _ = g.xyz(g.coord())
ph = g.math("MULTIPLY", g.math("SUBTRACT", sx, a0), 2 * math.pi * N_FRINGE / (a1 - a0))
fr = g.math("MULTIPLY_ADD", g.math("SINE", ph), 0.5)
g.nt.nodes[-1].inputs[2].default_value = 0.5
inx = g.math("MULTIPLY", g.math("GREATER_THAN", sx, a0), g.math("LESS_THAN", sx, a1))
iny = g.math("MULTIPLY", g.math("GREATER_THAN", sy, b0), g.math("LESS_THAN", sy, b1))
tr = g.math("MULTIPLY", g.math("MULTIPLY", inx, iny), g.math("POWER", fr, 1.8))
dark = g.new("ShaderNodeBsdfDiffuse"); dark.inputs["Color"].default_value = (0, 0, 0, 1)
clear = g.new("ShaderNodeBsdfTransparent")
mx = g.new("ShaderNodeMixShader")
g.put(mx.inputs[0], tr); g.put(mx.inputs[1], dark.outputs[0]); g.put(mx.inputs[2], clear.outputs[0])
g.nt.links.new(mx.outputs[0], g.out.inputs["Surface"])
slide.data.materials.append(g.m)
for attr in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission",
             "visible_volume_scatter"):
    setattr(slide, attr, False)

C.spot("Projector", tuple(L_POS), P_DIR, 1000, "#eef9ff", size_deg=100, blend=0.0, radius=0.0005)

# faint light paths: projector -> field, field -> camera
C.frustum(L_POS, corners, "#d6f3ff", 0.022, "beam_in")
C_IN = C_FRONT + C_DIR * 0.01
cam_field = [Vector((0.15 + x * 0.8, y * 0.8, 0.0)) for x, y in FIELD]
C.frustum(C_IN, cam_field, "#5ea0ff", 0.022, "beam_out")

# ------------------------------------------------------------------ light and camera
C.studio(target=(0, 0, 0.6), scale=1.5, key=0.5, fill=0.45, rim=0.9, top=0.25)
C.camera_look(loc=(-4.6, -9.6, 5.4), target=(-0.55, 0.25, 1.6), lens_mm=35)
C.finish(S, out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfdi.png"))
