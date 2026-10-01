#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_poster.py — 从 DSH 会话数据生成「Agent 全家福 · 谱系图」自包含 HTML。

输入: _genealogy_raw.json（由会话 jsonl.zstd 提取，见 README）
输出: agent全家福_谱系图.html（无外部依赖，离线可开）
"""
import json, os, html, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(f'{HERE}/_genealogy_raw.json', encoding='utf-8'))
hdr, cat, starts, ends, subs = raw['hdr'], raw['catalog'], raw['starts'], raw['ends'], raw['subs']

ROLE = {
    'accuracy': ('初审·准确性', '#4a9eff', '⚖'),
    'fluency': ('初审·流畅度', '#2ecc9b', '✎'),
    'long': ('长文本专审', '#f0a437', '📜'),
    'verify': ('对抗复核', '#e5556b', '⚔'),
    'named': ('专名分类审校', '#9b6ce0', '🔍'),
}


def role_of(label):
    l = str(label or '')
    if l.endswith('-accuracy'): return 'accuracy'
    if l.endswith('-fluency'): return 'fluency'
    if l.startswith('long-'): return 'long'
    if l.startswith('verify-'): return 'verify'
    return 'named'


def iso(ms):
    return datetime.datetime.fromtimestamp(ms / 1000)


# ---- 按 run 配对 start/end ----
byrun = collections.defaultdict(lambda: {'s': [], 'e': []})
for s in starts: byrun[s['runId']]['s'].append(s)
for e in ends: byrun[e['runId']]['e'].append(e)

agents = []
for rid, v in byrun.items():
    ss = sorted(v['s'], key=lambda x: x['time'])
    ee = sorted(v['e'], key=lambda x: x['time'])
    for i, s in enumerate(ss):
        end = ee[i] if i < len(ee) else {}
        cid = s.get('childId')
        sub = subs.get(cid, {})
        agents.append({
            'id': cid, 'label': s.get('label'), 'phase': s.get('phase'),
            'run': rid, 'seq': s.get('seq'), 'role': role_of(s.get('label')),
            't0': s.get('time'), 't1': end.get('time'), 'outcome': end.get('outcome', '?'),
            'bytes': sub.get('bytes', 0), 'lines': sub.get('lines', 0),
        })

# ---- 5 个专项子 agent（无 workflow 记录） ----
wf_ids = {a['id'] for a in agents}
for cid, c in cat.items():
    if cid in wf_ids: continue
    sub = subs.get(cid, {})
    agents.append({
        'id': cid, 'label': c.get('label'), 'phase': '专项审校', 'run': None,
        'seq': None, 'role': 'named', 't0': c.get('childCreatedAt'),
        't1': sub.get('mtime'), 'outcome': 'completed',
        'bytes': sub.get('bytes', 0), 'lines': sub.get('lines', 0),
    })

for a in agents:
    a['durSec'] = round((a['t1'] - a['t0']) / 1000, 1) if a['t0'] and a['t1'] else None

# ---- 阶段顺序 ----
PH_ORDER = ['试点审校', '审校A段', '审校B段', '长文本专审', '对抗复核', '专项审校']
phases = []
for p in PH_ORDER:
    mem = [a for a in agents if a['phase'] == p]
    if not mem: continue
    mem.sort(key=lambda a: (str(a['label'])))
    phases.append({
        'name': p, 'agents': mem,
        't0': min(a['t0'] for a in mem), 't1': max(a['t1'] or a['t0'] for a in mem),
        'roles': dict(collections.Counter(a['role'] for a in mem)),
    })

T0 = hdr['createdAt']
T1 = max(a['t1'] or a['t0'] for a in agents)
tot_bytes = sum(a['bytes'] for a in agents)
tot_dur = sum(a['durSec'] or 0 for a in agents)

# ---- 全家福卡片 ----
def card(a, idx):
    rn, col, glyph = ROLE[a['role']]
    dur = f"{a['durSec']:.0f}s" if a['durSec'] is not None else '—'
    kb = f"{a['bytes']/1024:.0f}K" if a['bytes'] else '—'
    t0s = iso(a['t0']).strftime('%m-%d %H:%M')
    tip = (f"{a['label']}\\n角色: {rn}\\n批次: {a['phase']}\\n会话: {a['id']}\\n"
           f"起始: {t0s}\\n耗时: {dur}\\n体积: {kb} / {a['lines']} 行\\n结果: {a['outcome']}")
    return (f'<div class="card" style="--c:{col}" data-role="{a["role"]}" data-phase="{html.escape(a["phase"])}" '
            f'title="{html.escape(tip)}">'
            f'<div class="ava">{glyph}</div>'
            f'<div class="lb">{html.escape(str(a["label"]))}</div>'
            f'<div class="mt">{dur} · {kb}</div></div>')


# ---- 谱系树 SVG ----
def tree_svg():
    W, pad = 1500, 40
    y0, dy_branch, dy_agent = 30, 34, 15
    rows = []
    y = 120
    for ph in phases:
        n = len(ph['agents'])
        per = 40
        rowsn = (n + per - 1) // per
        ph['_y'] = y
        ph['_h'] = max(dy_branch, rowsn * dy_agent + 14)
        y += ph['_h'] + 16
    H = y + 20
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" style="max-height:520px">']
    cx = W // 2
    out.append(f'<rect x="{cx-120}" y="6" width="240" height="34" rx="10" fill="#1f6feb"/>'
               f'<text x="{cx}" y="28" text-anchor="middle" fill="#fff" font-size="15" font-weight="700">'
               f'🏠 主控 Agent（Lead）</text>')
    bx = [120 + i * ((W - 240) / max(len(phases) - 1, 1)) for i in range(len(phases))]
    for i, ph in enumerate(phases):
        x = bx[i]
        py0 = ph['_y']
        pname = html.escape(ph['name'])
        out.append(f'<path d="M{cx} 40 C{cx} 70 {x} 70 {x} 92" fill="none" stroke="#4b5563" stroke-width="1.4"/>')
        _rk, col, _g = ROLE[max(ph['roles'], key=ph['roles'].get)]
        out.append(f'<rect x="{x-92}" y="{py0-24}" width="184" height="24" rx="7" fill="{col}" opacity="0.18" '
                   f'stroke="{col}" stroke-width="1"/>')
        out.append(f'<text x="{x}" y="{py0-7}" text-anchor="middle" fill="{col}" font-size="12.5" font-weight="700">'
                   f'{pname} · {len(ph["agents"])} agents</text>')
        gx, gy, per = x - 88, py0 + 4, 8
        for j, a in enumerate(ph['agents']):
            c2 = ROLE[a['role']][1]
            px = gx + (j % per) * 22
            py = gy + (j // per) * dy_agent
            lab = html.escape(str(a['label']))
            out.append(f'<circle cx="{px}" cy="{py}" r="7" fill="{c2}" fill-opacity="0.85" stroke="#0b0f14" stroke-width="0.6">'
                       f'<title>{lab} · {pname} · {a["durSec"] or "?"}s</title></circle>')
    out.append('</svg>')
    return '\n'.join(out)


legend = ''.join(f'<span class="lg"><i style="background:{c}"></i>{n}</span>' for k, (n, c, g) in ROLE.items())
phase_bar = ''.join(
    f'<div class="pb"><span class="pn">{html.escape(p["name"])}</span>'
    f'<span class="pv">{len(p["agents"])} agents · {(p["t1"]-p["t0"])/60000:.1f} min · '
    f'{iso(p["t0"]).strftime("%m-%d %H:%M")}→{iso(p["t1"]).strftime("%H:%M")}</span>'
    f'<span class="pb2" style="width:{(p["t1"]-p["t0"])/60000/60*100:.0f}%"></span></div>' for p in phases)

portraits = '\n'.join(
    f'<section class="grp" data-phase="{html.escape(p["name"])}">'
    f'<h3>{html.escape(p["name"])} <em>{len(p["agents"])}</em></h3>'
    f'<div class="wall">' + ''.join(card(a, i) for i, a in enumerate(p['agents'])) + '</div></section>'
    for p in phases)

tools = raw.get('tools') or {}
tool_rows = ''.join(
    f'<tr><td>{html.escape(k)}</td><td class="n">{v}</td>'
    f'<td><span class="tb" style="width:{v/max(tools.values())*100:.0f}%"></span></td></tr>'
    for k, v in sorted(tools.items(), key=lambda x: -x[1]))

HTML = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent 全家福 · 谱系图 — fallout_shelter_hanhua</title>
<style>
:root{{--bg:#0b0f14;--fg:#e6edf3;--dim:#8b949e;--line:#21262d;--card:#131a22}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.6 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}}
.wrap{{max-width:1560px;margin:0 auto;padding:28px 22px 60px}}
h1{{font-size:26px;margin:0 0 6px;letter-spacing:.5px}}
h1 small{{font-size:13px;color:var(--dim);font-weight:400;letter-spacing:0}}
.sub{{color:var(--dim);margin-bottom:22px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0 26px}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.kpi b{{display:block;font-size:24px;line-height:1.2}}
.kpi span{{color:var(--dim);font-size:12px}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;margin:0 0 26px}}
.panel h2{{font-size:16px;margin:0 0 14px;color:#c9d1d9}}
.legend{{margin:10px 0 0}}
.lg{{display:inline-flex;align-items:center;gap:6px;margin-right:16px;color:var(--dim);font-size:12.5px}}
.lg i{{width:11px;height:11px;border-radius:50%;display:inline-block}}
.pb{{position:relative;margin:8px 0;padding:7px 12px;background:#0f151d;border-radius:8px;overflow:hidden;display:flex;gap:14px;font-size:12.5px}}
.pb2{{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(90deg,#1f6feb33,#1f6feb11);z-index:0}}
.pn{{position:relative;z-index:1;min-width:96px;font-weight:600}}
.pv{{position:relative;z-index:1;color:var(--dim)}}
.grp{{margin-bottom:24px}}
.grp h3{{font-size:14.5px;margin:0 0 10px;color:#c9d1d9}}
.grp h3 em{{font-style:normal;color:var(--dim);font-weight:400}}
.wall{{display:grid;grid-template-columns:repeat(auto-fill,minmax(94px,1fr));gap:8px}}
.card{{background:#0f151d;border:1px solid var(--line);border-left:3px solid var(--c);border-radius:9px;padding:8px 6px;text-align:center;cursor:default;transition:.15s}}
.card:hover{{background:#17202b;transform:translateY(-2px)}}
.ava{{font-size:17px;line-height:1.1}}
.lb{{font-size:10.5px;color:#c9d1d9;word-break:break-all;margin-top:3px}}
.mt{{font-size:9.5px;color:var(--dim);margin-top:2px}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}}
td{{padding:4px 8px;border-bottom:1px solid var(--line)}}
td.n{{text-align:right;color:var(--dim);width:64px}}
.tb{{display:block;height:8px;background:linear-gradient(90deg,#1f6feb,#58a6ff);border-radius:4px}}
footer{{color:var(--dim);font-size:12px;border-top:1px solid var(--line);padding-top:14px}}
code{{background:#161b22;padding:1px 5px;border-radius:4px;font-size:12px}}
</style></head><body><div class="wrap">
<h1>🏠 Agent 全家福 · 谱系图 <small>fallout_shelter_hanhua 汉化项目</small></h1>
<div class="sub">根会话 <code>{hdr['id']}</code> · {iso(T0).strftime('%Y-%m-%d %H:%M')} 起 · 至 {iso(T1).strftime('%m-%d %H:%M')} ·
delegationDepth 0 → 1 · 全部由主控 Agent 直接派生（无一二级嵌套）</div>

<div class="kpis">
<div class="kpi"><b>{len(agents)}</b><span>子 Agent 总数</span></div>
<div class="kpi"><b>{len(phases)}</b><span>工作流批次 / 阶段</span></div>
<div class="kpi"><b>{sum(a['outcome']=='completed' for a in agents)}/{len(agents)}</b><span>正常完成</span></div>
<div class="kpi"><b>{tot_dur/3600:.1f}h</b><span>子 Agent 累计工时</span></div>
<div class="kpi"><b>{(T1-T0)/3600000:.1f}h</b><span>整体墙钟跨度</span></div>
<div class="kpi"><b>{tot_bytes/1024/1024:.0f} MB</b><span>子会话上下文总量</span></div>
<div class="kpi"><b>{len(raw['turns'])}</b><span>用户回合</span></div>
<div class="kpi"><b>{sum(tools.values())}</b><span>主控工具调用</span></div>
</div>

<div class="panel"><h2>① 谱系树（主控 → 批次 → 每个 Agent）</h2>
{tree_svg()}
<div class="legend">{legend}</div></div>

<div class="panel"><h2>② 批次时间线</h2>{phase_bar}</div>

<div class="panel"><h2>③ 全家福 · 集体照（{len(agents)} 位）</h2>
{portraits}</div>

<div class="panel"><h2>④ 主控 Agent 的工具调用</h2>
<table>{tool_rows}</table></div>

<footer>由 DSH 会话留档（<code>~/.dsh/sessions/--home-wangqiang-fallout_shelter_hanhua--</code>）自动生成 ·
生成器 <code>全家福/build_poster.py</code> · 数据 <code>全家福/_genealogy_raw.json</code></footer>
</div></body></html>'''

out = f'{HERE}/agent全家福_谱系图.html'
open(out, 'w', encoding='utf-8').write(HTML)
print(f'已生成 {out}  ({os.path.getsize(out)/1024:.0f} KB)')
print(f'  {len(agents)} 个子 agent / {len(phases)} 个阶段 / 累计工时 {tot_dur/3600:.1f}h')
