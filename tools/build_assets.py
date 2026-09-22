# Builds assets/ from the three A365 source folders and the Villa 71 brochure PDF.
# Exteriors come from the PDF's embedded JPEGs (native 1800 px, sharper than the page screenshots);
# the four low-res sources are upscaled first by tools/upscale.py into the scratchpad "up" folder.
import os, glob, fitz, numpy as np
from PIL import Image, ImageOps
A = "/Users/mammanali/Desktop/Desktop - Mamman’s MacBook Pro/A365"
S = "/private/tmp/claude-501/-Users-mammanali/02cd6160-066d-4b8d-afb1-2bba9b27b82c/scratchpad"
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(B, "assets")
PDF = fitz.open(f"{A}/Villa 71/Villa 71 Brochure.pdf")

def pdfimg(xref):
    info = PDF.extract_image(xref); import io
    return Image.open(io.BytesIO(info["image"])).convert("RGB")

def save(im, name, long=2000, q=82, sub="", short=None):
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size; L = max(w, h)
    if L > long:
        s = long / L; im = im.resize((round(w*s), round(h*s)), Image.LANCZOS)
    p = os.path.join(OUT, sub, name + ".jpg")
    im.save(p, "JPEG", quality=q, optimize=True, progressive=True)
    return im, os.path.getsize(p)//1024

total = 0
def log(name, im, kb):
    global total; total += kb; print(f"{name:26s} {im.size[0]}x{im.size[1]}  {kb} KB", flush=True)

# ---- recommended scheme (Latest Renders) ----
L = f"{A}/Villa 71 Latest Renders"
for src, name, long in [
    (f"{L}/Ex2 Post Pro.png", "hero", 2400),
    (f"{L}/Ex1 Post Pro.jpg", "gate", 2048),
    (f"{L}/Luxury_bungalow_architectural_ph…_2K_202609082021.jpg", "chalet", 2048),
    (f"{L}/Luxury_residence_photo_prompt_in…_2K_202609090916.jpg", "front-cloud", 2400),
    (f"{S}/up/rec-a.png", "rec-a", 2200), (f"{S}/up/rec-b.png", "rec-b", 2200), (f"{S}/up/rec-c.png", "rec-c", 2200),
    (f"{S}/up/opt-d-side.png", "opt-d-side", 1974),
]:
    if not os.path.exists(src): print("MISSING", src); continue
    im, kb = save(Image.open(src), name, long=long, q=84); log(name, im, kb)

# ---- the four options and the grounds, from the PDF ----
for xref, name in [(214,"opt-a-gate"),(225,"opt-b-gate"),(236,"opt-a-side"),(247,"opt-b-side"),(258,"opt-c-side"),
                   (405,"opt-c-front"),(415,"opt-b-front"),(426,"pool-1"),(438,"pool-2"),(449,"pool-3"),(461,"passage"),
                   (472,"chalet-b"),(484,"chalet-a"),(494,"aerial-1"),(508,"aerial-2")]:
    im, kb = save(pdfimg(xref), name, long=2000, q=82); log(name, im, kb)

# ---- interiors: 51 unique renders (four exact duplicates dropped) ----
INT = [  # source file, slug
 ("1 GUEST CHALET LIVING ROOM 2","chalet-living"),("2 GUEST CHALET KITCHEN 1","chalet-kitchen-1"),("2 GUEST CHALET KITCHEN 2","chalet-kitchen-2"),
 ("4 GRAND LOBBY 2","lobby"),("5 GRAND LOBBY ENTRANCE","lobby-entrance"),("5 LOUNGE","lounge"),("6 HOME OFFICE 2","office"),
 ("7 PRIVATE LOUNGE 1","private-lounge-1"),("7 PRIVATE LOUNGE 2","private-lounge-2"),
 ("8 MAIN LIVING ROOM 1","living-1"),("9 MAIN LIVING ROOM 2","living-2"),("9 MAIN LIVING ROOM CLOSE 2","living-3"),("9 MAIN LIVING ROOMDINING CLOSE","living-dining"),
 ("10 DINING 2","dining"),("11 INDOOR GARDEN 1","garden-1"),("11 INDOOR GARDEN 3","garden-2"),("11 KITCHEN 1","kitchen-1"),("11 KITCHEN 2","kitchen-2"),
 ("12 GYM 1","gym-1"),("12 GYM 2","gym-2"),("12 SUITE 1 BEDROOM","suite1-1"),("12 SUITE 1 BEDROOM 2","suite1-2"),
 ("13 SUITE 2 BEDROOM","suite2-1"),("13 SUITE 2 BEDROOM 2","suite2-2"),("14 SUITE 2 TOILET 2","suite2-bath"),
 ("15 SUITE 3 BEDROOM","suite3-1"),("15 SUITE 3 BEDROOM 2","suite3-2"),("16 SUITE 3 TOILET","suite3-bath-1"),("16 SUITE 3 TOILET 2","suite3-bath-2"),
 ("17 FAMILY LOUNGE","family-1"),("17 FAMILY LOUNGE 2","family-2"),("19 SUITE 4 BEDROOM","suite4-1"),("19 SUITE 4 BEDROOM 2","suite4-2"),
 ("21 SUITE 4 TOILET","suite4-bath-1"),("21 SUITE 4 TOILET 2","suite4-bath-2"),("22 BOX ROOM","boxroom"),
 ("23 MASTER SUITE LOUNGE AND MASTER SUITE BEDROOM","master-lounge-1"),("23 MASTER SUITE LOUNGE AND MASTER SUITE BEDROOM 2","master-lounge-2"),
 ("24 MASTER SUITE CLOSET","master-closet-1"),("24 Master suite closet 2","master-closet-2"),("27 master suite closet","master-closet-3"),
 ("25 MASTER SUITE TOILET","master-bath"),("26 MASTER SUITE BEDROOM","master-bed-1"),("26 MASTER SUITE BEDROOM 2","master-bed-2"),
 ("29 OUTDOOR EXPANSE TERRACE 1","terrace-1"),("29 OUTDOOR EXPANSE TERRACE 2","terrace-2"),("29 STAIRHALL","stairhall"),("31 OUTDOOR POOL","pool-house"),
 ("32 CINEMA ROOM 1","cinema-1"),("32 CINEMA ROOM 2","cinema-2"),("32 CIBEMA ROOM 2B","cinema-3"),
]
for src, slug in INT:
    im = Image.open(f"{A}/Villa 71 Interior Renders/{src}.jpg")
    big, kb = save(im, slug, long=1800, q=80, sub="i"); log("i/"+slug, big, kb)
    th, kb2 = save(big, slug, long=900, q=76, sub="t"); total += 0; print(f"   thumb {th.size} {kb2} KB")

# ---- plans: left panel of pages 14-17 at 300 dpi, white -> transparent, ink darkened ----
def plan(pn, name, clip):
    p = PDF[pn-1]; pix = p.get_pixmap(dpi=300, clip=fitz.Rect(*clip), alpha=False)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3).astype(np.int16)
    lum = a.mean(axis=2)
    alpha = np.clip((235 - lum) * 255 / (235 - 40), 0, 255).astype(np.uint8)
    # keep the soft green planting tint, otherwise ink
    rgb = np.clip(a, 0, 255).astype(np.uint8)
    out = np.dstack([rgb, alpha])
    im = Image.fromarray(out, "RGBA")
    bbox = Image.fromarray(alpha).point(lambda v: 255 if v > 24 else 0).getbbox()
    im = im.crop((max(bbox[0]-20,0), max(bbox[1]-20,0), min(bbox[2]+20, im.width), min(bbox[3]+20, im.height)))
    im.save(os.path.join(OUT, name + ".png"), optimize=True)
    print(f"{name:26s} {im.size}  {os.path.getsize(os.path.join(OUT,name+'.png'))//1024} KB", flush=True)
plan(14, "plan-ground", (40, 12, 392, 372)); plan(15, "plan-first", (40, 4, 392, 372)); plan(16, "plan-second", (36, 4, 392, 372)); plan(17, "plan-guest", (60, 40, 392, 340))

# ---- site plan: the green band of page 4 ----
p = PDF[3]; pix = p.get_pixmap(dpi=300, clip=fitz.Rect(0, 46, 595, 338), alpha=False)
im = Image.frombytes("RGB", (pix.w, pix.h), pix.samples)
im.save(os.path.join(OUT, "site-plan.jpg"), "JPEG", quality=86, optimize=True, progressive=True)
print("site-plan", im.size, os.path.getsize(os.path.join(OUT,'site-plan.jpg'))//1024, "KB")

# ---- og image 1200x630 from the gate view ----
g = Image.open(os.path.join(OUT, "gate.jpg")); og = ImageOps.fit(g, (1200, 630), Image.LANCZOS, centering=(0.5, 0.42))
og.save(os.path.join(OUT, "og.jpg"), "JPEG", quality=82, optimize=True)
print("TOTAL KB", total)
