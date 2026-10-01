#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_poster_png.py — 用 PIL 把同一份谱系数据画成 PNG 全家福海报。"""
import json, os, math, datetime, collections
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(f'{HERE}/_genealogy_raw.json', encoding='utf-8'))
hdr, cat, starts, ends, subs = raw['hdr'], raw['catalog'], raw['starts'], raw['ends'], raw['subs']

FB = '/home/wangqiang/.local/share/fonts/windows/msyhbd.ttc'
FR = '/home/wangqiang/.local/share/fonts/windows/msyh.ttc'
def F(sz, bold=False):
    return ImageFont.truetype(FB if bold else FR, sz)

ROLE = {
    'accuracy': ('初审·准确性', (74, 158, 255), '准'),
    'fluency':  ('初审·流畅度', (46, 204, 155), '畅'),
    'long':     ('长文本专审', (240, 164, 55), '长'),
    'verify':   ('对抗复核',   (229, 85, 107), '核'),
    'named':    ('专名分类审校', (155, 108, 224), '名'),
}
def role_of(l):
    l = str(l or '')
    if l.endswith('-accuracy'): return 'accuracy'
    if l.endswith('-fluency'): return 'fluency'
    if l.startswith('long-'): return 'long'
    if l.startswith('verify-'): return 'verify'
    return 'named'

byrun = collections.defaultdict(lambda: {'s': [], 'e': []})
for s in starts: byrun[s['runId']]['s'].append(s)
for e in ends: byrun[e['runId']]['e'].append(e)
agents = []
for rid, v in byrun.items():
    ss = sorted(v['s'], key=lambda x: x['time']); ee = sorted(v['e'], key=lambda x: x['time'])
    for i, s in enumerate(ss):
        e = ee[i] if i < len(ee) else {}
        sub = subs.get(s.get('childId'), {})
        agents.append({'label': s.get('label'), 'phase': s.get('phase'), 'role': role_of(s.get('label')),
                       't0': s.get('time'), 't1': e.get('time'), 'bytes': sub.get('bytes', 0),
                       'outcome': e.get('outcome', '?')})
wf = {s.get('childId') for s in starts}
for cid, c in cat.items():
    if cid in wf: continue
    sub = subs.get(cid, {})
    agents.append({'label': c.get('label'), 'phase': '专项审校', 'role': 'named',
                   't0': c.get('childCreatedAt'), 't1': sub.get('mtime'), 'bytes': sub.get('bytes', 0),
                   'outcome': 'completed'})

PH = ['试点审校', '审校A段', '审校B段', '长文本专审', '对抗复核', '专项审校']
groups = []
for p in PH:
    mem = sorted([a for a in agents if a['phase'] == p], key=lambda a: str(a['label']))
    if mem: groups.append((p, mem))

def iso(ms): return datetime.datetime.fromtimestamp(ms / 1000)

T0 = hdr['createdAt']; T1 = max(a['t1'] or a['t0'] for a in agents)
tot_dur = sum(((a['t1'] or a['t0']) - a['t0']) / 1000 for a in agents)
tot_mb = sum(a['bytes'] for a in agents) / 1024 / 1024

# ---------------- 画布 ----------------
W = 2000
M = 60
wall_per = 40
wall_rows = sum(math.ceil(len(m) / wall_per) for _, m in groups)
H = 300 + 500 + 120 + wall_rows * 56 + len(groups) * 46 + 230
img = Image.new('RGB', (W, H), (11, 15, 20))
d = ImageDraw.Draw(img)

def rr(xy, r, fill=None, outline=None, w=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)

def ctext(x, y, s, f, fill):
    d.text((x, y), s, font=f, fill=fill, anchor='mm')

# ---- 顶部 ----
d.rectangle([0, 0, W, 8], fill=(31, 111, 235))
ctext(W // 2, 74, 'Agent 全家福 · 谱系图', F(56, True), (230, 237, 243))
ctext(W // 2, 128, 'fallout_shelter_hanhua · 《辐射避难所》汉化项目', F(26), (139, 148, 158))
ctext(W // 2, 166, f"根会话 {hdr['id']}　·　{iso(T0).strftime('%Y-%m-%d %H:%M')} → {iso(T1).strftime('%m-%d %H:%M')}　·　delegationDepth 0 → 1（全部由主控直接派生）", F(21), (110, 118, 129))

# KPI
kpis = [(f"{len(agents)}", '子 Agent 总数'), (f"{len(groups)}", '批次 / 阶段'),
        (f"{sum(a['outcome']=='completed' for a in agents)}/{len(agents)}", '正常完成'),
        (f"{tot_dur/3600:.1f}h", '子 Agent 累计工时'), (f"{(T1-T0)/3600000:.1f}h", '整体墙钟跨度'),
        (f"{tot_mb:.0f} MB", '子会话上下文'), (f"{len(raw['turns'])}", '用户回合'),
        (f"{sum((raw.get('tools') or {}).values())}", '主控工具调用')]
kw = (W - 2 * M - 7 * 14) / 8
for i, (v, k) in enumerate(kpis):
    x = M + i * (kw + 14)
    rr([x, 196, x + kw, 268], 12, fill=(19, 26, 34), outline=(33, 38, 45))
    ctext(x + kw / 2, 222, v, F(27, True), (230, 237, 243))
    ctext(x + kw / 2, 250, k, F(16), (139, 148, 158))

# ---- 谱系树 ----
TY = 300
d.text((M, TY + 4), '① 谱系树：主控 → 批次 → 每个 Agent', font=F(24, True), fill=(201, 209, 217))

cx = W // 2
rr([cx - 150, TY + 46, cx + 150, TY + 96], 12, fill=(31, 111, 235))
ctext(cx, TY + 71, '主控 Agent（Lead）', F(22, True), (255, 255, 255))

n = len(groups)
band_top = TY + 140
colw = (W - 2 * M) / n
for i, (pname, mem) in enumerate(groups):
    gx = M + colw * (i + 0.5)
    d.line([cx, TY + 96, cx, TY + 118], fill=(75, 85, 99), width=3)
    d.line([gx, TY + 118, gx, band_top - 26], fill=(75, 85, 99), width=3)
    d.line([min(cx, gx), TY + 118, max(cx, gx), TY + 118], fill=(75, 85, 99), width=3)
    main = collections.Counter(a['role'] for a in mem).most_common(1)[0][0]
    col = ROLE[main][1]
    rr([gx - 116, band_top - 26, gx + 116, band_top + 4], 8, fill=tuple(int(c * .18) for c in col), outline=col)
    ctext(gx, band_top - 11, f'{pname} · {len(mem)}', F(19, True), col)
    per = 8
    for j, a in enumerate(mem):
        px = gx - 100 + (j % per) * 28
        py = band_top + 30 + (j // per) * 26
        c = ROLE[a['role']][1]
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=c, outline=(11, 15, 20), width=2)
        ctext(px, py + 1, ROLE[a['role']][2], F(13), (255, 255, 255))

# 图例
ly = band_top + 30 + max(math.ceil(len(m) / 8) for _, m in groups) * 26 + 26
lx = M
for k, (nm, c, g) in ROLE.items():
    cnt = sum(1 for a in agents if a['role'] == k)
    d.ellipse([lx, ly - 9, lx + 18, ly + 9], fill=c)
    d.text((lx + 26, ly - 9), f'{nm} ×{cnt}', font=F(18), fill=(170, 178, 188))
    lx += 26 + d.textlength(f'{nm} ×{cnt}', font=F(18)) + 40
nfail = sum(1 for a in agents if a['outcome'] != 'completed')
if nfail:
    d.ellipse([lx + 6, ly - 9, lx + 24, ly + 9], outline=(255, 90, 90), width=3, fill=None)
    d.text((lx + 32, ly - 9), f'红圈 = 首轮 failed（{nfail} 个，后由主控补跑）', font=F(18), fill=(200, 120, 120))

# ---- 全家福墙 ----
WY = ly + 54
d.text((M, WY), f'② 全家福 · 集体照（{len(agents)} 位子 Agent，按批次就座）', font=F(24, True), fill=(201, 209, 217))
y = WY + 52
for pname, mem in groups:
    main = collections.Counter(a['role'] for a in mem).most_common(1)[0][0]
    col = ROLE[main][1]
    rr([M, y, W - M, y + 40], 9, fill=(19, 26, 34), outline=(33, 38, 45))
    d.rectangle([M, y, M + 5, y + 40], fill=col)
    d.text((M + 18, y + 10), pname, font=F(21, True), fill=col)
    roles = collections.Counter(a['role'] for a in mem)
    txt = '　'.join(f'{ROLE[k][0]} {v}' for k, v in roles.most_common())
    d.text((M + 18 + d.textlength(pname, font=F(21, True)) + 20, y + 13), txt, font=F(16), fill=(139, 148, 158))
    t0 = min(a['t0'] for a in mem); t1 = max(a['t1'] or a['t0'] for a in mem)
    d.text((W - M - 18 - d.textlength(f'{(t1-t0)/60000:.0f} min', font=F(18)), y + 12),
           f'{(t1-t0)/60000:.0f} min', font=F(18), fill=(139, 148, 158))
    rows = math.ceil(len(mem) / wall_per)
    for j, a in enumerate(mem):
        px = M + 26 + (j % wall_per) * ((W - 2 * M - 40) / wall_per)
        py = y + 66 + (j // wall_per) * 56
        c = ROLE[a['role']][1]
        d.ellipse([px - 17, py - 17, px + 17, py + 17], fill=tuple(int(v * .85) for v in c))
        if a['outcome'] != 'completed':
            d.ellipse([px - 17, py - 17, px + 17, py + 17], outline=(255, 90, 90), width=3)
        ctext(px, py + 1, ROLE[a['role']][2], F(20, True), (255, 255, 255))
        lbl = str(a['label']).replace('-accuracy', '·准').replace('-fluency', '·畅')
        ctext(px, py + 26, lbl, F(12), (150, 158, 168))
    y += 66 + rows * 56 + 14

# ---- 页脚 ----
y += 12
d.line([M, y, W - M, y], fill=(33, 38, 45), width=2)
d.text((M, y + 14), f"共 {len(agents)} 位子 Agent：初审·准确性 {sum(1 for a in agents if a['role']=='accuracy')}　"
                    f"初审·流畅度 {sum(1 for a in agents if a['role']=='fluency')}　"
                    f"长文本专审 {sum(1 for a in agents if a['role']=='long')}　"
                    f"对抗复核 {sum(1 for a in agents if a['role']=='verify')}　"
                    f"专名分类审校 {sum(1 for a in agents if a['role']=='named')}　·　全部 delegationDepth=1（无二级嵌套）",
       font=F(18), fill=(150, 158, 168))
d.text((M, y + 44), '数据来源：DSH 会话留档 ~/.dsh/sessions/--home-wangqiang-fallout_shelter_hanhua--'
                    '　·　生成器：全家福/build_poster_png.py（PIL）　·　配套交互版：agent全家福_谱系图.html',
       font=F(17), fill=(110, 118, 129))

out = f'{HERE}/agent全家福_谱系图.png'
img.crop((0, 0, W, y + 60)).save(out, optimize=True)
print(f'已生成 {out}  ({os.path.getsize(out)/1024:.0f} KB)  画布 {W}×{y+60}')
