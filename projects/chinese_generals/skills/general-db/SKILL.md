---
name: GeneralDB
description: Answer questions about ancient Chinese generals — birth and death years, battles, achievements, offices (官職) — from a small SQLite database whose every row is grounded in an original 史書 passage. Use when asked about Chinese historical 武將 / 名將 (白起, 韓信, 關羽, 岳飛, 戚繼光 …), their wars, ranks or dates.
---

# GeneralDB（武將庫答問）

## 这个库是什么

`chinese_generals.db`（在同一目录的上两级）是一个 SQLite 库：**36 位中国古代武将**的
生卒、战役、功绩、官职与描述，跨 秦／西楚／兩漢／三國／兩晉／唐／南宋／明。
每一条事实都来自**史书原文**（史記、漢書、後漢書、三國志、晉書、舊唐書、新唐書、宋史、明史），
不是维基百科。

## 什么时候用

有人问这些武将的**生卒、战役、官職、功績、描述**，或要按朝代/战役查将时用本库。
库外的（菜谱、近现代、文学人物等）不用。

## 怎么引用

- 每条事实后标 `[id]`（该行的主键）。
- 再给**出处**：`source`（书名）+ `source_locator`（卷/篇）+ `source_url`。
- 例：`白起在長平大破趙軍，坑殺降卒四十萬 [battles id=6]（《史記·卷七十三·白起王翦列傳》）`。

## 库中没有答案时

- 直说「**库裡沒有**」，**不用**自己的常识补；若要点出库外常识，必须标注「这不是库里的内容」。
- **不许编造原文/引文**。要「扮演」某将，只能用库里的行拼接，并标注「模拟」。
- 生年多为 `null`、个别卒年未载：照实说「史书未载」，**不推算**。

## 细节（按需再读）

- 每张表有哪些列、视图是什么 → `reference.md`
- 可复制的查询 `python code/query.py …` 与 SQL → `queries.md`
- 日期（负数＝公元前）与名字标准化的规矩 → `dates-and-names.md`
- 逐字示范与三个角落情形（越界、假前提、要编引文）→ `examples.md`

## 语气

像史家：先结论，再 `[id]` 与出处；存疑处明说，不替它选一个。
