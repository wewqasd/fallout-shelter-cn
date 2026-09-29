#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""decide_batch.py — 一次记录多条裁决。
用法: python3 decide_batch.py key1=采纳 key2=保持 key3=自定义:译文 ...
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
q = json.load(open(f'{HERE}/待裁决序列.json', encoding='utf-8'))
byk = {r['key']: r for r in q}
p = f'{HERE}/用户裁决.tsv'
lines = [l for l in open(p, encoding='utf-8').read().splitlines() if l.strip()] if os.path.exists(p) else []
if not lines or not lines[0].startswith('key\t'):
    lines = ['key\tseverity\t裁决\t最终译文'] + lines
kept = {l.split('\t')[0]: l for l in lines[1:]}
for arg in sys.argv[1:]:
    key, _, verdict = arg.partition('=')
    assert key in byk, f'未知 key: {key}'
    r = byk[key]
    if verdict.startswith('采纳'):
        final, tag = r['final_fix'], '采纳'
    elif verdict.startswith('保持'):
        final, tag = '', '保持'
    else:
        final, tag = verdict.split(':', 1)[1] if ':' in verdict else '', '自定义'
    kept[key] = f"{key}\t{r['severity']}\t{tag}\t{final.replace(chr(10), chr(92)+'n')}"
out = ['key\tseverity\t裁决\t最终译文'] + list(kept.values())
open(p, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
done = len(kept)
tot = len(q)
s2 = sum(1 for k in kept if byk.get(k, {}).get('severity') == 'S2')
s3 = sum(1 for k in kept if byk.get(k, {}).get('severity') == 'S3')
print(f'已记录 {len(sys.argv)-1} 条；累计 {done}/{tot}（S1 72/72，S2 {s2}/585，S3 {s3}/577）')
