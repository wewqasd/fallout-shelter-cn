#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_network_html.py — 交互版 Agent Network（SVG，风格对齐 dsh-context）。

输入: _genealogy_raw.json + _agent_context.json + _layout.json（由 build_network.py 产出）
输出: agent网络_谱系图.html —— 悬停看详情、点击锁定并高亮该 agent 的谱系边。
"""
import json, os, math, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(f'{HERE}/_genealogy_raw.json', encoding='utf-8'))
ctx = json.load(open(f'{HERE}/_agent_context.json', encoding='utf-8'))
lay = json.load(open(f'{HERE}/_layout.json', encoding='utf-8'))['agents']
hdr = raw['hdr']

CATS = [('system', 'System Prompt', '系统提示', '#6366f1'),
        ('toolSchema', 'Tool Schemas', '工具结构', '#f59e0b'),
        ('user', 'User Messages', '用户消息', '#22c55e'),
        ('injected', 'Injected Context', '注入上下文', '#a855f7'),
        ('assistant', 'Assistant Messages', '助手消息', '#3b82f6'),
        ('toolResult', 'Tool Results', '工具结果', '#14b8a6')]
BRANCH = {'试点审校': '#4a9eff', '审校A段': '#2ecc9b', '审校B段': '#f0a437',
          '长文本专审': '#e5556b', '对抗复核': '#a855f7', '专项审校': '#14b8a6'}

for a in lay:
    c = ctx.get(a['id'], {})
    a['kb'] = round(c.get('bytes', 0) / 1024)
    a['requests'] = c.get('requests', 0)
    a['compN'] = c.get('compN', {})
    a['durS'] = round(a['dur'])
    a['t0s'] = datetime.datetime.fromtimestamp(a['t0'] / 1000).strftime('%m-%d %H:%M:%S')
    a['t1s'] = datetime.datetime.fromtimestamp((a['t1'] or a['t0']) / 1000).strftime('%H:%M:%S')

T0, T1 = hdr['createdAt'], max(a['t1'] or a['t0'] for a in lay)
tot_b = sum(a['kb'] for a in lay)
n_fail = sum(1 for a in lay if a['outcome'] != 'completed')
groups = {}
for a in lay: groups.setdefault(a['phase'], []).append(a)

# ---- SVG ----
RO = 23; RI = 14; SW = 9          # 外径 / 内孔 / 环宽
parts = []
parts.append('<g id="edges">')
for i, a in enumerate(lay):
    col = BRANCH[a['phase']]
    parts.append(f'<path class="edge e{i}" d="M1300,1300 L{a["x"]:.1f},{a["y"]:.1f}" stroke="{col}" '
                 f'stroke-width="1.6" stroke-opacity=".18" fill="none"/>')
parts.append('</g><g id="nodes">')
for i, a in enumerate(lay):
    comp = a['compN']; tot = sum(comp.values()) or 1
    segs = []
    off = 0.0
    C = 2 * math.pi * ((RO + RI) / 2)
    for key, en, zh, col in CATS:
        v = comp.get(key, 0)
        if v <= 0: continue
        frac = v / tot
        segs.append(f'<circle class="seg" r="{(RO + RI) / 2}" fill="none" stroke="{col}" stroke-width="{SW}" '
                    f'stroke-dasharray="{C*frac:.2f} {C*(1-frac):.2f}" stroke-dashoffset="{-off:.2f}"/>')
        off += C * frac
    ring = (f'<g transform="rotate(-90)" style="transform-origin:0 0">' + ''.join(segs) + '</g>')
    fail = ' fail' if a['outcome'] != 'completed' else ''
    tip = (f"{a['label']}｜{a['phase']}｜{a['kb']} KB｜{a['tools']} 次工具｜{a['steps']} 步｜"
           f"{a['durS']}s｜{a['outcome']}")
    parts.append(
        f'<g class="node{fail}" data-i="{i}" transform="translate({a["x"]:.1f},{a["y"]:.1f})">'
        f'<title>{tip}</title>'
        f'<circle class="halo" r="{RO+7}" fill="none" stroke="{BRANCH[a["phase"]]}" stroke-opacity="0"/>'
        f'<circle class="bg" r="{RO}" fill="#0f141b"/>' + ring +
        f'<circle r="{RI}" fill="#0b0f14"/>'
        f'<text class="pct" y="4" text-anchor="middle">{a["rel"]*100:.0f}%</text>'
        f'</g>')
parts.append('</g>')

# 分支标签
labels = []
for pname, mem in groups.items():
    xs = [a['x'] for a in mem]; ys = [a['y'] for a in mem]
    # 取离中心最远的点，沿同方向再外推
    far = max(mem, key=lambda a: (a['x'] - 1300) ** 2 + (a['y'] - 1300) ** 2)
    th = math.atan2(far['y'] - 1300, far['x'] - 1300)
    rr = math.hypot(far['x'] - 1300, far['y'] - 1300) + 80
    lx, ly = 1300 + rr * math.cos(th), 1300 + rr * math.sin(th)
    labels.append(f'<g class="blabel"><rect x="{lx-86:.0f}" y="{ly-30:.0f}" width="172" height="58" rx="14" '
                  f'fill="#0e1319" stroke="{BRANCH[pname]}" stroke-opacity=".55"/>'
                  f'<text x="{lx:.0f}" y="{ly-8:.0f}" text-anchor="middle" fill="{BRANCH[pname]}" '
                  f'font-size="22" font-weight="700">{pname}</text>'
                  f'<text x="{lx:.0f}" y="{ly+16:.0f}" text-anchor="middle" fill="#8b949e" font-size="16">'
                  f'{len(mem)} agents</text></g>')

JS = '''
const NODES = document.querySelectorAll('.node');
let lock = null;
function detail(i){
  const bar = document.getElementById('bar');
  if(i<0){ bar.innerHTML='<b>未选中</b><em>把鼠标移到任意节点上查看该 Agent 的上下文构成；点击可锁定并高亮它的谱系边</em>'; return; }
  const a = DATA[i];
  const seg = a.compN, tot = Object.values(seg).reduce((x,y)=>x+y,0)||1;
  const chips = CATS.filter(c=>seg[c[0]]>0).map(c=>
    `<span class="cc"><i style="background:${c[3]}"></i>${c[2]} ${(seg[c[0]]/tot*100).toFixed(0)}%</span>`).join('');
  bar.innerHTML = `<b>${a.label}</b><em>${a.phase}</em>`+
    `<span class="kv">${a.kb} KB · ${a.rel*100|0}% 批次占比 · ${a.requests} requests · ${a.tools} 工具 · ${a.steps} 步 · ${a.durS}s</span>`+
    `<div class="cs">${chips}</div>`+
    `<code>${a.id}</code> <span class="tm">${a.t0s} → ${a.t1s}</span>`+
    (a.outcome!=='completed'?`<span class="bad">首轮 ${a.outcome}</span>`:'');
}
NODES.forEach(n=>{
  n.addEventListener('mouseenter',()=>{ if(lock===null){ hi(+n.dataset.i,false); detail(+n.dataset.i);} });
  n.addEventListener('click',e=>{
    e.stopPropagation();
    if(lock===+n.dataset.i){ lock=null; hi(-1,true); }
    else { lock=+n.dataset.i; hi(lock,true); detail(lock); }
  });
});
document.addEventListener('click',()=>{ lock=null; hi(-1,true); });
function hi(i,strong){
  NODES.forEach(n=>{
    const on = (+n.dataset.i===i);
    n.classList.toggle('on', on);
    n.querySelector('.halo').setAttribute('stroke-opacity', on? (strong?'.95':'.5') : '0');
  });
  document.querySelectorAll('.edge').forEach(e=>e.classList.remove('lit'));
  if(i>=0){
    document.querySelectorAll('.e'+i).forEach(e=>e.classList.add('lit'));
  }
}
detail(-1);
'''
HTML = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Network · 本对话的 Agent 谱系网络</title>
<style>
:root{{--bg:#0b0f14;--fg:#e6edf3;--dim:#8b949e;--line:#21262d;--card:#0f141b}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.6 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}}
.wrap{{max-width:1500px;margin:0 auto;padding:22px}}
h1{{font-size:22px;margin:0 0 4px}} h1 small{{color:var(--dim);font-weight:400;font-size:13px}}
.sub{{color:var(--dim);font-size:13px;margin-bottom:12px}}
.chips{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}}
.chip{{background:#161d26;border:1px solid var(--line);border-radius:20px;padding:5px 14px;font-size:12.5px;color:#c9d1d9}}
svg{{width:100%;height:auto;display:block;background:radial-gradient(circle at 50% 50%,#0e141c,#0b0f14 70%);border-radius:16px;border:1px solid var(--line)}}
.node{{cursor:pointer}}
.node .bg{{transition:.15s}} .node:hover .bg{{fill:#1b2431}}
.node.on .bg{{fill:#20303f}}
.pct{{font-size:11px;fill:#dbe3ea;font-weight:700;pointer-events:none}}
.edge{{transition:stroke-opacity .15s,stroke-width .15s}}
.edge.lit{{stroke-opacity:.95;stroke-width:2.6}}
.blabel{{pointer-events:none}}
#bar{{position:sticky;bottom:0;margin-top:14px;background:#101720;border:1px solid var(--line);border-radius:14px;padding:12px 16px;font-size:13px;min-height:64px}}
#bar b{{font-size:15px}} #bar em{{font-style:normal;color:var(--dim);margin-left:10px}}
#bar .kv{{color:var(--dim);margin-left:12px}}
#bar .cs{{margin-top:6px;display:flex;gap:14px;flex-wrap:wrap}}
#bar .cc{{color:var(--dim);font-size:12px}} #bar .cc i{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}}
#bar code{{color:#58a6ff;font-size:11.5px}} #bar .tm{{color:var(--dim);font-size:11.5px;margin-left:8px}}
#bar .bad{{color:#ff6b6b;margin-left:10px}}
.leg{{display:flex;gap:18px;flex-wrap:wrap;margin-top:12px;color:var(--dim);font-size:12.5px}}
.leg i{{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px}}
.leg .ring{{border:3px solid #ff5a5a;border-radius:50%;width:13px;height:13px;background:none}}
</style></head><body><div class="wrap">
<h1>Agent Network <small>本对话的 Agent 谱系网络</small></h1>
<div class="sub">根会话 <code>{hdr['id']}</code> · {datetime.datetime.fromtimestamp(T0/1000):%Y-%m-%d %H:%M} → {datetime.datetime.fromtimestamp(T1/1000):%m-%d %H:%M} ·
风格参考 <a href="https://github.com/bowenliang123/dsh-context" style="color:#58a6ff">bowenliang123/dsh-context</a> 的 Agent Network · 点击节点锁定</div>
<div class="chips"><span class="chip">{len(lay)} agents</span><span class="chip">{n_fail} failed（已补跑）</span>
<span class="chip">{tot_b/1024:.0f} MB 上下文</span><span class="chip">{sum(a['tools'] for a in lay)} 工具调用</span>
<span class="chip">{sum(a['dur'] for a in lay)/3600:.1f} h 累计工时</span></div>
<svg viewBox="0 0 2600 2600" xmlns="http://www.w3.org/2000/svg">
<defs><radialGradient id="glow"><stop offset="0%" stop-color="#1f6feb" stop-opacity=".55"/><stop offset="100%" stop-color="#1f6feb" stop-opacity="0"/></radialGradient></defs>
<circle cx="1300" cy="1300" r="150" fill="url(#glow)"/>
{''.join(parts)}
{''.join(labels)}
<g><circle cx="1300" cy="1300" r="54" fill="#1f6feb"/><circle cx="1300" cy="1300" r="34" fill="#0b0f14"/>
<text x="1300" y="1306" text-anchor="middle" fill="#fff" font-size="20" font-weight="700">Lead</text></g>
</svg>
<div id="bar"></div>
<div class="leg">{''.join(f'<span><i style="background:{c[3]}"></i>{c[2]}</span>' for c in CATS)}
<span><i class="ring"></i>首轮 failed</span>
<span>节点中心 % = 相对本批次上下文体积</span></div>
<script>const DATA={json.dumps([{k:a[k] for k in ('id','label','phase','kb','rel','requests','tools','steps','durS','outcome','t0s','t1s')} | {'compN':a['compN']} for a in lay],ensure_ascii=False)};
const CATS={json.dumps([[c[0],c[1],c[2],c[3]] for c in CATS],ensure_ascii=False)};{JS}</script>
</div></body></html>'''
out = f'{HERE}/agent网络_谱系图.html'
open(out, 'w', encoding='utf-8').write(HTML)
print(f'已生成 {out} ({os.path.getsize(out)/1024:.0f} KB)  节点 {len(lay)}')
