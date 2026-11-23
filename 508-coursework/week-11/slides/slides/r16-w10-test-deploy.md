---
minutes: 0
---

# Session 10 · Three-tier testing pyramid &amp; Cloudflare deployment.

<div class="body">
<div class="frame fit"><span class="label">01 Unit · 02 Integration + LLM-Judge · 03 Playwright E2E</span><div class="pic"><Figure id="w10-test-pyramid" /></div></div>
<div class="frame fit"><span class="label">Cloudflare Pages ($0) + Worker Secret Proxy</span><div class="pic"><Figure id="w10-cloudflare" /></div></div>
</div>

::read::
Session 10: Decouple CSV/JSON data and pure logic from UI so `Vitest`/`pytest` and `@playwright/mcp` verify code and historical rules automatically; ship static/WebGL builds on Cloudflare Pages (`$0`) with API keys isolated inside a Cloudflare Worker.
