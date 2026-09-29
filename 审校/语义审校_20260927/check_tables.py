#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_tables.py — 校验「中英对照表」与编译输入表是否严格一致。

编译输入（权威源）: data/translations.json   ← patcher/resources.py 实际读取
派生产物（只给人看）: data/en_zh_pairs.tsv    ← scripts/make_pairs.py 生成
同源 TSV 视图        : data/translations.tsv

输出: 各表键集合/取值差异统计 + 差异样例（打印到 stdout）
"""
import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def load_json():
    with open(os.path.join(ROOT, "data", "translations.json"), encoding="utf-8") as f:
        return json.load(f)


def load_translations_tsv(path):
    """translations.tsv 为「续行块」格式：key<TAB>首行，后续物理行（含空行）属于同一值，
    值内的 \\n 写作真实换行。返回 {key: value}。"""
    rows = {}
    dup = []
    cur = None
    parts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if "\t" in line:
                if cur is not None:
                    rows[cur] = "\n".join(parts)
                cur, first = line.split("\t", 1)
                if cur in rows:
                    dup.append(cur)
                parts = [first]
            else:
                if cur is None:
                    continue
                parts.append(line)
    if cur is not None:
        rows[cur] = "\n".join(parts)
    return rows, dup


def load_pairs():
    rows = {}
    dup = []
    with open(os.path.join(ROOT, "data", "en_zh_pairs.tsv"), encoding="utf-8", newline="") as f:
        r = csv.reader(f, dialect="excel-tab")
        header = next(r)
        for row in r:
            if len(row) < 3:
                continue
            k, en, zh = row[0], row[1], row[2]
            if k in rows:
                dup.append(k)
            rows[k] = (en, zh)
    return header, rows, dup


def diff_report(name_a, a, name_b, b, limit=20):
    ka, kb = set(a), set(b)
    only_a, only_b = sorted(ka - kb), sorted(kb - ka)
    common = sorted(ka & kb)
    mismatch = [k for k in common if a[k] != b[k]]
    print(f"\n===== {name_a}  vs  {name_b}")
    print(f"  条目数: {len(a)} vs {len(b)}")
    print(f"  仅 {name_a} 有: {len(only_a)}  仅 {name_b} 有: {len(only_b)}")
    print(f"  同键不同值: {len(mismatch)}")
    for label, keys in (("仅A", only_a), ("仅B", only_b)):
        for k in keys[:limit]:
            print(f"    [{label}] {k}")
    for k in mismatch[:limit]:
        print(f"    [值不同] {k}")
        print(f"        A: {str(a[k])[:150]!r}")
        print(f"        B: {str(b[k])[:150]!r}")
    return only_a, only_b, mismatch


def main():
    cn = load_json()
    tsv, tsv_dup = load_translations_tsv(os.path.join(ROOT, "data", "translations.tsv"))
    header, pairs, pairs_dup = load_pairs()
    print(f"translations.json : {len(cn)} 键")
    print(f"translations.tsv  : {len(tsv)} 键（重复键 {len(tsv_dup)}）")
    print(f"en_zh_pairs.tsv   : {len(pairs)} 键（表头 {header}，重复键 {len(pairs_dup)}）")

    diff_report("translations.json", cn, "translations.tsv", tsv)
    pairs_zh = {k: v[1] for k, v in pairs.items()}
    pairs_en = {k: v[0] for k, v in pairs.items()}
    diff_report("translations.json", cn, "en_zh_pairs.tsv(中文列)", pairs_zh)

    # EN 列与 i2_dump.json 是否一致
    with open(os.path.join(ROOT, "data", "i2_dump.json"), encoding="utf-8") as f:
        dump = json.load(f)
    en1 = {k: v[0] for k, v in dump.items()}
    diff_report("en_zh_pairs.tsv(EN列)", pairs_en, "i2_dump.json[0]", en1)


if __name__ == "__main__":
    main()
