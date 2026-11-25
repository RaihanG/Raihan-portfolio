"""Concept figure: spatial frequency domain imaging (SFDI).

A projector casts sinusoidal fringes onto a tissue block; a camera records the
diffusely reflected light. Illustration only, no measured data.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import common as C  # noqa: E402

out, preview = C.args()
C.reset()
C.setup_render(out or "//sfdi.webp", preview)

# ---------------------------------------------------------------- tissue block
TOP = 0.0
tissue = C.rounded_box("Tissue", (5.2, 3.4, 1.1), (0, 0, TOP - 0.55), width=0.28)
tissue.modifiers["Bevel"].segments = 10
sub = tissue.modifiers.new("Sub", "SUBSURF")
sub.levels = sub.render_levels = 2
C.smooth(tissue)

m = C.principled("TissueSSS", (0.86, 0.52, 0.50), rough=0.42, sss=1.0,
                 sss_radius=(1.0, 0.32, 0.18), sss_scale=0.35, coat=0.25)
nt = m.node_tree
p = nt.nodes.get("Principled BSDF")
N = nt.nodes.new
L = nt.links.new

tc = N("ShaderNodeTexCoord")
sep = N("ShaderNodeSeparateXYZ")
L(tc.outputs["Object"], sep.inputs[0])

# fringe = (0.5 + 0.5 sin(2 pi f x)) ^ 1.6
FREQ = 1.15  # cycles per unit
mul = N("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 2 * math.pi * FREQ
sin = N("ShaderNodeMath"); sin.operation = "SINE"
half = N("ShaderNodeMath"); half.operation = "MULTIPLY_ADD"
half.inputs[1].default_value = 0.5; half.inputs[2].default_value = 0.5
pw = N("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 1.6
L(sep.outputs["X"], mul.inputs[0]); L(mul.outputs[0], sin.inputs[0])
L(sin.outputs[0], half.inputs[0]); L(half.outputs[0], pw.inputs[0])


def soft_window(axis_out, inner, outer):
    a = N("ShaderNodeMath"); a.operation = "ABSOLUTE"
    mr = N("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = inner
    mr.inputs["From Max"].default_value = outer
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    mr.clamp = True
    L(axis_out, a.inputs[0]); L(a.outputs[0], mr.inputs["Value"])
    return mr.outputs["Result"]


mx = soft_window(sep.outputs["X"], 1.55, 1.9)
my = soft_window(sep.outputs["Y"], 0.95, 1.25)
# only the top face
geo = N("ShaderNodeNewGeometry")
nsep = N("ShaderNodeSeparateXYZ")
L(geo.outputs["Normal"], nsep.inputs[0])
top = N("ShaderNodeMapRange")
top.inputs["From Min"].default_value = 0.75
top.inputs["From Max"].default_value = 0.97
top.clamp = True
L(nsep.outputs["Z"], top.inputs["Value"])

m1 = N("ShaderNodeMath"); m1.operation = "MULTIPLY"
m2 = N("ShaderNodeMath"); m2.operation = "MULTIPLY"
m3 = N("ShaderNodeMath"); m3.operation = "MULTIPLY"
L(mx, m1.inputs[0]); L(my, m1.inputs[1])
L(m1.outputs[0], m2.inputs[0]); L(top.outputs["Result"], m2.inputs[1])
L(m2.outputs[0], m3.inputs[0]); L(pw.outputs[0], m3.inputs[1])   # m3 = fringe * mask

strength = N("ShaderNodeMath"); strength.operation = "MULTIPLY"
strength.inputs[1].default_value = 2.2
L(m3.outputs[0], strength.inputs[0])
C._set(p, ["Emission Color", "Emission"], (*C.srgb((0.70, 1.0, 0.95)), 1))
L(strength.outputs[0], p.inputs["Emission Strength"])
C.assign(tissue, m)

# --------------------------------------------------------- projector + camera
body = C.principled("Body", (0.11, 0.13, 0.16), rough=0.32, coat=0.6)
glass = C.principled("Lens", (0.02, 0.03, 0.04), rough=0.05, metal=0.0, coat=1.0)
teal_ring = C.emissive("TealRing", C.TEAL, 6.0)
blue_ring = C.emissive("BlueRing", C.BLUE, 6.0)


def device(name, loc, target, size, ring_mat, lens_r):
    import bpy
    from mathutils import Vector
    grp = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(grp)
    grp.location = loc
    C.look_at(grp, target)
    b = C.rounded_box(name + "Body", size, (0, 0, 0), width=0.09, mat=body)
    b.parent = grp
    z_front = -size[2] / 2
    barrel = C.cylinder(name + "Barrel", lens_r * 1.25, 0.28, (0, 0, z_front - 0.12), mat=body)
    barrel.parent = grp
    C.bevel(barrel, 0.03, 4)
    lens = C.cylinder(name + "Glass", lens_r, 0.05, (0, 0, z_front - 0.27), mat=glass)
    lens.parent = grp
    bpy.ops.mesh.primitive_torus_add(major_radius=lens_r * 1.12, minor_radius=0.025,
                                     location=(0, 0, z_front - 0.27))
    ring = bpy.context.active_object
    C.smooth(C.assign(ring, ring_mat))
    ring.parent = grp
    stripe = C.rounded_box(name + "Stripe", (size[0] * 1.002, 0.05, size[2] * 0.55),
                           (0, size[1] / 2 - 0.12, 0), width=0.01, mat=ring_mat)
    stripe.parent = grp
    return grp, Vector(loc) + (Vector(target) - Vector(loc)).normalized() * (size[2] / 2 + 0.3)


PROJ = (-2.9, -0.4, 3.4)
CAM = (2.6, -0.9, 3.0)
proj, proj_lens = device("Projector", PROJ, (-0.15, 0, 0), (1.25, 0.95, 1.35), teal_ring, 0.32)
cam, cam_lens = device("Camera", CAM, (0.2, 0, 0), (0.95, 0.85, 1.0), blue_ring, 0.26)

# ------------------------------------------------------------ light frustums
z = TOP + 0.02
rect = [(-1.7, -1.1, z), (1.7, -1.1, z), (1.7, 1.1, z), (-1.7, 1.1, z)]
beam = C.mesh_from("Beam", [tuple(proj_lens)] + rect,
                   [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 4, 3, 2)],
                   C.glow_volume("BeamGlow", C.TEAL, 0.10))
small = [(-1.2, -0.8, z), (1.2, -0.8, z), (1.2, 0.8, z), (-1.2, 0.8, z)]
ret = C.mesh_from("Return", [tuple(cam_lens)] + small,
                  [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 4, 3, 2)],
                  C.glow_volume("ReturnGlow", C.BLUE, 0.045))

# ------------------------------------------------------------------ lighting
C.area_light("Key", (-3, -6, 8), (0, 0, 0), 900, 6)
C.area_light("Rim", (4, 6, 5), (0, 0, 0.5), 700, 5, color=(0.75, 0.95, 1.0))
C.area_light("Fill", (6, -4, 2), (0, 0, 0.5), 180, 4)
C.shadow_catcher(z=-1.1)

C.camera((0.6, -9.2, 6.0), (0.0, 0.2, 0.9), lens=46)
C.render()
