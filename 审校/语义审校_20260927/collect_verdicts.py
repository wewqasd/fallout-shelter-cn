#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collect_verdicts.py — 汇总复核结果，生成已确认清单 + 修复清单。
输入: vout/batch_*.json（复核员产出） + findings_all.json（初审去重结果）
输出: findings_verified.json / 修复清单_20260927.tsv / 汇总统计
"""
import json, os, glob, collections, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
d = json.load(open(f'{ROOT}/data/translations.json', encoding='utf-8'))

base = json.load(open(f'{HERE}/findings_all.json', encoding='utf-8'))
by_key = {r['key']: r for r in base['findings']}

SEV = {'S1', 'S2', 'S3'}
VERDICTS = ('confirm', 'confirm_fix_better', 'reject', 'uncertain')
vmap, bad, batches = {}, [], 0
for p in sorted(glob.glob(f'{HERE}/vout/batch_*.json')):
    try:
        j = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        bad.append({'file': os.path.basename(p), 'err': str(e)}); continue
    batches += 1
    for it in j.get('items', []):
        k = it.get('key')
        if k not in d:
            bad.append({'file': os.path.basename(p), 'err': 'unknown key', 'key': k}); continue
        v = it.get('verdict')
        if v not in VERDICTS:
            bad.append({'file': os.path.basename(p), 'err': f'verdict {v!r}', 'key': k}); continue
        vmap[k] = {'verdict': v, 'reason': (it.get('reason') or '').strip(),
                   'final_fix': (it.get('final_fix') or '').strip(),
                   'severity': it.get('severity') if it.get('severity') in SEV else None}

rows = []
for k, r in by_key.items():
    v = vmap.get(k)
    if v is None:
        continue
    if v['verdict'] == 'reject':
        r['status'] = 'rejected'; r['v_reason'] = v['reason']; r['final_fix'] = ''
    elif v['verdict'] == 'confirm':
        r['status'] = 'confirmed'; r['v_reason'] = v['reason']
        r['final_fix'] = r['fix']
    elif v['verdict'] == 'confirm_fix_better':
        r['status'] = 'confirmed'; r['v_reason'] = v['reason']
        r['final_fix'] = v['final_fix'] or r['fix']
    else:
        r['status'] = 'uncertain'; r['v_reason'] = v['reason']; r['final_fix'] = r['fix']
    if v.get('severity'):
        r['severity'] = v['severity']          # 以复核员重新判定的等级为准
    rows.append(r)

missing = [k for k in by_key if k not in vmap]
out = sorted(rows, key=lambda r: (r['status'] != 'confirmed', r['severity'], r['key']))
json.dump({'batches': batches, 'base': len(by_key), 'verified': len(rows), 'missing': missing,
           'bad': bad, 'findings': out},
          open(f'{HERE}/findings_verified.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print(f'复核批次 {batches}  初审 {len(by_key)}  已复核 {len(rows)}  未覆盖 {len(missing)}  非法 {len(bad)}')
print('状态分布', dict(collections.Counter(r['status'] for r in rows)))
print('确认项严重度', dict(collections.Counter(r['severity'] for r in rows if r['status'] == 'confirmed')))
if missing:
    print('未覆盖 key 样例:', missing[:10])

# ---- 修复清单 ----
conf = [r for r in rows if r['status'] == 'confirmed' and r['final_fix'] and r['final_fix'] != r['ZH']]
with open(f'{HERE}/修复清单_20260927.tsv', 'w', encoding='utf-8') as f:
    f.write('key\tnew_zh\tseverity\ttype\t旧译\n')
    for r in conf:
        f.write(f"{r['key']}\t{r['final_fix'].replace(chr(10), chr(92)+'n')}\t{r['severity']}\t{r['type']}\t{r['ZH'].replace(chr(10), chr(92)+'n')}\n")
print(f'修复清单: {len(conf)} 条 → 修复清单_20260927.tsv')
