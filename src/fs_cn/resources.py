"""resources.py — 汉化资源加载（翻译表 / EN 源 / 中文字体）。

源码运行时：从仓库根 data/ assets/ 加载；
PyInstaller 冻结运行时：从 _MEIPASS 的 data/ assets/ 加载（见 tools/build_exe.spec）。
"""
import json
import os
import sys

# 供前置校验使用的 EN 查询表（load_default_resources 填充；也可外部注入）
en_lookup = {}


def resource_base():
    """冻结时返回 _MEIPASS；源码运行时返回仓库根（src/fs_cn/ 的上三级）。"""
    if getattr(sys, "frozen", False):                     # EXE 内
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    here = os.path.dirname(os.path.abspath(__file__))     # .../src/fs_cn/
    return os.path.abspath(os.path.join(here, "..", ".."))   # 仓库根


def load_default_resources():
    """加载翻译表 + EN 源 + 字体字节；供 CLI/GUI 复用。源码/EXE 通用。"""
    global en_lookup
    root = resource_base()
    with open(os.path.join(root, "data", "translations.json"), encoding="utf-8") as f:
        cn = json.load(f)
    try:
        with open(os.path.join(root, "data", "i2_dump.json"), encoding="utf-8") as f:
            en_all = json.load(f)
        en_lookup = {k: v[0] for k, v in en_all.items()}
    except Exception:
        en_lookup = {}
    with open(os.path.join(root, "assets", "noto_sans_sc_cn.ttf"), "rb") as f:
        font = f.read()
    return cn, font
