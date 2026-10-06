# artifacts

本目录是中间产物，**不入 git**（见 `.gitignore`）。可随时重建：

| 子目录/文件 | 是什么 | 怎么重建 |
|---|---|---|
| `candidates/` | 每座建筑 2–13 张候选缩略图（约 126 张） | `python code\gather.py` |
| `contact_sheets/` | 每座一张带标签的候选对比图集 | `python code\contact_sheet.py` |
| `final_selection.jpg` | 最终 18 张照片的总览图 | `python code\final_sheet.py` |

正式的照片在项目根目录 `images/`（入 git）；正式数据库为根目录 `forbidden_city.db`。
