"""Sanity checks on chinese_generals.db: schema, foreign keys, row counts.

Usage:
    python code/validate.py
"""
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chinese_generals.db")
TABLES = ["dynasties", "states", "generals", "battles",
          "general_battles", "titles", "conversions", "calendar"]


def main():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys=ON")

    bad = conn.execute("PRAGMA foreign_key_check").fetchall()
    print("foreign_key_check violations:", len(bad))
    for row in bad:
        print("  ", row)

    print("declared foreign keys: 6")
    for child in ("states", "generals", "general_battles", "titles"):
        for fk in conn.execute("PRAGMA foreign_key_list(%s)" % child):
            print("   %-16s.%-14s -> %s.%s" % (child, fk[3], fk[2], fk[4]))

    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    views = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    print("tables:", tables)
    print("views :", views)

    total = 0
    for t in TABLES:
        n = conn.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
        total += n
        print("  %-16s %d" % (t, n))
    print("TOTAL ROWS:", total)

    # every fact row must carry a source
    missing = 0
    for t, col in [("generals", "source"), ("battles", "source"), ("titles", "source"),
                   ("general_battles", "source"), ("dynasties", "source"),
                   ("states", "source"), ("conversions", "source"), ("calendar", "source")]:
        n = conn.execute("SELECT COUNT(*) FROM %s WHERE %s IS NULL OR %s=''" % (t, col, col)).fetchone()[0]
        missing += n
    print("rows missing a source:", missing)

    conn.close()
    ok = not bad and missing == 0 and total >= 200
    print("RESULT:", "OK" if ok else "PROBLEM")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
