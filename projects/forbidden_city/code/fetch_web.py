"""Fetch the DPM / Baidu pages used for 角楼 and 钦安殿 as grounding originals."""
import os
import re
import urllib.request

UA = "Mozilla/5.0 (compatible; ForbiddenCityResearch/1.0)"
OUT = "sources/raw/web"

PAGES = [
    ("dpm-jiaolou", "https://www.dpm.org.cn/explore/building/236522.html"),
    ("dpm-qinandian", "https://www.dpm.org.cn/explore/building/236494.html"),
    ("dpm-qinandian-daochang", "https://www.dpm.org.cn/subject_600/buildingdetails/253790.html"),
    ("baidu-qinandian", "https://baike.baidu.com/item/%E9%92%A6%E5%AE%89%E6%AE%BF/7849864"),
]


def strip_html(html):
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;?", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, url in PAGES:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode("utf-8", "replace")
            text = strip_html(raw)
            path = os.path.join(OUT, name + ".txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(name, len(text))
        except Exception as exc:  # noqa: BLE001
            print("FAIL", name, exc)


if __name__ == "__main__":
    main()
