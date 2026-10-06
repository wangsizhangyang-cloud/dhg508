"""Tiny read-only helper for forbidden_city.db (standard library only).

Examples:
    python code/query.py buildings
    python code/query.py building taihedian
    python code/query.py fact 30
    python code/query.py search 火灾
    python code/query.py year 1889
"""
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = os.path.join(os.path.dirname(__file__), "..", "forbidden_city.db")


def rows(sql, args=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()


def show(rs, cols):
    for r in rs:
        print(" | ".join(f"{c}={r.get(c, '')}" for c in cols))
        print("-" * 40)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "buildings":
        show(rows("SELECT id,key,name_chn,name_eng,type,image FROM buildings ORDER BY id"),
             ["id", "name_chn", "name_eng", "type", "image"])
    elif cmd == "building":
        r = rows("SELECT * FROM buildings WHERE key=? OR name_eng LIKE ?",
                 (sys.argv[2], "%" + sys.argv[2] + "%"))
        show(r, ["id", "name_chn", "name_eng", "type", "image", "image_source",
                 "image_artist", "image_license"])
        if r:
            show(rows("SELECT facts_view.* FROM facts_view WHERE building=?",
                      (r[0]["name_chn"],)),
                 ["id", "year", "date", "fact", "source"])
    elif cmd == "fact":
        show(rows("SELECT * FROM facts_view WHERE id=?", (int(sys.argv[2]),)),
             ["id", "building", "year", "date", "fact", "people", "place",
              "source", "source_url", "note"])
        img = rows("""SELECT b.image, b.image_source, b.image_license
                      FROM facts_view f JOIN buildings b ON b.name_chn=f.building
                      WHERE f.id=?""", (int(sys.argv[2]),))
        if img:
            show(img, ["image", "image_source", "image_license"])
    elif cmd == "search":
        like = "%" + sys.argv[2] + "%"
        show(rows("""SELECT * FROM facts_view
                     WHERE fact LIKE ? OR people LIKE ? OR place LIKE ? OR note LIKE ?
                     ORDER BY year, id""", (like, like, like, like)),
             ["id", "building", "year", "fact", "note"])
    elif cmd == "year":
        show(rows("SELECT * FROM facts_view WHERE year=? ORDER BY id", (int(sys.argv[2]),)),
             ["id", "building", "date", "fact", "source"])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
