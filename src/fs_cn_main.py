#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fs_cn_main.py — EXE 打包入口（PyInstaller 主脚本，位于 fs_cn 包之外）。

fs_cn 包内模块使用相对导入（from .patcher import …），不能作为顶层脚本直接运行；
此文件在包外，仅负责启动 `fs_cn.gui.main()`。

源码运行：
    PYTHONPATH=src python src/fs_cn_main.py
    等价:    python -m fs_cn.gui
"""
import os
import sys

# 源码模式：保证 src/ 在 sys.path（PyInstaller 冻结时由 pathex 负责收集，无需此步）
_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from fs_cn.gui import main  # noqa: E402

if __name__ == "__main__":
    main()
