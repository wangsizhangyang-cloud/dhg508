# 《史記》人物库（shiji_people）

一份「抓《史記》原典 → 抽成有据的行 → 建关系库 → 核对 → 写成渐进式 skill」的作业。
收录《史記》**本紀＋世家＋列傳共 112 卷**所载人物：姓名、籍贯、本传小节、官职、事件、亲属，
以及「人物见於哪一卷」。每一条事实都以**《史記》原文**为据，**不用维基百科条目**。
答题 skill 在 `skills/shiji-db/SKILL.md`，扩库 skill 在 `skills/shiji-ingest/SKILL.md`。

## 文件

| 文件 | 是什么 |
|---|---|
| `shiji_people.db` | SQLite：7 表 + 2 视图，6 外键，共 **4331 行** |
| `sources/raw/wikisource/shiji-NNN.wiki` | 112 卷《史記》原文 wikitext（只读） |
| `sources/raw/sources_index.json` | 清单：卷次／篇名／pageid／revision／URL |
| `sources/processed/shiji-NNN.txt` | 清理后的正文（供逐字回查） |
| `data/extracted/{chapters,persons}.json` | 抽取出的行（每人带逐字 `source_quote`） |
| `data/manual/` | 手工订正／补录（按 key 覆盖，不删生成行） |
| `code/` | 抓取、抽取、建库、核对、查询脚本（Python 标准库 ＋ OpenCC） |
| `skills/shiji-db/` | 答题 skill（`SKILL.md` ＋ reference/queries/dates-and-names/examples） |
| `skills/shiji-ingest/` | 扩库 skill（抓原文→抽行→建库→核对，答问交回 shiji-db） |
| `rubric.md` · `test-questions.md` · `improvement-log.md` · `questions.md` | 评分、10 题测试、改进日志、未决问题 |
| `research/` | 设计、日志、出处、扩库步骤、日期规则、抽查与错误表 |
| `artifacts/` | 中间产物，不入 git |

## 数据模型

```text
chapters(id, slug, juan, category, title_original, title_chn,
         source, source_locator, source_url, pageid, revision, note)

persons(id, key, name_chn, name_original, heading_original, alt_names, category,
        origin_raw, description, source, source_locator, source_url,
        source_quote, note)

person_chapters(id, person_id → persons.id, chapter_id → chapters.id,
                relation_kind, source, source_locator, source_url,
                source_quote, note)                          -- 本傳 / 提及

offices(id, person_id → persons.id, title_chn, title_original,
        period_raw, period_norm, source, source_locator, source_url,
        source_quote, note)

events(id, person_id → persons.id, event_type, year_raw, year_norm, place,
       description, source, source_locator, source_url, source_quote, note)

relations(id, person_id → persons.id, related_name,
          related_person_id → persons.id, relation_type,
          source, source_locator, source_url, source_quote, note)

conversions(id, entity_type, entity_key, field, original, normalized,
            rule, source, source_locator, note)

persons_view / chapter_people_view   -- 只读视图，回答时用
```

外键 6 处（`person_chapters.person_id`、`person_chapters.chapter_id`、
`offices.person_id`、`events.person_id`、`relations.person_id`、
`relations.related_person_id`）。每行都有 `source`（书名）与 `source_locator`（卷/篇，即“页”）；
事实行另有逐字 `source_quote`；不确定处写在 `note`。

## 怎么重建

```powershell
# 1) 抓原文（需联网；慢，约 10s/卷）
python code\fetch_sources.py --probe        # 只看页面是否存在
python code\fetch_sources.py                # 抓 112 卷
python code\fetch_sources.py --reindex      # 由已有文件重建清单

# 2) 清文＋抽行，3) 建库
python code\extract.py
python code\build_db.py

# 4) 核对：逐字回原文 + 抽 20 行
python code\verify.py                       # -> research/outputs/verification.md

# 随手查库
python code\query.py person 白起
python code\query.py offices 白起
python code\query.py mentions 孔丘
python code\query.py chapter 73
```

## 出处与核对

事实以《史記》原文为据，原文在 `sources/raw/wikisource/`，正文在 `sources/processed/`。
`code/verify.py` 把库中**每一条** `source_quote`（含人名、籍贯）回原文逐字核对：
**2711/2711 通过，0 失败**；另以固定种子抽 20 行人工比对（见
`research/outputs/verification.md`），历次抽查发现并修正的 11 处问题记于
`research/outputs/row-check-errors.md`。

## 怎么扩库

加一卷 → 跑 `fetch_sources.py`／`extract.py`／`build_db.py`／`verify.py` 即可；
老行以 `key`／`slug` 为准不被破坏。手工订正写 `data/manual/*.json`。完整步骤见
`research/notes/how-to-grow.md`，操作见 `skills/shiji-ingest/SKILL.md`。

## 引用

用库回答时标 `[表 id=…]` 与出处（`《史記·卷篇·小節》`），例：

『白起者，郿人也 `[persons id=470]`（《史記·卷七十三白起王翦列傳第十三·白起》）；
昭王十三年為左庶長 `[offices id=46]`。』

## 运行环境

Python 3 ＋ `opencc-python-reimplemented`（`pip install opencc-python-reimplemented`）。
数据库文件不入 git（见 `.gitignore`）。
