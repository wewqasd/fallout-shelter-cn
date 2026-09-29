#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nextq.py — 打印下一条尚未裁决的条目（S1 → S2 → S3），供逐条提问使用。
用法: python3 nextq.py [起始序号] [条数]
默认打印 1 条；序号从 1 开始（含）。已裁决的 key 自动跳过。
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
q = json.load(open(f'{HERE}/待裁决序列.json', encoding='utf-8'))
done = set()
p = f'{HERE}/用户裁决.tsv'
if os.path.exists(p):
    for line in open(p, encoding='utf-8').read().splitlines()[1:]:
        if line.strip():
            done.add(line.split('\t')[0])
start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
shown = 0
for i, r in enumerate(q, 1):
    if i < start or r['key'] in done:
        continue
    print(f"===== 队列序号 {i} / {len(q)}   [{r['severity']} · {r['type']}]  已裁决 {len(done)}")
    print(f"key: {r['key']}")
    print(f"EN : {r['EN']}")
    print(f"ZH : {r['ZH']}")
    print(f"问题: {r['problem']}")
    print(f"建议: {r['final_fix']}")
    shown += 1
    if shown >= n:
        break
if not shown:
    print('没有未裁决条目了')
