#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_remaining.py — 完整版「一词多译」扫描（主写法 + 互斥异写）。

思路：
  对每个英文候选词 W：
    1) pool = 含 W 的条目（最长匹配，避免碎片）
    2) dominant = pool 中出现率最高的中文 n-gram（主写法）
    3) 异写 = 与 dominant **互斥**（同条几乎不共现）且不与它互为子串、出现 ≥2 条的中文 n-gram
       —— 互斥性是关键：真正的一词多译在同一条目里不会同时出现，
          而「同一句话的碎片」「其它成分」都与主写法高度共现，会被自动排除。
输出:
  remaining_variants.tsv  EN词 | 条目数 | 主写法(条数) | 异写(条数) | 异写样例key | 异写样例中文
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "remaining_variants.tsv")

CJK = re.compile(r"^[\u4e00-\u9fff·•‧・]+$")
TOKEN = re.compile(r"[\u4e00-\u9fff]+(?:[·•‧・][\u4e00-\u9fff]+)*")
WORD = re.compile(r"[A-Za-z][A-Za-z'’\-]*")

STOP = set("""a an the and or of to in on for with at by from is are was were be been being you your
yours we our us they them their it its he she his her i me my this that these those all any some no
not new add more less up down out off over under again now then here there what which who when where
why how can cannot could will would shall should may might must do does did done have has had get got
go goes going come comes coming make makes making take takes taking use uses used using yes ok okay
please level levels time times day days week weeks hour hours minute minutes second seconds quest
quests item items room rooms dweller dwellers vault vaults find found search select choose open close
save back next done cancel confirm start end play stop buy sell equip unequip reward rewards value
values name names type types total max min count number slot slots card cards pack packs only also just
each every both few many most other others same than too very well still even much more left right top
bottom best good great rare common legendary epic normal hard easy goal goals objective if so but
you'll we'll they'll it's i'm don't doesn't didn't can't won't there's that's what's let's""".split())


def word_match(text, term):
    pat = r"(?<![A-Za-z])" + re.escape(term).replace(r"\ ", r"\s+") + r"(?![A-Za-z])"
    return re.search(pat, text, re.IGNORECASE) is not None


def ngrams(zh):
    out = set()
    for seg in TOKEN.findall(zh):
        for n in range(2, min(10, len(seg)) + 1):
            for i in range(len(seg) - n + 1):
                g = seg[i:i + n]
                if CJK.match(g):
                    out.add(g)
    return out


def main():
    rows = list(csv.reader(open(os.path.join(ROOT, "data", "en_zh_pairs.tsv"),
                               encoding="utf-8", newline=""), dialect="excel-tab"))[1:]
    low = [en.lower() for _k, en, _z in rows]
    N = len(rows)
    global_df = Counter()
    zh_grams = []
    for _k, _en, zh in rows:
        gs = ngrams(zh)
        zh_grams.append(gs)
        for g in gs:
            global_df[g] += 1

    # 候选英文词：大写率高的词（含专名）+ 多词大写短语
    occ, cap, mid = Counter(), Counter(), Counter()
    for _k, en, _z in rows:
        for m in WORD.finditer(en):
            t = m.group(0)
            occ[t] += 1
            if t[0].isupper():
                cap[t] += 1
            if m.start() > 0 and en[m.start() - 1] not in ".!?\n":
                mid[t] += 1
        for m in re.finditer(r"\b[A-Z][A-Za-z'’\-]*(?:\s+(?:of|the|and|de|von|&)\s+|\s+)"
                             r"[A-Z][A-Za-z'’\-]*(?:\s+(?:of|the|and|de|von|&)\s+|\s+[A-Z][A-Za-z'’\-]*)*", en):
            seq = m.group(0).strip().rstrip(".")
            if len(seq.split()) >= 2 and "\n" not in seq and not re.search(r"[.!?,:;]", seq):
                occ[seq] += 1
                cap[seq] += 1
    # 专名口径：句中大写出现 ≥2 次（或本身是多词短语）
    cands = [t for t, c in occ.items()
             if c >= 3 and len(t) >= 3 and t.lower() not in STOP
             and cap[t] / c >= 0.7 and (mid[t] >= 2 or " " in t)]
    print(f"英文候选词 {len(cands)} 个")

    # 最长匹配池
    hits = []
    for i, l in enumerate(low):
        s = {t for t in cands if t.lower() in l and word_match(rows[i][1], t)}
        hits.append({t for t in s if not any(o != t and t.lower() in o.lower() for o in s)})
    short = [len(en.split()) <= 5 for _k, en, _z in rows]   # 标签类条目（短 EN）
    entry_of = defaultdict(list)
    for i, s in enumerate(hits):
        if not short[i]:
            continue
        for t in s:
            entry_of[t].append(i)

    out = []
    for term in cands:
        pool = entry_of.get(term, [])
        if len(pool) < 3:
            continue
        local = Counter()
        for i in pool:
            for g in zh_grams[i]:
                local[g] += 1
        dom_c = [(g, c) for g, c in local.items()
                 if c >= max(2, 0.35 * len(pool)) and global_df[g] / N <= 0.02]
        if not dom_c:
            continue
        dom, dom_n = max(dom_c, key=lambda x: (x[1], len(x[0])))
        alts = []
        for g, c in local.items():
            if g == dom or c < 2 or len(g) < 2:
                continue
            if global_df[g] / N > 0.02:
                continue
            if g in dom or dom in g:
                continue
            co = sum(1 for i in pool if g in zh_grams[i] and dom in zh_grams[i])
            if c < max(2, 0.06 * len(pool)):
                continue
            if co <= 0.15 * min(c, dom_n):
                alts.append((g, c))
        alts.sort(key=lambda x: -x[1])
        keep = []
        for g, c in alts:
            if any(g != h and (g in h or h in g) for h, _ in keep):
                continue
            keep.append((g, c))
        for g, c in keep:
            ex = [(rows[i][0], rows[i][1][:60], rows[i][2][:60]) for i in pool if g in zh_grams[i]]
            out.append((term, len(pool), dom, dom_n, g, c, ex[0][0], ex[0][2].replace("\n", " ")))
    out.sort(key=lambda x: (-x[1], -x[5]))
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, dialect="excel-tab")
        w.writerow(["EN词", "条目数", "主写法", "主写法条数", "异写", "异写条数", "异写样例key", "异写样例中文"])
        w.writerows(out)
    print(f"互斥异写候选 {len(out)} 条（涉及 {len(set(r[0] for r in out))} 个英文词）-> {OUT}")


if __name__ == "__main__":
    main()
