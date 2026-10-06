"""Small read-only helper for shiji_people.db.

Usage:
    python code/query.py person 白起
    python code/query.py chapter 73
    python code/query.py mentions 孔子
    python code/query.py offices 田單
    python code/query.py events 荊軻
    python code/query.py relations 周公旦
    python code/query.py search 長平
    python code/query.py sql "SELECT name_chn, category FROM persons LIMIT 5"
    python code/query.py off-topic        # what the skill should answer for out-of-scope asks
"""
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(os.path.dirname(HERE), "shiji_people.db")


def rows(sql, args=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    out = conn.execute(sql, args).fetchall()
    conn.close()
    return out


def cite(r):
    return "[%s id=%s] %s" % (r.get("_table", "row"), r["id"], r.get("source_locator", ""))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    cmd = sys.argv[1]
    arg = " ".join(sys.argv[2:])
    if cmd == "off-topic":
        print("本庫只收《史記》所載人物及其出處，此問題不在範圍內，恕不能答。")
    elif cmd == "person":
        for r in rows("SELECT * FROM persons WHERE name_chn=? OR name_original=? OR heading_original LIKE ?",
                      (arg, arg, "%" + arg + "%")):
            print("#%s %s (%s) — %s" % (r["id"], r["name_chn"], r["category"], r["source_locator"]))
            print("  origin: %s | quote: %s" % (r["origin_raw"], r["source_quote"]))
            print("  desc: %s" % (r["description"] or "")[:160])
    elif cmd == "chapter":
        for r in rows("SELECT * FROM chapters WHERE juan=?", (arg,)):
            print("#%s [%s] %s — %s" % (r["id"], r["category"], r["title_chn"], r["source_url"]))
    elif cmd == "mentions":
        for r in rows("""SELECT p.name_chn, c.juan, c.title_chn, pc.relation_kind, pc.source_locator
                         FROM person_chapters pc JOIN persons p ON p.id=pc.person_id
                         JOIN chapters c ON c.id=pc.chapter_id
                         WHERE p.name_chn=? OR p.name_original=? ORDER BY c.juan""", (arg, arg)):
            print(r["juan"], r["relation_kind"], r["title_chn"], "—", r["source_locator"])
    elif cmd == "offices":
        for r in rows("""SELECT o.*, p.name_chn FROM offices o JOIN persons p ON p.id=o.person_id
                         WHERE p.name_chn=? OR p.name_original=?""", (arg, arg)):
            print("%s: %s (%s) — %s" % (r["name_chn"], r["title_chn"], r["period_norm"], r["source_quote"]))
    elif cmd == "events":
        for r in rows("""SELECT e.*, p.name_chn FROM events e JOIN persons p ON p.id=e.person_id
                         WHERE p.name_chn=? OR p.name_original=?""", (arg, arg)):
            print("%s [%s] %s — %s" % (r["name_chn"], r["event_type"], r["year_norm"] or "", r["source_quote"]))
    elif cmd == "relations":
        for r in rows("SELECT * FROM relations WHERE person_id IN "
                      "(SELECT id FROM persons WHERE name_chn=? OR name_original=?)", (arg, arg)):
            print("%s 之 %s — %s" % (r["related_name"], r["relation_type"], r["source_quote"]))
    elif cmd == "search":
        like = "%" + arg + "%"
        for r in rows("SELECT * FROM persons WHERE description LIKE ? OR source_quote LIKE ? LIMIT 20", (like, like)):
            print("#%s %s — %s" % (r["id"], r["name_chn"], r["source_locator"]))
    elif cmd == "sql":
        for r in rows(arg):
            print(dict(r))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
