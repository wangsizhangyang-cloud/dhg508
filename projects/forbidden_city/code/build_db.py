"""Build the SQLite database from buildings.json + records.json."""
import json
import os
import sqlite3
import sys

BUILDINGS = "buildings.json"
RECORDS = "records.json"
DB = "forbidden_city.db"

SCHEMA = """
DROP VIEW IF EXISTS facts_view;
DROP TABLE IF EXISTS facts;
DROP TABLE IF EXISTS buildings;

CREATE TABLE buildings (
    id                 INTEGER PRIMARY KEY,
    key                TEXT UNIQUE,
    name_chn           TEXT NOT NULL,
    name_eng           TEXT NOT NULL,
    type               TEXT,
    image              TEXT,
    image_commons_title TEXT,
    image_source       TEXT,
    image_artist       TEXT,
    image_license      TEXT,
    image_note         TEXT,
    note               TEXT
);

CREATE TABLE facts (
    id             INTEGER PRIMARY KEY,
    building_id    INTEGER NOT NULL REFERENCES buildings(id),
    year           INTEGER,
    date           TEXT,
    fact           TEXT NOT NULL,
    people         TEXT,
    place          TEXT,
    source         TEXT NOT NULL,
    source_url     TEXT,
    source_locator TEXT,
    note           TEXT
);

CREATE INDEX idx_facts_building ON facts(building_id);
CREATE INDEX idx_facts_year ON facts(year);

CREATE VIEW facts_view AS
SELECT f.id,
       b.name_chn AS building,
       b.name_eng AS building_eng,
       f.year, f.date, f.fact, f.people, f.place,
       f.source, f.source_url, f.source_locator, f.note
FROM facts f JOIN buildings b ON b.id = f.building_id;
"""


def main():
    with open(BUILDINGS, encoding="utf-8") as fh:
        buildings = json.load(fh)
    with open(RECORDS, encoding="utf-8") as fh:
        records = json.load(fh)

    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)

    conn.executemany(
        """INSERT INTO buildings
           (id, key, name_chn, name_eng, type, image, image_commons_title,
            image_source, image_artist, image_license, image_note, note)
           VALUES (:id, :key, :name_chn, :name_eng, :type, :image,
                   :image_commons_title, :image_source, :image_artist,
                   :image_license, :image_note, :note)""",
        [{
            "id": b["id"], "key": b["key"], "name_chn": b["name_chn"],
            "name_eng": b["name_eng"], "type": b.get("type", ""),
            "image": b.get("image", ""),
            "image_commons_title": b.get("image_commons_title", ""),
            "image_source": b.get("image_source", ""),
            "image_artist": b.get("image_artist", ""),
            "image_license": b.get("image_license", ""),
            "image_note": b.get("image_note", ""),
            "note": b.get("note", ""),
        } for b in buildings],
    )

    conn.executemany(
        """INSERT INTO facts
           (id, building_id, year, date, fact, people, place,
            source, source_url, source_locator, note)
           VALUES (:id, :building_id, :year, :date, :fact, :people, :place,
                   :source, :source_url, :source_locator, :note)""",
        [{
            "id": r["id"], "building_id": r["building_id"], "year": r["year"],
            "date": r["date"], "fact": r["fact"], "people": r.get("people", ""),
            "place": r.get("place", ""), "source": r["source"],
            "source_url": r.get("source_url", ""),
            "source_locator": r.get("source_locator", ""),
            "note": r.get("note", ""),
        } for r in records],
    )
    conn.commit()

    nb = conn.execute("SELECT COUNT(*) FROM buildings").fetchone()[0]
    nf = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    conn.close()
    print(f"built {DB}: {nb} buildings, {nf} fact rows")


if __name__ == "__main__":
    sys.exit(main())
