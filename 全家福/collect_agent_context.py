#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collect_agent_context.py — 提取每个子 Agent 会话的上下文组成（按记录类型的字节量）。

输出 _agent_context.json：{childId: {bytes_total, records, tools, steps, comp{类别:字节}}}
组成映射对齐 dsh-context 的 Agent Network 六色分类。
"""
import json, os, re, sys, glob, subprocess, collections

SLUG = sys.argv[1] if len(sys.argv) > 1 else '--home-wangqiang-fallout_shelter_hanhua--'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.expanduser(f'~/.dsh/sessions/{SLUG}')
PAT = re.compile(r'^\{"type":"([^"]+)"')

# 记录类型 → dsh-context 的六色分类
COMP = {
    'system/message':        'system',
    'request/header':        'toolSchema',
    'user/message':          'user',
    'agent/inbox/spliced':   'injected',
    'system/reminder':       'injected',
    'context/inject':        'injected',
    'assistant/message':     'assistant',
    'tool/result':           'toolResult',
}
CATS = ['system', 'toolSchema', 'user', 'injected', 'assistant', 'toolResult']

out = {}
for dd in sorted(glob.glob(os.path.join(BASE, '*'))):
    if not os.path.isdir(dd):
        continue
    f = os.path.join(dd, 'session.v4.jsonl.zstd')
    if not os.path.exists(f):
        continue
    byt = collections.Counter()
    rec = collections.Counter()
    p = subprocess.Popen(['zstdcat', f], stdout=subprocess.PIPE, text=True, encoding='utf-8')
    for line in p.stdout:
        m = PAT.match(line)
        t = m.group(1) if m else '?'
        byt[t] += len(line)
        rec[t] += 1
    p.wait()
    comp = collections.Counter()
    for t, v in byt.items():
        comp[COMP.get(t, 'other')] += v
    compN = collections.Counter()
    for t, v in rec.items():
        compN[COMP.get(t, 'other')] += v
    out[os.path.basename(dd)] = {
        'bytes': sum(byt.values()), 'records': sum(rec.values()),
        'tools': rec.get('tool/call', 0), 'steps': rec.get('step/start', 0),
        'requests': rec.get('request/header', 0),
        'comp': {c: comp.get(c, 0) for c in CATS},
        'compN': {c: compN.get(c, 0) for c in CATS},
    }

json.dump(out, open(f'{HERE}/_agent_context.json', 'w', encoding='utf-8'), ensure_ascii=False)
tot = sum(v['bytes'] for v in out.values())
print(f'提取 {len(out)} 个子会话，合计 {tot/1024/1024:.1f} MB')
k = max(out, key=lambda x: out[x]['bytes'])
print(f"最大: {k} {out[k]['bytes']/1024:.0f}K 工具{out[k]['tools']} 步{out[k]['steps']} 请求{out[k]['requests']}")
