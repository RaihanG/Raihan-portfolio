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

## In progress: Blender concept figures (`figures-src/`)
Goal: two high-quality concept renders for the project cards inside `#panel-optics`
in `index.html` ("Optical mapping of tissue with SFDI" and "Tracheal PPG for SpO₂ in
ventilated patients").

- `figures-src/common.py`: shared helpers (Cycles, transparent film, AgX, site palette,
  materials, lights, camera, curve tubes).
- `figures-src/sfdi.py`: projector casting teal sinusoidal fringes on an SSS tissue block,
  camera collecting the returning light, faint volumetric beams.
- `figures-src/ppg.py`: cut-away trachea with cartilage rings and vessels, clear ET tube and
  cuff, optode on the cuff with red 650 nm and IR 870 nm (drawn violet) LEDs, blue fibre out.

Run (Blender 5.3, tested headless on Windows):
```
blender -b -P figures-src/sfdi.py -- --out preview_sfdi.png --preview
blender -b -P figures-src/ppg.py  -- --out preview_ppg.png  --preview
blender -b -P figures-src/sfdi.py -- --out assets/fig-sfdi.webp
blender -b -P figures-src/ppg.py  -- --out assets/fig-ppg.webp
```
`--preview` = 50% resolution, 48 samples. Final = 1600×1000, 384 samples, WEBP.

Status:
- `sfdi.py` runs without errors on Blender 5.3 (~1 min preview); the render has not been
  reviewed or tuned yet.
- `ppg.py` has not been run yet; expect possible API fixes.

Next steps:
1. Preview both, review, tune composition/lighting/fringe and beam strength.
2. Final renders to `assets/fig-sfdi.webp` and `assets/fig-ppg.webp`.
3. Add each as an `<img>` (with alt text, `loading="lazy"`, width/height) to its project card,
   add matching CSS, bump `?v=`, check desktop and mobile.
4. Owner uploads `index.html`, `style.css` and the new assets to FreeHosting.

## Later ideas (not requested yet)
Service & Teaching section, CV download, publication year badges/links, refresh stale
MICCAI/ISBI news, HTTPS or move to GitHub Pages.
