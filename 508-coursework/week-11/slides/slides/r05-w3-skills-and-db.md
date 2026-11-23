---
minutes: 0
---

# Session 3 · Progressive skills &amp; relational tables linked by keys.

<div class="body">
<div class="file"><div class="file-bar">.opencode/skills/history-db/SKILL.md</div><pre>
<span class="dim"># YAML frontmatter loaded first:</span>
name: history-db
description: Query the 1908 roster database
  and cite every row by [id].
&nbsp;
<span class="dim"># Body loaded only when invoked:</span>
1. Answer only from table rows; attach [id].
2. State gaps plainly; never fill from memory.
</pre></div>
<div class="frame hot"><span class="label">Relational Database · One Fact in One Place</span><div class="text">

- **`people` table:** `P2 李应林 → L2`, `P3 冼玉清 → L2`
- **`places` table:** `L2 | 南海 | 广州府 | 佛山` (written **once**)
- **Why foreign keys (`place_id`):** names vary (`钟荣光 / 鍾榮光`, `南海 / 南海县`); stable IDs prevent contradictions across 300 rows

</div></div>
</div>

::read::
Session 3: Skills load `name` + `description` first and pull full Markdown instructions on demand; relational databases store each entity once and link tables by stable IDs (`place_id → id`).
