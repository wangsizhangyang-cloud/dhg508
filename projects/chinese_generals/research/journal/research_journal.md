# 研究日志

## 2026-09-27

- 由模板建项目 `projects/chinese_generals`（`cp` 自 `templates/project_template/`）。
- 题目：建中国古代武将库，出处**只用史书原文**（不用维基百科条目），并写渐进式 skill。
- 原始出处：走中文维基文库（`zh.wikisource.org`）的古籍全文。写 `code/fetch_sources.py`
  抓 25 篇列传，存 `sources/raw/wikisource/`，并记 `wikisource_index.json`（页名、卷篇、URL、修订号）。
  - 教训：书名卷次命名不统一（《史記》作「卷073」，《後漢書》《舊唐書》《明史》作「卷24/卷67/卷125」），
    且访问频繁会 429。改为先 `--probe` 探页名、脚本内退避重试。
- 抽取：按列传分批抽成结构化行；每行必须带**逐字** `source_quote`，并与原文机器核对通过再落盘。
  共 36 将、260 官职、182 战役、185 将—役联结。
- 建库：`code/build_db.py` 由 `data/` 建 `chinese_generals.db`；8 表（另 2 视图），
  共 **866 行**（远超 200）。外键 6 处（states→dynasties、generals→states/dynasties、
  titles→generals、general_battles→generals/battles）。
- 核对：`code/verify.py` 整库逐字核对 **698/698** 通过；`code/check_sample.py` 抽 20 行写入
  `research/outputs/verification.md`。人工核年份（`artifacts/date_report.txt`）时发现 6 处数据缺陷：
  5 将 `died_raw` 漏填、馬援 `died_year` 缺——已按原文补齐/换算（见 `verification.md` 错误表）。
- 存疑留档：呂布卒年（199／建安三年之歧）、岳飛等卒年从阙、生年多不载。

## 待办

- 可继续扩将（加 `data/generals/batchNN.json` 重跑即可），并补出土文献/墓志等他源。
