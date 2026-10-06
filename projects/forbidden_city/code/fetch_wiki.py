"""Fetch plain-text Wikipedia article extracts as the grounding 'originals'."""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
UA = "ForbiddenCityResearch/1.0 (coursework)"

TITLES = [
    "Forbidden City",
    "Meridian Gate",
    "Gate of Supreme Harmony",
    "Hall of Supreme Harmony",
    "Hall of Central Harmony",
    "Hall of Preserving Harmony",
    "Palace of Heavenly Purity",
    "Hall of Union",
    "Palace of Earthly Tranquility",
    "Gate of Divine Prowess",
    "Corner towers of the Forbidden City",
    "Hall of Literary Glory",
    "Hall of Martial Valor",
    "Wenyuan Ge",
    "Hall of Mental Cultivation",
    "Nine Dragon Wall",
    "Cining Palace",
    "Palace of Gathered Elegance",
    "Qin'an Dian",
]

OUT = "sources/raw/wiki"


def api(params):
    params = dict(params)
    params["format"] = "json"
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as exc:  # noqa: BLE001
            print("retry", attempt, exc, file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("api failed")


def main():
    os.makedirs(OUT, exist_ok=True)
    index = {}
    for title in TITLES:
        data = api({
            "action": "query", "prop": "extracts", "explaintext": "1",
            "redirects": "1", "titles": title,
        })
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            resolved = page.get("title", title)
            text = page.get("extract", "")
            slug = resolved.replace(" ", "_").replace("/", "-")
            path = os.path.join(OUT, slug + ".txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            index[title] = {
                "requested": title,
                "resolved": resolved,
                "missing": "missing" in page,
                "chars": len(text),
                "file": slug + ".txt",
                "url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(resolved.replace(" ", "_")),
            }
            print(f"{title!r} -> {resolved!r} {len(text)} chars")
        time.sleep(0.5)

    with open(os.path.join("sources", "raw", "wiki_index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("wrote sources/raw/wiki_index.json")


if __name__ == "__main__":
    sys.exit(main())
