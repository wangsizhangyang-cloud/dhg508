"""Derive a person-person relation graph from the extracted 《史記》 rows.

The database's `relations` table only holds a little kinship; this script adds
relation kinds that are readable from the text, each carried by a verbatim
quote (or, for 同國, by the shared 卷):

    親屬  X of Y                  from relations (+ name resolution)
    君臣  A served ruler B        「事(B)」「臣事(B)」「為(B)相」「(B)之臣」
    敵對  A acted against B       one phrase names both round a hostile verb
    敵國  A attacked B's 國        「伐齊」「攻趙」 … B is of that 國, and the
                                  two share a 卷 (so they are not anachronisms
                                  where avoidable)
    同國  A and B are of one 國   same 國; prefer those seen in the same 卷

A person's 國 comes from, in order: the 世家/本紀 they have their 本傳 in, the
ruler they served, the 國名 in their 籍貫, their 名號 prefix.

Output: data/extracted/graph.json.  Rerun after extract.py/build_db.py.
Usage:  python code/build_graph.py
"""
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

from opencc import OpenCC

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "shiji_people.db")
PROC = os.path.join(ROOT, "sources", "processed")
PERSONS = os.path.join(ROOT, "data", "extracted", "persons.json")
CHAPTERS = os.path.join(ROOT, "data", "extracted", "chapters.json")
MAN = os.path.join(ROOT, "data", "manual")
OUT = os.path.join(ROOT, "data", "extracted", "graph.json")

CC = OpenCC("hk2s")
simp = CC.convert

STATES = ("秦", "齐", "楚", "燕", "赵", "魏", "韩", "宋", "鲁", "卫", "吴",
          "越", "陈", "杞", "郑", "晋", "周", "汉", "夏", "商", "殷")
# 籍貫/篇名裡認國；「陳留」是地名不是陳國，故陳字後不接留
STATE_ANY = re.compile("(秦|齐|楚|燕|赵|魏|韩|宋|鲁|卫|吴|越|陈(?!留)|杞|郑|晋|周|汉)")
# 卷篇 -> 國。世家用「X世家」全名，避免誤中《魏其武安侯》《韓信盧綰》等列傳篇名
CHAPTER_STATE = [
    ("吴太伯", "吴"), ("齐太公", "齐"), ("鲁周公", "鲁"), ("燕召公", "燕"),
    ("管蔡", "管蔡"), ("陈杞", "陈"), ("卫康叔", "卫"), ("宋微子", "宋"),
    ("晋世家", "晋"), ("楚世家", "楚"), ("越王", "越"), ("郑世家", "郑"),
    ("赵世家", "赵"), ("魏世家", "魏"), ("韩世家", "韩"), ("田敬仲完", "齐"),
    ("孔子", "鲁"), ("秦始皇", "秦"), ("项羽", "楚"), ("高祖", "汉"),
    ("吕太后", "汉"), ("孝文", "汉"), ("孝景", "汉"), ("孝武", "汉"),
    ("秦本纪", "秦"), ("夏本纪", "夏"), ("殷本纪", "殷"), ("周本纪", "周"),
    ("萧相国", "汉"), ("曹相国", "汉"), ("留侯", "汉"), ("陈丞相", "汉"),
    ("绛侯", "汉"), ("梁孝王", "汉"), ("五宗", "汉"), ("三王", "汉"),
    ("荆燕", "汉"), ("齐悼惠王", "汉"), ("外戚", "汉"), ("楚元王", "汉"),
    ("东越", "越"),
]
# 籍貫地名 -> 國（只放有把握的幾個）
PLACE_STATE = {
    "郿": "秦", "频阳": "秦", "陇西": "汉", "上蔡": "楚", "淮阴": "楚",
    "沛": "汉", "陈留": "汉", "平阳": "汉", "丰": "汉", "昌邑": "汉",
    "宛朐": "汉", "大梁": "魏", "邯郸": "赵", "蓟": "燕", "临淄": "齐",
    "临菑": "齐", "寿春": "楚", "郢": "楚", "曲阜": "鲁", "会稽": "越",
    "吴": "吴", "阳翟": "韩", "商丘": "宋",
}
ALIASES = {
    "秦昭王": "秦昭襄王", "昭王": "秦昭襄王", "秦始皇": "始皇帝", "秦王政": "始皇帝",
    "高祖": "刘邦", "汉高祖": "刘邦", "高帝": "刘邦", "沛公": "刘邦",
    "武帝": "孝武", "孝武皇帝": "孝武", "孝文皇帝": "孝文", "孝景皇帝": "孝景",
    "重耳": "晋文公", "公子重耳": "晋文公", "晋公子重耳": "晋文公",
    "句践": "越王句践", "勾践": "越王句践", "阖庐": "", "夫差": "",
    "汤": "成汤", "纣": "帝辛", "武王": "周武王", "文王": "周文王",
    "周公": "周公旦", "太公": "齐太公吕尚", "吕尚": "齐太公吕尚",
    "管子": "管仲", "晏子": "晏婴", "商君": "商鞅", "张子房": "张良",
    "绛侯": "绛侯周勃", "条侯": "绛侯周勃",
    "舜": "帝舜", "帝禹": "禹", "王余昧": "余眛", "秦惠王": "秦惠文王",
}
# 已知误挂的亲属行（句中人名并非本傳主人之親），建图时剔除
BAD_REL = {("优孟", "孙叔敖"), ("田儋", "齐王建"), ("禹", "舜"), ("禹", "帝禹"),
           ("黄帝", "西陵"), ("栗姬子", "栗姬"), ("程姬子", "程姬"),
           ("贾夫人子", "贾夫人"), ("唐姬子", "王唐姬"), ("唐姬子", "发"),
           ("余昧", "王余昧")}
BAD_REL = {(simp(a), b) for a, b in BAD_REL}
# 時期：由本傳卷次粗分，用來區分不同時期的人
ERA_NAMES = ["上古", "西周", "春秋", "戰國", "秦漢之際", "漢"]
ERA_BY_JUAN = {}
for _j in range(1, 5):
    ERA_BY_JUAN[_j] = 0
for _j in range(31, 34):
    ERA_BY_JUAN[_j] = 1
for _j in list(range(34, 43)) + [47, 62, 64, 66, 67]:
    ERA_BY_JUAN[_j] = 2
for _j in list(range(43, 47)) + list(range(5, 7)) + [63, 65] + list(range(68, 87)):
    ERA_BY_JUAN[_j] = 3
for _j in [48] + list(range(7, 9)) + list(range(87, 93)):
    ERA_BY_JUAN[_j] = 4
for _j in list(range(9, 13)) + list(range(49, 61)) + list(range(93, 131)):
    ERA_BY_JUAN[_j] = 5
ERA_BY_JUAN[61] = 0
HOSTILE = re.compile(r"攻|伐|击|擊|破|围|圍|败|敗|虏|虜|杀|殺|诛|誅|降|灭|滅|斩|斬|坑|阬")
WAR_STATE = re.compile(r"(?:攻|伐|击|擊|破|围|圍|败|敗|灭|滅|取|降)(%s)" % "|".join(STATES))
SERVED = [
    re.compile(r"事([\u4e00-\u9fff]{2,6})"),
    re.compile(r"(?:臣事|属|屬)([\u4e00-\u9fff]{2,6})"),
    re.compile(r"[为為]([\u4e00-\u9fff]{2,6})相"),
    re.compile(r"([\u4e00-\u9fff]{2,6})之臣"),
]


def section_texts():
    out = {}
    for name in os.listdir(PROC):
        if not name.endswith(".txt"):
            continue
        slug = name[:-4]
        text = open(os.path.join(PROC, name), encoding="utf-8").read()
        parts = re.split(r"^==\s*([^=\n]*?)\s*==\s*$", text, flags=re.M)
        for i in range(1, len(parts) - 1, 2):
            out[(slug, parts[i].strip())] = parts[i + 1].strip()
    return out


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[。！？])", text) if s.strip()]


def main():
    persons = json.load(open(PERSONS, encoding="utf-8"))
    manual = {}
    if os.path.isdir(MAN):
        for fn in sorted(os.listdir(MAN)):
            if fn.endswith(".json"):
                doc = json.load(open(os.path.join(MAN, fn), encoding="utf-8"))
                for mp in doc.get("persons", []):
                    manual[mp["key"]] = mp
    for p in persons:
        if p["key"] in manual:
            p.update(manual.pop(p["key"]))      # same overrides as build_db.py
    persons.extend(manual.values())             # and the same appended people
    for i, p in enumerate(persons, 1):               # ids as build_db.py assigns
        p["id"] = i
        m = re.search(r"(\d+)$", p["chapter_slug"])
        p["juan"] = int(m.group(1)) if m else 0
    chapters = {c["slug"]: c["title_original"] for c in
                json.load(open(CHAPTERS, encoding="utf-8"))}
    con = sqlite3.connect(DB)
    chap_sets = defaultdict(set)
    for pid, cid in con.execute("SELECT person_id, chapter_id FROM person_chapters"):
        chap_sets[pid].add(cid)
    con.close()
    sections = section_texts()

    by_name, shorts = {}, defaultdict(list)
    full_names = {}
    for p in persons:
        for n in (p["name_chn"], p["name_original"]):
            if n:
                full_names.setdefault(n, p["id"])
            if n and len(n) >= 2:
                by_name.setdefault(n, p["id"])
        shorts[p["id"]] = [n for n in (p["name_chn"], p["name_original"]) if n]
    name_of = {p["id"]: p["name_chn"] for p in persons}

    def resolve(raw, home=""):
        raw = raw.strip()
        if raw in by_name:
            return by_name[raw]
        if ALIASES.get(raw) and ALIASES[raw] in by_name:
            return by_name[ALIASES[raw]]
        cands = {pid for n, pid in by_name.items() if n.endswith(raw) and len(raw) >= 1}
        if len(cands) == 1:
            return next(iter(cands))
        if home:
            sc = [pid for pid in cands if name_of.get(pid, "").startswith(home)]
            if len(sc) == 1:
                return sc[0]
        return None

    def state_of(p):
        title = simp(chapters.get(p["chapter_slug"], ""))
        for key, st in CHAPTER_STATE:
            if key in title:
                return st
        origin = simp(p.get("origin_raw", "") or "")
        if "其先" in origin or "之先" in origin:
            return ""                          # 「其先齊人」講的是祖先，不是本人
        m = STATE_ANY.search(origin)          # 籍貫裡直接寫了國（楚人、趙之良將…）
        if m:
            return m.group(1)
        for place, st in PLACE_STATE.items():
            if place in origin:
                return st
        return ""                              # 不從姓名猜國，免得夏侯/韓/周等姓氏誤判

    for p in persons:
        p["state"] = state_of(p)
        p["era"] = ERA_BY_JUAN.get(p["juan"], -1)
        p["era_name"] = ERA_NAMES[p["era"]] if p["era"] >= 0 else ""

    edges = []
    served_by = defaultdict(list)
    # 親屬 + 君臣
    for p in persons:
        for r in p.get("relations", []):
            if (p["name_chn"], simp(r["related_name"])) in BAD_REL:
                continue
            tgt = resolve(r["related_name"], p["state"])
            if tgt and tgt != p["id"]:
                edges.append({"a": p["id"], "b": tgt, "type": "親屬",
                              "label": r["relation_type"], "quote": r["source_quote"],
                              "locator": p["source_locator"]})
        body = sections.get((p["chapter_slug"], p.get("heading_original", ""))) or \
            p.get("description", "")
        for s in sentences(body):
            for rx in SERVED:
                for m in rx.finditer(s):
                    tgt = resolve(m.group(1), p["state"])
                    if tgt and tgt != p["id"]:
                        edges.append({"a": p["id"], "b": tgt, "type": "君臣",
                                      "label": "事奉", "quote": s.strip(),
                                      "locator": p["source_locator"]})
                        served_by[p["id"]].append(tgt)

    # 國只由「本傳卷篇」與「籍貫」判定；不從姓氏、也不從所事之君推斷

    def person_body(p):
        return sections.get((p["chapter_slug"], p.get("heading_original", ""))) or \
            (p.get("description", "") + " " + p.get("source_quote", ""))

    # 敵對（人對人）+ 敵國（伐其國）
    for p in persons:
        home = p["state"]
        for s in sentences(person_body(p)):
            for m in HOSTILE.finditer(s):
                left, tail = s[:m.start()], s[m.end():]
                if not tail or not any(n in left for n in shorts[p["id"]]):
                    continue
                for q in persons:
                    if q["id"] == p["id"] or (len(q["name_chn"]) == 2
                                              and q["name_chn"][-1] in "公王侯君"):
                        continue
                    for n in shorts[q["id"]]:
                        pos = tail.find(n) if len(n) >= 2 else -1
                        if 0 <= pos <= 2 and not (pos > 0 and tail[pos - 1] in "之主其诸群军吏将"):
                            edges.append({"a": p["id"], "b": q["id"], "type": "敵對",
                                          "label": m.group(0), "quote": s.strip(),
                                          "locator": p["source_locator"]})
                            break
        if home:
            added = 0
            for s in sentences(person_body(p)):
                for m in WAR_STATE.finditer(s):
                    left = s[max(0, m.start() - 8):m.start()]
                    hit = False
                    for n in shorts[p["id"]]:
                        idx = left.rfind(n)
                        if idx < 0:
                            continue
                        after = left[idx + len(n):]
                        if re.match(r"(元|[一二三四五六七八九十百0-9]{1,3})年", after):
                            continue        # 「王僚二年」是紀年，不是行動者
                        hit = True
                        break
                    if not hit:
                        continue
                    st = m.group(1)
                    if st == home:
                        continue
                    peers = sorted(
                        (q for q in persons if q["state"] == st and q["id"] != p["id"]
                         and (chap_sets.get(p["id"], set()) & chap_sets.get(q["id"], set()))
                         and not any(persons[t - 1]["state"] == home
                                     for t in served_by[q["id"]])),
                        key=lambda q: -len(chap_sets.get(q["id"], ())))
                    for q in peers[:3]:
                        edges.append({"a": p["id"], "b": q["id"], "type": "敵國",
                                      "label": m.group(0), "quote": s.strip(),
                                      "locator": p["source_locator"]})
                        added += 1
                    if added >= 5:
                        break
                if added >= 5:
                    break

    # 手工核定的關係（data/manual/graph-edges.json），每條仍以《史記》原句為據
    man_path = os.path.join(MAN, "graph-edges.json")
    if os.path.exists(man_path):
        for e in json.load(open(man_path, encoding="utf-8")).get("edges", []):
            a, b = full_names.get(e["a"]), full_names.get(e["b"])
            if a and b and a != b:
                edges.append({"a": a, "b": b, "type": e["type"], "label": e["label"],
                              "quote": e.get("quote", ""), "locator": e.get("locator", ""),
                              "manual": True})

    # 同國：同國且同見於一卷者優先，不足則按卷次相近補
    degree = Counter()
    for e in edges:
        degree[e["a"]] += 1
        degree[e["b"]] += 1
    by_state = defaultdict(list)
    for p in persons:
        if p["state"]:
            by_state[p["state"]].append(p)
    for st, group in by_state.items():
        for p in group:
            peers = []
            for q in group:
                if q["id"] == p["id"]:
                    continue
                shared = len(chap_sets.get(p["id"], set()) & chap_sets.get(q["id"], set()))
                peers.append((shared, -abs(p["juan"] - q["juan"]), degree.get(q["id"], 0), q["id"]))
            peers.sort(reverse=True)
            for shared, _, _, qid in peers[:5]:
                edges.append({"a": p["id"], "b": qid, "type": "同國", "label": st,
                              "quote": "同為%s人/臣；同見 %d 卷。" % (st, shared),
                              "locator": ""})

    seen, uniq = set(), []
    era_of = {p["id"]: p["era"] for p in persons}
    for e in edges:
        if name_of.get(e["a"]) == name_of.get(e["b"]):
            continue                    # never link two rows of the same person/name
        k = (e["a"], e["b"], e["type"])
        if k in seen:
            continue
        seen.add(k)
        ea, eb = era_of.get(e["a"], -1), era_of.get(e["b"], -1)
        e["gap"] = abs(ea - eb) if ea >= 0 and eb >= 0 else None
        uniq.append(e)

    stats = Counter(e["type"] for e in uniq)
    out = {
        "nodes": [{"id": p["id"], "name": p["name_chn"], "name_original": p["name_original"],
                   "category": p["category"], "state": p["state"], "juan": p["juan"],
                   "era": p["era"], "era_name": p["era_name"],
                   "chapter_slug": p["chapter_slug"], "locator": p["source_locator"],
                   "origin": p.get("origin_raw", "")} for p in persons],
        "edges": uniq,
        "meta": {"node_count": len(persons), "edge_count": len(uniq), "by_type": dict(stats)},
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    adj = defaultdict(list)
    for e in uniq:
        adj[e["a"]].append(e)
        adj[e["b"]].append(e)
    deg = sorted((len(v), k) for k, v in adj.items())
    print("nodes", len(persons), "edges", len(uniq), dict(stats))
    print("degree: max", deg[-1][0], name_of.get(deg[-1][1]), "| median",
          deg[len(deg) // 2][0], "| zero", len(persons) - len(adj))
    for t in ("親屬", "君臣", "敵對", "敵國"):
        for e in [x for x in uniq if x["type"] == t][:4]:
            print("  %s %s - %s [%s] %s" % (t, name_of.get(e["a"]), name_of.get(e["b"]),
                                            e["label"], (e["quote"] or "")[:40]))
    for target in ("白起", "项羽", "廉颇", "孙武"):
        tid = next((p["id"] for p in persons if p["name_chn"] == target), None)
        if tid:
            kinds = Counter(e["type"] for e in adj.get(tid, []))
            print("ego %-4s state=%s neighbours=%d %s" % (
                target, next(p["state"] for p in persons if p["id"] == tid),
                len(adj.get(tid, [])), dict(kinds)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
