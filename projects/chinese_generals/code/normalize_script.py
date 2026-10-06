"""Normalise the non-quote fields of data/generals/*.json to Traditional.

The original 史書 text is Traditional; `source_quote` must stay verbatim, so it
is skipped. Everything else (names, places, notes, descriptions) is converted so
the database is internally consistent.

Usage:
    python code/normalize_script.py
"""
import glob
import json
import os
import sys

from zhconv import convert

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKIP = {"source_quote", "source_url", "source_slug"}


def _skip(key):
    # never touch verbatim original-wording fields
    return key in SKIP or key.endswith("_raw")


def walk(obj):
    if isinstance(obj, dict):
        return {k: (v if _skip(k) else walk(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v) for v in obj]
    if isinstance(obj, str):
        out = convert(obj, "zh-hant")
        # zhconv maps the surname 岳 to 嶽; the histories write 岳飛.
        return out.replace("嶽飛", "岳飛")
    return obj


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "data", "generals", "*.json")))
    for path in files:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(walk(data), fh, ensure_ascii=False, indent=2)
        print("normalised", os.path.basename(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
