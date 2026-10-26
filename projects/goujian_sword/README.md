# project: goujian_sword（越王勾践剑）

研究主题：越王勾践剑（春秋晚期青铜剑，1965 年湖北江陵望山一号楚墓出土，现藏湖北省博物馆）。目标：为该剑建立一份"有来源、可核查"的史料与图像资料集。

## 目录与内容

| 位置 | 内容 |
| --- | --- |
| `sources/raw/goujian_sword/goujian_sword_sources.md` | 史料与文献汇编：馆方档案、发掘与铭文考定、1977/2017 科学检测、禁止出境名录、人物背景文献（《史记·越王句践世家》），每条含出处链接与可靠度标注 |
| `sources/raw/goujian_sword/goujian_sword_image_sources.md` | 6 张实拍图的来源清单（Wikimedia Commons 文件页、拍摄者、许可） |
| `sources/raw/goujian_sword/images/` | 已下载图片（2000px 缩放版）；`images/inscription/` 为铭文专项（实物大图 + 解读图 + 矢描参考） |
| `code/build_goujian_sword.py`、`code/upgrade_pass2.py` …`code/upgrade_pass10.py`、`code/build_inscription_real.py`、`code/color_and_pattern.py` | 程序化建模与迭代脚本（Blender bpy，按馆方规格 + 对照 raw 实拍照片与文献记录；可重复执行）：细密缠绳、兽面阶梯、刃口研磨线、剑首旋转成型凹槽、暗纹铺满剑身+**交叉花朵纹**（对照实物修正）、剑尖内凹（前锋曲弧内凹）、椭圆琉璃/绿松石镶嵌（正面蓝、背面绿松石）、立式渲染；铭文按**权威线描摹本**（《集成》11621 体系，wuyuescripts.com 线描）逐字重建（自格向外读、字头朝格、两行分居剑脊）；`color_and_pattern.py` 一键"新铸原貌"配色（亮金+黑纹+艳镶嵌，末尾自检） |
| `research/outputs/goujian_sword_model_full.png`、`goujian_sword_model_hilt.png`、`goujian_sword_model_standing.png` | 3D 模型渲染图（平置全剑 + 柄部特写 + 立式主图，EEVEE） |
| `artifacts/goujian_sword.blend` | 模型 .blend 副本（artifacts/ 已被 git 忽略） |
| `research/journal/research_journal.md` | 进度日志 |

## 与其他项目的关联

- 与 `shiji_people` 同属《史记》人物谱系（越王句践本传在《史记·卷四十一》）。
- 吴越剑系的其他越王剑（越王者旨於睗剑、越王不寿剑、越王州句复合剑）可作后续扩展。
- 3D 模型为程序化近似重建（非扫描、非AI生成）：规格依据馆方描述；铭文 8 字按实物照片逐字提取（字形、排布、字向对照实物）；剑格兽面细节为简化。
