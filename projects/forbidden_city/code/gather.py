"""Fetch metadata + thumbnail for each curated candidate image."""
import json
import os
import sys
import time
import urllib.parse

from commons import imageinfo, download
from curated_candidates import CURATED

OUTDIR = "artifacts/candidates"
META = "research/notes/candidate_meta.json"
THUMB_W = 1400


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    all_titles = []
    index = {}
    for key, titles in CURATED.items():
        for i, t in enumerate(titles, 1):
            label = f"{key}-{i:02d}"
            index[t] = label
            all_titles.append(t)

    meta = {}
    if os.path.exists(META):
        with open(META, encoding="utf-8") as fh:
            meta = json.load(fh)

    # batches of 50
    for b in range(0, len(all_titles), 50):
        batch = all_titles[b:b + 50]
        info = imageinfo(batch)
        for title, rec in info.items():
            label = index.get(title)
            if not label:
                continue
            rec["label"] = label
            rec["requested_title"] = title
            meta[label] = rec
        time.sleep(1)

    with open(META, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)

    for label, rec in sorted(meta.items()):
        url = rec.get("thumburl") or rec.get("url")
        if not url:
            print("NO URL", label, file=sys.stderr)
            continue
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            ext = ".jpg"
        path = os.path.join(OUTDIR, label + ext)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        try:
            size = download(url, path)
            print(label, size, path, file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            print("FAIL", label, exc, file=sys.stderr)
        time.sleep(0.5)

    print("candidates:", len(meta))


if __name__ == "__main__":
    main()
