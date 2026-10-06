# 示例查询（queries）

先把工作目录放在项目根，然后：

```powershell
python code\query.py person 白起          # 某人的行 + 籍貫 + 本傳引文
python code\query.py offices 白起         # 某人官職（帶紀年）
python code\query.py events 荊軻          # 某人事件（分類 + 紀年）
python code\query.py relations 周公旦     # 某人親屬關係
python code\query.py mentions 孔子        # 這人見於哪些卷
python code\query.py chapter 73           # 卷七十三的基本信息
python code\query.py search 長平          # 引文全文搜索
python code\query.py off-topic            # 越界問題的標準答法
```

等價 SQL（可直接 `python code\query.py sql "…"`）：

```sql
-- 「白起是誰、哪裡人、出處」
SELECT name_chn, origin_raw, source_locator, source_quote
FROM persons WHERE name_chn = '白起';

-- 「白起任过哪些官」——跨表：persons × offices
SELECT p.name_chn, o.title_chn, o.period_norm, o.source_quote
FROM persons p JOIN offices o ON o.person_id = p.id
WHERE p.name_chn = '白起';

-- 「誰見於卷七十三」（跨表：chapters × person_chapters × persons）
SELECT c.juan, p.name_chn, pc.relation_kind
FROM person_chapters pc
JOIN persons p  ON p.id = pc.person_id
JOIN chapters c ON c.id = pc.chapter_id
WHERE c.juan = 73;

-- 「荊軻有哪些『卒/死』以外的事件」
SELECT event_type, year_norm, source_quote
FROM events e JOIN persons p ON p.id = e.person_id
WHERE p.name_chn = '荊軻';

-- 「某卷的人物總表」
SELECT name_chn, heading_original FROM persons
WHERE source_locator LIKE '史記·卷八十六%';
```

回答时记住：每条事实后面标 `[表名 id=…]` 并附 `source_locator`。
