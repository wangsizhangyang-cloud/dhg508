# Code

本项目代码位于 **`E:\508fp`**（课程仓库之外），未复制进本目录，避免大文件与重复数值源。

## 位置

| 模块 | 路径 | 说明 |
|---|---|---|
| Web 游戏 | `E:\508fp\战国群雄游戏\` | `index.html`、`game_data.js`、`map_data.js`、`sim_layer.js`、`i18n.js` |
| 本地 LLM 代理 | `E:\508fp\战国群雄游戏\_server.mjs` | 静态服务 + `/__llm`，Key 从本机文件/环境变量读取 |
| 数据导出 | `E:\508fp\_tools\export_godot_data.mjs` | Web → Godot JSON |
| Godot 切片 | `E:\508fp\zhanguo-godot\` | `scripts/main.gd`、`scripts/map_view.gd`、`data/*.json` |
| 数据库 | `E:\508fp\春秋战国兵种数据库.db`、`春秋战国武将数据库.db` | 15/13；190/1215/190 |

## 运行

```powershell
# Web：双击
E:\508fp\战国群雄游戏\index.html

# Web + 本地 LLM 代理
E:\508fp\战国群雄游戏\run_serve.bat
# 然后打开 http://127.0.0.1:8642/

# 重新导出 Godot 数据
node E:\508fp\_tools\export_godot_data.mjs

# Godot（需安装 Godot 4.4+）
godot --path E:\508fp\zhanguo-godot
```

## 为什么不复制进 code/

- 数据库约 376KB、人物图 190 张、省份 JSON 250KB，属于 `artifacts/` 级别的大文件；
- 代码与数据在 `E:\508fp` 已能独立运行，复制会制造第二个数值源；
- 课程要求「大文件不入 Git」；本目录只保留索引，实际代码位置以 `E:\508fp` 为准。

若后续需要把代码纳入课程仓库，建议只复制 `战国群雄游戏\` 的源码与 `zhanguo-godot\` 的脚本/JSON，数据库与图片放 `artifacts/` 并在 `artifacts/README.md` 登记。
