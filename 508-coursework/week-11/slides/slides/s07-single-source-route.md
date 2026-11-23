---
minutes: 5
---

# One source of truth from CSV to PDF.

<div class="route">
<div class="step"><span class="yr">01 · Data</span><p class="what">`evidence.csv`</p><p class="how">`claim · locator · 据/推断/设 · limit`</p></div>
<div class="arrow">→</div>
<div class="step"><span class="yr">02 · Script</span><p class="what">`make_evidence_table.py`</p><p class="how">writes `evidence-table.tex`</p></div>
<div class="arrow">→</div>
<div class="step red"><span class="yr">03 · Overleaf</span><p class="what">`main.tex` + `references.bib`</p><p class="how">`XeLaTeX` + `biblatex-chicago` → PDF</p></div>
</div>

<!--
代码、CSV 证据表、`references.bib` 和最终 PDF 同源，不要手敲表格或另写脱节的 Word。
-->

::read::
`evidence.csv` generates `evidence-table.tex`, which compiles with `main.tex` and `references.bib` on Overleaf.
