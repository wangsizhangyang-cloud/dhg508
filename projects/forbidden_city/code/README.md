# code

只依赖 Python 标准库（本机 `python` 即可，无需 pip 安装）。脚本按执行顺序：

| 脚本 | 作用 |
|---|---|
| `commons.py` | Wikimedia Commons API 小工具：`search` / `info` / `download` |
| `curated_candidates.py` | 每座建筑的候选图片清单（人工挑选） |
| `batch_search.py` | 在 Commons 搜索候选（结果写入 `research/notes/candidates.json`） |
| `gather.py` | 取候选图元数据并下载缩略图到 `artifacts/candidates/` |
| `contact_sheet.py` | 每座拼一张带标签的对比图集到 `artifacts/contact_sheets/` |
| `selection.py` | 最终选定的建筑与照片（含中英文名） |
| `select_images.py` | 下载选定照片到 `images/` 并写 `manifest.json` |
| `final_sheet.py` | 18 张选定照片的总览图 `artifacts/final_selection.jpg` |
| `fetch_wiki.py` / `fetch_wiki_zh.py` | 抓维基百科原文到 `sources/raw/wiki*` |
| `fetch_web.py` | 抓故宫博物院官网页面到 `sources/raw/web` |
| `build_db.py` | 由 `buildings.json` + `records.json` 建 `forbidden_city.db` |
| `verify.py` | 抽 18 行回原文逐字核对 |
| `query.py` | 只读查询小工具（见 `python code/query.py`） |

注意：`gather.py` / `select_images.py` 等会访问网络（Wikimedia Commons），
并会触发速率限制；脚本已带重试与延时。
