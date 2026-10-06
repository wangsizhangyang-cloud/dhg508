# Code

《史記》人物库的脚本（Python 标准库 + OpenCC）。全部幂等，可反复重跑。

| 脚本 | 作用 |
|---|---|
| `fetch_sources.py` | 从中文维基文库抓《史記》卷 wikitext → `sources/raw/`；`--probe` 只探页，`--reindex` 重建清单 |
| `extract.py` | 清 wikitext → `sources/processed/`；按小节抽人物 → `data/extracted/*.json` |
| `build_db.py` | 读 `data/extracted/`（＋`data/manual/`）建 `shiji_people.db` |
| `verify.py` | 逐字回原文校验 + 固定种子抽 20 行 → `research/outputs/verification.md` |
| `query.py` | 只读查询：`person` / `offices` / `events` / `relations` / `mentions` / `chapter` / `search` / `sql` / `off-topic` |

## 顺序

```powershell
python code\fetch_sources.py     # 需联网
python code\extract.py
python code\build_db.py
python code\verify.py
```

依赖：`pip install opencc-python-reimplemented`。数据库与 `__pycache__` 不入 git。
