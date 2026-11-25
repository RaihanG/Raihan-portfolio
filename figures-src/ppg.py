"""Concept figure: tracheal photoplethysmography (PPG), photographic.

Trachea cut transversely through the sensor: the cut face shows the wall in section (mucosa and
submucosa, C-shaped cartilage open posteriorly, trachealis). An endotracheal tube with its cuff sits
inside; a flex-PCB optode on the cuff carries a red (660 nm) LED, a photodiode and an infrared LED
(drawn violet) facing the mucosa, and the light glows in the wall section above them.
Illustration only, no measured data. Facts: brief.md.
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

# Trachea axis = x. Angle phi in the y-z plane: phi=0 top (+z), 90 front (-y, camera side),
# 180 bottom, 270 back (+y, posterior: the cartilage gap and trachealis muscle).
R_IN, R_SUB, R_OUT = 1.0, 1.10, 1.19
X_CUT, X_END = 0.9, -3.3                       # transverse cut through the sensor; far end
PITCH, RING_W = 0.42, 0.25
GAP = (232.0, 308.0)                          # posterior gap of the C-rings


def d(phi):
    a = math.radians(phi)
    return Vector((0.0, -math.sin(a), math.cos(a)))


def annulus(name, r0, r1, x0, x1, p0, p1, mat, step=2.0):
    """Closed solid: annular sector between radii r0..r1, x0..x1, angles p0..p1 (deg)."""
    full = (p1 - p0) >= 359.99
    n = max(3, int(round((p1 - p0) / step)))
    verts, faces = [], []
    for i in range(n + (0 if full else 1)):
        a = p0 + (p1 - p0) * i / n
        for x, r in ((x0, r0), (x1, r0), (x1, r1), (x0, r1)):
            verts.append(tuple(Vector((x, 0, 0)) + d(a) * r))
    m = len(verts) // 4
    for i in range(n if full else n):
        j = (i + 1) % m
        a, b = 4 * i, 4 * j
        faces += [(a + 0, a + 1, b + 1, b + 0),      # inner
                  (a + 3, b + 3, b + 2, a + 2),      # outer
                  (a + 0, b + 0, b + 3, a + 3),      # x0 end
                  (a + 1, a + 2, b + 2, b + 1)]      # x1 end
    if not full:
        faces += [(0, 3, 2, 1), (4 * (m - 1), 4 * (m - 1) + 1, 4 * (m - 1) + 2, 4 * (m - 1) + 3)]
    o = C.mesh_obj(name, verts, faces, mat, smooth=True, sharp_deg=35)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    return o


# ------------------------------------------------------------------ materials
# mucosa + submucosa as one subsurface medium (so light spreads through it), coloured by radius
wall = C._N("wall")
wall.set(Roughness=0.32, Subsurface_Weight=1.0, Subsurface_Radius=(1.0, 0.4, 0.3), Subsurface_Scale=0.22,
         Coat_Weight=0.55, Coat_Roughness=0.12)
co = wall.coord()
sx, sy, sz = wall.xyz(co)
rad = wall.math("SQRT", wall.math("ADD", wall.math("MULTIPLY", sy, sy), wall.math("MULTIPLY", sz, sz)))
# fine submucosal vessel network on the luminal surface
vor = wall.new("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE")
wall.put(vor.inputs["Vector"], co); vor.inputs["Scale"].default_value = 7.0
vor.inputs["Randomness"].default_value = 1.0
ves = wall.math("MULTIPLY", wall.maprange(vor.outputs["Distance"], 0.0, 0.03, 1.0, 0.0),
                wall.maprange(wall.noise(co, 3.0), 0.4, 0.6))
base = wall.ramp(wall.maprange(rad, R_IN, R_SUB), [(0.0, "#b8454d"), (0.35, "#c9676a"), (1.0, "#dca196")])
base = wall.mix(wall.math("MULTIPLY", ves, wall.maprange(rad, R_IN + 0.01, R_IN, 0.0, 1.0)), base, "#8e2330")
wall.set(Base_Color=wall.mix(wall.maprange(wall.noise(co, 14.0, 6.0), 0.3, 0.7), "#bd585c", base) if False else base)
wall.bump(wall.noise(co, 40.0, 8.0, 0.6), 0.12, 0.01)

cart = C._N("cartilage")
cart.set(Base_Color="#dfe6ea", Roughness=0.28, Subsurface_Weight=0.8, Subsurface_Radius=(0.9, 0.85, 0.8),
         Subsurface_Scale=0.04, Coat_Weight=0.4)
px = cart.xyz(cart.coord())[0]               # only the two transverse cut planes show bare cartilage
nx = cart.math("MAXIMUM", cart.math("GREATER_THAN", px, X_CUT - 0.003), cart.math("LESS_THAN", px, X_END + 0.003))
hyaline = cart.mix(cart.noise(cart.coord(), 20.0), "#cfdbe0", "#e9eff1")     # cut face: hyaline cartilage
outside = cart.mix(cart.noise(cart.coord(), 14.0), "#d39d92", "#ddb0a4")     # outer surface: adventitia
cart.set(Base_Color=cart.mix(nx, outside, hyaline))

lig = C.tissue("#cf8f86", sss_radius=(1.0, 0.4, 0.25), sss_scale=0.05, rough=0.45, coat=0.25,
               mottle="#c98a83", mottle_scale=20.0, name="ligament")
muscle = C.tissue("#a8484c", sss_radius=(1.0, 0.3, 0.15), sss_scale=0.04, rough=0.5, coat=0.2,
                  mottle="#93393f", mottle_scale=25.0, name="trachealis")

# ------------------------------------------------------------------ trachea
annulus("Wall", R_IN, R_SUB, X_END, X_CUT, 0.0, 360.0, wall.m, step=1.5)
x = X_CUT - RING_W * 0.5 + 0.06               # the cut passes through a ring, near its edge
rings = []
while x - RING_W / 2 > X_END:
    rings.append(x)
    x -= PITCH
for xc in rings:
    a0, a1 = max(xc - RING_W / 2, X_END), min(xc + RING_W / 2, X_CUT)
    annulus("Ring", R_SUB, R_OUT, a0, a1, GAP[1] - 360.0, GAP[0], cart.m)
    annulus("Muscle", R_SUB, R_OUT - 0.04, a0, a1, GAP[0], GAP[1], muscle.m)
edges = sorted([X_END] + [v for xc in rings for v in (max(xc - RING_W / 2, X_END), min(xc + RING_W / 2, X_CUT))] + [X_CUT])
for i in range(0, len(edges) - 1, 2):          # annular ligaments between the rings
    if edges[i + 1] - edges[i] > 1e-3:
        annulus("Ligament", R_SUB, R_OUT - 0.02, edges[i], edges[i + 1], 0.0, 360.0, lig.m)

# ------------------------------------------------------------------ endotracheal tube
R_T, WALL_T = 0.40, 0.045
pvc = C.glass_tint("#e8f2f6", "#8fb1c2", edge_amount=0.6, ior=1.5, rough=0.04)
path = [(1.55, 0, -0.08), (0.0, 0, -0.08), (-2.4, 0, -0.08), (-3.7, 0, 0.05), (-4.7, 0, 0.6),
        (-5.4, 0, 1.6), (-5.75, 0, 2.9)]
tube = C.fiber_path(path, R_T, pvc, 48)
tube.data.use_fill_caps = False
tube.data.bevel_resolution = 12
sol = tube.modifiers.new("wall", "SOLIDIFY"); sol.thickness = WALL_T; sol.offset = -1
# bevelled tip (the end beyond the cut, facing the camera)
bpy.ops.object.select_all(action="DESELECT")
tube.select_set(True); bpy.context.view_layer.objects.active = tube
bpy.ops.object.convert(target="MESH")
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(1.55 + 0.85, 0, -0.08), rotation=(0, math.radians(-38), 0))
cutter = bpy.context.object
cutter.scale = (1.0, 1.2, 1.2)
bo = tube.modifiers.new("tip", "BOOLEAN"); bo.object = cutter; bo.operation = "DIFFERENCE"; bo.solver = "EXACT"
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=1.0, location=(1.2, 0.3, -0.08), rotation=(math.pi / 2, 0, 0))
eye = bpy.context.object                       # Murphy eye on the far side
bo2 = tube.modifiers.new("eye", "BOOLEAN"); bo2.object = eye; bo2.operation = "DIFFERENCE"; bo2.solver = "EXACT"
bpy.context.view_layer.objects.active = tube
for mname in ("tip", "eye"):
    bpy.ops.object.modifier_apply(modifier=mname)
bpy.data.objects.remove(cutter); bpy.data.objects.remove(eye)

line = C._mat("radiopaque", **{"Base Color": C.hex_rgb("#1d5fd1"), "Roughness": 0.35})
C.fiber_path([((1.05 if i == 0 else p[0]), 0.375, p[2]) for i, p in enumerate(path)], 0.016, line, 48)

# cuff: thin high-volume balloon around the tube, sealed against the mucosa, cut with the trachea
cuff_m = C._mat("cuff", **{"Base Color": C.hex_rgb("#f4f7f8"), "Roughness": 0.14, "Transmission Weight": 0.96,
                           "IOR": 1.4, "Coat Weight": 0.3})
prof = []
for i in range(41):
    t = i / 40
    xx = -0.55 + t * 2.4
    rr = R_T + (R_IN - 0.012 - R_T) * min(1.0, math.sin(math.pi * t) * 1.6) ** 0.8
    prof.append((xx, rr))
cv, cf = [], []
NS = 128
for xx, rr in prof:
    for k in range(NS):
        p = Vector((xx, 0, -0.08 * (1 - (rr - R_T) / (R_IN - R_T)))) + d(360.0 * k / NS) * rr
        cv.append(tuple(p))
for i in range(len(prof) - 1):
    for k in range(NS):
        a, b = i * NS + k, i * NS + (k + 1) % NS
        cf.append((a, b, b + NS, a + NS))
cuff = C.mesh_obj("Cuff", cv, cf, cuff_m, smooth=True, sharp_deg=0)
import bmesh  # noqa: E402
bm = bmesh.new(); bm.from_mesh(cuff.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.x > X_CUT + 1e-4], context="VERTS")
bm.to_mesh(cuff.data); bm.free()
cs = cuff.modifiers.new("shell", "SOLIDIFY"); cs.thickness = 0.012; cs.offset = -1
C.no_shadow(cuff)

# ------------------------------------------------------------------ optode on the cuff (top, at the cut)
flex = C._mat("flex", **{"Base Color": C.hex_rgb("#c8892d"), "Roughness": 0.3, "Coat Weight": 0.7,
                         "Subsurface Weight": 0.2, "Subsurface Scale": 0.01})
R_O = R_IN - 0.035                             # optode sits between cuff and mucosa
X_O = X_CUT - 0.08
annulus("Flex", R_O - 0.012, R_O, X_O - 0.6, X_CUT - 0.005, -19.0, 19.0, flex, step=1.0)
# flex lead back along the cuff and the tube to the outside
lead = [(X_O - 0.6, 0, R_O - 0.01), (-0.6, 0, R_T + 0.08), (-2.4, 0, R_T - 0.06), (-3.7, 0, R_T + 0.05),
        (-4.75, 0.0, R_T + 0.62), (-5.5, 0, 1.62 + R_T * 0.6), (-5.85, 0, 2.9)]
C.fiber_path(lead, 0.03, flex, 48).scale = (1, 1, 1)
pilot = C._mat("pilot", **{"Base Color": C.hex_rgb("#e9eef0"), "Roughness": 0.25, "Transmission Weight": 0.6})
C.fiber_path([(-0.4, 0.16, R_T + 0.02), (-2.4, 0.16, R_T - 0.06 + 0.0), (-3.7, 0.18, R_T + 0.05),
              (-4.7, 0.2, R_T + 0.6), (-5.45, 0.2, 1.6 + R_T * 0.6), (-5.8, 0.2, 2.9)], 0.022, pilot, 48)

red_led = C._mat("led_red", **{"Base Color": C.hex_rgb("#ff3b3b"), "Emission Color": C.hex_rgb("#ff2a2a"),
                               "Emission Strength": 6.0, "Roughness": 0.15, "Coat Weight": 1.0})
ir_led = C._mat("led_ir", **{"Base Color": C.hex_rgb("#9b5cff"), "Emission Color": C.hex_rgb("#8a4dff"),
                             "Emission Strength": 6.0, "Roughness": 0.15, "Coat Weight": 1.0})
pd = C._mat("photodiode", **{"Base Color": C.hex_rgb("#1a2236"), "Roughness": 0.08, "Coat Weight": 1.0,
                             "Metallic": 0.2})
for phi, mat in ((-12.0, red_led), (0.0, pd), (12.0, ir_led)):
    c = Vector((X_O, 0, 0)) + d(phi) * (R_O + 0.012)
    C._box((0.12, 0.15, 0.03), tuple(c), mat, 0.005, rot=(math.radians(-phi), 0, 0))
for phi, col, name in ((-12.0, "#ff2a2a", "Red660"), (12.0, "#8f55ff", "IR")):
    c = Vector((X_O, 0, 0)) + d(phi) * (R_O + 0.03)
    C.spot(name, tuple(c), d(phi), 340.0, col, size_deg=150, blend=1.0, radius=0.02)

# ------------------------------------------------------------------ light and camera
C.studio(target=(-0.8, 0, 0.3), scale=1.6, key=0.5, fill=0.45, rim=0.9, top=0.3, key_dir=(0.6, -0.7, 0.8))
C.camera_look(loc=(7.6, -4.0, 3.1), target=(-0.95, 0.2, 0.7), lens_mm=38)
C.finish(S, out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "ppg.png"))
