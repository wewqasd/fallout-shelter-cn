#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_chunks.py — 生成语义审校用的上下文连续分片。

做法：把 14064 条按 key 的「自然序」（数字段补零，保证 _2_ 排在 _10_ 前面）排序，
顺序切分为每片 180 条。这样同一任务、同一角色的相邻台词会落在同一片里，
审校 agent 看得到上下文，也便于用 grep 在同片内取上下文。

同时生成 chunks_long/：英文 ≥100 字符的长文本（任务描述/帮助页/教程），每片 60 条，
单独做「逐句完整性」专审。

用法: python3 build_chunks.py
输出: chunks/chunk_NNN.tsv、chunks_long/long_NNN.tsv、manifest.json
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CHUNK = 180
LONG_CHUNK = 60
LONG_MIN = 100

d = json.load(open(f'{ROOT}/data/translations.json', encoding='utf-8'))
i2 = json.load(open(f'{ROOT}/data/i2_dump.json', encoding='utf-8'))
assert set(d) == set(i2)


def natkey(k):
    """数字段补零，使 _2_ 排在 _10_ 之前。"""
    return ''.join(p.zfill(6) if p.isdigit() else p for p in re.split(r'(\d+)', k))


def clean(s):
    """单行化：制表符→空格，换行→字面 \\n（审校端按字面理解）。"""
    return s.replace('\t', ' ').replace('\n', '\\n').replace('\r', '')


def write(dirname, prefix, keys, per):
    os.makedirs(os.path.join(HERE, dirname), exist_ok=True)
    out = []
    for i in range(0, len(keys), per):
        ks = keys[i:i + per]
        cid = f'{i // per + 1:03d}'
        p = os.path.join(HERE, dirname, f'{prefix}_{cid}.tsv')
        with open(p, 'w', encoding='utf-8') as f:
            f.write('key\tEN\tZH\n')
            for k in ks:
                f.write(f'{k}\t{clean(i2[k][0])}\t{clean(d[k])}\n')
        out.append({'id': cid, 'path': os.path.relpath(p, ROOT), 'n': len(ks),
                    'first': ks[0], 'last': ks[-1]})
    return out


keys = sorted(d, key=natkey)
man = write('chunks', 'chunk', keys, CHUNK)
longs = [k for k in keys if len(i2[k][0]) >= LONG_MIN]
man_long = write('chunks_long', 'long', longs, LONG_CHUNK)
json.dump({'chunks': man, 'chunks_long': man_long},
          open(os.path.join(HERE, 'manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'chunks: {len(man)} 片 × {CHUNK} = {len(keys)} 条')
print(f'chunks_long: {len(man_long)} 片 × {LONG_CHUNK} = {len(longs)} 条（EN≥{LONG_MIN} 字符）')
