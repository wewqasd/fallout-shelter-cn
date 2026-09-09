# 辐射避难所（Fallout Shelter）Steam 版中文汉化

《辐射避难所》Steam 版（Bethesda，版本 2.6.0，无官方中文）的汉化项目：14064 条文本，
直接修改游戏资源实现，并提供零依赖一键汉化 EXE（对游戏版本自适应）。

## 项目说明

本项目整体为 **vibe coding（AI 辅助编程）产物**：汉化工具代码、翻译文本与审校
均由 AI 大模型辅助完成，作者已对主要流程实机验证。可能存在未发现的 bug 或
疏漏，如遇问题欢迎反馈，也请多多包涵。

## 译文来源与审校说明

- **来源构成**：翻译文本约 **85% 基于盛大代理《辐射避难所》安卓版官方中文**
  （版权归其原版权方所有），在此基础上针对 Steam 版进行了
  文本补全与本地化适配；其余约 **15% 由 AI 大模型完成翻译与审核**。
- **审校方式**：全文案经 AI 模型（DeepSeek V4 Flash、DeepSeek V4 Flash Vision、
  GLM 5.3 Flash、Gemini 3.7 Flash）批量翻译、审校与一致性检查，并做了多轮
  术语/一致性批量修订；作者在游戏内实际游玩验证过汉化效果。
  非完全人工逐条审校，如有疏漏欢迎反馈。

## 两种安装方式

### ① 成品 data.unity3d（直接覆盖）
- 从 Release 下载 `data.unity3d`
- 关闭游戏 → 复制到 `游戏目录\FalloutShelter_Data\` 覆盖（**先备份原版**）→ 启动

### ② FalloutShelterCN.exe（一键汉化，零依赖）
- 从 Release 下载 `FalloutShelterCN.exe`（不需要安装 Python）
- 双击 → 自动定位游戏目录（找不到则提示选择 Fallout Shelter 文件夹）→ 一键汉化
- 汉化前自动备份 `data.unity3d → data.unity3d.bak.v5`；「一键还原」随时恢复原版

## 版本自适应机制

- 对游戏版本自适应：游戏更新后直接重新运行 `FalloutShelterCN.exe` 即可汉化，
  无需等待新版发布；新版本新增的文本会保留英文，不会报错。
- 定位文本用的是游戏文件里的内容锚点，不依赖版本号或游戏进程，
  所以游戏更新后依然能准确找到需要替换的位置。

## 来源声明与免责声明

- **非官方声明**：本项目为玩家社区自制汉化，与 Bethesda Softworks 及其授权方
  **无任何关联**，未获其认可或赞助；游戏名称、商标与素材版权归原版权方所有。
  翻译文本的来源构成见上文「译文来源与审校说明」。
- 本项目的汉化文本与工具仅供学习交流，游戏本体请通过 Steam 等正规渠道购买正版。
- 字体 `cjk_font_v6_pua.ttf` 基于 Noto Sans SC（SIL OFL 1.1）构建，可自由再分发。

## License

- 代码（scripts/ tools/）：**MIT**（见 LICENSE）
- 翻译表（data/）：**学习交流授权**——个人学习/研究可自由使用；非商用再分发须注明来源与本声明；禁止商用
- 字体（assets/）：**SIL OFL 1.1**（见 assets/OFL.txt）
- 翻译表中官方中文部分版权归原版权方所有，本仓库不对其主张权利

## 目录结构

```
├── data/          # 翻译表 steam_cn_full.json/.tsv（14064 键）+ 中英对照 steam_cn_en_zh.tsv + EN 参考
├── scripts/       # 核心：patch_core（手术核心）/ game_dir（定位/备份）/ 提取与字体构建
├── tools/         # EXE 打包：GUI 主程序 / build_exe.spec / build_exe.bat
├── assets/        # 中文字体 cjk_font_v6_pua.ttf（OFL 许可 + FONT.md 说明）+ 图标
├── docs/          # 技术手册（解包/字体/压缩/打包原理）
└── requirements.txt
```

## 构建

### 构建汉化 data.unity3d（Linux/Windows 均可）
```bash
pip install -r requirements.txt
python scripts/patch_core.py --src "<游戏目录>/FalloutShelter_Data/data.unity3d" \
    --out build/data.unity3d
```

### 打包 EXE（Windows 侧，需 Python 3.12）
```bat
py -3.12 -m pip install unitypy==1.25.3 pyinstaller
py -3.12 -m PyInstaller --noconfirm --clean tools\build_exe.spec
:: 产出 dist\FalloutShelterCN.exe
```
