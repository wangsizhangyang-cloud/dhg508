"""Turn the raw 《史記》 wikitext into growable, source-stamped rows.

Pipeline (idempotent; rerunning after adding chapters does the same steps):

    sources/raw/wikisource/shiji-NNN.wiki   (verbatim chapter)
        -> sources/processed/shiji-NNN.txt  (cleaned classical text)
        -> data/extracted/chapters.json     (one row per 卷)
        -> data/extracted/persons.json      (one nested record per 人物 section,
                                             with offices / events / relations)

Rules are deliberately transparent and printed at the end so a reader can see
exactly how each column was produced.  Every generated fact carries a verbatim
`source_quote` (a substring of the cleaned chapter) so verify.py can re-check it.

Usage:
    python code/extract.py
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

from opencc import OpenCC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "sources", "raw", "wikisource")
PROC = os.path.join(ROOT, "sources", "processed")
INDEX = os.path.join(ROOT, "sources", "raw", "sources_index.json")
OUT = os.path.join(ROOT, "data", "extracted")

CC = OpenCC("hk2s")
# rare/variant forms the converter leaves alone (seen in Wikisource headings)
VARIANT = {"髙": "高", "愼": "慎", "眛": "昧", "皙": "晰", "竫": "靖",
           "郞": "郎", "敎": "教", "衞": "卫"}


def to_simp(s):
    return CC.convert("".join(VARIANT.get(c, c) for c in s))


CATEGORY = {}
for _j in range(1, 13):
    CATEGORY[_j] = "本紀"
for _j in range(13, 23):
    CATEGORY[_j] = "表"
for _j in range(23, 31):
    CATEGORY[_j] = "書"
for _j in range(31, 61):
    CATEGORY[_j] = "世家"
for _j in range(61, 131):
    CATEGORY[_j] = "列傳"

# Section headings that are commentary/group labels, not people.
BLACKLIST = {
    "論", "評論", "评论", "贊", "索隱述贊", "太史公曰", "太史公論", "太史公自序",
    "校勘記", "校勘", "注釋", "註釋", "序", "序言", "目錄", "史論", "司馬遷評",
    "褚先生補", "正義", "結語", "其他弟子", "斠勘", "總結", "九世亂", "卜", "命曰",
    "此", "後論", "陳", "杞", "神龜出於江水", "周朝", "漢朝", "齊王", "廣陵王", "燕王",
}
SKIP_CONTAINS = [
    "至", "以降", "之後", "死後", "先祖", "稱王前", "諸王", "太史公", "序", "贊",
    "論", "評論", "校勘", "注釋", "註釋", "目錄", "正義", "結語", "其他弟子",
    "校吏", "裨將", "索引",
]
TITLES = [
    "丞相", "相國", "國相", "令尹", "太宰", "上將軍", "大將軍", "將軍", "裨將", "都尉",
    "校尉", "中尉", "太尉", "廷尉", "郡守", "太守", "縣令", "縣尉", "御史",
    "中大夫", "諫大夫", "大夫", "郎中", "中郎", "侍郎", "侍中", "太傅", "少傅",
    "太子太傅", "司馬", "內史", "左庶長", "右庶長", "左更", "中更", "右更",
    "大良造", "國尉", "客卿", "上卿", "上大夫", "中庶子", "太僕", "郡尉", "左徒",
    "柱國", "執珪", "公乘", "庶長",
]

RE_ERA = re.compile(r"([\u4e00-\u9fff]{1,6}?)(元|二|三|四|五|六|七|八|九|十|"
                    r"[一二三四五六七八九十百]{1,3}|\d{1,3})年")
RE_DEATH = re.compile(r"死|卒|薨|自殺|自剄|伏劍|伏誅|見殺|被殺|崩|弑|誅")
RE_BATTLE = re.compile(r"伐|攻|擊|圍|破|敗|拔|戰|取|降|滅|克|大破|敗走|擊破")
RE_APPOINT = re.compile(r"為|拜|封|遷|立為|以為")
RE_OFFICE = re.compile(r"為([^，。所]{1,4}?(?:君|侯|王|公))")
RE_REL = re.compile(r"之(子|孫|弟|兄|父|叔|伯|從父|兄子|少子|長子|女|母)")
STOPNAME = set("而亦以於于其與及爲为是故乃所生立讓让辭辞辟皆從从見见殺杀曰也之"
               "使封言求臣昔本國国請请謂谓告令召聞闻知欲能敢可後后前今此")
SINGLE_CHAR_OK = set("禹啓舜堯湯紂桀羿嚳契益稷")
LEAD_STOP = set("我吾予其爾汝而乃公君先今是夫且然故")

DROP_TEMPLATES = {
    "wikipedia", "header2", "header", "pd-old", "textquality", "reflist",
    "footer", "lzh-wikipedia", "zh-classical-wikipedia", "alsosee", "anchor",
    "註", "注意", "原文沒有標點", "!", "*", "fact", "citation needed",
}


def _template(m):
    name = m.group(1).strip()
    body = m.group(2)
    if name.lower() in DROP_TEMPLATES:
        return ""
    first = body.split("|")[0].strip()
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", first):
        return ""
    return first


def _variant(m):
    body = m.group(1)
    if ";" in body and ":" in body:
        for key in ("zh-hans", "zh-cn", "zh"):
            for part in body.split(";"):
                k, _, v = part.partition(":")
                if k.strip() == key and v:
                    return v
        return body.split(";")[0].partition(":")[2] or body
    return body


def clean_wikitext(t):
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"<ref[^>]*/\s*>", "", t)
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    t = t.replace("{{!}}", "|")
    # -{zh:繁;zh-hans:简;zh-hant:繁}- -> simplified variant; nested markers too
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r"-\{(.*?)\}-", _variant, t, flags=re.S)
    t = t.replace("-{", "").replace("}-", "")
    # drop meta templates, keep the first argument of content templates
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r"\{\{([^{}|\n]+)\|?([^{}]*)\}\}", _template, t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)  # stray html wrappers, keep their text
    t = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    t = t.replace("'''", "").replace("''", "")
    t = re.sub(r"^\{\|.*?^\|\}", "", t, flags=re.S | re.M)
    t = t.replace("__TOC__", "")
    t = re.sub(r"\[https?://\S+\s+([^\]]+)\]", r"\1", t)
    t = re.sub(r"^----+$", "", t, flags=re.M)
    t = re.sub(r"[ \t\u00a0]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def chapter_title(raw):
    m = re.search(r"\|\s*section\s*=\s*([^\n|]+)", raw)
    return m.group(1).strip() if m else ""


def is_person_heading(h):
    h = h.strip()
    if not h or h in BLACKLIST:
        return False
    for bad in SKIP_CONTAINS:
        if bad in h:
            return False
    if re.fullmatch(r"[（(].*[）)]", h):
        return False
    return True


def split_names(h):
    """Heading -> list of (name, honorific, disambiguation)."""
    h = h.replace("-{", "").replace("}-", "").strip()
    dis = ""
    m = re.match(r"^(.*?)[（(]([^）)]*)[）)]\s*$", h)
    if m:
        h, dis = m.group(1).strip(), m.group(2).strip()
    out = []
    for part in re.split(r"[、]", h):
        part = part.strip()
        if not part:
            continue
        toks = part.split()          # splits on ASCII and U+3000 whitespace
        if len(toks) > 1:
            name, honor = toks[-1], " ".join(toks[:-1])
        else:
            name, honor = part, ""
        out.append((name, honor, dis))
    return out


def first_quote(section):
    first = re.split(r"[。]", section, maxsplit=1)[0].strip()
    if not first:
        return "", ""
    first = first.lstrip("」』）】〕 \u3000")
    quote = first + "。"
    if len(quote) > 100:
        quote = quote[:100]
    origin = ""
    m = re.search(r"[，,]([^，,。]{1,14})也", first)
    if m:
        origin = m.group(1)
    return quote, origin


def person_quote(name, body):
    """First sentence that opens with this person's name, + origin, + index."""
    sents = sentences(body)
    for i, s in enumerate(sents[:8]):
        j = s.find(name)
        if 0 <= j <= 3:
            q = s if s.endswith(("。", "！", "？")) else s + "。"
            if len(q) > 100:
                q = q[:100]
            origin = ""
            m = re.search(r"者?[，,]([^，,。]{1,14})也", s)
            if m:
                origin = m.group(1)
            return q, origin, i
    return "", "", 0


def sentences(text):
    return [s.strip().lstrip("」』）】〕")
            for s in re.split(r"(?<=[。！？])", text) if s.strip()]


def mentions(s, name):
    if name in s:
        return True
    return len(name) > 2 and name[:2] in s


def clauses(sentence):
    return [c for c in re.split(r"[，,；;：:]", sentence) if c.strip()]


def extract_person_events(name, section):
    evs = []
    for s in sentences(section):
        if not (6 <= len(s) <= 120) or not mentions(s, name):
            continue
        etype = None
        if RE_DEATH.search(s):
            etype = "卒/死"
        elif RE_APPOINT.search(s) and any(t in s for t in TITLES):
            etype = "任官"
        elif RE_OFFICE.search(s):
            etype = "封爵"
        elif RE_BATTLE.search(s):
            etype = "征伐"
        if not etype:
            continue
        era = RE_ERA.search(s)
        evs.append({
            "event_type": etype,
            "year_raw": era.group(0) if era else "",
            "description": s.strip(),
            "source_quote": s.strip(),
        })
        if len(evs) >= 8:
            break
    return evs


def extract_offices(name, section):
    offs = []
    for s in sentences(section):
        if not (6 <= len(s) <= 120) or not mentions(s, name):
            continue
        title = ""
        for cl in clauses(s):
            if not mentions(cl, name):
                continue
            m = RE_OFFICE.search(cl)
            if m:
                title = m.group(1)
            if not title:
                for t in TITLES:
                    if t in cl:
                        title = t
                        break
            if title:
                if name in title or (len(name) > 2 and name[:2] in title):
                    title = ""   # a title that merely renames the person
                else:
                    break
        if not title:
            continue
        era = RE_ERA.search(s)
        offs.append({
            "title_original": title,
            "period_raw": era.group(0) if era else "",
            "source_quote": s.strip(),
        })
        if len(offs) >= 6:
            break
    return offs


def extract_relations(name, section):
    rels = []
    strip = "".join(sorted(LEAD_STOP))
    for s in sentences(section):
        if not mentions(s, name):
            continue
        m2 = re.search(r"之(子|孫|弟|兄|父|叔|伯|少子|長子|女|母)(?:曰|名)"
                       r"([\u4e00-\u9fff]{1,4})", s)
        if m2:
            rn, rtype = m2.group(2), m2.group(1)
        else:
            m = RE_REL.search(s)
            if not m:
                continue
            j = m.start()
            k = j
            while (k > 0 and j - k < 4 and re.match(r"[\u4e00-\u9fff]", s[k - 1])
                   and s[k - 1] not in STOPNAME):
                k -= 1
            rn, rtype = s[k:j].lstrip(strip), m.group(1)
        if not rn or rn == name or to_simp(rn) == name:
            continue
        rels.append({"related_name": rn, "relation_type": rtype,
                     "source_quote": s.strip()})
        if len(rels) >= 4:
            break
    return rels


def int_to_cn(n):
    d = "零一二三四五六七八九"
    if n < 10:
        return d[n]
    if n < 20:
        return "十" + (d[n % 10] if n % 10 else "")
    if n < 100:
        return d[n // 10] + "十" + (d[n % 10] if n % 10 else "")
    h, r = n // 100, n % 100
    out = d[h] + "百"
    if r == 0:
        return out
    if r < 10:
        return out + "零" + d[r]
    return out + d[r // 10] + "十" + (d[r % 10] if r % 10 else "")


def main():
    os.makedirs(PROC, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    with open(INDEX, encoding="utf-8") as fh:
        index = json.load(fh)

    chapters = []
    persons = []
    for row in index:
        juan = row["juan"]
        slug = row["slug"]
        with open(os.path.join(ROOT, row["file"].replace("/", os.sep)), encoding="utf-8") as fh:
            raw = fh.read()
        cleaned = clean_wikitext(raw)
        with open(os.path.join(PROC, slug + ".txt"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(cleaned)

        title = clean_wikitext(chapter_title(raw)).strip()
        cat = CATEGORY.get(juan, "")
        bare = re.sub(r"^[卷巻][零一二三四五六七八九十百0-9]+\s*", "", title).strip()
        locator = "史記·卷%s%s" % (int_to_cn(juan), bare.replace(" ", ""))
        chapters.append({
            "slug": slug,
            "juan": juan,
            "category": cat,
            "title_original": title,
            "source_locator": locator,
            "source_url": row["source_url"],
            "pageid": row.get("pageid"),
            "revision": row.get("revision"),
            "chars": len(cleaned),
        })

        parts = re.split(r"^==\s*([^=\n]*?)\s*==\s*$", cleaned, flags=re.M)
        seen = set()
        idx = 0
        for i in range(1, len(parts) - 1, 2):
            heading_raw = parts[i].strip()
            body = parts[i + 1].strip()
            if not is_person_heading(heading_raw):
                continue
            for (name, honor, dis) in split_names(heading_raw):
                if not name or len(name) > 8 or name in seen:
                    continue
                seen.add(name)
                idx += 1
                quote, origin, start = person_quote(name, body)
                sents = sentences(body)
                if quote:
                    desc = "".join(sents[start:start + 3])[:150]
                else:
                    quote = body[:60]
                    desc = "".join(sents[:3])[:150]
                note = ""
                if honor:
                    note = "標題含稱號／關係詞「%s」。" % honor
                if dis:
                    note = (note + " " if note else "") + "史書標題作「%s」以區別同名。" % dis
                if not quote:
                    note = note + "同節合傳，首句未必繫於此人。"
                persons.append({
                    "key": "%s-%02d" % (slug, idx),
                    "individual": name,
                    "name_chn": to_simp(name),
                    "name_original": name,
                    "heading_original": heading_raw,
                    "alt_names": honor,
                    "category": cat,
                    "chapter_slug": slug,
                    "origin_raw": origin,
                    "description": desc,
                    "source": "《史記》",
                    "source_locator": "%s·%s" % (locator, heading_raw.replace(" ", "")),
                    "source_url": row["source_url"],
                    "source_quote": quote or body[:40],
                    "note": note,
                    "offices": extract_offices(name, body),
                    "events": extract_person_events(name, body),
                    "relations": extract_relations(name, body),
                })

    with open(os.path.join(OUT, "chapters.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(chapters, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "persons.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(persons, fh, ensure_ascii=False, indent=2)

    print("chapters      %d" % len(chapters))
    print("persons       %d" % len(persons))
    print("offices       %d" % sum(len(p["offices"]) for p in persons))
    print("events        %d" % sum(len(p["events"]) for p in persons))
    print("relations     %d" % sum(len(p["relations"]) for p in persons))
    return 0


if __name__ == "__main__":
    sys.exit(main())
