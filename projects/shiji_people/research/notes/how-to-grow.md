# 怎么扩库（how-to-grow）

本库的设计目标：**加新材料＝照同一套步骤再跑一遍，只增行、不破老行。**

## 固定管线

```text
sources/raw/wikisource/shiji-NNN.wiki   （原文，只读，不入 git 之外的改动）
        └─ code/extract.py     ─► sources/processed/shiji-NNN.txt   （清出的正文）
                               └─► data/extracted/chapters.json     （每卷一行的元数据）
                               └─► data/extracted/persons.json      （每人一条嵌套记录）
        └─ code/build_db.py    ─► shiji_people.db                   （7 表 2 视图）
        └─ code/verify.py      ─► research/outputs/verification.md  （完整性＋20 行抽查）
```

## 加一卷（或一批卷）

1. **抓**：`python code\fetch_sources.py`（全量）或 `python code\fetch_sources.py 65`（指定卷）。
   已有文件的卷会重抓覆盖；网络慢时脚本会退避重试。完成後
   `sources/raw/sources_index.json` 记下 `pageid`/`revision`/`source_url`。
2. **清＋抽**：`python code\extract.py`。它会重写 `sources/processed/` 与 `data/extracted/`。
3. **建库**：`python code\build_db.py`。以 `persons.key`、`chapters.slug` 为准，
   老行保持、新行追加；外键用 `PRAGMA foreign_keys` 打开，建完跑 `PRAGMA foreign_key_check`。
4. **核对**：`python code\verify.py` 必须 0 失败；再人工看 `research/outputs/verification.md`
   的 20 行抽查。

> 只加一卷时，`extract.py` 会重算全部卷（幂等）。若只想要增量，可给 `fetch` 指定卷后照常跑全流程，
> 因为 JSON 是按 slug 排序、按 key 去重的。

## 手工订正／补录

放到 `data/manual/NN.json`，形状与 `data/extracted/persons.json` 相同；`build_db.py` 会按 `key`
**覆盖**生成行（只覆盖给出的字段），不删除别的行。适合修某人的籍贯、补一条确凿的官职等。

## 不改代码就能扩的来源

- **新增卷**：如上。
- **新增人物**：多来自新卷；若某人在既有卷里没有独立小节，可写进 manual。
- **新增事实类型**：加表或在 `events.event_type` 里加枚举，再改 `build_db.py` 的插入与
  `skills/shiji-db/reference.md` 的列说明。

## 版本与可复现

`sources_index.json` 记每卷的 `revision`。Wikisource 页面可能被校勘改动；需要严格复现时，
把 `source_url` 换成固定 `oldid=…` 的连结（抓取时用 `action=query&prop=revisions&rvprop=ids`）。
