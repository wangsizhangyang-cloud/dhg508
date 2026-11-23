---
minutes: 0
---

# Session 5 · Web application architecture, API contracts, and costs.

<div class="body">
<div class="frame fit"><span class="label">Session 5 · Static browser files vs. backend &amp; model calls</span><div class="pic"><Figure id="w05-app-arch" /></div></div>
<div class="frame hot"><span class="label">What runs where — and what costs money</span><div class="text">

- **Browser (`HTML/CSS/JS`):** layout, local JSON search, pre-computed vectors (`$0` per click)
- **Backend / Worker:** holds API secrets, validates input, routes live LLM/tool calls
- **Rule:** pre-compute fixed historical corpora offline; pay tokens only for live reasoning

</div></div>
</div>

::read::
Session 5: Distinguish static frontend execution (`$0`) from backend API/model routing; pre-compute fixed lookups and embeddings locally rather than paying per visitor click.
