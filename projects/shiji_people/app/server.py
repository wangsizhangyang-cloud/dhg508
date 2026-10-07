"""Shiji People — a small web app over shiji_people.db.

    python app/server.py            then open http://localhost:8000
    set DEEPSEEK_API_KEY=sk-...     to enable the real model call

Standard library only.  Data: ../shiji_people.db and
../data/extracted/graph.json (built by code/build_graph.py).

Endpoints
    GET  /                 the page (static/index.html)
    GET  /api/health       quick status
    GET  /api/people       everyone, with degree (for the search page)
    GET  /api/ego?id=N|name=    one person + their neighbours only
    GET  /api/person?name= offices / events / relations / mentions
    POST /api/ask          {"question": "..."} -> DeepSeek-grounded answer
"""
import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

HERE = Path(__file__).parent
ROOT = HERE.parent
DB = ROOT / "shiji_people.db"
GRAPH = ROOT / "data" / "extracted" / "graph.json"
INDEX_HTML = HERE / "static" / "index.html"
PORT = int(os.environ.get("PORT", 8000))

DEEPSEEK_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")

SYSTEM_PROMPT = """你是《史記》人物庫的答問助手。規矩：
1. 只根據下面提供的資料行回答；不要用資料以外的知識補內容。
2. 每條事實後標 [表名 id=N] 與出處（source_locator，形如《史記·卷七十三白起王翦列傳第十三·白起》）。
3. 資料沒有的，直說「庫中沒有」；不要推算生年，不把紀年換算成公元。
4. 不許編造《史記》原文或引文。
5. 問題與《史記》人物無關時，說明本庫只收《史記》人物並拒絕。
答覆用簡潔史家口吻，先結論後出處。"""


# ---------------------------------------------------------------- data

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def load_graph():
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in g["nodes"]}
    adj = {}
    for e in g["edges"]:
        adj.setdefault(e["a"], []).append(e)
        if e["b"] != e["a"]:
            adj.setdefault(e["b"], []).append(e)
    degree = {nid: len(v) for nid, v in adj.items()}
    by_name = {}
    for n in g["nodes"]:
        for nm in (n["name"], n["name_original"]):
            by_name.setdefault(nm, n["id"])
    return {"nodes": nodes, "edges": g["edges"], "adj": adj,
            "degree": degree, "by_name": by_name, "meta": g["meta"]}


G = load_graph()

TYPE_ORDER = {"親屬": 0, "君臣": 1, "敵對": 2, "敵國": 3, "同國": 4}


def people():
    out = []
    for nid, n in G["nodes"].items():
        out.append({"id": nid, "name": n["name"], "name_original": n["name_original"],
                    "category": n["category"], "state": n["state"], "juan": n["juan"],
                    "origin": n.get("origin", ""), "degree": G["degree"].get(nid, 0)})
    out.sort(key=lambda x: (-x["degree"], x["id"]))
    return out


def ego(nid):
    node = G["nodes"].get(nid)
    if not node:
        return None
    edges = G["adj"].get(nid, [])
    best = {}
    for e in edges:
        other = e["b"] if e["a"] == nid else e["a"]
        if other == nid:
            continue
        on = G["nodes"].get(other, {})
        if on.get("name") == node["name"]:
            continue                    # a row of the same person must not appear
        if other not in best or TYPE_ORDER.get(e["type"], 9) < TYPE_ORDER.get(best[other]["type"], 9):
            best[other] = e
    # one neighbour per name (two 卷 can hold the same person, e.g. 始皇帝)
    chosen = {}
    for other, e in best.items():
        nm = G["nodes"][other]["name"]
        rank = (TYPE_ORDER.get(e["type"], 9), -G["degree"].get(other, 0))
        if nm not in chosen or rank < chosen[nm][0]:
            chosen[nm] = (rank, other, e)
    neighbours = []
    for _, other, e in chosen.values():
        on = G["nodes"][other]
        neighbours.append({"id": other, "name": on["name"], "category": on["category"],
                           "state": on["state"], "era_name": on.get("era_name", ""),
                           "relation": e["type"], "label": e["label"], "gap": e.get("gap"),
                           "quote": e.get("quote", ""), "locator": e.get("locator", ""),
                           "degree": G["degree"].get(other, 0)})
    neighbours.sort(key=lambda x: (TYPE_ORDER.get(x["relation"], 9), -G["degree"].get(x["id"], 0)))
    return {"center": node, "neighbours": neighbours,
            "degree": G["degree"].get(nid, 0),
            "by_relation": {t: sum(1 for x in neighbours if x["relation"] == t)
                            for t in TYPE_ORDER}}


def person_bundle(person_id):
    con = db()
    row = con.execute("SELECT * FROM persons WHERE id=?", (person_id,)).fetchone()
    if not row:
        con.close()
        return None
    p = dict(row)
    r = con.execute
    bundle = {
        "person": p,
        "offices": [dict(x) for x in r(
            "SELECT id,title_chn,period_norm,source_locator,source_quote FROM offices "
            "WHERE person_id=?", (person_id,))],
        "events": [dict(x) for x in r(
            "SELECT id,event_type,year_norm,source_locator,source_quote FROM events "
            "WHERE person_id=?", (person_id,))],
        "mentions": [dict(x) for x in r(
            "SELECT pc.id,c.juan,c.title_chn,pc.relation_kind,pc.source_locator "
            "FROM person_chapters pc JOIN chapters c ON c.id=pc.chapter_id "
            "WHERE pc.person_id=? ORDER BY c.juan", (person_id,))],
    }
    con.close()
    return bundle


# ---------------------------------------------------------------- model call

def find_persons(question, limit=3):
    con = db()
    hits = []
    for r in con.execute("SELECT id,key,name_chn,name_original,source_locator,"
                         "origin_raw,description,source_quote FROM persons"):
        for name in {r["name_chn"], r["name_original"]}:
            if name and len(name) >= 2 and name in question:
                hits.append((len(name), r))
                break
    con.close()
    hits.sort(key=lambda x: -x[0])
    seen, out = set(), []
    for _, r in hits:
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
        if len(out) >= limit:
            break
    return out


def build_context(question):
    chunks = []
    for p in find_persons(question):
        b = person_bundle(p["id"]) or {"offices": [], "events": [], "mentions": []}
        chunks.append("人物 [persons id=%d] %s（%s）" % (p["id"], p["name_chn"], p["source_locator"]))
        chunks.append("  籍貫：%s；本傳引文：%s" % (p["origin_raw"] or "未載", p["source_quote"]))
        for o in b["offices"][:8]:
            chunks.append("  官職 [offices id=%d] %s（%s）— %s" % (
                o["id"], o["title_chn"], o["period_norm"] or "未紀年", o["source_locator"]))
        for e in b["events"][:8]:
            chunks.append("  事件 [events id=%d] %s %s — %s" % (
                e["id"], e["event_type"], e["year_norm"] or "", e["source_quote"]))
        men = ", ".join("卷%d%s" % (m["juan"], m["relation_kind"]) for m in b["mentions"][:14])
        chunks.append("  見於：%s" % men)
        nid = p["id"]
        for e in G["adj"].get(nid, [])[:10]:
            other = e["b"] if e["a"] == nid else e["a"]
            on = G["nodes"].get(other, {}).get("name", other)
            chunks.append("  關係 [graph %s] %s - %s：%s" % (e["type"], on, e["label"], e.get("quote", "")))
    con = db()
    for kw in re.findall(r"[\u4e00-\u9fff]{2,4}", question):
        for r in con.execute("SELECT id,name_chn,origin_raw,source_locator FROM persons "
                             "WHERE description LIKE ? OR source_quote LIKE ? LIMIT 2",
                             ("%" + kw + "%", "%" + kw + "%")):
            chunks.append("檢索 [persons id=%d] %s — %s — %s" % (
                r["id"], r["name_chn"], r["origin_raw"], r["source_locator"]))
        if len(chunks) > 60:
            break
    con.close()
    return "\n".join(chunks[:80])


def ask_deepseek(question, context):
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("no-key")
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "資料：\n%s\n\n問題：%s" % (context, question)},
        ],
        "stream": False,
    }
    req = urllib.request.Request(
        DEEPSEEK_URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
        method="POST")
    with urllib.request.urlopen(req, timeout=120) as fh:
        data = json.loads(fh.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"], data.get("usage", {})


# ---------------------------------------------------------------- http

class Handler(BaseHTTPRequestHandler):
    def send(self, status, body: bytes, kind: str):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, obj, status=200):
        self.send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                  "application/json; charset=utf-8")

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            return self.send(200, INDEX_HTML.read_bytes(), "text/html; charset=utf-8")
        if u.path == "/api/health":
            return self.send_json({"ok": True, "persons": len(G["nodes"]),
                                   "edges": len(G["edges"]), "by_type": G["meta"]["by_type"],
                                   "model": "deepseek" if os.environ.get("DEEPSEEK_API_KEY")
                                   else "no-key (local retrieval only)"})
        if u.path == "/api/people":
            return self.send_json(people())
        if u.path == "/api/ego":
            nid = None
            if q.get("id"):
                nid = int(q["id"][0])
            elif q.get("name"):
                nid = G["by_name"].get(q["name"][0])
            data = ego(nid) if nid else None
            if not data:
                return self.send_json({"error": "庫中沒有此人"}, 404)
            return self.send_json(data)
        if u.path == "/api/person":
            name = q.get("name", [""])[0]
            nid = G["by_name"].get(name)
            if not nid:
                con = db()
                row = con.execute("SELECT id FROM persons WHERE name_chn=? OR name_original=? "
                                  "LIMIT 1", (name, name)).fetchone()
                con.close()
                nid = row["id"] if row else None
            if not nid:
                return self.send_json({"error": "庫中沒有「%s」" % name}, 404)
            return self.send_json(person_bundle(nid))
        self.send(404, b"not found", "text/plain")

    def do_POST(self):
        if urlparse(self.path).path != "/api/ask":
            return self.send(404, b"not found", "text/plain")
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:  # noqa: BLE001
            return self.send_json({"error": "bad json"}, 400)
        question = (body.get("question") or "").strip()
        if not question:
            return self.send_json({"error": "empty question"}, 400)
        context = build_context(question)
        try:
            answer, usage = ask_deepseek(question, context)
            return self.send_json({"answer": answer, "source": "deepseek:" + DEEPSEEK_MODEL,
                                   "usage": usage, "context": context})
        except RuntimeError:
            return self.send_json({
                "answer": "尚未設置 DEEPSEEK_API_KEY，無法調用模型。\n"
                          "以下只是庫中檢索到的原始行（非模型作答）：\n\n" + (context or "（未檢索到相關人物）"),
                "source": "local-db-only", "context": context})
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            return self.send_json({"answer": "DeepSeek 調用失敗：HTTP %s %s" % (exc.code, detail),
                                   "source": "deepseek-error", "context": context}, 502)
        except Exception as exc:  # noqa: BLE001
            return self.send_json({"answer": "DeepSeek 調用失敗：%s" % exc,
                                   "source": "deepseek-error", "context": context}, 502)

    def log_message(self, fmt, *args):
        print("  " + fmt % args)


if __name__ == "__main__":
    if not DB.exists() or not GRAPH.exists():
        raise SystemExit("missing %s or %s (run code/build_db.py then code/build_graph.py)"
                         % (DB, GRAPH))
    print("Shiji People app -> http://localhost:%d   (Ctrl+C to stop)" % PORT)
    print("graph: %d people, %d relations %s" % (len(G["nodes"]), len(G["edges"]),
                                                 G["meta"]["by_type"]))
    print("model: %s" % ("DeepSeek " + DEEPSEEK_MODEL if os.environ.get("DEEPSEEK_API_KEY")
                         else "no DEEPSEEK_API_KEY -> local retrieval only"))
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
