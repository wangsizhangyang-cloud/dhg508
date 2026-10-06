"""Small helpers to query Wikimedia Commons (search, metadata, download).

Standard library only. Used to find one people-free photo per Forbidden City
building and to record its source + license for citation.
"""
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "ForbiddenCityResearch/1.0 (coursework; contact: student)"


def api(params, tries=6):
    params = dict(params)
    params["format"] = "json"
    query = urllib.parse.urlencode(params)
    last = None
    for attempt in range(tries):
        req = urllib.request.Request(API + "?" + query, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(3 * (attempt + 1))
    raise last


def search(term, limit=25):
    data = api({
        "action": "query",
        "list": "search",
        "srsearch": term,
        "srnamespace": "6",
        "srlimit": str(limit),
    })
    return [r["title"] for r in data.get("query", {}).get("search", [])]


def imageinfo(titles):
    """titles: list of File: titles (max 50). Returns extmetadata + urls."""
    data = api({
        "action": "query",
        "titles": "|".join(titles),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata|user|sha1",
        "iiurlwidth": "1600",
    })
    out = {}
    for page in data.get("query", {}).get("pages", {}).values():
        if "imageinfo" not in page:
            continue
        info = page["imageinfo"][0]
        meta = info.get("extmetadata", {})
        def g(k):
            v = meta.get(k, {}).get("value", "")
            return v
        out[page["title"]] = {
            "title": page["title"],
            "descriptionurl": info.get("descriptionurl", ""),
            "url": info.get("url", ""),
            "thumburl": info.get("thumburl", info.get("url", "")),
            "width": info.get("width"),
            "height": info.get("height"),
            "mime": info.get("mime"),
            "artist": g("Artist"),
            "license": g("LicenseShortName"),
            "credit": g("Credit"),
            "objectname": g("ObjectName"),
            "imagedescription": g("ImageDescription"),
            "datetime": g("DateTimeOriginal"),
        }
    return out


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp, open(path, "wb") as fh:
        fh.write(resp.read())
    return os.path.getsize(path)


def main():
    cmd = sys.argv[1]
    if cmd == "search":
        for t in search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 25):
            print(t)
    elif cmd == "info":
        titles = sys.argv[2:]
        info = imageinfo(titles)
        print(json.dumps(info, ensure_ascii=False, indent=1))
    elif cmd == "download":
        url, path = sys.argv[2], sys.argv[3]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(download(url, path), path)
    else:
        raise SystemExit("unknown cmd: " + cmd)


if __name__ == "__main__":
    main()
