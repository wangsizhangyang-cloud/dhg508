"""Verify the database against the original 史書 texts.

Two jobs:
  1. Integrity: every non-empty source_quote must appear verbatim in the
     source file it cites (mapped through source_url -> wikisource_index).
  2. Spot check: print N random rows (default 20) beside their original
     wording, so a human can compare.

Usage:
    python code/verify.py            # integrity + 20-row check
    python code/verify.py 30         # 30-row check
"""
import json
import os
import random
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "chinese_generals.db")
INDEX = os.path.join(ROOT, "sources", "raw", "wikisource_index.json")

TABLES = ["generals", "titles", "battles", "general_battles", "dynasties", "states", "calendar"]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    with open(INDEX, encoding="utf-8") as fh:
        index = json.load(fh)
    url_to_path = {}
    for row in index:
        path = os.path.join(ROOT, row["file"].replace("/", os.sep))
        url_to_path[row["source_url"]] = path

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cache = {}

    def text_for(url):
        if url not in url_to_path:
            return None
        path = url_to_path[url]
        if path not in cache:
            with open(path, encoding="utf-8") as fh:
                cache[path] = fh.read()
        return cache[path]

    checked = passed = failed = 0
    failures = []
    items = []
    for table in TABLES:
        for row in conn.execute("SELECT * FROM %s" % table):
            if "source_quote" not in row.keys():
                continue
            items.append((table, row["id"], row["source_url"], (row["source_quote"] or "").strip()))
    for row in conn.execute("SELECT id,source_url,born_raw,died_raw FROM generals"):
        for fld in ("born_raw", "died_raw"):
            if (row[fld] or "").strip():
                items.append(("generals." + fld, row["id"], row["source_url"], row[fld].strip()))
    for table, rid, url, quote in items:
        if not quote:
            continue
        checked += 1
        source = text_for(url)
        if source is None:
            failed += 1
            failures.append((table, rid, "NO-SOURCE-FILE", quote))
        elif quote in source:
            passed += 1
        else:
            failed += 1
            failures.append((table, rid, "QUOTE-NOT-FOUND", quote))

    print("INTEGRITY: %d/%d quoted rows matched their source" % (passed, checked))
    for table, rid, kind, quote in failures[:40]:
        print("  FAIL %-16s %-22s id=%s  %s" % (table, kind, rid, quote[:60]))

    print("\nRANDOM %d-ROW CHECK (compare with the original)" % n)
    pool = []
    for table in TABLES:
        for row in conn.execute("SELECT * FROM %s" % table):
            if "source_quote" not in row.keys():
                continue
            if (row["source_quote"] or "").strip():
                pool.append((table, dict(row)))
    pool.sort(key=lambda x: (x[0], x[1]["id"]))
    rng = random.Random(508)
    for table, row in rng.sample(pool, min(n, len(pool))):
        source = text_for(row["source_url"]) or ""
        quote = (row["source_quote"] or "").strip()
        locator = row["source_locator"] or ""
        print("-" * 72)
        print("[%s id=%s] %s" % (table, row["id"], locator))
        print("  source_quote :", quote[:110])
        print("  in original  :", "YES" if quote in source else "NO")

    conn.close()
    if failures:
        print("\n%d integrity failures" % len(failures))
        return 1
    print("\nAll quoted rows grounded in the originals.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
