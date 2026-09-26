#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""count_variants.py — 对一组候选中文写法做全库计数，用于发现同义混用。

输入: 同目录 variants.txt（每行一个候选写法，# 开头为注释）
输出: stdout，按组列出「写法 × 条数 + 样例 key」
"""
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def main():
    groups = []
    with open(os.path.join(HERE, "variants.txt"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            groups.append([s.strip() for s in line.split("|") if s.strip()])
    rows = list(csv.reader(open(os.path.join(ROOT, "data", "en_zh_pairs.tsv"),
                               encoding="utf-8", newline=""), dialect="excel-tab"))[1:]
    for g in groups:
        print(f"### {' vs '.join(g)}")
        for s in g:
            hit = [(k, en, zh) for k, en, zh in rows if s in zh]
            keys = ", ".join(k for k, _e, _z in sorted(hit)[:3])
            print(f"  {s}: {len(hit)} 条   样例: {keys}")
        print()


if __name__ == "__main__":
    main()
