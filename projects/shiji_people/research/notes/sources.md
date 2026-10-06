# 出处与取材（sources）

## 规则

- **只用原典**：所有事实来自司馬遷《史記》正文，**不用维基百科条目**（`{{Wikipedia|…}}`
  模板在清理时被显式丢弃）。
- **原文来源**：中文维基文库（`zh.wikisource.org`）所藏的《史記》公有领域**原典文本**，
  按卷抓取，逐卷留档于 `sources/raw/wikisource/shiji-NNN.wiki`（wikitext 原样）。
  这是**一手文献的电子转写**，不是百科条目；每卷记 `pageid` 与 `revision`。
- **“页”＝卷·篇·小节**：`source_locator` 形如
  `史記·卷七十三白起王翦列傳第十三·白起`（书·卷篇·小节标题）。
- **逐字引文**：每条事实的 `source_quote` 必须是该卷处理后正文（`sources/processed/`）的**子串**，
  由 `code/verify.py` 逐条回原文验证。

## 抓取清单

`code/fetch_sources.py` 默认抓：

- 本紀 卷001–012
- 世家 卷031–060
- 列傳 卷061–130

共 **112 卷**（跳过卷013–030 的表／书，它们不是人物传记）。
`sources/raw/sources_index.json` 是清单：`slug / title / juan / pageid / revision / source_url / chars`。

## 已知的文本问题

- 文库正文含后人**校勘记**（`{{註|…}}`、`{{按|…}}` 等）。清理时把整段 meta 模板去掉，
  但个别校勘字仍可能混入；以 `source_quote` 回原文为准。
- 正文用旧字形（`衞`、`髙`、`呉`、`撃`…）与 `-{zh:…}-` 转换标记；清理与繁简转换规则见
  `date-conversion.md` 与 `improvement-log.md`。

## 不入库的东西

- 维基百科条目、网络二手文章、现代论著——一律不取为**事实来源**；如引用须另立“库外”说明。
- `{{Wikipedia|…}}`、页面装饰、导航模板。
