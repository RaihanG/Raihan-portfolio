"""Shared helpers for the website's Blender concept figures (photographic look).

Builds on the vendored schematic-figure kit in kit/ (scene.py, apparatus3d.py): studio world, real
materials (anodised and brushed metal, glass, subsurface tissue), Cycles. Run a scene from the repo root:
  blender -b --factory-startup -P figures-src/sfdi.py -- --out assets/fig-sfdi.webp [--preview]

The kit renders on a transparent film; finish() then lays the render over the site's card colour
(--bg-elev #0e151d) so the WebP drops into the project card with no visible edge.
"""
import math
import os
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "kit"))
from scene import setup, hex_rgb, cylinder, fiber_path, shadow_floor, camera_look, _mat  # noqa: E402,F401
from apparatus3d import (look, studio, anodized, brushed_metal, painted, matte, camera_box,  # noqa: E402,F401
                         breadboard, no_shadow, _box, _N, glass_tint, mesh_obj)

CARD_BG = "#0e151d"


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out, preview = None, False
    for i, a in enumerate(argv):
        if a == "--out":
            # Blender resolves bare relative paths against the drive root on Windows.
            out = os.path.abspath(argv[i + 1])
        if a == "--preview":
            preview = True
    return out, preview


def start(preview, w=1600, h=1000, samples=256):
    S = setup(w, h, 24 if preview else samples)
    look(S)
    S.render.resolution_percentage = 50 if preview else 100
    S.cycles.sample_clamp_indirect = 6.0
    return S


def group(objs, loc=(0, 0, 0), rot=Matrix.Identity(3)):
    """Move a list of objects (built around the origin) as one rigid part."""
    bpy.context.view_layer.update()
    M = Matrix.Translation(Vector(loc)) @ rot.to_4x4()
    for o in objs:
        if o.parent is None:
            o.matrix_world = M @ o.matrix_world
    return M


def rot_y(deg):
    return Matrix.Rotation(math.radians(deg), 3, "Y")


def basis(n, hint=(1, 0, 0)):
    """3x3 rotation whose z axis is n and whose x axis is as close to `hint` as possible."""
    n = Vector(n).normalized()
    u = Vector(hint) - Vector(hint).dot(n) * n
    u.normalize()
    v = n.cross(u)
    return Matrix((u, v, n)).transposed()


def glow_mat(color, alpha, strength=1.0):
    """Faint self-lit veil for drawn light paths (works on the transparent film, unlike volumes)."""
    g = _N("veil")
    g.set(Base_Color=color, Emission_Color=color, Emission_Strength=strength, Alpha=alpha, Roughness=1.0)
    g.set(Specular_IOR_Level=0.0)
    return g.m


def frustum(apex, corners, color, alpha, name="frustum"):
    verts = [tuple(apex)] + [tuple(c) for c in corners]
    faces = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1)]
    o = mesh_obj(name, verts, faces, glow_mat(color, alpha), smooth=False)
    o.visible_shadow = False
    o.visible_glossy = False
    return o


def spot(name, loc, direction, energy, color="#ffffff", size_deg=60, blend=0.2, radius=0.02):
    bpy.ops.object.light_add(type="SPOT", location=loc)
    L = bpy.context.object
    L.name = name
    L.data.energy = energy
    L.data.color = hex_rgb(color)[:3]
    L.data.spot_size = math.radians(size_deg)
    L.data.spot_blend = blend
    L.data.shadow_soft_size = radius
    L.rotation_euler = Vector(direction).to_track_quat("-Z", "Y").to_euler()
    return L


def tissue(color, sss_radius=(1.0, 0.35, 0.18), sss_scale=0.15, rough=0.45, coat=0.0,
           mottle=None, mottle_scale=6.0, bump=0.0, bump_scale=60.0, name="tissue"):
    """Subsurface tissue with colour mottling and fine surface relief."""
    g = _N(name)
    g.set(Roughness=rough, Subsurface_Weight=1.0, Subsurface_Radius=sss_radius, Subsurface_Scale=sss_scale,
          Coat_Weight=coat, Coat_Roughness=0.15)
    co = g.coord()
    if mottle:
        n = g.noise(co, mottle_scale, 6.0, 0.6)
        col = g.ramp(n, [(0.3, mottle), (0.7, color)])
        g.set(Base_Color=col)
        g.set(Subsurface_Radius=sss_radius)
    else:
        g.set(Base_Color=color)
    if bump:
        g.bump(g.noise(co, bump_scale, 8.0, 0.65), bump, 0.01)
    return g


def finish(S, out):
    """Render on the transparent film, then lay it over CARD_BG and save (WebP or PNG)."""
    tmp = os.path.splitext(out)[0] + "_rgba.png"
    S.render.image_settings.file_format = "PNG"
    S.render.image_settings.color_mode = "RGBA"
    S.render.filepath = tmp
    bpy.ops.render.render(write_still=True)
    src = bpy.data.images.load(tmp)
    w, h = src.size
    px = np.array(src.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bg = np.array([int(CARD_BG[i:i + 2], 16) / 255 for i in (1, 3, 5)], dtype=np.float32)
    a = px[..., 3:4]
    px[..., :3] = px[..., :3] * a + bg * (1 - a)
    px[..., 3] = 1.0
    img = bpy.data.images.new("out", w, h, alpha=False)
    img.colorspace_settings.name = src.colorspace_settings.name
    img.pixels[:] = px.ravel()
    img.filepath_raw = out
    if out.lower().endswith(".webp"):
        img.file_format = "WEBP"
        S.render.image_settings.file_format = "WEBP"
        S.render.image_settings.quality = 90
    else:
        img.file_format = "PNG"
        S.render.image_settings.file_format = "PNG"
    S.render.image_settings.color_mode = "RGB"
    img.save_render(out, scene=S)
    os.remove(tmp)
    print("Saved:", out)
