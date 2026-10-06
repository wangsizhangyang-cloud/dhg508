"""Spot-check fact rows against the saved original sources.

Each check states: fact id -> source file it cites -> a string that must
appear verbatim in that source. If the string is absent the row is suspect.
"""
import os
import sqlite3
import sys

DB = "forbidden_city.db"

WIKI = "sources/raw/wiki"
WIKIZH = "sources/raw/wiki_zh"
WEB = "sources/raw/web"

CHECKS = [
    (52, os.path.join(WIKIZH, "乾清宫.txt"), "乾清宫始建于明朝永乐十八年"),
    (54, os.path.join(WIKIZH, "乾清宫.txt"), "正德九年（1514年）正月十六日晚放煙火不慎"),
    (107, os.path.join(WIKIZH, "武英殿.txt"), "同治八年（1869年），武英殿遭遇火灾"),
    (140, os.path.join(WIKIZH, "儲秀宮.txt"), "花费63万两白银大规模整修储秀宫"),
    (131, os.path.join(WIKIZH, "慈寧宮.txt"), "乾隆三十四年（1769年），将慈寧宮正殿由單檐廡殿頂改建為重檐廡殿頂"),
    (21, os.path.join(WIKIZH, "太和門.txt"), "光緒十四年，十二月十五日（1889年1月16日）"),
    (30, os.path.join(WIKIZH, "太和殿.txt"), "康熙三十四年（1695年）至康熙三十六年（1697年）重建"),
    (48, os.path.join(WIKIZH, "保和殿.txt"), "乾隆五十四年（1789年）起，保和殿成为每科殿试的固定场所"),
    (67, os.path.join(WIKIZH, "交泰殿.txt"), "保留其中的25枚"),
    (76, os.path.join(WIKIZH, "坤宁宫.txt"), "康熙四年（1665年）康熙帝大婚"),
    (142, os.path.join(WIKIZH, "儲秀宮.txt"), "婉容"),
    (86, os.path.join(WEB, "dpm-jiaolou.txt"), "建成于明永乐十八年（1420年）"),
    (88, os.path.join(WEB, "dpm-jiaolou.txt"), "高27.50m"),
    (144, os.path.join(WEB, "dpm-qinandian.txt"), "嘉靖十四年（1535年）添建墙垣"),
    (150, os.path.join(WEB, "dpm-qinandian.txt"), "抱厦 3间，后拆除"),
    (5, os.path.join(WIKI, "Forbidden_City.txt"), "residence of 24 Ming and Qing dynasty Emperors"),
    (33, os.path.join(WIKIZH, "太和殿.txt"), "狻猊、狎鱼、獬豸、斗牛、行什"),
    (119, os.path.join(WIKI, "Hall_of_Mental_Cultivation.txt"), "Timely Clearing After Snowfall by Wang Xizhi"),
]


def main():
    conn = sqlite3.connect(DB)
    ok = fail = 0
    for fid, path, needle in CHECKS:
        row = conn.execute("SELECT fact FROM facts WHERE id=?", (fid,)).fetchone()
        if row is None:
            print(f"MISSING ROW {fid}")
            fail += 1
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"NO SOURCE {fid} {path}: {exc}")
            fail += 1
            continue
        hit = needle in text
        ok += hit
        fail += (not hit)
        print(f"[{'OK ' if hit else 'FAIL'}] id={fid}  {os.path.basename(path)}")
        print(f"        needle: {needle}")
        print(f"        row   : {row[0][:90]}")
    conn.close()
    print(f"\n{ok}/{ok + fail} checks passed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
