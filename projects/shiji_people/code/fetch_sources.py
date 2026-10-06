"""Download 《史記》 chapters from Chinese Wikisource (primary text).

Wikipedia articles are NOT used. Wikisource hosts the public-domain original
text of 司馬遷《史記》. Each downloaded chapter (卷) is the "document"; the
section heading inside it is the "page"/locator quoted by the database rows.

We keep the raw wikitext verbatim in sources/raw/wikisource/ and write a
sources/raw/sources_index.json manifest with page id, revision id, URL, juan,
and the chapter title.

Usage:
    python code/fetch_sources.py --probe       # only check the pages exist
    python code/fetch_sources.py               # download all chapters
    python code/fetch_sources.py 65            # only 史記/卷065
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://zh.wikisource.org/w/api.php"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "sources", "raw", "wikisource")
INDEX = os.path.join(ROOT, "sources", "raw", "sources_index.json")
UA = "shiji-people-coursework/1.0 (research; contact: student)"

# 卷001-012 本紀, 卷013-022 表, 卷023-030 書, 卷031-060 世家, 卷061-130 列傳.
# 表 and 書 are calendars/treatises, not biographies, so they are skipped.
BENJI = list(range(1, 13))
SHIJIA = list(range(31, 61))
LIEZHUAN = list(range(61, 131))
JUANS = BENJI + SHIJIA + LIEZHUAN


def title_for(juan):
    return "史記/卷%03d" % juan


def page_url(title):
    return "https://zh.wikisource.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return fh.read()


def _get_retry(url, tries=6):
    for i in range(tries):
        try:
            return _get(url)
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and i < tries - 1:
                time.sleep(3 * (i + 1))
                continue
            raise
        except Exception:
            if i < tries - 1:
                time.sleep(2 * (i + 1))
                continue
            raise


def api(params):
    params = dict(params)
    params["format"] = "json"
    params["formatversion"] = "2"
    url = API + "?" + urllib.parse.urlencode(params)
    return json.loads(_get_retry(url).decode("utf-8"))


def probe(title):
    data = api({"action": "query", "titles": title, "prop": "info", "redirects": 1})
    p = data["query"]["pages"][0]
    return ("missing" not in p), p.get("pageid"), p.get("lastrevid")


def fetch(title):
    data = api({"action": "parse", "page": title, "prop": "wikitext", "redirects": 1})
    if "error" in data:
        raise RuntimeError(data["error"].get("info", "api error"))
    return data["parse"]["wikitext"], data["parse"].get("revid")


def reindex():
    """Rebuild sources_index.json from the .wiki files already on disk."""
    rows = []
    for juan in JUANS:
        slug = "shiji-%03d" % juan
        path = os.path.join(OUTDIR, slug + ".wiki")
        if not os.path.exists(path):
            continue
        title = title_for(juan)
        try:
            exists, pid, lastrev = probe(title)
        except Exception as exc:  # noqa: BLE001
            print("PROBE-ERR", slug, type(exc).__name__)
            continue
        with open(path, encoding="utf-8") as fh:
            wikitext = fh.read()
        rows.append({
            "slug": slug,
            "title": title,
            "text": "史記",
            "juan": juan,
            "file": "sources/raw/wikisource/" + slug + ".wiki",
            "source_url": page_url(title),
            "pageid": pid,
            "revision": lastrev,
            "chars": len(wikitext),
        })
        print("INDEXED  ", slug, "rev=", lastrev)
        time.sleep(0.5)
    with open(INDEX, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)
    print("wrote", INDEX, "with", len(rows), "chapters")
    return 0


def main():
    probe_only = "--probe" in sys.argv
    if "--reindex" in sys.argv:
        return reindex()
    only = [int(a) for a in sys.argv[1:] if a.isdigit()]
    juans = only or JUANS
    os.makedirs(OUTDIR, exist_ok=True)
    existing = {}
    if os.path.exists(INDEX):
        with open(INDEX, encoding="utf-8") as fh:
            existing = {row["slug"]: row for row in json.load(fh)}

    index = []
    for juan in juans:
        slug = "shiji-%03d" % juan
        title = title_for(juan)
        try:
            exists, pid, lastrev = probe(title)
        except Exception as exc:  # noqa: BLE001
            print("PROBE-ERR", slug, type(exc).__name__)
            continue
        if not exists:
            print("MISSING  ", slug, title)
            continue
        if probe_only:
            print("OK       ", slug, title, "pageid=", pid, "rev=", lastrev)
            continue
        try:
            wikitext, rev = fetch(title)
        except Exception as exc:  # noqa: BLE001
            print("FETCH-ERR", slug, type(exc).__name__, exc)
            time.sleep(1.0)
            continue
        path = os.path.join(OUTDIR, slug + ".wiki")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(wikitext)
        row = {
            "slug": slug,
            "title": title,
            "text": "史記",
            "juan": juan,
            "file": "sources/raw/wikisource/" + slug + ".wiki",
            "source_url": page_url(title),
            "pageid": pid,
            "revision": rev,
            "chars": len(wikitext),
        }
        index.append(row)
        print("FETCHED  ", slug, "%d chars rev=%s" % (len(wikitext), rev))
        time.sleep(1.0)

    if not probe_only:
        # merge with anything already there, newest wins per slug
        merged = dict(existing)
        merged.update({row["slug"]: row for row in index})
        rows = [merged[k] for k in sorted(merged)]
        with open(INDEX, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rows, fh, ensure_ascii=False, indent=2)
        print("wrote", INDEX, "with", len(rows), "chapters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
