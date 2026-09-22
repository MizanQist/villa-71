# Fetches the thirty panoramas of the Kuula collection 7TWdq and builds assets/vr/ (full 4096x2048, p/ previews, t/ thumbnails).
# The share page embeds the collection as base64 JSON in window.KUULA_COLLECTION; each post's photo lives at
# https://files.kuula.io/<uuid>/<name>-<size>.jpg. Room names shown on the site are the ROOMS list in index.html.
import re, json, base64, os, sys, urllib.request
from PIL import Image
SHARE = "https://kuula.co/share/LMHdf/collection/7TWdq?logo=0&info=1&fs=1&vr=0&sd=1&thumbs=1"
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(B, "assets", "vr")
for d in ("", "p", "t"): os.makedirs(os.path.join(OUT, d), exist_ok=True)
def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()
html = get(SHARE).decode("utf-8", "ignore")
col = json.loads(base64.b64decode(re.search(r'window\.KUULA_COLLECTION=\{id:"[^"]+",data:"([^"]+)"', html).group(1)))
for k, post in enumerate(col["posts"], 1):
    ph = post["photos"][0]; n = f"{k:02d}"
    url = f"https://files.kuula.io/{post['uuid']}/{ph['name']}-{ph['sizes'][0]}.jpg"
    src = os.path.join(OUT, f"src-{n}.jpg"); open(src, "wb").write(get(url))
    im = Image.open(src).convert("RGB"); W, H = im.size
    im.resize((4096, 2048), Image.LANCZOS).save(os.path.join(OUT, n + ".jpg"), "JPEG", quality=72, optimize=True, progressive=True)
    im.resize((1024, 512), Image.LANCZOS).save(os.path.join(OUT, "p", n + ".jpg"), "JPEG", quality=76, optimize=True)
    im.crop((int(W*.30), int(H*.30), int(W*.70), int(H*.70))).resize((320, 160), Image.LANCZOS).save(os.path.join(OUT, "t", n + ".jpg"), "JPEG", quality=78, optimize=True)
    os.remove(src); print(n, post["description"], (W, H), flush=True)
