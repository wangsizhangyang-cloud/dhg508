import json, os, sqlite3, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c = sqlite3.connect(os.path.join(ROOT, "chinese_generals.db"))
c.row_factory = sqlite3.Row
out = []
out.append("=== GENERALS (born/died raw -> normalized) ===")
for r in c.execute("SELECT key,name_chn,born_raw,born_year,died_raw,died_year FROM generals ORDER BY id"):
    out.append("%-14s born[%s | %s]  died[%s | %s]" % (
        r["key"], r["born_raw"], r["born_year"], r["died_raw"], r["died_year"]))
out.append("")
out.append("=== BATTLES (year_raw -> year) ===")
for r in c.execute("SELECT id,key,name_chn,year_raw,year,place FROM battles ORDER BY id"):
    if r["year_raw"] or r["year"] is not None:
        out.append("%-4s %-24s raw=[%s]  year=%s  place=%s" % (
            r["id"], r["name_chn"], r["year_raw"], r["year"], r["place"]))
with open(os.path.join(ROOT, "artifacts", "date_report.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out))
print("wrote artifacts/date_report.txt", len(out), "lines")
