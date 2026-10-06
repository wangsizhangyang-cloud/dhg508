# data/manual

手工订正／补录目录。`build_db.py` 会把这里所有 `*.json` 读入，按 `persons[].key` **覆盖**
`data/extracted/persons.json` 中同一 `key` 的字段（只覆盖给出的字段，不删除行）。

形状与 `data/extracted/persons.json` 相同，例如：

```json
{
  "persons": [
    {
      "key": "shiji-073-01",
      "origin_raw": "郿人",
      "note": "手工校：籍貫從「郿」。——示例，未實際使用"
    }
  ]
}
```

适合：修正某人的籍贯/名字、补一条确凿的官职或事件、为没有独立小节的人物补录。
不要在这里改 `source_quote` 以外的原文；引文仍须能回 `sources/processed/` 找到。
