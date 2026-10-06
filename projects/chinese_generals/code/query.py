"""Read-only helper for chinese_generals.db (standard library only).

Examples:
    python code/query.py generals                 # list all generals
    python code/query.py general guanyu           # one general + titles + battles
    python code/query.py dynasty 唐                # generals of a dynasty
    python code/query.py state shuhan
    python code/query.py battle 合肥之戰
    python code/query.py search 長平
    python code/query.py year -260
    python code/query.py off-topic
"""
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chinese_generals.db")


def rows(sql, args=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()


def show(rs, cols):
    for r in rs:
        print(" | ".join("%s=%s" % (c, r.get(c, "")) for c in cols))
        print("-" * 40)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd, arg = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
    if cmd == "generals":
        show(rows("SELECT id,key,name_chn,state,dynasty,born_year,died_year FROM generals_view ORDER BY id"),
             ["id", "name_chn", "state", "dynasty", "born_year", "died_year"])
    elif cmd == "general":
        g = rows("SELECT * FROM generals_view WHERE key=? OR name_chn=?", (arg, arg))
        show(g, ["id", "key", "name_chn", "name_original", "courtesy_name", "state", "dynasty",
                 "born_raw", "born_year", "died_raw", "died_year", "achievement", "source", "source_url"])
        if g:
            gid = g[0]["id"]
            print("== 官職 ==")
            show(rows("SELECT id,title_chn,title_original,period,source_locator,source_quote FROM titles WHERE general_id=? ORDER BY id", (gid,)),
                 ["id", "title_chn", "period", "source_locator"])
            print("== 戰役 ==")
            show(rows("SELECT * FROM battle_roles_view WHERE general=? ORDER BY year", (g[0]["name_chn"],)),
                 ["battle", "year", "year_raw", "place", "role", "outcome", "source_locator"])
    elif cmd == "dynasty":
        show(rows("SELECT id,key,name_chn,state,dynasty,born_year,died_year FROM generals_view WHERE dynasty=? ORDER BY id", (arg,)),
             ["id", "name_chn", "state", "dynasty", "born_year", "died_year"])
    elif cmd == "state":
        show(rows("SELECT id,key,name_chn,state,dynasty FROM generals_view WHERE state=? ORDER BY id", (arg,)),
             ["id", "name_chn", "state", "dynasty"])
    elif cmd == "battle":
        show(rows("SELECT * FROM battles WHERE name_chn LIKE ? OR name_original LIKE ?", ("%" + arg + "%", "%" + arg + "%")),
             ["id", "name_chn", "name_original", "year", "year_raw", "place", "source", "source_locator", "source_quote"])
    elif cmd == "search":
        like = "%" + arg + "%"
        show(rows("""SELECT id,name_chn,state,dynasty,achievement FROM generals_view
                     WHERE name_chn LIKE ? OR achievement LIKE ? OR description LIKE ? OR source_quote LIKE ?
                     ORDER BY id""", (like, like, like, like)),
             ["id", "name_chn", "dynasty", "achievement"])
    elif cmd == "year":
        show(rows("SELECT * FROM battle_roles_view WHERE year=? ORDER BY general", (int(arg),)),
             ["general", "battle", "year", "year_raw", "place", "outcome"])
    elif cmd == "off-topic":
        print("本庫只收中國古代武將（生卒、戰役、官職、事蹟），收錄範圍外者一概要說「庫裡沒有」。")
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
