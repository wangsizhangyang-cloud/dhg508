"""Build chinese_generals.db from data/ (curated rows) + sources index.

Growable by design: drop another JSON file with the same shape into
data/generals/ and rerun this script. Existing rows keep their keys, so old
rows are not broken.

Usage:
    python code/build_db.py
"""
import glob
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "chinese_generals.db")
DATA = os.path.join(ROOT, "data")
INDEX = os.path.join(ROOT, "sources", "raw", "wikisource_index.json")

SCHEMA = """
DROP VIEW IF EXISTS generals_view;
DROP VIEW IF EXISTS battle_roles_view;
DROP TABLE IF EXISTS conversions;
DROP TABLE IF EXISTS general_battles;
DROP TABLE IF EXISTS titles;
DROP TABLE IF EXISTS battles;
DROP TABLE IF EXISTS generals;
DROP TABLE IF EXISTS states;
DROP TABLE IF EXISTS dynasties;
DROP TABLE IF EXISTS calendar;

CREATE TABLE dynasties (
    id            INTEGER PRIMARY KEY,
    key           TEXT UNIQUE NOT NULL,
    name_chn      TEXT NOT NULL,
    name_original TEXT,
    period_note   TEXT,
    source        TEXT NOT NULL,
    source_locator TEXT,
    source_url    TEXT,
    note          TEXT
);

CREATE TABLE states (
    id            INTEGER PRIMARY KEY,
    key           TEXT UNIQUE NOT NULL,
    name_chn      TEXT NOT NULL,
    name_original TEXT,
    dynasty_id    INTEGER NOT NULL REFERENCES dynasties(id),
    source        TEXT NOT NULL,
    source_locator TEXT,
    source_url    TEXT,
    note          TEXT
);

CREATE TABLE generals (
    id            INTEGER PRIMARY KEY,
    key           TEXT UNIQUE NOT NULL,
    name_chn      TEXT NOT NULL,
    name_original TEXT,
    courtesy_name TEXT,
    state_id      INTEGER NOT NULL REFERENCES states(id),
    dynasty_id    INTEGER NOT NULL REFERENCES dynasties(id),
    born_raw      TEXT,
    born_year     INTEGER,
    died_raw      TEXT,
    died_year     INTEGER,
    achievement   TEXT,
    description   TEXT,
    source        TEXT NOT NULL,
    source_locator TEXT,
    source_url    TEXT,
    source_quote  TEXT,
    note          TEXT
);

CREATE TABLE battles (
    id            INTEGER PRIMARY KEY,
    key           TEXT,
    name_chn      TEXT NOT NULL,
    name_original TEXT,
    year          INTEGER,
    year_raw      TEXT,
    place         TEXT,
    source        TEXT NOT NULL,
    source_locator TEXT,
    source_url    TEXT,
    source_quote  TEXT,
    note          TEXT,
    UNIQUE(name_chn, year, year_raw)
);

CREATE TABLE general_battles (
    id            INTEGER PRIMARY KEY,
    general_id    INTEGER NOT NULL REFERENCES generals(id),
    battle_id     INTEGER NOT NULL REFERENCES battles(id),
    role          TEXT,
    outcome       TEXT,
    source        TEXT NOT NULL,
    source_locator TEXT,
    source_url    TEXT,
    source_quote  TEXT,
    note          TEXT,
    UNIQUE(general_id, battle_id)
);

CREATE TABLE titles (
    id            INTEGER PRIMARY KEY,
    general_id    INTEGER NOT NULL REFERENCES generals(id),
    title_chn     TEXT NOT NULL,
    title_original TEXT,
    period        TEXT,
    source        TEXT NOT NULL,
    source_locator TEXT,
    source_url    TEXT,
    source_quote  TEXT,
    note          TEXT
);

CREATE TABLE conversions (
    id            INTEGER PRIMARY KEY,
    entity_type   TEXT NOT NULL,
    entity_key    TEXT NOT NULL,
    field         TEXT NOT NULL,
    original      TEXT,
    normalized    TEXT,
    rule          TEXT NOT NULL,
    source        TEXT NOT NULL,
    source_locator TEXT,
    source_url    TEXT,
    note          TEXT
);

CREATE TABLE calendar (
    id            INTEGER PRIMARY KEY,
    state_key     TEXT,
    system        TEXT NOT NULL,
    source        TEXT NOT NULL,
    source_locator TEXT,
    source_url    TEXT,
    note          TEXT
);

CREATE INDEX idx_generals_state ON generals(state_id);
CREATE INDEX idx_generals_dynasty ON generals(dynasty_id);
CREATE INDEX idx_titles_general ON titles(general_id);
CREATE INDEX idx_gb_general ON general_battles(general_id);
CREATE INDEX idx_gb_battle ON general_battles(battle_id);
CREATE INDEX idx_battles_year ON battles(year);

CREATE VIEW generals_view AS
SELECT g.id, g.key, g.name_chn, g.name_original, g.courtesy_name,
       s.name_chn AS state, d.name_chn AS dynasty,
       g.born_raw, g.born_year, g.died_raw, g.died_year,
       g.achievement, g.description,
       g.source, g.source_locator, g.source_url, g.source_quote, g.note
FROM generals g JOIN states s ON s.id = g.state_id
                JOIN dynasties d ON d.id = g.dynasty_id;

CREATE VIEW battle_roles_view AS
SELECT gb.id, g.name_chn AS general, b.name_chn AS battle, b.year, b.year_raw,
       b.place, gb.role, gb.outcome,
       gb.source, gb.source_locator, gb.source_url, gb.source_quote, gb.note
FROM general_battles gb JOIN generals g ON g.id = gb.general_id
                        JOIN battles b ON b.id = gb.battle_id;
"""


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    with open(INDEX, encoding="utf-8") as fh:
        index = {row["slug"]: row for row in json.load(fh)}

    def src(slug):
        row = index.get(slug)
        if not row:
            return ("《" + slug + "》", "", "")
        return ("《" + row["text"] + "》", row.get("section", ""), row.get("source_url", ""))

    dynasties = load_json(os.path.join(DATA, "reference", "dynasties.json"))
    states = load_json(os.path.join(DATA, "reference", "states.json"))
    calendar = load_json(os.path.join(DATA, "reference", "calendar.json"))
    cal = {c["state_key"]: c for c in calendar}

    general_files = sorted(glob.glob(os.path.join(DATA, "generals", "*.json")))
    generals = []
    for path in general_files:
        generals.extend(load_json(path)["generals"])
    keys = [g["key"] for g in generals]
    if len(keys) != len(set(keys)):
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        raise SystemExit("duplicate general keys: %s" % dupes)

    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)

    state_dynasty = {s["key"]: s["dynasty_key"] for s in states}
    state_ids, dynasty_ids = {}, {}
    for i, d in enumerate(dynasties, 1):
        doc, sec, url = src(d["source_slug"])
        conn.execute("INSERT INTO dynasties(id,key,name_chn,name_original,period_note,source,source_locator,source_url,note)"
                     " VALUES(?,?,?,?,?,?,?,?,?)",
                     (i, d["key"], d["name_chn"], d.get("name_original", ""), d.get("period_note", ""),
                      doc, sec, url, d.get("note", "")))
        dynasty_ids[d["key"]] = i
    for i, s in enumerate(states, 1):
        doc, sec, url = src(s["source_slug"])
        conn.execute("INSERT INTO states(id,key,name_chn,name_original,dynasty_id,source,source_locator,source_url,note)"
                     " VALUES(?,?,?,?,?,?,?,?,?)",
                     (i, s["key"], s["name_chn"], s.get("name_original", ""),
                      dynasty_ids[s["dynasty_key"]], doc, sec, url, s.get("note", "")))
        state_ids[s["key"]] = i
    for i, c in enumerate(calendar, 1):
        doc, sec, url = src(c["source_slug"])
        conn.execute("INSERT INTO calendar(id,state_key,system,source,source_locator,source_url,note)"
                     " VALUES(?,?,?,?,?,?,?)",
                     (i, c["state_key"], c["system"], doc, sec, url, c.get("note", "")))

    for g in generals:
        if g["state_key"] not in state_ids:
            raise SystemExit("unknown state_key %r for general %r" % (g["state_key"], g["key"]))

    battle_ids = {}
    gid = bid = tcount = ccount = 0
    for g in generals:
        gid += 1
        st = g["state_key"]
        doc, sec, url = src(g["source_slug"])
        conn.execute(
            "INSERT INTO generals(id,key,name_chn,name_original,courtesy_name,state_id,dynasty_id,"
            "born_raw,born_year,died_raw,died_year,achievement,description,source,source_locator,source_url,source_quote,note)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (gid, g["key"], g["name_norm"], g.get("name_original", ""), g.get("courtesy_name", ""),
             state_ids[st], dynasty_ids[state_dynasty[st]],
             g.get("born_raw", ""), g.get("born_year"), g.get("died_raw", ""), g.get("died_year"),
             g.get("achievement", ""), g.get("description", ""),
             doc, g.get("source_locator", sec), url, g.get("source_quote", ""), g.get("note", "")))

        for t in g.get("titles", []):
            tcount += 1
            tdoc, tsec, turl = src(t["source_slug"])
            conn.execute(
                "INSERT INTO titles(general_id,title_chn,title_original,period,source,source_locator,source_url,source_quote,note)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (gid, t["title_norm"], t.get("title_original", t["title_norm"]), t.get("period", ""),
                 tdoc, t.get("source_locator", tsec), turl, t.get("source_quote", ""), t.get("note", "")))

        for b in g.get("battles", []):
            identity = (b["name_norm"], b.get("year"), b.get("year_raw", ""))
            if identity not in battle_ids:
                bid += 1
                bdoc, bsec, burl = src(b["source_slug"])
                conn.execute(
                    "INSERT INTO battles(id,key,name_chn,name_original,year,year_raw,place,source,source_locator,source_url,source_quote,note)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (bid, b.get("key", ""), b["name_norm"], b.get("name_original", ""),
                     b.get("year"), b.get("year_raw", ""), b.get("place", ""),
                     bdoc, b.get("source_locator", bsec), burl, b.get("source_quote", ""), b.get("note", "")))
                battle_ids[identity] = bid
            b_id = battle_ids[identity]
            bdoc, bsec, burl = src(b["source_slug"])
            conn.execute(
                "INSERT OR IGNORE INTO general_battles(general_id,battle_id,role,outcome,source,source_locator,source_url,source_quote,note)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (gid, b_id, b.get("role", ""), b.get("outcome", ""),
                 bdoc, b.get("source_locator", bsec), burl, b.get("source_quote", ""), b.get("note", "")))

    for g in generals:
        sysrule = cal.get(g["state_key"], {}).get("system", "以史書所載紀年直接對應。")
        doc, sec, url = src(g["source_slug"])
        for field, raw, year in (("born", g.get("born_raw", ""), g.get("born_year")),
                                 ("died", g.get("died_raw", ""), g.get("died_year"))):
            if not raw and year is None:
                continue
            ccount += 1
            rule = sysrule if year is not None else "原文未載明確年代，不作數字換算，保留原文。"
            conn.execute(
                "INSERT INTO conversions(entity_type,entity_key,field,original,normalized,rule,source,source_locator,source_url,note)"
                " VALUES(?,?,?,?,?,?,?,?,?,?)",
                ("general", g["key"], field, raw, "" if year is None else str(year),
                 rule, doc, g.get("source_locator", sec), url, g.get("note", "")))
        if g.get("name_original") and g["name_original"] != g["name_norm"]:
            ccount += 1
            conn.execute(
                "INSERT INTO conversions(entity_type,entity_key,field,original,normalized,rule,source,source_locator,source_url,note)"
                " VALUES(?,?,?,?,?,?,?,?,?,?)",
                ("general", g["key"], "name", g["name_original"], g["name_norm"],
                 "以史書列傳標目／常用名為標準名（normalized），原名保留於 original，不改字。",
                 doc, g.get("source_locator", sec), url, ""))

    for b in conn.execute("SELECT id,key,name_chn,year,year_raw,source,source_locator,source_url,note FROM battles"):
        if b[3] is None and not b[4]:
            continue
        ccount += 1
        rule = "以史書所載紀年（year_raw）對應公元（year，負數為公元前）；具體換算基準見 calendar 表。"
        conn.execute(
            "INSERT INTO conversions(entity_type,entity_key,field,original,normalized,rule,source,source_locator,source_url,note)"
            " VALUES(?,?,?,?,?,?,?,?,?,?)",
            ("battle", b[1] or b[2], "year", b[4], "" if b[3] is None else str(b[3]),
             rule, b[5], b[6], b[7], b[8]))

    conn.commit()
    counts = {}
    for name in ("dynasties", "states", "general_battles", "battles", "titles", "generals", "conversions", "calendar"):
        counts[name] = conn.execute("SELECT COUNT(*) FROM %s" % name).fetchone()[0]
    total = sum(counts.values())
    conn.close()
    print("built", DB)
    for k in ("dynasties", "states", "generals", "battles", "general_battles", "titles", "conversions", "calendar"):
        print("  %-16s %d" % (k, counts[k]))
    print("  TOTAL ROWS       %d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
