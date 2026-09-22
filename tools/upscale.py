# Real-ESRGAN x2 (ONNX, CPU) for the low-resolution sources: the three Ex2 crops and the Option D side view.
import os, sys, time, numpy as np, onnxruntime as ort
from PIL import Image, ImageOps
MODEL = "/Users/mammanali/Desktop/Desktop - Mamman’s MacBook Pro/Cova Manor Brochure/tools/print/models/real_esrgan_x2.onnx"
A = "/Users/mammanali/Desktop/Desktop - Mamman’s MacBook Pro/A365"
S = "/private/tmp/claude-501/-Users-mammanali/02cd6160-066d-4b8d-afb1-2bba9b27b82c/scratchpad"
OUT = os.path.join(S, "up"); os.makedirs(OUT, exist_ok=True)
TILE, PAD, SC = 256, 16, 2
so = ort.SessionOptions(); so.log_severity_level = 3
sess = ort.InferenceSession(MODEL, so, providers=["CPUExecutionProvider"])
def upscale(im):
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    H, W = a.shape[:2]
    Hp = (H + TILE - 1) // TILE * TILE; Wp = (W + TILE - 1) // TILE * TILE
    a = np.pad(a, ((PAD, Hp - H + PAD), (PAD, Wp - W + PAD), (0, 0)), mode="reflect")
    out = np.zeros((Hp * SC, Wp * SC, 3), dtype=np.uint8)
    n = (Hp // TILE) * (Wp // TILE); k = 0; t0 = time.time()
    for y in range(0, Hp, TILE):
        for x0 in range(0, Wp, TILE):
            tile = a[y:y + TILE + 2*PAD, x0:x0 + TILE + 2*PAD]
            o = sess.run(None, {"input": np.ascontiguousarray(tile.transpose(2, 0, 1)[None])})[0][0].transpose(1, 2, 0)
            o = o[PAD*SC:(PAD+TILE)*SC, PAD*SC:(PAD+TILE)*SC]
            out[y*SC:(y+TILE)*SC, x0*SC:(x0+TILE)*SC] = np.clip(o * 255.0 + 0.5, 0, 255).astype(np.uint8)
            k += 1
            if k % 10 == 0 or k == n: print(f"   tile {k}/{n}  {time.time()-t0:.0f}s", flush=True)
    return Image.fromarray(out[:H*SC, :W*SC])
JOBS = [
 (f"{A}/Villa 71 Latest Renders/Ex2A Post Pro.png", "rec-a"),
 (f"{A}/Villa 71 Latest Renders/Ex2b Post Pro.png", "rec-b"),
 (f"{A}/Villa 71 Latest Renders/Ex2c Post Pro.png", "rec-c"),
 (f"{S}/pdfimg/p13_x267_987x1080.jpeg", "opt-d-side"),
]
for src, name in JOBS:
    im = ImageOps.exif_transpose(Image.open(src)); print(f"[{name}] {im.size}", flush=True); t = time.time()
    big = upscale(im); big.save(os.path.join(OUT, name + ".png")); print(f"[{name}] done {big.size} in {time.time()-t:.0f}s", flush=True)
print("ALL DONE", flush=True)
