# 参考与出处（bibliography）

## 一手文献（本库唯一事实来源）

- 司馬遷：《史記》，全 130 篇。本库使用 **本紀 12 ＋ 世家 30 ＋ 列傳 70 ＝ 112 卷**。
  电子文本取自中文维基文库公版转写，按卷抓取，逐卷留档并记修订号。

  逐卷的卷次、篇名、页面 ID、修订号与 URL，见机读清单
  `sources/raw/sources_index.json`；原文原件在 `sources/raw/wikisource/shiji-NNN.wiki`，
  清理后的正文在 `sources/processed/shiji-NNN.txt`。

  示例条目（完整 112 条见上清单）：

  | slug | 卷篇 | 来源页 |
  |---|---|---|
  | shiji-007 | 卷七 項羽本紀 第七 | https://zh.wikisource.org/wiki/史記/卷007 |
  | shiji-073 | 卷七十三 白起王翦列傳 第十三 | https://zh.wikisource.org/wiki/史記/卷073 |
  | shiji-086 | 卷八十六 刺客列傳 第二十六 | https://zh.wikisource.org/wiki/史記/卷086 |
  | shiji-109 | 卷一百九 李將軍列傳 第四十九 | https://zh.wikisource.org/wiki/史記/卷109 |
  | shiji-111 | 卷一百十一 衛將軍驃騎列傳 第五十一 | https://zh.wikisource.org/wiki/史記/卷111 |
  | shiji-130 | 卷一百三十 太史公自序 第七十 | https://zh.wikisource.org/wiki/史記/卷130 |

## 工具

- OpenCC（`hk2s`）用于繁→简与异体字统一（名字与职官名的标准名）。
- Python 标准库 `sqlite3`／`urllib`；无第三方运行依赖（除 OpenCC）。

## 未采用

- 维基百科及其它百科条目、网络二手文章——**不作为事实来源**；如需引用，须标注「库外」。
