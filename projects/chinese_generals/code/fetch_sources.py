"""Download primary-source chapters (史書) from Chinese Wikisource.

Wikipedia articles are deliberately NOT used. Wikisource hosts the original
classical texts; each downloaded chapter is the "document" and the section
heading is the "page"/locator quoted by the database rows.

Usage:
    python code/fetch_sources.py --probe     # only check the pages exist
    python code/fetch_sources.py             # download all chapters
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser

API = "https://zh.wikisource.org/w/api.php"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "sources", "raw", "wikisource")
MANIFEST = os.path.join(HERE, "sources_manifest.json")
INDEX = os.path.join(ROOT, "sources", "raw", "wikisource_index.json")
UA = "chinese-generals-coursework/1.0 (research; contact: student)"


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        if tag in ("p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return fh.read()


def _get_retry(url, tries=6):
    for i in range(tries):
        try:
            return _get(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and i < tries - 1:
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


def page_url(title):
    return "https://zh.wikisource.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))


def to_text(html):
    p = _Text()
    p.feed(html)
    text = "".join(p.parts)
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch(title):
    data = api({"action": "parse", "page": title, "prop": "text", "redirects": 1})
    if "error" in data:
        raise RuntimeError(data["error"].get("info", "api error"))
    html = data["parse"]["text"]
    rev = data["parse"].get("revid")
    return to_text(html), rev


def probe(title):
    data = api({"action": "query", "titles": title, "prop": "info", "redirects": 1})
    pages = data["query"]["pages"]
    p = pages[0]
    return ("missing" not in p), p.get("pageid")


def main():
    probe_only = "--probe" in sys.argv
    with open(MANIFEST, encoding="utf-8") as fh:
        manifest = json.load(fh)
    os.makedirs(OUTDIR, exist_ok=True)
    index = []
    for item in manifest:
        title = item["title"]
        try:
            exists, pid = probe(title)
        except Exception as exc:  # noqa: BLE001
            print("PROBE-ERR", item["slug"], type(exc).__name__)
            exists, pid = False, None
        if not exists:
            print("MISSING  ", item["slug"], title)
            continue
        if probe_only:
            print("OK       ", item["slug"], title, "pageid=", pid)
            continue
        try:
            text, rev = fetch(title)
        except Exception as exc:  # noqa: BLE001
            print("FETCH-ERR", item["slug"], type(exc).__name__, exc)
            time.sleep(1.0)
            continue
        path = os.path.join(OUTDIR, item["slug"] + ".txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        index.append({
            "slug": item["slug"],
            "title": title,
            "text": item["text"],
            "section": item["section"],
            "people": item.get("people", []),
            "file": "sources/raw/wikisource/" + item["slug"] + ".txt",
            "source_url": page_url(title),
            "revision": rev,
            "chars": len(text),
        })
        print("FETCHED  ", item["slug"], "%d chars" % len(text))
        time.sleep(1.5)
    if not probe_only:
        with open(INDEX, "w", encoding="utf-8") as fh:
            json.dump(index, fh, ensure_ascii=False, indent=2)
        print("wrote", INDEX, "with", len(index), "chapters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
