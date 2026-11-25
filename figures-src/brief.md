# Concept figures: brief, facts, spec

Two hero renders for the project cards in `#panel-optics` (16:10, shown ~500 px wide on desktop,
~290 px on phones, on the dark card colour `#0e151d`). No labels in the image: the card text names
everything. Revision 2 (Nov 2026): the owner found revision 1 cartoonish; this one aims for a
photographic lab render (real materials, studio light, anatomical detail), not flat neon.

Must not imply: any measured result, data, numbers, a specific commercial device, or a clinical claim.

## SFDI

Takeaway: patterned light is projected onto layered tissue and a camera records the diffusely
reflected light, so the optical properties below the surface can be mapped without cutting.

Facts (standard SFDI setup, e.g. Cuccia et al. 2009; commercial and lab systems alike):
- A projector (DMD light engine) and a scientific camera both sit above the sample, looking down.
  The camera is near normal; the projector is a few tens of degrees off normal, so specular glare
  from the projector misses the camera.
- Crossed linear polarisers in front of projector and camera reject specular reflection.
- The projected pattern is a 1-D sinusoid (fringes) over a rectangular field; spatial frequencies
  of order 0-0.5 mm^-1. Several phases are projected in sequence (only one is drawn).
- Skin layers, top to bottom: epidermis (~0.1 mm, thin), dermis (1-4 mm, vascular), subcutaneous
  fat (lobules). Drawn thicknesses are schematic, the epidermis exaggerated so it reads.
- The fringes blur slightly with depth in tissue (diffuse scattering); the subsurface material shows
  this physically rather than by a drawn effect.

Spec: Hero: SFDI rig and skin block, rendered with Blender (photographic), kit parts from
`kit/apparatus3d.py` (camera_box, anodised/brushed materials) and custom tissue geometry.
3/4 view from front-left so the cut face shows the layers; both devices on one overhead rail.

## Tracheal PPG

Takeaway: an optical sensor on the cuff of a breathing tube shines red and infrared light into the
tracheal wall and detects the light that returns, giving a pulse signal for SpO2.

Facts:
- An endotracheal tube (clear PVC, blue radiopaque line, depth marks, bevelled tip with Murphy eye)
  runs through the larynx into the trachea; its inflated cuff seals against the tracheal mucosa.
  A thin pilot line runs from the cuff along the tube to the outside.
- Trachea: C-shaped hyaline cartilage rings (open posteriorly, closed by the trachealis membrane),
  joined by annular ligaments; inner surface is pink, moist mucosa with a fine vascular network.
- Reflectance PPG: LEDs (red ~660 nm and infrared ~880-940 nm) and a photodiode side by side on the
  cuff surface, facing the mucosa; light diffuses through the wall and part returns to the detector.
  The leads run along the tube to the outside.
- Infrared is invisible; it is drawn violet to tell it apart from red (site convention).

Spec: Hero: trachea section with an anatomical window cut open over the sensor, rendered with
Blender (photographic). The window's cut face shows the wall layers and cartilage in section with
the light glowing in the tissue next to the sensor.
