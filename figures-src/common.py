"""Shared helpers for the website's Blender concept figures.

Run a scene with:
  blender -b -P figures-src/sfdi.py -- --out assets/fig-sfdi.webp [--preview]
"""
import math
import sys

import bpy
import bmesh
from mathutils import Vector

# Site palette (style.css)
TEAL = (0.208, 0.878, 0.784)    # --accent  #35e0c8
BLUE = (0.369, 0.627, 1.0)      # --accent-2 #5ea0ff
GRAPHITE = (0.035, 0.045, 0.055)


def srgb(c):
    """sRGB 0-1 triple -> linear, for node colour inputs."""
    def f(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(f(v) for v in c)


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out, preview = None, False
    for i, a in enumerate(argv):
        if a == "--out":
            out = argv[i + 1]
        if a == "--preview":
            preview = True
    return out, preview


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_render(out, preview, res=(1600, 1000)):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48 if preview else 384
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 12
    sc.cycles.transmission_bounces = 12
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 50 if preview else 100
    sc.render.film_transparent = True
    for vt, look in (("AgX", "AgX - Medium High Contrast"), ("Filmic", "Medium High Contrast")):
        try:
            sc.view_settings.view_transform = vt
            try:
                sc.view_settings.look = look
            except TypeError:
                pass
            break
        except TypeError:
            continue
    ims = sc.render.image_settings
    if out.lower().endswith(".webp"):
        ims.file_format = "WEBP"
        ims.quality = 90
    else:
        ims.file_format = "PNG"
    ims.color_mode = "RGBA"
    sc.render.filepath = out
    world = bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (*srgb((0.05, 0.07, 0.09)), 1)
    bg.inputs["Strength"].default_value = 0.35


def _set(node, names, value):
    for n in names if isinstance(names, (list, tuple)) else [names]:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return True
    return False


def principled(name, color, rough=0.5, metal=0.0, transmission=0.0, ior=1.45,
               sss=0.0, sss_radius=(1.0, 0.35, 0.2), sss_scale=0.1,
               emission=None, emission_strength=0.0, coat=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    _set(p, "Base Color", (*srgb(color), 1))
    _set(p, "Roughness", rough)
    _set(p, "Metallic", metal)
    _set(p, "IOR", ior)
    _set(p, ["Transmission Weight", "Transmission"], transmission)
    _set(p, ["Subsurface Weight", "Subsurface"], sss)
    _set(p, "Subsurface Radius", sss_radius)
    _set(p, "Subsurface Scale", sss_scale)
    _set(p, ["Coat Weight", "Clearcoat"], coat)
    _set(p, "Alpha", alpha)
    if emission is not None:
        _set(p, ["Emission Color", "Emission"], (*srgb(emission), 1))
        _set(p, "Emission Strength", emission_strength)
    return m


def emissive(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*srgb(color), 1)
    e.inputs["Strength"].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], o.inputs["Surface"])
    return m


def glow_volume(name, color, strength, density=0.0):
    """Volume-only material: a faint beam of light."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    _set(v, "Density", density)
    _set(v, "Color", (*srgb(color), 1))
    _set(v, ["Emission Strength"], strength)
    _set(v, ["Emission Color"], (*srgb(color), 1))
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(v.outputs[0], o.inputs["Volume"])
    return m


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def bevel(obj, width, segments=5):
    b = obj.modifiers.new("Bevel", "BEVEL")
    b.width = width
    b.segments = segments
    b.limit_method = "ANGLE"
    return obj


def rounded_box(name, size, loc, width=0.06, mat=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    bevel(o, width, 6)
    if mat:
        assign(o, mat)
    return o


def cylinder(name, r, depth, loc, rot=(0, 0, 0), verts=96, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth,
                                        location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    smooth(o)
    if mat:
        assign(o, mat)
    return o


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def area_light(name, loc, target, power, size, color=(1, 1, 1)):
    l = bpy.data.lights.new(name, "AREA")
    l.energy = power
    l.size = size
    l.color = srgb(color)
    o = bpy.data.objects.new(name, l)
    bpy.context.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    return o


def spot(name, loc, target, power, color, angle_deg=30, blend=0.6, radius=0.02):
    l = bpy.data.lights.new(name, "SPOT")
    l.energy = power
    l.color = srgb(color)
    l.spot_size = math.radians(angle_deg)
    l.spot_blend = blend
    l.shadow_soft_size = radius
    o = bpy.data.objects.new(name, l)
    bpy.context.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    return o


def point(name, loc, power, color, radius=0.05):
    l = bpy.data.lights.new(name, "POINT")
    l.energy = power
    l.color = srgb(color)
    l.shadow_soft_size = radius
    o = bpy.data.objects.new(name, l)
    bpy.context.collection.objects.link(o)
    o.location = loc
    return o


def camera(loc, target, lens=50, dof=None):
    c = bpy.data.cameras.new("Camera")
    c.lens = lens
    if dof:
        c.dof.use_dof = True
        c.dof.focus_distance = dof[0]
        c.dof.aperture_fstop = dof[1]
    o = bpy.data.objects.new("Camera", c)
    bpy.context.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    bpy.context.scene.camera = o
    return o


def shadow_catcher(size=40, z=0.0):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    o = bpy.context.active_object
    o.name = "ShadowCatcher"
    o.is_shadow_catcher = True
    return o


def mesh_from(name, verts, faces, mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    if mat:
        assign(o, mat)
    return o


def curve_tube(name, points, radius, mat=None, hollow=False, resolution=24):
    """Smooth tube through 3D points (NURBS-like via Bezier auto handles)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 8
    cu.resolution_u = resolution
    cu.use_fill_caps = not hollow
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    if mat:
        cu.materials.append(mat)
    return o


def delete_verts(obj, keep):
    """Remove mesh vertices for which keep(co) is False (in object space)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    gone = [v for v in bm.verts if not keep(v.co)]
    bmesh.ops.delete(bm, geom=gone, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def render():
    bpy.ops.render.render(write_still=True)
