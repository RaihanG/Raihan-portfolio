# Agent notes: Raihan portfolio

Handover notes for any coding agent (Claude Code, etc.) picking up this repo on another machine.

## What this is
- Static personal academic website: `index.html`, `style.css`, `script.js`, `assets/`.
- Repo: https://github.com/RaihanG/Raihan-portfolio
- Live site: http://raihangoni.info (FreeHosting.com, DirectAdmin; HTTPS not enabled yet).
- **Pushing to GitHub does NOT deploy.** The owner uploads changed files by hand to
  `/domains/raihangoni.info/public_html` in the FreeHosting file manager.

## Ground rules
- Don't commit, push or upload unless the owner asks.
- Never type the owner's passwords; they sign in to GitHub/FreeHosting themselves.
- Research figures on the public site must be **concept illustrations only**: no result
  plots, no volunteer data, no numbers (papers are under review).
- Cambridge role wording: "course tutor" (not "supervision") for *AI and ML Data Pipelines*;
  "lab demonstrator" for two Python and AI courses. Visiting PhD role sits under Education,
  not Experience. Don't use university logos (brand rules); use the text affiliation line.

## Conventions
- Design tokens live on `:root` in `style.css` (dark theme; `--accent #35e0c8`,
  `--accent-2 #5ea0ff`, `--bg #0a0f15`). Fonts: Fraunces, Inter, JetBrains Mono.
- Cache busting: `style.css?v=YYYYMMDD` and `script.js?v=YYYYMMDD` in `index.html`.
  **Bump the `?v=` value whenever style.css or script.js changes.**
- `.js .reveal` elements fade in on scroll (IntersectionObserver). If screenshots look faded
  in a hidden/background browser, it's frozen transitions, not a bug.
- Nav collapses at `max-width: 1000px`; hero reorders at `920px`. Check 375, 820 and 1280 px.

## Local preview
Any static server works, e.g. `python -m http.server 5173` or `npx serve -l 5173`.
(The original Windows machine had neither, so a PowerShell HttpListener script was used.)

## Blender concept figures (`figures-src/`)
Two photographic concept renders sit at the top of the project cards inside `#panel-optics`:
`assets/fig-sfdi.webp` and `assets/fig-ppg.webp` (1600x1000, ~40-60 KB). Revision 1 was flat neon and
the owner found it cartoonish; revision 2 is a journal-style lab render. Brief, facts and must-nots:
`figures-src/brief.md` (read it before changing anatomy or optics).

- `figures-src/kit/`: vendored copy of the schematic-figure skill's Blender kit (`scene.py`,
  `apparatus3d.py`): studio world, anodised/brushed metal, lab glass, camera body, breadboard.
- `figures-src/common.py`: helpers on top of the kit. Renders on a transparent film, then `finish()`
  lays the image over the card colour `--bg-elev #0e151d` and saves WebP, so it blends into the card.
- `figures-src/sfdi.py`: overhead rail with a DLP-style projector (30 deg off vertical) and a camera
  (near normal), both with polarisers, over a skin block cut to show epidermis, dermis with vessels
  and fat. The fringes are a real projection: a near-point spot light shines through a sinusoidal
  "slide" seen only by shadow rays, so subsurface scattering softens them physically.
- `figures-src/ppg.py`: trachea cut transversely through the sensor (C-shaped cartilage open
  posteriorly, trachealis, annular ligaments, mucosa with vessel texture), ET tube with bevel,
  Murphy eye, blue line and pilot line, thin cuff, amber flex-PCB optode (red LED, photodiode,
  IR LED drawn violet) whose light glows in the wall section.

Render from the repo root (Blender 5.2; ~5 s preview, ~8 s final on the RTX GPU):
```
blender -b --factory-startup -P figures-src/sfdi.py -- --out preview_sfdi.png --preview
blender -b --factory-startup -P figures-src/sfdi.py -- --out assets/fig-sfdi.webp
blender -b --factory-startup -P figures-src/ppg.py  -- --out assets/fig-ppg.webp
```
`--preview` = 50% resolution, 24 samples. Final = 256 samples. `--out` is made absolute against the
current folder (Blender otherwise resolves it against the drive root).

## Later ideas (not requested yet)
Service & Teaching section, CV download, publication year badges/links, refresh stale
MICCAI/ISBI news, HTTPS or move to GitHub Pages.
