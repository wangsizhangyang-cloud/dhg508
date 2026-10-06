# code

只依赖 Python 标准库（本机 `python` 即可，无需 pip 安装）。按执行顺序：

| 脚本 | 作用 |
|---|---|
| `sources_manifest.json` | 要抓的史書篇目清单（Wikisource 页名 → 本地 slug） |
| `fetch_sources.py` | 从中文维基文库抓原文 → `sources/raw/wikisource/`，并写 `wikisource_index.json`；`--probe` 只检查是否存在 |
| `build_db.py` | 由 `data/`（水印化的行）+ 原文索引建 `chinese_generals.db` |
| `verify.py` | 把库中每条 `source_quote`（及将领的 `born_raw`/`died_raw`）回原文逐字核对；默认另抽 20 行人工比对 |
| `check_sample.py` | 抽 20 行，连同原文上下文写成 `research/outputs/verification.md` |
| `date_report.py` | 导出所有生卒/年份的原文→标准化对照（供人工核年份） |
| `query.py` | 只读查询小工具（见 `python code/query.py`） |

重建全库（无需联网，原文已存）：

```powershell
python code\build_db.py
python code\verify.py
```

重新抓原文（需要联网，中文维基文库）：

```powershell
python code\fetch_sources.py --probe
python code\fetch_sources.py
```

注意：`fetch_sources.py` 会触发速率限制（HTTP 429），脚本已带退避重试与延时。
