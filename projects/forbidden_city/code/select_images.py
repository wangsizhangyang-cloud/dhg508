"""Download the chosen candidate for each building at ~2048px and record
source + license metadata into images/manifest.json."""
import json
import os
import re
import sys
import time
import urllib.parse

from commons import imageinfo, download
from selection import BUILDINGS, SELECTED

META = "research/notes/candidate_meta.json"
OUTDIR = "images"
WIDTH = 2048


def safe(s):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", s).strip("-")


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    with open(META, encoding="utf-8") as fh:
        meta = json.load(fh)

    names = {key: (num, chn, eng) for num, key, chn, eng in BUILDINGS}
    manifest = {}

    for key, label in SELECTED.items():
        rec = meta.get(label)
        if not rec:
            print("MISSING META", label, file=sys.stderr)
            continue
        title = rec["requested_title"]
        num, chn, eng = names[key]
        info = imageinfo([title]).get(title, {})
        url = info.get("thumburl") or info.get("url")
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            ext = ".jpg"
        fname = f"bld-{num:02d}-{safe(key)}{ext}"
        path = os.path.join(OUTDIR, fname)
        if not (os.path.exists(path) and os.path.getsize(path) > 0):
            size = download(url, path)
            print("downloaded", fname, size, file=sys.stderr)
        manifest[key] = {
            "id": num,
            "name_chn": chn,
            "name_eng": eng,
            "image": fname,
            "commons_title": title,
            "description_url": info.get("descriptionurl", rec.get("descriptionurl", "")),
            "artist": info.get("artist", rec.get("artist", "")),
            "license": info.get("license", rec.get("license", "")),
            "credit": info.get("credit", rec.get("credit", "")),
            "image_datetime": info.get("datetime", ""),
        }
        time.sleep(0.3)

    with open(os.path.join(OUTDIR, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    print("wrote", os.path.join(OUTDIR, "manifest.json"), len(manifest))


if __name__ == "__main__":
    main()
