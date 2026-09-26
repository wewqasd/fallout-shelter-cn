#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""show_term.py — 核查单个专名在译文里的中文写法。

用法:
  python3 show_term.py "Deathclaw"            # 全部条目 + 写法频次
  python3 show_term.py "Deathclaw" --limit 40 # 限制条数
  python3 show_term.py "Deathclaw" --only "死爪,死亡爪"   # 只列含指定写法的条目

输出三部分:
  1) 命中条目总数
  2) 中文 n-gram 频次（len 2-8，≥2 条出现；用于发现不同写法）
  3) 逐条 key / EN / ZH（默认最多 40 条，按 key 排序）
"""
import csv
import os
import re
import sys
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CJK = re.compile(r"^[\u4e00-\u9fff·•‧・]+$")
WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")


def word_match(text, term):
    pat = r"(?<![A-Za-z])" + re.escape(term).replace(r"\ ", r"\s+") + r"(?![A-Za-z])"
    return re.search(pat, text, re.IGNORECASE) is not None


def main():
    term = sys.argv[1]
    limit = 40
    only = None
    if "--zh" in sys.argv:
        s = sys.argv[sys.argv.index("--zh") + 1]
        rows = list(csv.reader(open(os.path.join(ROOT, "data", "en_zh_pairs.tsv"),
                                    encoding="utf-8", newline=""), dialect="excel-tab"))[1:]
        hit = [(k, en, zh) for k, en, zh in rows if s in zh]
        print(f"# 中文串 {s!r}：全库命中 {len(hit)} 条")
        for k, en, zh in sorted(hit)[:60]:
            print(f"- {k}\n    EN: {en[:130]!r}\n    ZH: {zh[:130]!r}")
        return
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    if "--only" in sys.argv:
        only = [s.strip() for s in sys.argv[sys.argv.index("--only") + 1].split(",") if s.strip()]

    rows = list(csv.reader(open(os.path.join(ROOT, "data", "en_zh_pairs.tsv"),
                                encoding="utf-8", newline=""), dialect="excel-tab"))[1:]
    hit = [(k, en, zh) for k, en, zh in rows if word_match(en, term)]
    print(f"# 专名: {term}")
    print(f"命中条目: {len(hit)} / {len(rows)}")

    df = Counter()
    for _k, _en, zh in hit:
        seen = set()
        for seg in re.findall(r"[\u4e00-\u9fff]+(?:[·•‧・][\u4e00-\u9fff]+)*", zh):
            for n in range(2, min(9, len(seg)) + 1):
                for i in range(len(seg) - n + 1):
                    g = seg[i:i + n]
                    if CJK.match(g):
                        seen.add(g)
        for g in seen:
            df[g] += 1
    top = sorted([(g, c) for g, c in df.items() if c >= 2], key=lambda x: (-x[1], -len(x[0])))
    kept = []
    for g, c in top:                      # 先长后短；丢弃被更长候选包含的碎片
        if any(g != h and g in h for h, _ in kept):
            continue
        kept.append((g, c))
    print("\n## 中文写法候选（极大 n-gram，出现 ≥2 条，按条数降序）")
    for g, c in kept[:30]:
        print(f"   {g:<20} {c:>4} 条  ({c/len(hit):.0%})")

    print(f"\n## 逐条明细（最多 {limit} 条）")
    n = 0
    for k, en, zh in sorted(hit):
        if only and not any(o in zh for o in only):
            continue
        print(f"- {k}\n    EN: {en[:150]!r}\n    ZH: {zh[:150]!r}")
        n += 1
        if n >= limit:
            print(f"  …（共 {len(hit)} 条，已截断）")
            break


if __name__ == "__main__":
    main()
