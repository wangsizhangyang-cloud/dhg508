---
minutes: 5
---

# Citations: `biblatex-chicago` (Notes-Bibliography).

<div class="body">
<div class="file"><div class="file-bar">paper/main.tex</div><pre>
<span class="hl">\usepackage[notes, backend=biber,</span>
<span class="hl">  autolang=other, isbn=false]{biblatex-chicago}</span>
\addbibresource{references.bib}
&nbsp;
% Place \autocite[page]{key} after punctuation:
Demand management never produces a certain
result.<span class="hl">\autocite[150]{tobin1986macro}</span>
&nbsp;
<span class="hl">\printbibliography[title={Bibliography}]</span>
</pre></div>
<div class="file"><div class="file-bar">paper/references.bib</div><pre>
@incollection{tobin1986macro,
  author         = {Tobin, James},
  title          = {Luelun fei jizhongxing jingji
                    de hongguan kongzhi},
  <span class="hl">titleaddon     = {略論非集中型經濟的宏觀控制},</span>
  <span class="hl">usere          = {On Macroeconomic Control in</span>
  <span class="hl">                  Decentralized Economies},</span>
  booktitle      = {Hongguan jingji de guanli yu gaige},
  booktitleaddon = {宏觀經濟的管理與改革},
  publisher      = {Jingji ribao chubanshe},
  location       = {Beijing},
  date           = {1986},
  pages          = {149--158}
}
</pre></div>
</div>

<!--
用 `biblatex-chicago`，标点后写 `\autocite[页码]{key}` 自动出芝加哥脚注；中文条目照右边示例填 `titleaddon` 和 `usere`。
-->

::read::
Use `biblatex-chicago` (`\autocite[page]{key}` after punctuation) with BibLaTeX entries in `references.bib`.
