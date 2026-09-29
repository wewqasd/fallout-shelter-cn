#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""汇总 out/*.json：校验字段与 key 合法性 → findings_all.json + 复核批次 batches/。
用法: python3 collect.py [--batches N]
"""
import json, os, sys, glob, collections, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SEV = {'S1', 'S2', 'S3'}
CONF = {'high', 'medium', 'low'}
TYPES = {'误译','漏译','多译','数字','指代','乱译','语序','生硬','语气','病句','错别字','其他'}

d = json.load(open(os.path.join(ROOT, 'data/translations.json'), encoding='utf-8'))
i2 = json.load(open(os.path.join(ROOT, 'data/i2_dump.json'), encoding='utf-8'))

rows, bad, files = [], [], sorted(glob.glob(os.path.join(HERE, 'out', '*.json')))
lens_seen = {}
for p in files:
    name = os.path.basename(p)
    try:
        j = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        bad.append({'file': name, 'err': f'JSON 解析失败: {e}'})
        continue
    cid = j.get('chunk'); lens = j.get('lens')
    lens_seen[f'{cid}_{lens}'] = len(j.get('findings', []))
    for f in j.get('findings', []):
        k = f.get('key', '')
        if k not in d:
            bad.append({'file': name, 'err': f'未知 key', 'key': k}); continue
        if f.get('severity') not in SEV:
            bad.append({'file': name, 'err': f'severity 非法 {f.get("severity")!r}', 'key': k}); continue
        rows.append({
            'key': k, 'chunk': cid, 'lens': lens,
            'severity': f.get('severity'),
            'type': f.get('type') if f.get('type') in TYPES else '其他',
            'confidence': f.get('confidence') if f.get('confidence') in CONF else 'medium',
            'problem': (f.get('problem') or '').strip(),
            'fix': (f.get('fix') or '').strip(),
            'EN': i2[k][0], 'ZH': d[k],
        })

# 同一 key 多条 → 合并：取最严重等级 + 最长的问题描述
RANK = {'S1': 0, 'S2': 1, 'S3': 2}
merged = {}
for r in rows:
    cur = merged.get(r['key'])
    if cur is None:
        merged[r['key']] = r
        continue
    keep, other = (r, cur) if RANK[r['severity']] < RANK[cur['severity']] else (cur, r)
    if len(other['problem']) > len(keep['problem']):
        keep['problem'] = keep['problem'] + ' ／ ' + other['problem']
    if len(other['fix']) > len(keep['fix']) and RANK[other['severity']] == RANK[keep['severity']]:
        keep['fix'] = other['fix']
    keep['lens'] = '+'.join(sorted(set(keep['lens'].split('+')) | set(other['lens'].split('+'))))
    keep['dup'] = True
    merged[r['key']] = keep

res = sorted(merged.values(), key=lambda r: (r['severity'], r['key']))
json.dump({'files': len(files), 'raw': len(rows), 'unique_keys': len(res), 'bad': bad, 'findings': res},
          open(os.path.join(HERE, 'findings_all.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(bad, open(os.path.join(HERE, 'findings_bad.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print(f'文件数 {len(files)}  原始条数 {len(rows)}  去重后 {len(res)}  非法 {len(bad)}')
print('严重度分布', dict(collections.Counter(r['severity'] for r in res)))
print('类型分布  ', dict(collections.Counter(r['type'] for r in res).most_common()))
if bad[:5]:
    print('非法样例:', bad[:5])
missing = [f'{i:03d}_{l}' for i in range(1, 80) for l in ('accuracy', 'fluency')
           if f'{i:03d}_{l}' not in lens_seen]
print(f'缺失审校单元 {len(missing)}: {missing}')

# ---- 生成复核批次 ----
BATCH = int(sys.argv[sys.argv.index('--batches') + 1]) if '--batches' in sys.argv else 10
bdir = os.path.join(HERE, 'batches')
os.makedirs(bdir, exist_ok=True)
for f in glob.glob(os.path.join(bdir, 'batch_*.json')):
    os.remove(f)
for i in range(0, len(res), BATCH):
    grp = res[i:i + BATCH]
    json.dump({'batch': i // BATCH + 1, 'items': grp},
              open(os.path.join(bdir, f'batch_{i//BATCH+1:03d}.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
print(f'复核批次 {len(range(0, len(res), BATCH))} 个（每批 {BATCH} 条）→ batches/')
