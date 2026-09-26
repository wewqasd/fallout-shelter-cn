#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_bundle.py — 校验已汉化的 data.unity3d 内嵌 I2 表是否与翻译表逐条一致。

用法: python tools/verify_bundle.py <data.unity3d> <translations.json>
退出码 0 = 翻译表全部写入；1 = 有缺失/不一致（可在 CI 里当门禁）。
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

import UnityPy                      # noqa: E402
from fs_cn import patcher           # noqa: E402


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    bundle, table = sys.argv[1], sys.argv[2]
    env = UnityPy.load(bundle)
    raw = anchor = None
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        r = o.get_raw_data()
        for a in patcher.ANCHORS:
            if a in r:
                raw, anchor = r, a
                break
        if raw is not None:
            break
    if raw is None:
        print("!! 未找到 I2 LanguageSource（锚点全部缺失）")
        return 1
    terms, _last, LC, _first = patcher.parse_terms(raw, anchor)
    cn = json.load(open(table, encoding="utf-8"))
    vals = {t[0].decode("ascii"): t[2] for t in terms}
    missing = [k for k in cn if k not in vals]
    wrong = [k for k, zh in cn.items() if k in vals and not any(v == zh for v in vals[k])]
    print(f"锚点={anchor.decode() if isinstance(anchor, bytes) else anchor} "
          f"terms={len(terms)} LC={LC} 表={len(cn)} 缺失={len(missing)} 不一致={len(wrong)}")
    for s in ("定居者", "奶油小马", "战斗装甲", "每日任务", "保护者机器人", "领头死爪"):
        n = sum(1 for k, zh in cn.items() if s in zh and k in vals and any(v == zh for v in vals[k]))
        print(f"  含『{s}』且已写入: {n}")
    if missing or wrong:
        print("!! 未完全写入；缺失样例:", missing[:5], " 不一致样例:", wrong[:5])
        return 1
    print(f"校验通过：翻译表 {len(cn)} 条全部写入包内")
    return 0


if __name__ == "__main__":
    sys.exit(main())
