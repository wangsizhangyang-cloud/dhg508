"""Write research/outputs/verification.md: 20 random rows beside the original.

Usage:
    python code/check_sample.py
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
OUT = os.path.join(ROOT, "research", "outputs", "verification.md")

TABLES = ["generals", "titles", "battles", "general_battles", "dynasties", "states"]


def main():
    with open(INDEX, encoding="utf-8") as fh:
        index = json.load(fh)
    url_to_path = {r["source_url"]: os.path.join(ROOT, r["file"].replace("/", os.sep)) for r in index}
    cache = {}

    def original(url):
        if url not in url_to_path:
            return ""
        path = url_to_path[url]
        if path not in cache:
            with open(path, encoding="utf-8") as fh:
                cache[path] = fh.read()
        return cache[path]

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    pool = []
    for table in TABLES:
        for row in conn.execute("SELECT * FROM %s" % table):
            if "source_quote" not in row.keys():
                continue
            if (row["source_quote"] or "").strip():
                pool.append((table, dict(row)))
    pool.sort(key=lambda x: (x[0], x[1]["id"]))
    rng = random.Random(508)
    sample = rng.sample(pool, 20)

    lines = ["# 核对：20 行随机抽样回原文", "",
             "由 `code/check_sample.py` 生成（随机种子 508）。每行给出库中值与所引原文，",
             "并在原文中定位 `source_quote` 的上下文供人工比对。", ""]
    for table, row in sample:
        src = original(row["source_url"])
        quote = row["source_quote"].strip()
        at = src.find(quote)
        ctx = src[max(0, at - 30):at + len(quote) + 30] if at >= 0 else "（未找到）"
        lines.append("## [%s id=%s] %s" % (table, row["id"], row.get("source_locator", "")))
        if table == "generals":
            lines.append("- 库中：%s（%s），生 %s｜%s，卒 %s｜%s" % (
                row.get("name_chn"), row.get("state_id"), row.get("born_raw"), row.get("born_year"),
                row.get("died_raw"), row.get("died_year")))
        elif table == "titles":
            lines.append("- 库中：%s（%s）" % (row.get("title_chn"), row.get("period")))
        elif table == "battles":
            lines.append("- 库中：%s，年份 %s｜%s，地 %s" % (
                row.get("name_chn"), row.get("year"), row.get("year_raw"), row.get("place")))
        elif table == "general_battles":
            lines.append("- 库中：将%s，役%s，%s，%s" % (
                row.get("general_id"), row.get("battle_id"), row.get("role"), row.get("outcome")))
        lines.append("- 引文：`%s`" % quote)
        lines.append("- 原文：`…%s…`" % ctx.replace("\n", " "))
        lines.append("- 命中：%s" % ("YES" if quote in src else "NO"))
        lines.append("")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote", OUT, "with", len(sample), "rows")
    conn.close()


if __name__ == "__main__":
    sys.exit(main())
