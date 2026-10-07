"""Build shiji_people.db from data/extracted/ (+ optional data/manual/).

Growable by design: adding a new chapter only means rerunning
fetch_sources.py -> extract.py -> build_db.py.  Rows are keyed, so old rows are
kept and new ones appended.  Hand corrections go into data/manual/*.json and
override by key/slug; they never delete generated rows.

Schema: 7 tables, 6 foreign keys, 2 read views.  Every fact row carries
`source` (the book) + `source_locator` (卷/篇, i.e. the page) + a verbatim
`source_quote`, plus a `note` for anything uncertain.

Usage:
    python code/build_db.py
"""
import glob
import json
import os
import re
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

from opencc import OpenCC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "shiji_people.db")
PROC = os.path.join(ROOT, "sources", "processed")
EXT = os.path.join(ROOT, "data", "extracted")
MAN = os.path.join(ROOT, "data", "manual")

CC = OpenCC("hk2s")
VARIANT = {"髙": "高", "愼": "慎", "眛": "昧", "皙": "晰", "竫": "靖",
           "郞": "郎", "敎": "教", "衞": "卫"}


def to_simp(s):
    return CC.convert("".join(VARIANT.get(c, c) for c in s))


CN = {"元": 1, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
      "八": 8, "九": 9, "十": 10, "百": 100}

YEAR_RULE = ("提取「紀年主體＋年序」為結構化紀年（如『昭王十三年』→『昭王13年』）；"
             "不換算公元，因史書紀年與公元之對應須專門考訂，本庫不臆斷。")
NAME_RULE = "OpenCC hk2s 繁→簡並統一少數異體字，得到標準名；原文名不改，另存 name_original。"
MANUAL_RULE = "手工校訂：以常用名為標準名；史書標題原字保留於 name_original 與 source_locator。"

SCHEMA = """
DROP VIEW IF EXISTS persons_view;
DROP VIEW IF EXISTS chapter_people_view;
DROP TABLE IF EXISTS conversions;
DROP TABLE IF EXISTS relations;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS offices;
DROP TABLE IF EXISTS person_chapters;
DROP TABLE IF EXISTS persons;
DROP TABLE IF EXISTS chapters;

CREATE TABLE chapters (
    id             INTEGER PRIMARY KEY,
    slug           TEXT UNIQUE NOT NULL,
    juan           INTEGER NOT NULL,
    category       TEXT,                  -- 本紀 / 世家 / 列傳 ...
    title_original TEXT NOT NULL,         -- 「卷七十三 白起王翦列傳 第十三」
    title_chn      TEXT,
    source         TEXT NOT NULL,         -- 《史記》
    source_locator TEXT NOT NULL,         -- 史記·卷七十三白起王翦列傳第十三
    source_url     TEXT,
    pageid         INTEGER,
    revision       INTEGER,
    note           TEXT
);

CREATE TABLE persons (
    id              INTEGER PRIMARY KEY,
    key             TEXT UNIQUE NOT NULL,
    name_chn        TEXT NOT NULL,
    name_original   TEXT NOT NULL,
    heading_original TEXT,
    alt_names       TEXT,
    category        TEXT,
    origin_raw      TEXT,
    description     TEXT,
    source          TEXT NOT NULL,
    source_locator  TEXT NOT NULL,
    source_url      TEXT,
    source_quote    TEXT,
    note            TEXT
);

CREATE TABLE person_chapters (
    id             INTEGER PRIMARY KEY,
    person_id      INTEGER NOT NULL REFERENCES persons(id),
    chapter_id     INTEGER NOT NULL REFERENCES chapters(id),
    relation_kind  TEXT NOT NULL,          -- 本傳 / 提及
    source         TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    source_url     TEXT,
    source_quote   TEXT,
    note           TEXT,
    UNIQUE(person_id, chapter_id)
);

CREATE TABLE offices (
    id             INTEGER PRIMARY KEY,
    person_id      INTEGER NOT NULL REFERENCES persons(id),
    title_chn      TEXT NOT NULL,
    title_original TEXT,
    period_raw     TEXT,
    period_norm    TEXT,
    source         TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    source_url     TEXT,
    source_quote   TEXT,
    note           TEXT
);

CREATE TABLE events (
    id             INTEGER PRIMARY KEY,
    person_id      INTEGER NOT NULL REFERENCES persons(id),
    event_type     TEXT NOT NULL,
    year_raw       TEXT,
    year_norm      TEXT,
    place          TEXT,
    description    TEXT,
    source         TEXT NOT NULL,
    source_locator TEXT NOT NULL,
    source_url     TEXT,
    source_quote   TEXT,
    note           TEXT
);

CREATE TABLE relations (
    id                INTEGER PRIMARY KEY,
    person_id         INTEGER NOT NULL REFERENCES persons(id),
    related_name      TEXT NOT NULL,
    related_person_id INTEGER REFERENCES persons(id),
    relation_type     TEXT NOT NULL,
    source            TEXT NOT NULL,
    source_locator    TEXT NOT NULL,
    source_url        TEXT,
    source_quote      TEXT,
    note              TEXT
);

CREATE TABLE conversions (
    id             INTEGER PRIMARY KEY,
    entity_type    TEXT NOT NULL,
    entity_key     TEXT NOT NULL,
    field          TEXT NOT NULL,
    original       TEXT,
    normalized     TEXT,
    rule           TEXT NOT NULL,
    source         TEXT NOT NULL,
    source_locator TEXT,
    note           TEXT
);

CREATE INDEX idx_pc_person ON person_chapters(person_id);
CREATE INDEX idx_pc_chapter ON person_chapters(chapter_id);
CREATE INDEX idx_offices_person ON offices(person_id);
CREATE INDEX idx_events_person ON events(person_id);
CREATE INDEX idx_relations_person ON relations(person_id);
CREATE INDEX idx_persons_name ON persons(name_chn);

CREATE VIEW persons_view AS
SELECT p.id, p.key, p.name_chn, p.name_original, p.alt_names, p.category,
       p.origin_raw, p.description,
       c.title_chn AS chapter, c.juan,
       p.source, p.source_locator, p.source_url, p.source_quote, p.note
FROM persons p
LEFT JOIN person_chapters pc ON pc.person_id = p.id AND pc.relation_kind = '本傳'
LEFT JOIN chapters c ON c.id = pc.chapter_id;

CREATE VIEW chapter_people_view AS
SELECT c.juan, c.title_chn AS chapter, p.name_chn AS person,
       pc.relation_kind, pc.source_locator
FROM person_chapters pc
JOIN persons p ON p.id = pc.person_id
JOIN chapters c ON c.id = pc.chapter_id;
"""


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def cn_num(s):
    if not s:
        return ""
    if s.isdigit():
        return s
    if "百" in s:
        a, _, b = s.partition("百")
        return str((CN.get(a, 1) or 1) * 100 + (int(cn_num(b)) if b else 0))
    total = 0
    if s.startswith("十"):
        total, s = 10, s[1:]
    elif "十" in s:
        a, _, b = s.partition("十")
        total = CN.get(a, 1) * 10
        s = b
    for ch in s:
        if ch in CN and CN[ch] < 10:
            total += CN[ch]
        else:
            return ""
    return str(total)


def norm_year(raw):
    """『昭王十三年』->『昭王13年』（保留主體，年序轉阿拉伯數字）。"""
    m = re.match(r"^([\u4e00-\u9fff]{1,6}?)(元|[一二三四五六七八九十百]{1,3}|\d{1,3})年$", raw)
    if not m:
        return raw
    num = cn_num(m.group(2))
    return "%s%s年" % (m.group(1), num) if num else raw


def main():
    chapters = load(os.path.join(EXT, "chapters.json"))
    persons = load(os.path.join(EXT, "persons.json"))

    manual_persons = []
    if os.path.isdir(MAN):
        for path in sorted(glob.glob(os.path.join(MAN, "*.json"))):
            doc = load(path)
            manual_persons.extend(doc.get("persons", []))
    manual_by_key = {p["key"]: p for p in manual_persons}
    manual_keys = set(manual_by_key)
    for p in persons:
        if p["key"] in manual_by_key:
            p.update(manual_by_key.pop(p["key"]))
    persons.extend(manual_by_key.values())

    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)

    chapter_id = {}
    for i, c in enumerate(chapters, 1):
        chapter_id[c["slug"]] = i
        conn.execute(
            "INSERT INTO chapters(id,slug,juan,category,title_original,title_chn,"
            "source,source_locator,source_url,pageid,revision,note)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (i, c["slug"], c["juan"], c["category"], c["title_original"],
             to_simp(c["title_original"]), "《史記》", c["source_locator"],
             c["source_url"], c.get("pageid"), c.get("revision"),
             "本卷為《史記》卷篇之一；正文由中文維基文庫轉錄，見 source_url 與 revision。"))

    pid = 0
    name_to_pid = {}
    for p in persons:
        pid += 1
        chapter_id_of = chapter_id.get(p["chapter_slug"])
        note = p.get("note", "")
        if p.get("origin_raw"):
            note = (note + " " if note else "") + "籍貫原文「%s」，未改字。" % p["origin_raw"]
        conn.execute(
            "INSERT INTO persons(id,key,name_chn,name_original,heading_original,"
            "alt_names,category,origin_raw,description,source,source_locator,"
            "source_url,source_quote,note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (pid, p["key"], p["name_chn"], p["name_original"], p.get("heading_original", ""),
             p.get("alt_names", ""), p.get("category", ""), p.get("origin_raw", ""),
             p.get("description", ""), p.get("source", "《史記》"),
             p["source_locator"], p["source_url"], p.get("source_quote", ""), note))
        name_to_pid.setdefault(p["name_chn"], pid)
        if chapter_id_of:
            conn.execute(
                "INSERT OR IGNORE INTO person_chapters(person_id,chapter_id,relation_kind,"
                "source,source_locator,source_url,source_quote,note)"
                " VALUES(?,?,?,?,?,?,?,?)",
                (pid, chapter_id_of, "本傳", p.get("source", "《史記》"),
                 p["source_locator"], p["source_url"], p.get("source_quote", ""),
                 "本傳（列傳／世家／本紀）之人物小節。"))

        for o in p.get("offices", []):
            raw = o.get("period_raw", "")
            conn.execute(
                "INSERT INTO offices(person_id,title_chn,title_original,period_raw,"
                "period_norm,source,source_locator,source_url,source_quote,note)"
                " VALUES(?,?,?,?,?,?,?,?,?,?)",
                (pid, to_simp(o["title_original"]), o["title_original"], raw,
                 norm_year(raw) if raw else "", p.get("source", "《史記》"),
                 p["source_locator"], p["source_url"], o["source_quote"],
                 "同一小句內含本傳人名與職官，按職官詞表抽取；句中所涉他人不另區分。"))
        for e in p.get("events", []):
            raw = e.get("year_raw", "")
            conn.execute(
                "INSERT INTO events(person_id,event_type,year_raw,year_norm,place,"
                "description,source,source_locator,source_url,source_quote,note)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (pid, e["event_type"], raw, norm_year(raw) if raw else "", "",
                 e.get("description", ""), p.get("source", "《史記》"),
                 p["source_locator"], p["source_url"], e["source_quote"],
                 "該句含本傳人名，按動詞詞表歸類；句中所涉他人不另區分。"))
        for r in p.get("relations", []):
            rel_pid = name_to_pid.get(to_simp(r["related_name"]))
            conn.execute(
                "INSERT INTO relations(person_id,related_name,related_person_id,"
                "relation_type,source,source_locator,source_url,source_quote,note)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (pid, to_simp(r["related_name"]), rel_pid, r["relation_type"],
                 p.get("source", "《史記》"), p["source_locator"], p["source_url"],
                 r["source_quote"], "同句含本傳人名；關係方向以原文為準。"
                 + ("" if rel_pid else " 所涉親屬未單列為本庫人物。")))

    # 提及: link every person to every chapter whose text names them.
    text_cache = {}
    linked = 0
    for p in persons:
        name = p["name_chn"]
        orig = p["name_original"]
        if len(orig) < 2 and orig not in set("禹啓舜堯湯紂桀"):
            continue
        for c in chapters:
            slug = c["slug"]
            if slug == p["chapter_slug"]:
                continue
            if slug not in text_cache:
                with open(os.path.join(PROC, slug + ".txt"), encoding="utf-8") as fh:
                    text_cache[slug] = fh.read()
            if name in text_cache[slug] or orig in text_cache[slug]:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO person_chapters(person_id,chapter_id,"
                    "relation_kind,source,source_locator,source_url,source_quote,note)"
                    " VALUES(?,?,?,?,?,?,?,?)",
                    (name_to_pid[p["name_chn"]], chapter_id[slug], "提及", "《史記》",
                     c["source_locator"], c["source_url"], "", "本篇正文提及此人。"))
                linked += cur.rowcount

    # conversions: every name, era-date and office-title normalisation we did.
    ccount = 0
    for p in persons:
        if p["name_chn"] != p["name_original"]:
            ccount += 1
            conn.execute(
                "INSERT INTO conversions(entity_type,entity_key,field,original,"
                "normalized,rule,source,source_locator,note) VALUES(?,?,?,?,?,?,?,?,?)",
                ("person", p["key"], "name", p["name_original"], p["name_chn"],
                 MANUAL_RULE if p["key"] in manual_keys else NAME_RULE,
                 "《史記》", p["source_locator"], ""))
    for row in conn.execute("SELECT id,year_raw,year_norm,source,source_locator "
                            "FROM events WHERE year_raw<>''"):
        ccount += 1
        conn.execute(
            "INSERT INTO conversions(entity_type,entity_key,field,original,"
            "normalized,rule,source,source_locator,note) VALUES(?,?,?,?,?,?,?,?,?)",
            ("event", "event:%d" % row[0], "year", row[1], row[2], YEAR_RULE,
             row[3], row[4], "未換算公元。"))
    for row in conn.execute("SELECT id,period_raw,period_norm,source,source_locator "
                            "FROM offices WHERE period_raw<>''"):
        ccount += 1
        conn.execute(
            "INSERT INTO conversions(entity_type,entity_key,field,original,"
            "normalized,rule,source,source_locator,note) VALUES(?,?,?,?,?,?,?,?,?)",
            ("office", "office:%d" % row[0], "period", row[1], row[2], YEAR_RULE,
             row[3], row[4], "未換算公元。"))
    for row in conn.execute("SELECT id,title_chn,title_original,source,source_locator "
                            "FROM offices WHERE title_chn<>title_original"):
        ccount += 1
        conn.execute(
            "INSERT INTO conversions(entity_type,entity_key,field,original,"
            "normalized,rule,source,source_locator,note) VALUES(?,?,?,?,?,?,?,?,?)",
            ("office", "office:%d" % row[0], "title", row[2], row[1], NAME_RULE,
             row[3], row[4], "職官名繁簡／異體轉換。"))

    conn.commit()
    counts = {}
    for t in ("chapters", "persons", "person_chapters", "offices", "events",
              "relations", "conversions"):
        counts[t] = conn.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
    total = sum(counts.values())
    fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    conn.close()

    print("built", DB)
    for t in ("chapters", "persons", "person_chapters", "offices", "events",
              "relations", "conversions"):
        print("  %-16s %d" % (t, counts[t]))
    print("  %-16s %d" % ("TOTAL ROWS", total))
    print("  mention links    %d" % linked)
    print("  FK violations    %d" % len(fk_violations))
    return 1 if fk_violations else 0


if __name__ == "__main__":
    sys.exit(main())
