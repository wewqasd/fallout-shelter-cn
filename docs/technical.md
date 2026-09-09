# 汉化技术手册

> 本文档说明本汉化项目的工作原理，覆盖：**解包与数据提取、中文字体构建与注入、
> 翻译写回、资源压缩与打包**。面向想了解实现细节或复现构建流程的开发者。
>
> 相关文件：`src/fs_cn/patcher.py`（手术核心）、`scripts/extract_i2.py`（提取）、
> `scripts/build_font.py`（字体构建）、`tools/build_exe.spec`（EXE 打包）。

---

## 1. 总览：data.unity3d 是什么

- 游戏的文本、字体、界面组件全部打包在单个 **UnityFS bundle** `data.unity3d`（481 MB，LZ4 压缩）里。
- 汉化的思路是**直接改写这个文件**：定位文本对象 → 替换为中文 → 原样 LZ4 存回，不依赖运行时 hook。
- 解析工具是 **UnityPy 1.25.3**（`pyproject.toml` 已固定版本，Windows 侧另有 cp312 wheel）。

## 2. 解包与数据提取

### 2.1 加载 bundle

```python
import UnityPy
env = UnityPy.load("data.unity3d")
objs = list(env.objects)          # 全部对象（MonoBehaviour / Font / MonoScript …）
```

`o.type.name` 区分对象类型；MonoBehaviour 的原始字节用 `o.get_raw_data()`，
改写后要用 `o.set_raw_data(bytes)`（`current_raw()` 辅助函数处理两种情况）。

### 2.2 文本在哪：I2 LanguageSource

两版游戏（Steam / 安卓）都用 **I2 Localization** 插件存文本。Steam 版全部 14064 条文本
在**一个** 7.4 MB 的 MonoBehaviour 里（pid≈20953，resources.assets），二进制布局：

```
[int klen][key(ascii)][对齐4][flags+category][int langcnt]
[langcnt × [int len][utf8 值][对齐4]]
[2 × [int cnt][cnt × int]]      # 每条 term 尾部的两个 int 数组
```

- 语言槽 6 列：en/es/fr/it/de/ru（**无中文**），写回时全槽写中文，天然抗语言列顺序变化。
- 解析难点：`flags+category` 字段**长度可变**（0–2 个 int），位置不确定 →
  不能固定偏移解析，必须用**扫描式解析**（见 2.4）。

### 2.3 定位：内容锚点（pid 无关）

不硬编码 path_id（对象 id 随版本/平台变化），而是**扫描内容特征**：

- 主锚点：`Achievement_Xbox_Completed_01`（term key 字节），命中后取含该字节的最大对象；
- 备选锚点：`ActivateRewards` / `Attention` / `Baby_NewBabyArrived`（版本更新若删了主锚点依次尝试）；
- 对象必须是 MonoBehaviour 且原始字节中包含锚点。

### 2.4 扫描式解析（最稳）

`parse_terms()`：从锚点往前 4 字节开始，逐条读 `[klen][key]`，key 对齐 4 后
在 **200 字节窗口内**用 `try_parse_langcnt()` 试探候选偏移——先要求"后面跟合法 key"
（need_key=True），失败再放宽（need_key=False）。合法性校验：

- `1 ≤ langcnt ≤ 40`；每条语言值 `0 ≤ len ≤ 100000` 且不越界；
- 尾部两个 int 数组 `0 ≤ cnt ≤ 5000` 且不越界；
- key 只含可见 ASCII（32–126）。

任意一条 parse 试探通过即按该布局读整条 term，循环直到 key 不合法为止。

### 2.5 提取脚本用法

```bash
python scripts/extract_i2.py <data.unity3d> <out.json>
# 输出 {key: [6 语言值]}，即 data/i2_dump.json（EN 源，基准参照）
```

- `data/translations.json`：**权威翻译表** {key: 中文}（14064 键），
  `fs_cn.patcher` 写回时使用；`.tsv` 为同内容编辑用表格（两者必须保持同步）。
- `data/i2_dump.json`：I2 全量 dump（EN+5 语言，索引 0 = EN），
  用于前置校验的 EN 基准与"包内 EN 是否变化"的版本情报比对。

## 3. 中文字体：构建、压缩与注入

### 3.1 基底与压缩

- 基底是**国服官方思源黑体（Noto Sans SC，SIL OFL 1.1，允许自由再分发）**，
  已做字形子集化与优化（覆盖简体常用字 + 游戏文本用字），成品
  `assets/noto_sans_sc_cn.ttf` 10.6 MB（upem 1000，TrueType glyf）。
- **子集化基底不在本仓库**（约 6 MB 的 `cjk_font_v5_official.ttf` 已归档）；
  公开复现需自行准备 OFL 思源黑体基底，或直接使用 Release 附带的成品字体。

### 3.2 PUA 手柄按键字形（本字体最大特色）

游戏文本里的按键标记 `[A]~[DD]`（共 16 种：A/B/X/Y/LT/RT/LB/RB/CV/MN/L/R/DL/DR/DU/DD）
原本由运行时组件 ReplaceButtonImages 渲染成手柄图标。汉化后该机制不再生效，
因此**直接在字体里造了 16 个 PUA 字形**：

| 标记 | 码位 | 标记 | 码位 |
|---|---|---|---|
| `[A]` | U+E000 | `[CV]` | U+E008 |
| `[B]` | U+E001 | `[MN]` | U+E009 |
| `[X]` | U+E002 | `[L]` | U+E00A |
| `[Y]` | U+E003 | `[R]` | U+E00B |
| `[LT]` | U+E004 | `[DL]` | U+E00C |
| `[RT]` | U+E005 | `[DR]` | U+E00D |
| `[LB]` | U+E006 | `[DU]` | U+E00E |
| `[RB]` | U+E007 | `[DD]` | U+E00F |

译文中出现 PUA 字符时**绕过 ReplaceButtonImages**，直接由字体渲染图标。
字形设计：实心圆盘 + 镂空字母/三角（二次贝塞尔圆弧常数 0.9142，实心 CW / 镂空 CCW），
字母轮廓借自 DejaVuSans 按中心对齐缩放，方向键为指向性镂空三角。

### 3.3 构建脚本

```bash
PYTHONPATH=.pylibs python scripts/build_font.py
# 需要: assets/cjk_font_v5_official.ttf（基底，已归档）+ 系统 DejaVuSans.ttf
# 产出: assets/noto_sans_sc_cn.ttf（含自带验证：16 个 PUA cmap 齐全、FF00-FF0F 字形与基底一致）
```

脚本用 fontTools 在基底 glyph 表上追加 `uniE000..uniE00F`，cmap 挂 (3,1)/(3,10) 两个子表，
并补 vmtx 竖排度量。**验证断言**确保 PUA 字形与基底字形不冲突。

### 3.4 注入：替换 7 个 Font 对象

```python
for fobj in objs:
    if fobj.type.name == 'Font':
        fo = fobj.read()
        fo.m_FontData = list(font_bytes)   # 原版英文 TTF（FuturaStd 等，28~128KB）→ CJK
        fo.save()
```

原版有 7 个 Font 对象（FuturaStd/monofonto 等英文 TTF），全部替换为同一个 CJK 字体字节。

### 3.5 FontManager 清理

按 MonoScript 类名定位 FontManager（`m_ClassName` 映射，pid 无关），
把 `customFonts` 列表里**非空 PPtr 引用置零**（原版 13 个引用、11 个非空），
让游戏只走动态 TrueType 路径，避免字体渲染回退到英文。

### 3.6 UILabel 渲染路径"钉死"（对标竞品 forced/assigned，零 typetree 依赖）

NGUI UILabel 的 MonoBehaviour 字节布局（6000.0.58 离线校准）：

```
[16B header][12B m_Script][m_Name str][基类 UIRect/UIWidget = 132B]
[mFontTypografy 12B][mTrueTypeFont 12B][mText str][…20 个字段 136B…][mForceTrueTypeFont 4B]
```

两步操作（常量 `_BASE_CLASS_FIELD_LEN=132`、`_FORCE_AFTER_TEXT=136`）：

1. **force**：`mForceTrueTypeFont` 0→1，强制标签走 TrueType 动态字体（= 已替换的 CJK）；
   实测 **2807 个**标签。
2. **assign**：`mTrueTypeFont` 空引用的标签，指派该 asset 内**频次最高的字体**
   （dominant，即已 CJK 化的 Font 引用）；实测 **29 个**。

安全机制：bool 只认 {0,1}、fileID 必须落在合法范围（0=本 asset，1..N=external），
结构校验不过的标签**跳过并计数，绝不写坏字节**；若将来 NGUI 布局变化，
功能自动退化（校验全失败 → 跳过），不会破坏文件。

## 4. 翻译写回与前置校验

### 4.1 写回逻辑（fs_cn.patcher.patch_bundle）

| 情形 | 行为 |
|---|---|
| term 名匹配 | 全语言槽写中文（14058 条） |
| 表有、包无（旧 term 被删/改名） | 默认**中止**；`--allow-unmatched` 跳过并汇报 |
| 包有、表无（版本新增 term） | **保留原文英文**，`fallback` 计数汇报 |
| 换行/按键标记/括号文本与包内 EN 差异 | **仅警告**（设计内自适应，见 4.2） |
| FontManager/UILabel/静态标签/REACH NOW 找不到 | **警告不中止**（结构可能已变，自动退化） |

改写采用"头 + 逐条重建 + 尾"拼接，逐条 `rebuild_term()` 后
`obj.set_raw_data(bytes)` 整体回写。

### 4.2 前置校验：唯一硬中止 = `{0}` 占位符不一致

- **硬项**：译文与包内 EN 的 `{x}` 占位符集合不一致 → 中止（真结构损坏信号）。
- **警告项**（设计内自适应，不中止）：
  - 换行段数不同（翻译时有意合并/拆分）；
  - 按键标记：EN 的 `[A]~[DD]` 在译文中应被 PUA 字形替代或删去，否则警告；
  - 括号 token 差异（如 `[Content line 2]` → `[内容线2]`）。
- **版本情报**：包内 EN 与基准 `i2_dump.json` 有差异的 term 数 → `en_changed`
  汇报（游戏可能已更新）。校验基于**包内实际 EN**，所以版本更新后依然准确。

## 5. 其他手术

- **REACH NOW → 现在到达**：等长 16 B 块替换（`[int len][bytes][pad]` 两版等长，内容定位）。
- **静态标签 9 个**：SPIN/SCIENCE SPIN/CAPITALIST SPIN/Lucky Spin/EXPERIMENTAL VAULTS/
  GO TO EXPERIEMNTAL VAULT/GO TO STANDARD VAULT/WELCOME TO/ARE YOU SURE YOU\nWANT TO LOGOUT?
  在 UILabel 的 mText 里做 UTF-8 长度+padding 原位替换（不改变对象字节长度）。

## 6. 保存与体积

```python
env.save("lz4", outdir)    # 或 "none" 兜底（防 MemoryError）
```

- packer 默认 **lz4**：原版 481 MB → 汉化成品约 **530 MB**（中文字体 + 更长文本）。
- **坑**：UnityPy 输出文件名 = `ntpath.basename(src)`，不是固定 `data.unity3d`；
  `patch_bundle` 保存后按实际产物 `shutil.move` 到目标路径（v5.13 修复过此 bug）。

## 7. EXE 一键汉化（PyInstaller 打包）

- 入口：`src/fs_cn/gui.py`（GUI，含 `--selfcheck` 无头自检）；
  spec：`tools/build_exe.spec`（SPECPATH 相对路径，任意 cwd 可打包）。
- **内嵌资源**：翻译表 + EN 源 + 字体 + UnityPy（含 Boost pyd 与 `resources/lzma.tpk`，
  tpk 需在 spec 里手动加 datas）。
- 用户动作：双击 → 自动定位游戏目录（Steam libraryfolders.vdf / 注册表 / 常见路径）
  → 备份 `data.unity3d → data.unity3d.bak.v5` → 汉化；「一键还原」随时恢复。
- 打包（Windows 侧，Python 3.12）：
  ```bat
  py -3.12 -m pip install unitypy==1.25.3 pyinstaller
  py -3.12 -m PyInstaller --noconfirm --clean tools\build_exe.spec
  ```

## 8. 验证链路（改动核心后必做）

1. 构建后 md5 对比预期（v5.13 = `9a2eab7bcd29b5cd2a698ba6231e049a`）；
2. 冻结 EXE `--selfcheck` 输出 md5 == 源码构建 md5（确定性验证）；
3. 幂等：对已汉化包重跑，输出 md5 不变；
4. UI 状态抽查：全部 UILabel force=1、无空字体引用。

## 9. 版本自适应一览

| 层 | 定位方式 | 版本变化时 |
|---|---|---|
| I2 LanguageSource | 内容锚点（主+3 备选） | 换锚点继续找，找不到报错 |
| FontManager | MonoScript 类名 | 类名变了 → 警告跳过 |
| 字体/静态标签/REACH NOW | 内容字节 | 内容变了 → 警告跳过 |
| UILabel 渲染钉死 | 字节布局 + 安全校验 | 布局变了 → 自动退化跳过 |
| 翻译写回 | term 名匹配 + 前置校验 | 新增 term 保英文，删除 term 可跳过 |
