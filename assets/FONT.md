# 中文字体说明（noto_sans_sc_cn.ttf）

## 这是什么

本字体 = **Noto Sans SC（思源黑体）子集化精简版 + 16 个自绘手柄按键字形**。

## 构成

- **基底**：Google 出品的 Noto Sans SC（思源黑体），SIL OFL 1.1 许可，允许自由使用/修改/再分发
- **精简**：保留 CJK 统一表意基本区全量（约 2.1 万字）+ 扩展 A（约 6600 字）+ 中日标点、
  西文符号等共约 3.1 万字形；砍掉游戏用不到的扩展 B~F 生僻字、谚文音节等，
  体积从全量 60MB+ 压到 10.6MB
- **PUA 手柄字形**：自绘 16 个手柄按键图标，放在 Unicode 私用区 **U+E000–U+E00F**（PUA），
  对应游戏文本标记 `[A] [B] [X] [Y] [LT] [RT] [LB] [RB] [CV] [MN] [L] [R] [DL] [DR] [DU] [DD]`。
  译文直接写 PUA 字符，由本字体渲染成图标（绕过游戏原 ReplaceButtonImages 组件）

## 许可

SIL Open Font License 1.1 —— 详情见本目录 `OFL.txt`。

## 重建

构建脚本：`scripts/build_font.py`（需准备 OFL 思源黑体基底 + DejaVuSans）；
字体原理详见 `docs/technical.md` 第 3 章。
