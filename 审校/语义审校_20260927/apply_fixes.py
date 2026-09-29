#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_fixes.py — 把审定后的修订写回 data/translations.json，并重建三表。

用法:
  python3 apply_fixes.py 修复清单.tsv          # 落地
  python3 apply_fixes.py 修复清单.tsv --dry    # 只预览

清单格式（UTF-8，制表符分隔，首行表头）:
  key <TAB> new_zh <TAB> note(可省略)
  new_zh 中的换行写成字面 \n（反斜杠+n），脚本会还原成真实换行。

安全约束（写回前全部通过才落盘）:
  * key 必须存在于 translations.json
  * new_zh 非空
  * {0}/{1} 占位符集合必须与 EN 一致（硬项）
  * 换行段数必须与 EN 一致
  * 与旧值相同的条目跳过
写回后自动重建 translations.tsv + en_zh_pairs.tsv，并做一次三方一致性自检。
"""
import json, os, re, subprocess, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DRY = '--dry' in sys.argv
PATH = next((a for a in sys.argv[1:] if not a.startswith('--')), None)
assert PATH, '需要修复清单路径'

PH = re.compile(r'\{[0-9]+\}')
d = json.load(open(f'{ROOT}/data/translations.json', encoding='utf-8'))
i2 = json.load(open(f'{ROOT}/data/i2_dump.json', encoding='utf-8'))
EN = {k: v[0] for k, v in i2.items()}

rows, problems, skipped, unusual = [], [], [], []
with open(PATH, encoding='utf-8') as f:
    header = f.readline()
    for ln, line in enumerate(f, 2):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            problems.append((ln, '字段不足', line[:60])); continue
        k, new = parts[0].strip(), parts[1].replace('\\n', '\n')
        if k not in d:
            problems.append((ln, '未知 key', k)); continue
        if not new.strip():
            problems.append((ln, '空值', k)); continue
        if new == d[k]:
            skipped.append(k); continue
        if set(PH.findall(new)) != set(PH.findall(EN[k])):
            problems.append((ln, f'占位符不一致 ZH={sorted(set(PH.findall(new)))} EN={sorted(set(PH.findall(EN[k])))}', k)); continue
        if len(new.split('\n')) != len(d[k].split('\n')):
            problems.append((ln, f'换行段数 {len(new.split(chr(10)))} != 现译 {len(d[k].split(chr(10)))}', k)); continue
        if '\\' in new and '\\' not in d[k]:
            problems.append((ln, '新译文引入了反斜杠', k)); continue
        ratio = len(new) / max(len(d[k]), 1)
        if ratio < 0.5 or ratio > 2.5:
            unusual.append((k, len(d[k]), len(new), ratio))
        rows.append((k, d[k], new))

rows_kv = {k: n for k, _o, n in rows}
print(f'待改 {len(rows)} 条   跳过(与旧值相同) {len(skipped)} 条   拒绝 {len(problems)} 条')
for ln, why, k in problems[:20]:
    print(f'  [拒绝] 第{ln}行 {k}: {why}')
if problems:
    print('存在被拒绝的条目，已中止（请修正清单后重跑）')
    sys.exit(2)
for k, old, new in rows[:10]:
    print(f'  {k}\n     旧: {old[:80]!r}\n     新: {new[:80]!r}')
if len(rows) > 10:
    print(f'  … 其余 {len(rows)-10} 条')
if unusual:
    print(f'\n长度变动较大（需人工过一眼）{len(unusual)} 条：')
    for k, a, b, r in sorted(unusual, key=lambda x: abs(x[3]-1), reverse=True)[:25]:
        print(f'  {r:5.2f}x  {a:4d}->{b:4d}  {k}')
        print(f'        旧: {d[k][:70]!r}')
        print(f'        新: {rows_kv.get(k, "")[:70]!r}')
if DRY:
    print('(--dry 预览，未写盘)')
    sys.exit(0)

for k, _old, new in rows:
    d[k] = new

open(f'{ROOT}/data/translations.json', 'w', encoding='utf-8').write(
    json.dumps(d, ensure_ascii=False, indent=1) + '\n')
with open(f'{ROOT}/data/translations.tsv', 'w', encoding='utf-8') as f:
    for k, v in d.items():
        parts = v.split('\n')
        f.write(k + '\t' + parts[0] + '\n')
        for x in parts[1:]:
            f.write(x + '\n')
subprocess.run([sys.executable, f'{ROOT}/scripts/make_pairs.py'], cwd=ROOT, check=True)
subprocess.run([sys.executable, f'{HERE}/check_tables.py'], check=True)
print(f'已写回三表，共 {len(rows)} 条修改')
