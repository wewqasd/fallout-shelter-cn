#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collect_genealogy.py — 从 DSH 会话留档提取 Agent 谱系数据。

数据来源（只读，不修改）:
  ~/.dsh/sessions/<project-slug>/session-<root-id>/session.v4.jsonl.zstd   ← 根会话事件流
  ~/.dsh/sessions/<project-slug>/<child-uuid>/session.v4.jsonl.zstd        ← 每个子 agent 的会话

输出: _genealogy_raw.json
  hdr     根会话头（id / createdAt / delegationDepth / agentPreset）
  catalog 273 条 subagent/catalog（childId → label / childCreatedAt / mode）
  starts  268 条 tool-workflow/agent-start（runId / seq / label / phase / childId / time）
  ends    268 条 tool-workflow/agent-end（runId / seq / outcome / time）
  subs    273 个子会话元数据（createdAt / parent / depth / origin / bytes / lines / mtime）
  turns   用户回合时间戳
  tools   主控工具调用计数

用法:
  python3 collect_genealogy.py [project-slug] [root-session-id]
默认 project-slug = --home-wangqiang-fallout_shelter_hanhua--
"""
import json, os, sys, glob, subprocess, collections

SLUG = sys.argv[1] if len(sys.argv) > 1 else '--home-wangqiang-fallout_shelter_hanhua--'
ROOT_ID = sys.argv[2] if len(sys.argv) > 2 else 'session-124f2d98-88a2-4082-adbe-bc828d43dc39'
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.expanduser(f'~/.dsh/sessions/{SLUG}')
ROOT = os.path.join(BASE, ROOT_ID, 'session.v4.jsonl.zstd')
assert os.path.exists(ROOT), f'找不到根会话: {ROOT}'


def stream(path):
    p = subprocess.Popen(['zstdcat', path], stdout=subprocess.PIPE, text=True, encoding='utf-8')
    for line in p.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except Exception:
            continue
    p.wait()


cat, starts, ends, turns, hdr = {}, [], [], [], None
tools = collections.Counter()
for r in stream(ROOT):
    t, d = r.get('type'), (r.get('data') or {})
    if t == 'session':
        hdr = r
    elif t == 'subagent/catalog':
        cat[d.get('childId')] = {**d, 'time': r.get('time')}
    elif t == 'tool-workflow/agent-start':
        starts.append({**d, 'time': r.get('time')})
    elif t == 'tool-workflow/agent-end':
        ends.append({**d, 'time': r.get('time')})
    elif t == 'turn/start':
        turns.append({'time': r.get('time'), 'seq': r.get('seq')})
    elif t == 'tool/call':
        tools[d.get('name') or d.get('toolName') or '?'] += 1

subs = {}
for dd in glob.glob(os.path.join(BASE, '*')):
    if not os.path.isdir(dd) or os.path.basename(dd).startswith('session-'):
        continue
    f = os.path.join(dd, 'session.v4.jsonl.zstd')
    if not os.path.exists(f):
        continue
    try:
        head = subprocess.run(['zstdcat', f], stdout=subprocess.PIPE, text=True,
                              encoding='utf-8', timeout=120).stdout
    except Exception:
        continue
    try:
        h = json.loads(head.split('\n', 1)[0])
    except Exception:
        continue
    subs[h['id']] = {'createdAt': h.get('createdAt'), 'parent': h.get('parentSession'),
                     'depth': h.get('delegationDepth'), 'origin': h.get('origin'),
                     'preset': h.get('agentPreset'), 'bytes': os.path.getsize(f),
                     'lines': head.count('\n'), 'mtime': int(os.path.getmtime(f) * 1000)}

out = {'hdr': hdr, 'catalog': cat, 'starts': starts, 'ends': ends, 'subs': subs,
       'turns': turns, 'tools': dict(tools)}
json.dump(out, open(f'{HERE}/_genealogy_raw.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(f'根会话 {hdr["id"]}: catalog={len(cat)} start={len(starts)} end={len(ends)} 子会话={len(subs)} 回合={len(turns)}')
print(f'阶段: {collections.Counter(s.get("phase") for s in starts).most_common()}')
