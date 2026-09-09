"""cli.py — 命令行汉化入口（源码构建版）。

用法：
    pip install -e .                 # 或 PYTHONPATH=src
    fs-cn-patch --src 原版/data.unity3d --out 汉化/data.unity3d
    等价于: python -m fs_cn.cli --src ... --out ...

GUI 版本入口: python -m fs_cn.gui（或 fs-cn-gui）
"""
import argparse
import sys

from .patcher import patch_bundle
from .resources import load_default_resources


def main(argv=None):
    ap = argparse.ArgumentParser(description="fs_cn — 版本自适应汉化手术（命令行）")
    ap.add_argument("--src", required=True, help="原版 data.unity3d 路径")
    ap.add_argument("--out", required=True, help="输出汉化 data.unity3d 路径")
    ap.add_argument("--allow-unmatched", action="store_true", help="表有包无的 term 跳过而非中止")
    ap.add_argument("--skip-validate", action="store_true", help="跳过前置结构校验")
    ap.add_argument("--packer", default="lz4", choices=["lz4", "none", "original"])
    args = ap.parse_args(argv)

    cn, font = load_default_resources()
    try:
        r = patch_bundle(args.src, args.out, cn, font,
                         allow_unmatched=args.allow_unmatched,
                         validate=not args.skip_validate,
                         packer=args.packer)
        print("\nRESULT:", r)
    except Exception as e:
        print(f"\n错误: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
