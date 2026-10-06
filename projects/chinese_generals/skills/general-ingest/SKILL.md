---
name: GeneralIngest
description: Add new material to the chinese_generals database — fetch an original 史書 chapter, turn it into grounded rows with verbatim quotes, rebuild, and verify. Use when the task is to extend the database (a new general, a new source chapter) rather than to answer a question.
---

# GeneralIngest（扩库）

## 这个 skill 做什么

往 `chinese_generals.db` **加新材料**：抓一篇史书原文 → 抽成带逐字引文的行 → 建库 → 核对。
加完把问答应交回 **GeneralDB**（`../general-db/SKILL.md`）。

## 步骤（照做，见 `research/notes/how-to-grow.md`）

1. **抓原文**：在 `code/sources_manifest.json` 加一条；先 `python code\fetch_sources.py --probe`
   确认页名（各书卷次补零不一致、易 429），再 `python code\fetch_sources.py`。
   原文入 `sources/raw/wikisource/`，只读不改。
2. **抽行**：新增 `data/generals/batchNN.json`，形状同现有文件。硬规矩：
   - 每行都要有 `source_slug` / `source_locator` / `source_quote`；
   - `source_quote` **逐字**来自对应原文，不许改写、不许加标点；
   - 日期保留 `*_raw`，公元年用数字（公元前为负），未载就留 `null`；
   - `state_key` 必须在 `data/reference/states.json` 里；不确定写 `note`。
3. **建库**：`python code\build_db.py`（按 `key` 重建，老行不破坏）。
4. **核对**：`python code\verify.py` 必须 0 失败；
   `python code\check_sample.py`、`python code\date_report.py` 供人工复核。
   失败就回原文改 `data/`，重跑第 3、4 步。

## 交回

新将入库后，**用 GeneralDB 的规矩回答**（`[id]` + source），并确认它能被问到。
出处与版本分别补进 `research/notes/sources.md` 与 `research/references/bibliography.md`；
因答案不佳而改的，记 `improvement-log.md`。
