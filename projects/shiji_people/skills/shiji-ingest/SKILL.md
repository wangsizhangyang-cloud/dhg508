---
name: ShijiIngest
description: Add new material to the shiji_people database — fetch a 《史記》 卷 from Wikisource, turn it into grounded rows with verbatim quotes, rebuild, and verify. Use when the task is to extend the database (a new 卷/篇 or person) rather than to answer a question.
---

# ShijiIngest（扩库）

## 这个 skill 做什么

往 `shiji_people.db` **加新材料**：抓一卷《史記》原文 → 清成正文 → 抽成带逐字引文的行 →
建库 → 核对。加完把问答应交回 **ShijiDB**（`../shiji-db/SKILL.md`）。

## 步骤（照做，详见 `research/notes/how-to-grow.md`）

1. **抓原文**：`python code\fetch_sources.py`（默认抓本紀＋世家＋列傳 112 卷；
   只抓某卷：`python code\fetch_sources.py 65`）。原文入 `sources/raw/wikisource/*.wiki`，
   **只读不改**；`sources/raw/sources_index.json` 记页名／卷次／URL／修订号。
2. **抽行**：`python code\extract.py`。它把 wikitext 清成 `sources/processed/*.txt`，
   再按 `==小節==` 抽人物，逐條寫 `data/extracted/{chapters,persons}.json`。
   硬规矩：
   - 每行都有 `source_locator`（書·卷篇·小節）与逐字 `source_quote`；
   - 引文必须是该卷处理後正文的**子串**，不改写、不加标点；
   - 人名标准名（繁→简）另存 `name_chn`，原文名存 `name_original`，不改原字；
   - 纪年只抽「纪年主体＋年序」存 `year_norm`，**不换算公元**。
   需要手工订正时，写 `data/manual/NN.json`（形状同 `data/extracted/persons.json`），
   按 `key` 覆盖，不删生成行。
3. **建库**：`python code\build_db.py`（按 `key`/`slug` 重建，老行不破坏）。
4. **核对**：`python code\verify.py` 必须 **0 失败**；另抽 20 行人工比对
   （`research/outputs/verification.md`）。失败就回原文改，重跑第 2–4 步。

## 交回

新卷入库後，**用 ShijiDB 的规矩回答**（`[id]`＋source），并确认它能被问到。
出处／版本补进 `research/notes/sources.md` 与 `research/references/bibliography.md`；
因答案不佳而改的，记 `improvement-log.md`。
