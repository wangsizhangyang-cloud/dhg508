# 表与列（reference）

库文件：`shiji_people.db`（项目根）。共 **7 张表 + 2 个视图**，6 处外键，全部事实行都有
`source`、`source_locator`、`source_quote` 与 `note`。

```text
chapters(id, slug, juan, category, title_original, title_chn,
         source, source_locator, source_url, pageid, revision, note)

persons(id, key, name_chn, name_original, heading_original, alt_names, category,
        origin_raw, description, source, source_locator, source_url,
        source_quote, note)

person_chapters(id, person_id → persons.id, chapter_id → chapters.id,
                relation_kind, source, source_locator, source_url,
                source_quote, note)                       -- 本傳 / 提及

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
```

外键共 6 处：`person_chapters.person_id`、`person_chapters.chapter_id`、
`offices.person_id`、`events.person_id`、`relations.person_id`、
`relations.related_person_id`。

## 两个视图

- `persons_view`：人物一行，带出**本傳**所屬的卷與篇名，最常用。
- `chapter_people_view`：卷 × 人物 × `relation_kind`，用来「谁见于哪一卷」。

## 几个约定

- `category`：`本紀` / `世家` / `列傳`（另有 `表` / `書` 兩類未收人物）。
- `name_original` 保留《史記》小節標題的原字；`name_chn` 是繁→簡標準名（規則見
  `dates-and-names.md`），兩者並存。
- `source_locator` 形如 `史記·卷七十三白起王翦列傳第十三·白起`：書 · 卷篇 · 小節。
- `source_quote` **逐字**取自該卷處理後原文（`sources/processed/`），可回原文核對。
- `conversions` 記錄每一次**日期或名字**標準化：`original → normalized` 及所用 `rule`。
