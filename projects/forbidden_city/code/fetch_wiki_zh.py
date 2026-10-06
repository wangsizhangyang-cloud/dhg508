"""Fetch plain-text Chinese Wikipedia extracts (fallback grounding sources)."""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://zh.wikipedia.org/w/api.php"
UA = "ForbiddenCityResearch/1.0 (coursework)"

TITLES = [
    "北京故宫",
    "午门",
    "太和门",
    "太和殿",
    "中和殿",
    "保和殿",
    "乾清宫",
    "交泰殿",
    "坤宁宫",
    "神武门",
    "故宫角楼",
    "文华殿",
    "武英殿",
    "文渊阁 (北京)",
    "养心殿",
    "九龙壁",
    "慈宁宫",
    "储秀宫",
    "钦安殿",
]

OUT = "sources/raw/wiki_zh"


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
        for page in data.get("query", {}).get("pages", {}).values():
            resolved = page.get("title", title)
            text = page.get("extract", "")
            slug = resolved.replace(" ", "_").replace("/", "-")
            with open(os.path.join(OUT, slug + ".txt"), "w", encoding="utf-8") as fh:
                fh.write(text)
            index[title] = {
                "requested": title, "resolved": resolved,
                "missing": "missing" in page, "chars": len(text),
                "file": slug + ".txt",
                "url": "https://zh.wikipedia.org/wiki/" + urllib.parse.quote(resolved.replace(" ", "_")),
            }
            print(f"{title!r} -> {resolved!r} {len(text)} chars")
        time.sleep(0.6)

    with open(os.path.join("sources", "raw", "wiki_zh_index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("wrote sources/raw/wiki_zh_index.json")


if __name__ == "__main__":
    sys.exit(main())
