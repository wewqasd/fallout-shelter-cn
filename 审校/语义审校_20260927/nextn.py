#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nextn.py [n] [sev] — 打印接下来 n 条未裁决条目（默认 10 条，仅 S2）。"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
q = json.load(open(f'{HERE}/待裁决序列.json', encoding='utf-8'))
dec = set()
p = f'{HERE}/用户裁决.tsv'
if os.path.exists(p):
    for line in open(p, encoding='utf-8').read().splitlines()[1:]:
        if line.strip():
            dec.add(line.split('\t')[0])
n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
sev = sys.argv[2] if len(sys.argv) > 2 else 'S2'
rem = [(i, r) for i, r in enumerate(q, 1) if r['key'] not in dec and (sev == 'all' or r['severity'] == sev)]
print(f"# {sev} 剩余 {len(rem)} 条；已裁决 {len(dec)}/{len(q)}")
for i, r in rem[:n]:
    print("=" * 70)
    print(f"[{i}] {r['severity']} · {r['type']}  {r['key']}")
    print("EN :", r['EN'].replace('\n', ' ⏎ '))
    print("ZH :", r['ZH'].replace('\n', ' ⏎ '))
    print("问题:", r['problem'].replace(' ／ ', '\n   ／ '))
    print("建议:", r['final_fix'].replace('\\n', ' ⏎ '))
