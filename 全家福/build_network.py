#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_network.py — 按 dsh-context「Agent Network」风格渲染本会话的 Agent 谱系网络。

参考: https://github.com/bowenliang123/dsh-context （docs/agent-network.png）
  一个节点 = 一个 agent；圆环 = 该 agent 的上下文组成；中心 = 相对规模；彩线 = 谱系边。

输入: _genealogy_raw.json + _agent_context.json
输出: agent网络_谱系图.png / agent网络_谱系图.html
"""
import json, os, math, datetime, collections
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(f'{HERE}/_genealogy_raw.json', encoding='utf-8'))
ctx = json.load(open(f'{HERE}/_agent_context.json', encoding='utf-8'))
hdr, cat, starts, ends, subs = raw['hdr'], raw['catalog'], raw['starts'], raw['ends'], raw['subs']

FB = '/home/wangqiang/.local/share/fonts/windows/msyhbd.ttc'
FR = '/home/wangqiang/.local/share/fonts/windows/msyh.ttc'
F = lambda sz, b=False: ImageFont.truetype(FB if b else FR, sz)

# dsh-context 六色 + 分类
CATS = [('system', 'System Prompt', '系统提示', (99, 102, 241)),
        ('toolSchema', 'Tool Schemas', '工具结构', (245, 158, 11)),
        ('user', 'User Messages', '用户消息', (34, 197, 94)),
        ('injected', 'Injected Context', '注入上下文', (168, 85, 247)),
        ('assistant', 'Assistant Messages', '助手消息', (59, 130, 246)),
        ('toolResult', 'Tool Results', '工具结果', (20, 184, 166))]
CATC = {k: c for k, _, _, c in CATS}

BRANCH = {
    '试点审校': (74, 158, 255), '审校A段': (46, 204, 155), '审校B段': (240, 164, 55),
    '长文本专审': (229, 85, 107), '对抗复核': (168, 85, 247), '专项审校': (20, 184, 166),
}
ROLE = {'accuracy': ('初审·准确性', (74, 158, 255), '准'), 'fluency': ('初审·流畅度', (46, 204, 155), '畅'),
        'long': ('长文本专审', (240, 164, 55), '长'), 'verify': ('对抗复核', (229, 85, 107), '核'),
        'named': ('专名分类审校', (168, 85, 247), '名')}


def role_of(l):
    l = str(l or '')
    if l.endswith('-accuracy'): return 'accuracy'
    if l.endswith('-fluency'): return 'fluency'
    if l.startswith('long-'): return 'long'
    if l.startswith('verify-'): return 'verify'
    return 'named'


# ---- 组装 agents ----
byrun = collections.defaultdict(lambda: {'s': [], 'e': []})
for s in starts: byrun[s['runId']]['s'].append(s)
for e in ends: byrun[e['runId']]['e'].append(e)
agents = []
for rid, v in byrun.items():
    ss = sorted(v['s'], key=lambda x: x['time']); ee = sorted(v['e'], key=lambda x: x['time'])
    for i, s in enumerate(ss):
        e = ee[i] if i < len(ee) else {}
        agents.append({'id': s.get('childId'), 'label': s.get('label'), 'phase': s.get('phase'),
                       'role': role_of(s.get('label')), 't0': s.get('time'), 't1': e.get('time'),
                       'outcome': e.get('outcome', '?')})
wf_ids = {s.get('childId') for s in starts}
for cid, c in cat.items():
    if cid in wf_ids: continue
    agents.append({'id': cid, 'label': c.get('label'), 'phase': '专项审校', 'role': 'named',
                   't0': c.get('childCreatedAt'), 't1': subs.get(cid, {}).get('mtime'), 'outcome': 'completed'})
for a in agents:
    c = ctx.get(a['id'], {})
    a['bytes'] = c.get('bytes', 0); a['tools'] = c.get('tools', 0); a['steps'] = c.get('steps', 0)
    a['requests'] = c.get('requests', 0)
    a['comp'] = c.get('compN', {})          # 按条目数的六类构成
    a['dur'] = ((a['t1'] or a['t0']) - a['t0']) / 1000
root_ctx = ctx.get(hdr['id'], {})
T0, T1 = hdr['createdAt'], max(a['t1'] or a['t0'] for a in agents)
tot_b = sum(a['bytes'] for a in agents)

PH = ['试点审校', '审校A段', '审校B段', '长文本专审', '对抗复核', '专项审校']
groups = []
for p in PH:
    mem = sorted([a for a in agents if a['phase'] == p], key=lambda a: str(a['label']))
    if not mem: continue
    mx = max(a['bytes'] for a in mem)
    for a in mem: a['rel'] = a['bytes'] / mx                # 相对本批次规模（节点中心%）
    groups.append((p, mem))

# ---------------- 布局：放射星型 ----------------
W = H = 2600
CXX = CYY = W / 2
img = Image.new('RGB', (W, H), (10, 13, 18))
d = ImageDraw.Draw(img)
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))       # 用于发光/连线
dl = ImageDraw.Draw(layer)

n_b = len(groups)
R0, DR = 300, 112          # 起始半径 / 每层半径增量
ARC_MAX = math.radians(56)  # 每个扇区可用角宽

root_r = 54
pos = {}
for bi, (pname, mem) in enumerate(groups):
    theta = -math.pi / 2 + bi * (2 * math.pi / n_b)
    col = BRANCH[pname]
    placed, k = [], 0
    while len(placed) < len(mem):
        r = R0 + k * DR
        cap = max(1, int(ARC_MAX * r / 52))
        base = len(placed)
        take = min(cap, len(mem) - base)
        span = ARC_MAX * min(1, take / cap)
        for j in range(take):
            t = theta - span / 2 + (span * (j + 0.5) / take if take > 1 else 0)
            a = mem[base + j]
            a['x'] = CXX + r * math.cos(t); a['y'] = CYY + r * math.sin(t); a['r'] = 19
            a['br'] = col; a['theta'] = t; a['arc_k'] = k
            placed.append(a); pos[a['id']] = a
        k += 1
    # 扇区标题（放在最外层弧之外，加暗色底衬避免压住节点）
    tmid = theta
    rr = R0 + (k - 1) * DR + 74
    lx_, ly_ = CXX + rr * math.cos(tmid), CYY + rr * math.sin(tmid)
    t1, t2 = f'{pname}', f'{len(mem)} agents'
    w1 = d.textlength(t1, font=F(29, True)); w2 = d.textlength(t2, font=F(20))
    pw = max(w1, w2) + 34
    d.rounded_rectangle([lx_ - pw / 2, ly_ - 30, lx_ + pw / 2, ly_ + 28], radius=14,
                        fill=(14, 19, 25), outline=col + (110,))
    d.text((lx_, ly_ - 12), t1, font=F(29, True), fill=col, anchor='mm')
    d.text((lx_, ly_ + 14), t2, font=F(20), fill=(140, 148, 158), anchor='mm')

# 连线：root → 每个 agent
for a in agents:
    col = a['br']
    dl.line([CXX, CYY, a['x'], a['y']], fill=col + (52,), width=2)
# root 光环
for rad, al in ((root_r + 26, 40), (root_r + 16, 70)):
    dl.ellipse([CXX - rad, CYY - rad, CXX + rad, CYY + rad], outline=(31, 111, 235, al), width=3)
img = Image.alpha_composite(img.convert('RGBA'), layer.filter(ImageFilter.GaussianBlur(0.6)))
d = ImageDraw.Draw(img)


# 甜甜圈
def donut(cx, cy, ro, comp, rel, outcome, br):
    total = sum(comp.values()) or 1
    start = -90
    for k, (key, _, _, col) in enumerate(CATS):
        v = comp.get(key, 0)
        if v <= 0: continue
        ext = 360 * v / total
        d.pieslice([cx - ro, cy - ro, cx + ro, cy + ro], start, start + ext, fill=col)
        start += ext
    d.ellipse([cx - ro * .62, cy - ro * .62, cx + ro * .62, cy + ro * .62], fill=(15, 20, 27))
    if outcome != 'completed':
        d.ellipse([cx - ro - 4, cy - ro - 4, cx + ro + 4, cy + ro + 4], outline=(255, 90, 90), width=3)
    txt = f'{rel*100:.0f}%'
    f = F(15, True)
    d.text((cx, cy + 1), txt, font=f, fill=(226, 233, 240), anchor='mm')


for a in agents:
    donut(a['x'], a['y'], 21, a['comp'], a['rel'], a['outcome'], a['br'])
# root 节点
donut(CXX, CYY, root_r, {}, 1.0, 'completed', (31, 111, 235))
d.text((CXX, CYY + 1), 'Lead', font=F(22, True), fill=(255, 255, 255), anchor='mm')

# 标题
d.text((70, 54), 'Agent Network · 本对话的 Agent 谱系网络', font=F(52, True), fill=(235, 241, 247))
d.text((70, 122), f'根会话 {hdr["id"]}　·　{datetime.datetime.fromtimestamp(T0/1000):%Y-%m-%d %H:%M} → '
                  f'{datetime.datetime.fromtimestamp(T1/1000):%m-%d %H:%M}　·　'
                  f'风格参考 dsh-context 的 Agent Network', font=F(23), fill=(140, 148, 158))
# 顶部 chips
chips = [f'{len(agents)} agents', f'{sum(1 for a in agents if a["outcome"]!="completed")} failed（已补跑）',
         f'{tot_b/1024/1024:.0f} MB 上下文', f'{sum(a["tools"] for a in agents)} 子 agent 工具调用',
         f'{sum(a["dur"] for a in agents)/3600:.1f} h 累计工时']
x = 70
for c in chips:
    w = d.textlength(c, font=F(22)) + 40
    d.rounded_rectangle([x, 168, x + w, 212], radius=22, fill=(24, 32, 41), outline=(40, 48, 58))
    d.text((x + 20, 190), c, font=F(22), fill=(190, 198, 208), anchor='lm')
    x += w + 14

# 图例
ly = H - 74
lx = 70
for key, en, zh, col in CATS:
    d.ellipse([lx, ly - 10, lx + 20, ly + 10], fill=col)
    d.text((lx + 28, ly - 11), zh, font=F(21), fill=(190, 198, 208))
    lx += 30 + d.textlength(zh, font=F(21)) + 34
d.ellipse([lx, ly - 10, lx + 20, ly + 10], fill=(40, 46, 56))
d.text((lx + 28, ly - 11), '空闲（环未填满）', font=F(21), fill=(190, 198, 208))
lx += 30 + d.textlength('空闲（环未填满）', font=F(21)) + 34
d.ellipse([lx, ly - 12, lx + 22, ly + 12], outline=(255, 90, 90), width=3)
d.text((lx + 30, ly - 11), '红圈 = 首轮 failed', font=F(21), fill=(200, 120, 120))

d.text((70, H - 34), '节点：圆环 = 该 Agent 会话的条目构成（六色，按条目数占比）；中心 % = 相对本批次上下文体积；'
                     '连线 = 主控派生的谱系边（按批次着色）；红圈 = 首轮 failed', font=F(20), fill=(110, 118, 129))
d = ImageDraw.Draw(img)
out_png = f'{HERE}/agent网络_谱系图.png'
img.convert('RGB').save(out_png, optimize=True)
print(f'已生成 {out_png} ({os.path.getsize(out_png)/1024:.0f} KB) 画布 {W}×{H}  节点 {len(agents)}')
json.dump({'agents': [{k: v for k, v in a.items() if k not in ('comp',)} for a in agents]},
          open(f'{HERE}/_layout.json', 'w', encoding='utf-8'), ensure_ascii=False)
