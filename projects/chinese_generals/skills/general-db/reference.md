# 表与视图（库结构）

数据库：`chinese_generals.db`（项目根目录）。8 张表 + 2 个视图。

| 表 | 一行是什么 | 关键列 | 外键 |
|---|---|---|---|
| `dynasties` | 一个朝代/时期 | `id, key, name_chn, period_note, source, source_locator, note` | — |
| `states` | 一个政权（秦、曹魏、蜀漢…） | `id, key, name_chn, dynasty_id, source, note` | `dynasty_id → dynasties.id` |
| `generals` | 一位武将 | `id, key, name_chn, name_original, courtesy_name, state_id, dynasty_id, born_raw, born_year, died_raw, died_year, achievement, description, source, source_locator, source_quote, note` | `state_id → states.id`；`dynasty_id → dynasties.id` |
| `battles` | 一个战役 | `id, key, name_chn, name_original, year, year_raw, place, source, source_locator, source_quote, note` | — |
| `general_battles` | 一位将参加一个役 | `id, general_id, battle_id, role, outcome, source, source_locator, source_quote, note` | `general_id → generals.id`；`battle_id → battles.id` |
| `titles` | 一位将的一个官职/封号 | `id, general_id, title_chn, title_original, period, source, source_locator, source_quote, note` | `general_id → generals.id` |
| `conversions` | 一条「原文→标准化」的换算记录 | `id, entity_type, entity_key, field, original, normalized, rule, source, note` | （逻辑指向 generals/battles） |
| `calendar` | 一个政权的纪年基准 | `id, state_key, system, source, note` | — |

外键共 6 处：

```text
states.dynasty_id          → dynasties.id
generals.state_id          → states.id
generals.dynasty_id        → dynasties.id
titles.general_id          → generals.id
general_battles.general_id → generals.id
general_battles.battle_id  → battles.id
```

视图（回答时优先用）：

- `generals_view`：`generals` 连上 `states`/`dynasties`，多出 `state`、`dynasty` 两列。
- `battle_roles_view`：`general_battles` 连上 `generals`/`battles`，
  列为 `general, battle, year, year_raw, place, role, outcome, source…`。

行数（构建后）：dynasties 10 · states 12 · generals 36 · battles 182 ·
general_battles 185 · titles 260 · conversions 169 · calendar 12，共 **866 行**。

`source` 是书名（如《史記》），`source_locator` 是卷/篇（即“页”），
`source_quote` 是从该篇逐字复制的一句证据。
