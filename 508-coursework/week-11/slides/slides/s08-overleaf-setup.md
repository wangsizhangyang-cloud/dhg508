---
minutes: 5
---

# Compile on Overleaf with `dhg508-overleaf-template.zip`.

<div class="body">
<div class="term">
<div class="term-bar"><span>Terminal · Local table script</span></div>
<pre>
<span class="blk">$ cp -R 508-coursework/week-11/paper-template \</span>
<span class="blk">    projects/my_project/paper</span>
&nbsp;
<span class="blk">$ python3 projects/my_project/paper/make_evidence_table.py</span>
<span class="ok">Wrote paper/evidence-table.tex</span>
</pre>
<div class="term-foot">Verified on Overleaf (XeLaTeX + Biber)</div>
</div>
<div class="frame hot"><span class="label">Overleaf · 4 Steps</span><div class="text">

1. **New Project → Upload Project** → `dhg508-overleaf-template.zip`
2. **Menu → Compiler → `XeLaTeX`**
3. Click **Recompile**
4. **Download PDF** (`paper/design-paper.pdf`) + **Source** back to Git

</div></div>
</div>

<!--
直接上传 `dhg508-overleaf-template.zip` 到 Overleaf，Menu 切 XeLaTeX 点 Recompile 就能出 PDF；写完把 PDF 和源码下载回你自己的 GitHub `paper/`。
-->

::read::
Upload `dhg508-overleaf-template.zip` to Overleaf, select `XeLaTeX`, click `Recompile`, and commit the PDF and sources back to `paper/`.
