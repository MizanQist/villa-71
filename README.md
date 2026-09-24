# Villa 71

Web brochure for Villa 71 — a private residence of seven en-suite suites with a guest chalet, staff quarters, pool, cinema and gym in Guzape, Abuja, designed by Designetic & A365 Designs. Compiled by Mizan Qist Limited.

Nine pages, one file: `index.html` carries the markup, styles and interactions; `assets/` holds the visualisations (exteriors at the top level at full size for the lightbox, with the 1400 px copies the page itself shows in `assets/m/`; interiors in `assets/i/` with `assets/t/` thumbnails), the four floor plans and the site plan. Fonts load from Google Fonts (Cormorant, Manrope).

## Sources

Three folders in `~/Desktop/Desktop - Mamman’s MacBook Pro/A365`:

- `Villa 71` — the original design brochure PDF (28 pages) and page screenshots. The four exterior schemes (A white, B beige, C white, D beige), the pool, chalet and aerial views, the guest-chalet plan and the site plan are extracted from the PDF's embedded images by `tools/build_assets.py`.
- `Villa 71/Guzape Plans For Brochure All.pdf` — the June 2026 drawing set (A_71_23, Arc. Sadiq Abu): site plan, basement, ground, first and second floor plans, two elevations and a section. The floor plans on page 06 and the site plan on page 04 come from it (`plan-basement/ground/first/second.png`, `site-plan.png`), and page 07's sun study is a section through the approach balcony (53 m², 3.7 m deep, the Suite 6 balcony 2.7 m above it and the roof with its slats), drawn in the Governor's Lodge manner with the profile angle simplified to the sun's altitude.
- `Villa 71 Latest Renders` — the latest visualisations of the recommended scheme (Option B: travertine, white render, timber). The three Ex2 crops are upscaled x2 with Real-ESRGAN (`tools/upscale.py`), as is the low-resolution Option D view.
- `Villa 71 Interior Renders` — 55 interior renders; four exact duplicates are dropped, leaving 51.
- The Kuula collection `INTERIOR DESIGN` (https://kuula.co/share/LMHdf/collection/7TWdq) — thirty equirectangular panoramas, fetched at their largest size by `tools/fetch_panoramas.py` into `assets/vr/` (4096 × 2048 full, `p/` 1024 × 512 previews, `t/` thumbnails). The site renders them itself with a small WebGL viewer, so the tour works without Kuula and inside sandboxed previews. Rooms are fetched ahead of the viewer (current, neighbours, then the rest) so they open sharp; the first room is warmed a few seconds after the page loads.

## Hosting

The site is static. On GitHub Pages, serve the `main` branch from `/` — `.nojekyll` is included so nothing is processed. `robots.txt` and the page's robots meta keep the brochure out of search results; remove both when the development goes public.

## Editing

- Copy lives in `index.html`. The plan tabs are in `PLAN`; the tour's room order and names in `ROOMS` (files `assets/vr/NN.jpg` in that order). The client's description sits on page 02 (`.story`) and its three features are repeated as `.feat` items and in the specification.
- To replace a visualisation, overwrite the file of the same name in `assets/` and its 1400 px copy in `assets/m/` (interiors: `assets/i/` and the thumbnail in `assets/t/`).
- Page 07 (climate and ground) uses the sun's altitude only, so it needs no north point; the section geometry (floor heights, projections) is set in the constants at the top of its script block.
- Client review of 2026-09-24 removed the four-scheme comparison page, the pool, side-passage and aerial views, and the elevation and section tabs; the site plan is the June 2026 sheet.
- Credits: the closing page names A365 Designs as the design contact; Mizan Qist Limited appears only as the brochure's compiler, on one line under the disclaimer.
- Re-run `python3 tools/build_assets.py` after `python3 tools/upscale.py` to rebuild every asset from the source folders.
