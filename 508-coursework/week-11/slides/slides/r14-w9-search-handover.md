---
minutes: 0
---

# Session 9 · Scholarly search rules, index refactoring, and 2-agent handover.

<div class="body">
<div class="frame"><span class="label">Scholarly Search &amp; Doc Refactoring</span><div class="text">

- **`scholarly-search` skill:** OpenAlex API + `agent-browser` (respecting `robots.txt`); Google Scholar / Baidu operated by you in browser
- **Refactor long docs:** split an 850-line `design-document.md` into an ~80-line **master index** linking to `docs/characters/*.md` &amp; `docs/scenes/*.md`

</div></div>
<div class="frame hot"><span class="label">Two-Agent Handover via Git Files</span><div class="text">

- **Agent 1 (Research):** close-reads pages (`[据]` / `[推断]` / `[限定]`) → writes `handover.md` + `data/evidence.csv`
- **Agent 2 (Implementation):** attaches `@handover.md` to build scenes &amp; JSON cards
- **Rule:** chat coordinates work; **committed repository files remain the source of truth**

</div></div>
</div>

::read::
Session 9: Search open indexes via API/CLI while respecting `robots.txt`, refactor overgrown design docs into a master index + modules, and hand off verified claims between Research and Implementation agents through committed files (`handover.md` + `evidence.csv`).
