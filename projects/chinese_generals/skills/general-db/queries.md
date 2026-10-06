# 例查询

只读工具（标准库，无需安装）：

```powershell
python code\query.py generals              # 全部武将 + 朝代/生卒
python code\query.py general guanyu        # 一位将：官职 + 战役
python code\query.py dynasty 唐             # 某朝代的将
python code\query.py state shuhan
python code\query.py battle 合肥之戰
python code\query.py search 長平           # 关键词搜人/功绩/引文
python code\query.py year -260            # 某年的战役
python code\query.py off-topic            # 越界请求的标准回答
```

自己写 Python 也可以（`python` 即可，无依赖）：

```python
import sqlite3
c = sqlite3.connect(r"chinese_generals.db")
for r in c.execute("SELECT id,name_chn,state,dynasty,born_year,died_year FROM generals_view ORDER BY id"):
    print(r)
```

常用 SQL：

```sql
-- 一位将的官职（带出处）
SELECT id, title_chn, title_original, period, source, source_locator, source_quote
FROM titles WHERE general_id = (SELECT id FROM generals WHERE key='guanyu') ORDER BY id;

-- 一位将参加的战役
SELECT * FROM battle_roles_view WHERE general = '關羽' ORDER BY year;

-- 一役的参与者
SELECT general, role, outcome, source_url FROM battle_roles_view WHERE battle = '合肥之戰';

-- 跨表：朝代 → 将 → 役 + 出处
SELECT d.name_chn AS dynasty, g.name_chn AS general, b.name_chn AS battle, b.year,
       gb.source_locator, gb.source_url
FROM general_battles gb
JOIN generals g ON g.id = gb.general_id
JOIN dynasties d ON d.id = g.dynasty_id
JOIN battles b ON b.id = gb.battle_id
WHERE d.name_chn = '三國' AND b.year = 219;

-- 某条换算原文→标准化
SELECT entity_key, field, original, normalized, rule FROM conversions WHERE entity_key='lvbu';
```

引用时取 `source` + `source_locator` + `source_url`，并标 `[id]`。
