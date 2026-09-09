#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_pairs.py — 重新生成中英对照表 data/en_zh_pairs.tsv（key \t EN \t 中文）。

用法: python scripts/make_pairs.py [仓库根]
输入: data/translations.json（中文权威表） + data/i2_dump.json（I2 六语言 dump，索引 0 = EN）
输出: data/en_zh_pairs.tsv
"""
import json
import os
import sys

ROOT = os.path.abspath(
    sys.argv[1] if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)


def main():
    with open(os.path.join(ROOT, "data", "translations.json"), encoding="utf-8") as f:
        cn = json.load(f)
    with open(os.path.join(ROOT, "data", "i2_dump.json"), encoding="utf-8") as f:
        en_all = json.load(f)
    en1 = {k: v[0] for k, v in en_all.items()}
    assert set(cn) == set(en1), f"键不一致: CN={len(cn)} EN={len(en1)}"
    rows = sorted(cn.items())
    out = os.path.join(ROOT, "data", "en_zh_pairs.tsv")
    with open(out, "w", encoding="utf-8") as f:
        f.write("key\tEN\t中文\n")
        for k, z in rows:
            f.write(f"{k}\t{en1[k]}\t{z}\n")
    print(f"已生成: {out} ({len(rows)} 行)")


if __name__ == "__main__":
    main()
