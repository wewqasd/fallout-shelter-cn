#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""decide.py — 记录用户对单条修订的裁决（按 key 记录，避免错位）。
用法: python3 decide.py <key> <采纳|保持> [自定义译文]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
q = json.load(open(f'{HERE}/待裁决序列.json', encoding='utf-8'))
byk = {r['key']: r for r in q}
key = sys.argv[1]
verdict = sys.argv[2]
custom = sys.argv[3] if len(sys.argv) > 3 else ''
assert key in byk, f'未知 key: {key}'
r = byk[key]
if verdict.startswith('采纳'):
    final, tag = r['final_fix'], '采纳'
elif verdict.startswith('保持'):
    final, tag = '', '保持'
else:
    final, tag = custom, '自定义'
lines = []
p = f'{HERE}/用户裁决.tsv'
if os.path.exists(p):
    lines = [l for l in open(p, encoding='utf-8').read().splitlines() if l.strip()]
    lines = [l for l in lines if l.split('\t')[0] != key and l.startswith('key\t') is False or l.startswith('key\t')]
if not lines or not lines[0].startswith('key\t'):
    lines = ['key\tseverity\t裁决\t最终译文'] + lines
lines.append(f"{key}\t{r['severity']}\t{tag}\t{final.replace(chr(10), chr(92)+'n')}")
open(p, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(f'已记录 {key} → {tag}（累计 {len(lines)-1}/{len(q)}）')
