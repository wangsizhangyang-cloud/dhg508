# Week 11 · Final Run, Overleaf Design Paper (`biblatex-chicago`), and Post-Mortem

Prepare for our final class on **Wednesday 25 November 2026**.

**Session 11 slides & semester review:** [Reading edition (`slides/read/index.html`)](slides/read/index.html) · [Reslides deck (`slides/`)](slides/README.md)

**Overleaf starter template:** [`dhg508-overleaf-template.zip`](dhg508-overleaf-template.zip) · Unpacked files: [`paper-template/`](paper-template/)

**Mention your difficulties.**

## Overview

Next Wednesday (**25 November**) is your **final hand-in**:

1. **End-to-end runnability is enough.** Freeze features now—do not start new modules. Make sure your live Cloudflare `https://` URL opens cleanly on another device, your automated tests (`Vitest`/`pytest` + `Playwright`) pass, and your design paper compiles to PDF on Overleaf.
2. **Final bug clinic in class.** If one stubborn bug still blocks you, record the exact error and reproduction steps and bring it next Wednesday—we will fix it together before your final commit.

---

## Step-by-Step Guide

### 1. Freeze scope and clean up your live build

1. Mark scope frozen in `docs/plan.md`; fix broken states, `"TODO"`s, or raw JSON dumps.
2. Add a 2–4 sentence note on your live page (`About` or footer) stating the historical context, `据 / 推断 / 设`, and AI tools used.
3. Confirm `.env`, `.dev.vars`, and API keys are in `.gitignore` (and large binaries stay in `artifacts/`), then re-deploy to Cloudflare Pages and re-run your tests.

### 2. Generate `evidence-table.tex` from your CSV

1. Copy [`paper-template/`](paper-template/) into your project:
   ```bash
   cp -R 508-coursework/week-11/paper-template projects/<your_project>/paper
   ```
2. Put your claims and design elements in `paper/evidence.csv` (`claim,evidence,locator,level,limit`, where `level` is `据`, `推断`, or `设`).
3. Run the generator script (do not hand-type LaTeX table rows):
   ```bash
   python3 paper/make_evidence_table.py
   # Or from an existing CSV:
   python3 paper/make_evidence_table.py data/evidence.csv paper/evidence-table.tex
   ```

### 3. Write `main.tex` (~1,500–2,500 words / 3–6 PDF pages)

- **Citations (`biblatex-chicago` Notes-Bibliography):** `main.tex` uses `\usepackage[notes, backend=biber, autolang=other, isbn=false]{biblatex-chicago}` and `\addbibresource{references.bib}`. Place `\autocite[page]{key}` **after punctuation** for Chicago footnotes, and keep BibLaTeX entries in `references.bib` (see [`paper-template/references.bib`](paper-template/references.bib) for Chinese `titleaddon` / `usere` examples). Check every page locator yourself.
- **Six sections in `main.tex`:**
  1. **Historical Question & Medium:** Your historical/cultural question and why an interactive medium is needed.
  2. **Sources & Scholarly Conversation:** Primary source limits + **at least three scholarly works** cited via `\autocite`.
  3. **Architecture & Boundaries:** Data/logic setup, Cloudflare route, temporal/epistemic cutoffs, and your exported `schematic.png` (uncomment `\begin{figure}`).
  4. **Evidence Table:** Included via `\input{evidence-table.tex}`.
  5. **Verification & Playtesting:** What your tests check + fixes and regression tests from **at least two external users**.
  6. **Post-Mortem:** Concrete notes on (1) what worked, (2) what failed or drifted and how you fixed it, (3) what changed, and (4) remaining limits & AI tools used.

### 4. Compile on Overleaf and sync back to Git

1. Open [Overleaf](https://www.overleaf.com/project) → **New Project → Upload Project** → upload [`dhg508-overleaf-template.zip`](dhg508-overleaf-template.zip) (or a zip of your `paper/` files + `schematic.png`).
2. Click **Menu** (top left) → set **Compiler** to **`XeLaTeX`**.
3. Click **Recompile** (`Biber` and `Noto Serif CJK SC` run automatically).
4. Click **Download PDF** → save as `paper/design-paper.pdf` in your Git repo, and click **Menu → Download → Source** if you edited text on Overleaf so `paper/main.tex` and `paper/references.bib` stay synced in GitHub.

### 5. Final Repository Checklist (before Wed 25 November)

```text
<your_project>/
├── README.md                  # Live https:// URL + run & test commands
├── docs/
│   ├── plan.md
│   ├── schematic.png
│   └── user-feedback.md       # >=2 external testers + fixes & tests
├── data/ (or research/)       # Notes, journal & evidence.csv
├── src/ & tests/              # Clean source + passing tests
└── paper/
    ├── evidence.csv
    ├── make_evidence_table.py
    ├── evidence-table.tex
    ├── references.bib         # >=3 scholarly works + primary sources
    ├── main.tex               # biblatex-chicago source
    └── design-paper.pdf       # Compiled PDF
```

**In class on Wednesday 25 November:** open your live public URL, show `paper/design-paper.pdf`, and resolve any remaining final bug together if needed.

---

# 第十一週 · 終版跑通、Overleaf 論文（`biblatex-chicago`）與 Post-Mortem

請為 **2026 年 11 月 25 日（星期三）**的最後一堂課做好準備。

**第十一講投影片與全學期複習包：** [閱讀版（`slides/read/index.html`）](slides/read/index.html) · [Reslides 課件源碼（`slides/`）](slides/README.md)

**Overleaf 極簡模板：** [`dhg508-overleaf-template.zip`](dhg508-overleaf-template.zip) · 解壓文件：[`paper-template/`](paper-template/)

**請說明你遇到的困難。**

## 總覽

下週三（**11 月 25 日**）即為本課程**期末交付**：

1. **全鏈路跑通即可。** 本週封版不再加新功能，確保 Cloudflare 公開 `https://` 網址在其他設備正常運行、自動化測試（`Vitest`/`pytest` + `Playwright`）通過、並在 Overleaf 編譯出設計論文 PDF。
2. **課堂排障兜底。** 如還剩個別修不掉的 Final Bug，記下完整報錯與重現步驟帶到下週課堂，當場一起修好再提交最終 commit。

---

## 分步指南

### 1. 封版並清理線上版本

1. 在 `docs/plan.md` 鎖定範圍，修掉失效按鈕、`"TODO"` 與裸露 JSON。
2. 在頁面（`About` 或頁腳）加 2–4 句說明：歷史背景、`據／推斷／設` 區分與所用 AI 工具。
3. 確認 API Key 已寫入 `.gitignore`、大文件放在 `artifacts/`，重新部署至 Cloudflare Pages 並跑通測試。

### 2. 從 CSV 自動生成 `evidence-table.tex`

1. 將 [`paper-template/`](paper-template/) 複製進專案：
   ```bash
   cp -R 508-coursework/week-11/paper-template projects/<你的專案名>/paper
   ```
2. 在 `paper/evidence.csv` 填入五欄數據：`claim,evidence,locator,level,limit`（`level` 填 `據`、`推斷` 或 `設`）。
3. 執行腳本生成表格（切勿手敲 LaTeX 表格）：
   ```bash
   python3 paper/make_evidence_table.py
   # 或指定現有 CSV 路徑：
   python3 paper/make_evidence_table.py data/evidence.csv paper/evidence-table.tex
   ```

### 3. 撰寫 `main.tex`（約 1,500–2,500 英文詞／3–6 頁 PDF）

- **引用規範（`biblatex-chicago` 註釋—書目制）：** 模板使用 `\usepackage[notes, backend=biber, autolang=other, isbn=false]{biblatex-chicago}` 與 `\addbibresource{references.bib}`。在標點符號後寫 `\autocite[頁碼]{key}` 自動生成芝加哥腳註，中文條目寫法參考 [`paper-template/references.bib`](paper-template/references.bib)（`titleaddon` 與 `usere`），所有頁碼須親自核對原書。
- **六個小節：**
  1. **Historical Question & Medium：** 歷史／文化問題，以及為何需要互動媒介。
  2. **Sources & Scholarly Conversation：** 一手材料局限 + 引用並討論**至少三項學術研究**（`\autocite`）。
  3. **Architecture & Boundaries：** 系統結構、Cloudflare 部署、年代／認知邊界，並嵌入導出的 `schematic.png`（取消 `\begin{figure}` 註釋）。
  4. **Evidence Table：** 透過 `\input{evidence-table.tex}` 自動載入。
  5. **Verification & Playtesting：** 自動化測試覆蓋內容 + **至少兩位外部測試者**反饋及新增的防回歸測試。
  6. **Post-Mortem：** 簡明記錄 (1) 哪些有效、(2) 哪些失敗或跑偏及如何修復、(3) 做了甚麼調整、(4) 剩餘局限與所用 AI 工具。

### 4. 上傳 Overleaf 編譯並同步回 Git

1. 打開 [Overleaf](https://www.overleaf.com/project) → **New Project → Upload Project** → 上傳 [`dhg508-overleaf-template.zip`](dhg508-overleaf-template.zip)（或你自己的 `paper/` 壓縮包）。
2. 點擊左上角 **Menu** → 將 **Compiler** 設為 **`XeLaTeX`**。
3. 點擊 **Recompile**（自動執行 `Biber` 與中文字體渲染）。
4. 點擊 **Download PDF** 存為 `paper/design-paper.pdf`；若在 Overleaf 修改過文字，同時點擊 **Menu → Download → Source** 同步回 GitHub 的 `paper/` 目錄。

### 5. 最終儲存庫檢查清單（11 月 25 日課前）

```text
<你的專案>/
├── README.md                  # 公開 https:// 網址 + 運行與測試指令
├── docs/
│   ├── plan.md
│   ├── schematic.png
│   └── user-feedback.md       # >=2 位外部測試者反饋與新增測試
├── data/（或 research/）       # 筆記、日誌與 evidence.csv
├── src/ & tests/              # 乾淨源碼 + 通過的測試
└── paper/
    ├── evidence.csv
    ├── make_evidence_table.py
    ├── evidence-table.tex
    ├── references.bib         # >=3 項學術文獻 + 一手史料
    ├── main.tex               # biblatex-chicago 論文源碼
    └── design-paper.pdf       # 編譯好的最終 PDF
```

**11 月 25 日課堂安排：** 打開線上公開網址、展示 `paper/design-paper.pdf`、現場修掉剩餘 Final Bug（如有）即可完成提交。
