# 《史記》人物關係 — the app

Week 5's app, built on `../shiji_people.db` and `../data/extracted/graph.json`
(611 people, 112 卷, every fact with a 《史記》 locator). A Python server, one
web page, and a **real DeepSeek call**.

```powershell
# from projects/shiji_people
python code\build_db.py           # if not built yet
python code\build_graph.py        # derives the relation graph
$env:DEEPSEEK_API_KEY = "sk-..."  # keep it in the environment, never in a file
python app\server.py              # then open http://localhost:8000
PORT=8765 python app\server.py    # if 8000 is taken
```

Without a key the app still runs: the 問一問 tab then returns the **retrieved DB
rows** labelled `local-db-only` instead of a model answer.

## The two screens

1. **檢索（landing page）** — a search box over all 611 people, filterable by
   篇類 (本紀/世家/列傳) and 國, each card showing 籍貫 and how many relations
   they have. Click a person.
2. **人物關係網（ego network）** — only **that person and their neighbours**.
   Unrelated people never appear. The centre is the person; each neighbour is
   placed on a ring and joined by an edge coloured by relation type:

   | Edge colour | Type | How it is read from 《史記》 |
   |---|---|---|
   | 深紅 | 親屬 | `relations` (+ name resolution) |
   | 藍 | 君臣 | 「事(B)」「臣事(B)」「為(B)相」「(B)之臣」 |
   | 橙（虛線） | 敵對 | one phrase names both people round a hostile verb |
   | 紫（點線） | 敵國 | 「伐齊」「攻趙」 — the person attacked that 國; the neighbour is of it |
   | 灰 | 同國 | same 國, preferring those seen in the same 卷 |

   Click an edge to read its 《史記》 quote and locator; click a neighbour to
   open *their* network (a back button walks the trail). The side panel shows
   籍貫、國、時期、本傳引文、官職、事件、見於哪些卷, each with `[table id=…]`.

   **Controls.** Each relation type is a button: click to hide/show that kind of
   edge (親屬/君臣/敵對/敵國/同國). A 時期 selector filters by era — 全部 / ±1 期 /
   僅同期人 (default), so a 秦漢之際 man like 項羽 is not shown beside a 春秋 楚
   man; every person carries an era from their 本傳 卷次 (上古→西周→春秋→戰國→
   秦漢之際→漢), shown on hover and in the side panel.

   Every one of the 611 people has a page. Some (99) have no derivable
   relation yet — the page says so rather than inventing one.

3. **問一問** — the server pulls the relevant rows and asks DeepSeek, which must
   cite `[table id=N]` and 《史記·卷篇》.

## Where the fixture was, and what replaced it

The demo's `ask_model()` returned `fixtures/model-response.json` for every input.
Here the corresponding spot is `ask_deepseek()` in `server.py`: a real
`POST https://api.deepseek.com/chat/completions` with `model=deepseek-flash`
(override with `DEEPSEEK_MODEL`), `Authorization: Bearer $DEEPSEEK_API_KEY`,
non-streaming. There is no fixture file.

The system prompt pins the Week 4 rules: answer only from the supplied rows, cite
`[table id=N]` + `source_locator`, say 庫中沒有 when absent, never convert 紀年 to
公元, never fabricate 《史記》 text, refuse off-topic questions.

## Endpoints

| Method | Path | Returns |
|---|---|---|
| GET | `/` | the page |
| GET | `/api/health` | `{ok, persons, edges, by_type, model}` |
| GET | `/api/people` | everyone with degree (search page) |
| GET | `/api/ego?id=N` or `?name=白起` | one person + neighbours only |
| GET | `/api/person?name=白起` | offices / events / mentions |
| POST | `/api/ask` | `{question}` → `{answer, source, usage, context}` |

## Honest limits

- 親屬/敵對 are exact but rare (24 / 1 edges). Beyond the automatic derivation
  there is a curated layer, `../data/manual/graph-edges.json`: 45 relations
  (君臣/親屬) checked one by one, each with a verbatim 《史記》 sentence and its
  卷篇. Eight people who have no `==小節==` heading in their 卷 (韓信, 項梁,
  范增, 扶蘇, 趙高, 蒙毅, 田橫, 田榮) are added by
  `../data/manual/02-missing-persons.json`, also with quotes.
- 國 comes only from the 卷篇 (世家/本紀) and the 籍貫 — never from the first
  character of a name (夏侯婴 is 沛人/漢, not 夏; 韓非 is 韓, but 老子 is 楚 and
  莊子 is 未定). Origins that only say 「其先齊人」 (蒙恬) stay 未定, and
  place-names that look like states (陳留、潁川、隴西) are not read as 陳/韓/秦.
- 敵國 and 同國 are **國-level**: they pair people of the same or opposing 國 and
  can join figures of different generations. Each edge carries its quote so the
  reader can judge; this is stated in the page legend too.
- 君臣 comes from service phrases and a small alias table (秦昭王→秦昭襄王 …).

## Files

| File | What it does |
|---|---|
| `server.py` | stdlib HTTP server: page, SQLite, `graph.json`, DeepSeek |
| `static/index.html` | search page + ego network + ask box (plain HTML+JS, no libraries) |
| `../code/build_graph.py` | derives the graph from the extracted rows |

Python standard library only (OpenCC needed only by the build scripts).
