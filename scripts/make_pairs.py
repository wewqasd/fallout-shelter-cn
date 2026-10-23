#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_pairs.py — 重新生成中英对照表 data/en_zh_pairs.tsv（key \t EN \t 中文）。

用法: python scripts/make_pairs.py [仓库根]
输入: data/translations.json（中文权威表） + 最新 EN 基准 i2_dump_<ver>.json（回退 i2_dump.json）
输出: data/en_zh_pairs.tsv
"""
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(
    sys.argv[1] if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
)


def pick_en_dump(root):
    """选最新的 EN 基准（i2_dump_<ver>.json 优先于 i2_dump.json）。

    基准随游戏版本更新而增加；译文表应与最新基准同键，否则说明表未跟进。
    """
    cands = []
    for p in glob.glob(os.path.join(root, "data", "i2_dump*.json")):
        m = re.search(r"i2_dump_(\d+)\.json$", os.path.basename(p))
        cands.append((int(m.group(1)) if m else 0, p))
    if not cands:
        raise SystemExit("未找到 data/i2_dump*.json")
    return max(cands)[1]


def main():
    with open(os.path.join(ROOT, "data", "translations.json"), encoding="utf-8") as f:
        cn = json.load(f)
    en_path = pick_en_dump(ROOT)
    with open(en_path, encoding="utf-8") as f:
        en_all = json.load(f)
    print(f"EN 基准: {os.path.basename(en_path)} ({len(en_all)} 键)")
    en1 = {k: v[0] for k, v in en_all.items()}
    assert set(cn) == set(en1), f"键不一致: CN={len(cn)} EN={len(en1)}"
    rows = sorted(cn.items())
    out = os.path.join(ROOT, "data", "en_zh_pairs.tsv")
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, dialect="excel-tab", quoting=csv.QUOTE_MINIMAL)
        w.writerow(["key", "EN", "中文"])
        for k, z in rows:
            w.writerow([k, en1[k], z])
    print(f"已生成: {out} ({len(rows)} 行)")


if __name__ == "__main__":
    main()
