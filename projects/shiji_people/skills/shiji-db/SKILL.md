---
name: ShijiDB
description: Answer questions about people recorded in 司馬遷《史記》 — who they were, their 籍貫, offices, key events and family relations — from a small SQLite database whose every fact is grounded in the original 《史記》 text. Use when asked about a 史記 person (黃帝, 項羽, 韓信, 張良, 孔子, 屈原, 荊軻, 李廣, 衞青 …) or about which 卷/篇 mentions them.
---

# ShijiDB（《史記》人物庫答問）

## 这个库是什么

`shiji_people.db`（本目录的上两级）是一个 SQLite 库，收录**《史記》中列傳、世家、本紀
各小節所載的人物**：姓名、籍貫、本傳小節、官職、重要行事、親屬關係，以及「誰見於哪一卷」。
每一條事實都來自**《史記》原文**，不是維基百科；原文由中文維基文庫轉錄，並記下頁面版本。

## 什么时候用

有人問《史記》人物的**是誰、哪裡人、做過什麼、任過什麼官、和誰什麼關係、見於哪一卷**時用本庫。
南北朝以後的人、文學虛構人物、與《史記》無關的問題，一律不用（見「庫中沒有答案時」）。

## 怎么引用

1. 每條事實後標 `[id]`（該行主鍵，並寫清是哪張表）。
2. 再給**出處**：`source`（書名）＋ `source_locator`（卷／篇，即「頁」）＋ `source_quote`。
3. 例：
   `白起者，郿人也 `[persons id=1]`（《史記·卷七十三白起王翦列傳第十三·白起》，原文「白起者，郿人也。」）。`

## 库中没有答案时

- 直說「**庫裡沒有**」，**不要**用自己的常識補；若確要提庫外常識，必須標明「這不是庫裡的內容」。
- **不許編造原文／引文**。要「模擬」某人語氣，只能用庫中的行拼接，並醒目標「模擬」。
- 生年多未載：照實說「史書未載」，**不由年齡回推**。
- 問題不在範圍（菜譜、近現代、假前提）：拒絕、或先用庫中行糾正前提，再照實答。

## 细节（按需再读，不要一次全读）

- 每張表有哪些列、兩個視圖是什麼 → `reference.md`
- 可複製的 `python code/query.py …` 與 SQL 範例 → `queries.md`
- 日期與名字的換算規矩、存疑怎麼寫 → `dates-and-names.md`
- 逐字示範與角落情形（越界、假前提、要編引文、日期陷阱）→ `examples.md`

## 语气

像史家：先結論，再 `[id]` 與出處；原文與標準名並列；存疑處明說，不替它選一個。
