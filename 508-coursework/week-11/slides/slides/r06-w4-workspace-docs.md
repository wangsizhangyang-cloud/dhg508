---
minutes: 0
---

# Session 4 · Workspace layout &amp; three kinds of documents.

<div class="body">
<div class="tree"><span class="label">projects/my_project/</span><pre>
├─ AGENTS.md             <span class="hl">rules that always hold</span>
├─ sources/
│  ├─ raw/               <span class="dim">originals, never edited</span>
│  └─ processed/         <span class="dim">OCR, crops, clean .md</span>
├─ research/             <span class="dim">design, journal, notes, refs</span>
├─ artifacts/            <span class="dim">large dumps/DBs (gitignored)</span>
└─ code/                 <span class="dim">repeatable scripts</span>
</pre></div>
<div class="frame hot"><span class="label">Three Document Types · One Job per File</span><div class="text">

1. **Index (`README.md` / `SKILL.md`):** what exists and where to look next
2. **Procedure (`add-data.md`):** step-by-step workflow pointing to schema files
3. **Principles (`AGENTS.md`):** short, hard rules (`raw/` read-only; test before done)

</div></div>
</div>

::read::
Session 4: Every file kind has one canonical folder so both humans and agents can find it; keep documents short and modular across index, procedure, and hard principles (`AGENTS.md`).
