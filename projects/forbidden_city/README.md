# 紫禁城建筑小库（Forbidden City buildings）

一份「找图 → 抽事实 → 建小库 → 核对」的作业：为北京故宫的 **18 座建筑**各选一张
**没有人物、只有建筑**的在线照片（Wikimedia Commons，逐张肉眼核验），并把每座建筑的
史实抽成一行行记录，存进 SQLite。`SKILL.md` 里的 **ForbiddenCityTeller（紫禁城述者）**
按这些行回答问题、并按图认建筑。

## 文件

| 文件 | 是什么 |
|---|---|
| `forbidden_city.db` | SQLite：`buildings` 19 条（18 座建筑 + 1 条整体）、`facts` 150 行 |
| `buildings.json` | 建筑表源数据：中英文名、类型、照片文件、作者、许可、Commons 页面 |
| `records.json` | 事实行：`id / building_id / year / date / fact / people / place / source / source_url / source_locator / note` |
| `images/` | 18 张照片（每座一张，均无人像）+ `manifest.json`（出处元数据） |
| `SKILL.md` | 给 agent 的说明与规矩 |
| `code/` | 抓取、建库、核对脚本（Python 标准库，无需安装依赖） |
| `sources/raw/` | 抽取事实所依据的原文（维基百科中/英文条目、故宫博物院官网页面） |
| `artifacts/` | 中间产物（候选图、对比图集），不入 git |

## 数据模型

```text
buildings(id, key, name_chn, name_eng, type, image,
          image_commons_title, image_source, image_artist, image_license, image_note, note)
facts(id, building_id → buildings.id, year, date, fact, people, place,
      source, source_url, source_locator, note)
facts_view  -- facts 与建筑名连表后的只读视图
```

一行一件事；每行都带 `source`、`source_url`、`source_locator`（条目内的位置），
`note` 记存疑处（例如「太和门面阔九间/七间两说」「角楼 72/76 条脊两说」）。

## 18 座建筑

午门 · 太和门 · 太和殿 · 中和殿 · 保和殿 · 乾清宫 · 交泰殿 · 坤宁宫 · 神武门 ·
角楼 · 文华殿 · 武英殿 · 文渊阁 · 养心殿 · 九龙壁 · 慈宁宫 · 储秀宫 · 钦安殿

## 怎么重建

```powershell
# 1) 建库（读 buildings.json + records.json）
python code\build_db.py

# 2) 抽几条回原文核对（18 项）
python code\verify.py

# 3) 随手查库
python code\query.py buildings
python code\query.py building taihedian
python code\query.py fact 30
python code\query.py search 火灾
```

重新下载照片（需要联网，Wikimedia Commons）：

```powershell
python code\gather.py           # 候选图元数据 + 缩略图 → artifacts/candidates
python code\contact_sheet.py    # 每座一张对比图集 → artifacts/contact_sheets
python code\select_images.py    # 下载选定照片 → images/ + manifest.json
python code\fetch_wiki.py       # 抓维基原文 → sources/raw/wiki
python code\fetch_wiki_zh.py    # 抓中文维基原文 → sources/raw/wiki_zh
python code\fetch_web.py        # 抓故宫博物院官网页面 → sources/raw/web
```

## 照片的来源与许可

18 张照片均取自 Wikimedia Commons（多为 CC BY / CC BY-SA / CC0），每张的作者、
许可与页面地址记在 `images/manifest.json` 与 `buildings.json` 里，演示时应一并注明。
选图时逐张放大核对：**不含人物、只有建筑**；同一座建筑只用一张。

## 出处

事实主要依据维基百科中英文条目与故宫博物院官网，原文存在 `sources/raw/`。
`records.json` 每行都写明取自哪一条、哪一节。抽取后已抽 18 行回原文逐字核对
（`code/verify.py`，18/18 通过）。
