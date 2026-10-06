# 怎么扩库（同样的步骤，跑一遍即可）

新增材料的流程是**固定的**：抓原文 → 抽成带逐字引文的行 → 建库 → 核对。
老行以 `key` 为准，新增文件不会破坏老行。

## 0. 环境

只依赖 Python 标准库（本机 `python` 即可）。

## 1. 抓原文（`sources/raw/`）

1. 在 `code/sources_manifest.json` 里加一条：
   `{"slug": "songshi-366", "title": "宋史/卷366", "text": "宋史", "section": "...", "people": ["..."]}`
   —— `title` 是维基文库页名（**注意各书卷次补零不一致**，先 `--probe`）。
2. `python code\fetch_sources.py --probe`，确认页名存在。
3. `python code\fetch_sources.py`，抓全文 → `sources/raw/wikisource/`，并更新
   `sources/raw/wikisource_index.json`。
   - 原文只读，不就地改；清洗后的文本放 `sources/processed/`。

## 2. 抽成行（`data/generals/`）

新增 `data/generals/batchNN.json`，形状与现有文件一致：

```json
{"generals": [{
  "key": "ascii-slug", "name_norm": "标准名", "name_original": "史书原写",
  "courtesy_name": "字", "state_key": "见 data/reference/states.json",
  "born_raw": "原文生年用语或空", "born_year": null,
  "died_raw": "原文卒年用语", "died_year": -257,
  "achievement": "...", "description": "...", "note": "存疑处",
  "source_slug": "songshi-366", "source_locator": "宋史·卷三百六十六·某某傳",
  "source_quote": "从原文逐字复制的一句",
  "titles":  [{"title_norm":"","title_original":"","period":"","note":"","source_slug":"","source_locator":"","source_quote":""}],
  "battles": [{"key":"","name_norm":"","name_original":"","year":null,"year_raw":"","place":"","note":"","role":"","outcome":"","source_slug":"","source_locator":"","source_quote":""}]
}]}
```

硬规矩：

- **每一行**（将军、每条官职、每个战役）都要有 `source_slug`、`source_locator`、`source_quote`。
- `source_quote` 必须**逐字**来自 `sources/raw/wikisource/<slug>.txt`，不许改写、不许加标点。
- 日期：原文写 `*_raw`，公元年写数字（公元前为负），为 null 就留空 `year`。
- `state_key` 必须已在 `data/reference/states.json` 中。
- 不确定照实写进 `note`，不猜。

## 3. 建库（根目录 `chinese_generals.db`）

```powershell
python code\build_db.py
```

它会读 `data/generals/*.json` + `data/reference/*.json`，重建全部表；同名战役按
`(名, 年, 原文年)` 自动合并，其他表按 `key` 唯一。

## 4. 核对

```powershell
python code\verify.py          # 整库逐字核对 + 抽 20 行
python code\check_sample.py    # 20 行写 research/outputs/verification.md
python code\date_report.py     # 所有年份「原文→标准化」对照，供人工核
```

`verify.py` 必须 0 失败。失败就回原文找正确写法，修 `data/`，重跑第 3、4 步。

## 5. 归档

- 新原文列入 `research/notes/sources.md`。
- 版本/整理本列入 `research/references/bibliography.md`。
- 因答案不佳而改动的，记 `improvement-log.md`。
