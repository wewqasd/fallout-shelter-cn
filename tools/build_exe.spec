# -*- mode: python ; coding: utf-8 -*-
"""build_exe.spec — PyInstaller 打包 FalloutShelterCN.exe（路线 A，零依赖单文件）。
置于仓库根；PyInstaller 从仓库根运行（python -m PyInstaller tools/build_exe.spec）。

内嵌资源（resource_base() 从 _MEIPASS 读取，均须存在）：
  data/steam_cn_full.json   翻译表 (14064 键)
  data/new_version_terms_full.json  EN 源（供结构校验）
  assets/cjk_font_v6_pua.ttf  中文字体 (OFL，可再分发)
"""
import os

# SPECPATH = spec 所在目录（tools/）；仓库根 = SPECPATH/..
_ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

# 资源目录，按 (源路径, "目标子目录") 打到 _MEIPASS 下
datas = [
    (os.path.join(_ROOT, "data", "steam_cn_full.json"), "data"),
    (os.path.join(_ROOT, "data", "new_version_terms_full.json"), "data"),
    (os.path.join(_ROOT, "assets", "cjk_font_v6_pua.ttf"), "assets"),
]

# UnityPy 需要的隐式导入 + Boost pyd 一并收集
hiddenimports = [
    "UnityPy", "UnityPy.UnityPyBoost", "UnityPyBoost",
    "UnityPy.files", "UnityPy.classes", "UnityPy.streams",
    "UnityPy.resources",               # Tpk 类型树数据库（lzma.tpk）
]

# UnityPy.resources/*.tpk 属数据文件，PyInstaller 默认不打包 → 手动收集
import glob as _glob
_upy_pkg = None
try:
    import UnityPy as _upy
    _upy_pkg = os.path.dirname(os.path.abspath(_upy.__file__))
except Exception:
    _upy_pkg = None
if _upy_pkg:
    _res = os.path.join(_upy_pkg, "resources")
    if os.path.isdir(_res):
        for _f in _glob.glob(os.path.join(_res, "*.tpk")) + _glob.glob(os.path.join(_res, "*.py")):
            datas.append((_f, "UnityPy/resources"))

a = Analysis(
    [os.path.join(SPECPATH, "falloutshelter_cn_gui.py")],
    pathex=[os.path.join(_ROOT, "scripts"), SPECPATH],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["numpy", "matplotlib"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="FalloutShelterCN",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                       # 关闭 UPX 省事（字体数据自带压缩）
    runtime_tmpdir=None,
    console=False,                   # 纯 GUI，不弹控制台
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(_ROOT, "assets", "falloutshelter.ico"),  # 游戏原版图标（从 FalloutShelter.exe 提取）
)
