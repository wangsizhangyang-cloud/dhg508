# 中国古代武将库（Chinese generals）

一份「抓史书原文 → 抽成有据的行 → 建关系库 → 核对 → 写成渐进式 skill」的作业。
**36 位中国古代武将**的生卒、战役、功绩、官职、描述，全部以**史书原文**为据
（史記／漢書／後漢書／三國志／晉書／舊唐書／新唐書／宋史／明史），**不用维基百科条目**。
skill `skills/general-db/SKILL.md` 按这些行回答问题并给出处。

## 文件

| 文件 | 是什么 |
|---|---|
| `chinese_generals.db` | SQLite：8 表 + 2 视图，共 **866 行** |
| `data/generals/batchNN.json` | 抽取的行为源数据（每行带逐字 `source_quote`） |
| `data/reference/{dynasties,states,calendar}.json` | 朝代、政权、纪年基准 |
| `sources/raw/wikisource/` | 25 篇史书原文；`wikisource_index.json` 记页名/卷篇/URL/修订号 |
| `code/` | 抓取、建库、核对、查询脚本（Python 标准库，无需安装） |
| `skills/general-db/` | 答题 skill（`SKILL.md` + `reference.md`/`queries.md`/`dates-and-names.md`/`examples.md`） |
| `skills/general-ingest/` | 扩库 skill（抓原文→抽行→建库→核对，答问交回 general-db） |
| `rubric.md` · `test-questions.md` · `improvement-log.md` · `questions.md` | 评分、10 题测试、改进日志、未决问题 |
| `research/` | 设计、日志、出处、扩库步骤、日期规则、核对报告 |
| `artifacts/` | 中间产物（年份对照表等），不入 git |

## 数据模型

```text
dynasties(id, key, name_chn, period_note, source, source_locator, note)
states(id, key, name_chn, dynasty_id → dynasties.id, source, note)

generals(id, key, name_chn, name_original, courtesy_name,
         state_id → states.id, dynasty_id → dynasties.id,
         born_raw, born_year, died_raw, died_year,
         achievement, description, source, source_locator, source_quote, note)

battles(id, key, name_chn, name_original, year, year_raw, place,
        source, source_locator, source_quote, note)

general_battles(id, general_id → generals.id, battle_id → battles.id,
                role, outcome, source, source_locator, source_quote, note)

titles(id, general_id → generals.id, title_chn, title_original, period,
       source, source_locator, source_quote, note)

conversions(id, entity_type, entity_key, field, original, normalized, rule, source, note)
calendar(id, state_key, system, source, note)

generals_view / battle_roles_view   -- 只读视图，回答时用
```

外键 6 处（`states.dynasty_id`、`generals.state_id`、`generals.dynasty_id`、
`titles.general_id`、`general_battles.general_id`、`general_battles.battle_id`）。
每行都带 `source`（书名）与 `source_locator`（卷/篇，即“页”）；事实行另有逐字 `source_quote`。

## 36 位武将

白起 · 王翦 · 蒙恬 · 項羽 · 韓信 · 李廣 · 衛青 · 霍去病 · 趙充國 · 馬援 · 班超 ·
呂布 · 張遼 · 張郃 · 徐晃 · 關羽 · 張飛 · 馬超 · 黃忠 · 趙雲 · 周瑜 · 呂蒙 · 陸遜 ·
羊祜 · 杜預 · 陶侃 · 李靖 · 李勣 · 郭子儀 · 薛仁貴 · 韓世忠 · 岳飛 ·
徐達 · 常遇春 · 戚繼光 · 俞大猷

## 怎么重建

```powershell
# 1) 建库（读 data/ + 原文索引，无需联网）
python code\build_db.py

# 2) 整库逐字核对 + 抽 20 行
python code\verify.py
python code\check_sample.py     # -> research/outputs/verification.md
python code\date_report.py      # -> artifacts/date_report.txt

# 3) 随手查库
python code\query.py generals
python code\query.py general guanyu
python code\query.py dynasty 唐
python code\query.py battle 合肥之戰
```

重新抓史书原文（需要联网，中文维基文库）：

```powershell
python code\fetch_sources.py --probe
python code\fetch_sources.py
```

## 出处与核对

事实以史书原文为据，原文存于 `sources/raw/wikisource/`。`code/verify.py` 把库中**每一句**
`source_quote`（含将领 `born_raw`/`died_raw`）回原文逐字核对，**698/698 通过**；
另抽 20 行人工比对见 `research/outputs/verification.md`（内含 6 处数据缺陷的原因与修正）。

## 怎么扩库

加一篇史书 → 抽成带逐字引文的新 `data/generals/batchNN.json` → 重跑 `build_db.py` 与
`verify.py` 即可；老行以 `key` 为准，不被破坏。完整步骤见 `research/notes/how-to-grow.md`，
操作见 `skills/general-ingest/SKILL.md`。

## 引用

用库回答时标 `[id]` 与出处（`《書·卷篇》`），例：
『白起於長平大破趙軍，坑殺降卒四十萬 `[battles id=6]`（《史記·卷七十三·白起王翦列傳》）。』
