#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机械扫描：用确定性规则找出「重大错误 / 不通顺」的高危候选，作为 LLM 审校的交叉校验。
只读 data/*，输出到 审校/语义审校_20260927/mech/。"""
import json, re, os, sys, collections, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, '审校', '语义审校_20260927', 'mech')
os.makedirs(OUT, exist_ok=True)

d = json.load(open(os.path.join(ROOT, 'data/translations.json'), encoding='utf-8'))
i2 = json.load(open(os.path.join(ROOT, 'data/i2_dump.json'), encoding='utf-8'))

CJK = r'\u4e00-\u9fff\u3400-\u4dbf'
items = sorted(d.items())
findings = collections.defaultdict(list)

def add(cat, key, detail):
    findings[cat].append((key, detail))

# ---------- 0. 空值 / 纯空白 ----------
for k, v in items:
    if not v.strip():
        add('00_空值', k, repr(v))

# ---------- 1. 数字不一致 ----------
def dig(s): return sorted(re.findall(r'\d+', s.replace(',', '')))
CN_DIGIT = re.compile(r'[零一二两三四五六七八九十百千万]')
for k, v in items:
    en = i2[k][0]
    if '{0}' in en or '{1}' in en:
        continue                      # 占位符数字由 validate 管
    de, dz = dig(en), dig(v)
    if not de:
        continue                      # EN 没有数字则不管
    if de == dz:
        continue
    if not dz and CN_DIGIT.search(v):
        continue                      # ZH 用中文数字表达，视为已译
    add('01_数字不一致', k, f'EN={de} ZH={dz} | EN:{en[:80]!r} ZH:{v[:80]!r}')

# ---------- 2. 残留英文 ----------
WHITELIST = set('''XP SPECIAL HP AP I II III IV V T-60 T-51 T-45 T-60f T-60d VATS NCR PC NPC ID
Pip-Boy MrHandy MisterHandy Reddit Steam Xbox PlayStation PS4 PS5 PC XboxOne Windows Mac iOS Android
LOL OK EULA DLC PvP PvE Cosplay RobCo Mr Handy VR QT UI DPS AOE FPS AI NPCs Vault Vault-Tec
Fallout Shelter Fallout'''.split())
def ascii_tokens(s):
    return [t for t in re.findall(r"[A-Za-z][A-Za-z'\.\-]*", s)]
LEFT = re.compile(r'[\u4e00-\u9fff]')
for k, v in items:
    toks = ascii_tokens(v)
    odd = [t for t in toks if t not in WHITELIST and len(t) > 1]
    if odd:
        add('02_残留英文', k, f'{odd[:6]} | {v[:90]!r}')

# ---------- 3. 繁体字 ----------
_pairs = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trad_pairs.txt'), encoding='utf-8').read().split()
TRAD = set()
for _pr in _pairs:
    if len(_pr) == 2 and _pr[0] != _pr[1]:
        TRAD.add(_pr[1])
for k, v in items:
    hit = [ch for ch in v if ch in TRAD]
    if hit:
        add('03_疑似繁体', k, f'{"".join(hit)} | {v[:80]!r}')

# ---------- 4. 中文里的半角标点 ----------
BADP = re.compile(rf'([{CJK}])\s*([,.;:!?])|([,.;:!?])\s*([{CJK}])')
for k, v in items:
    if re.search(rf'[A-Za-z0-9]\s*[,.;:!?]', v):
        continue                       # 英文/数字旁的半角属正常
    if BADP.search(v):
        add('04_半角标点', k, v[:90])

# ---------- 5. 句末标点不一致 ----------
END = {'.': '。', '!': '！', '?': '？', '…': '…'}
for k, v in items:
    en = i2[k][0].rstrip().rstrip('"”\'’')
    zh = v.rstrip()
    if not en or not zh:
        continue
    e_end = en[-1] if en else ''
    z_end = zh[-1] if zh else ''
    zh_ok = '。！？…'
    if e_end in END:
        if z_end not in zh_ok:
            add('05_句末标点', k, f'EN…{en[-24:]!r} vs ZH…{zh[-24:]!r}')
    elif e_end.isalnum() or e_end in ')]}>':
        if z_end in '。！？':
            add('05_句末标点', k, f'EN无句末标点但ZH有 | EN…{en[-24:]!r} vs ZH…{zh[-24:]!r}')

# ---------- 6. 长度比异常 ----------
for k, v in items:
    en = i2[k][0]
    if len(en) < 12:
        continue
    r = len(v) / max(len(en), 1)
    if r < 0.16:
        add('06_疑似漏译(过短)', k, f'ratio={r:.2f} | EN({len(en)}):{en[:90]!r} ZH({len(v)}):{v[:90]!r}')
    elif r > 0.90:
        add('06_疑似多译(过长)', k, f'ratio={r:.2f} | EN({len(en)}):{en[:90]!r} ZH({len(v)}):{v[:90]!r}')

# ---------- 7. 叠字/重复异常 ----------
DUP = re.compile(r'(的的|了了|是是|我我|你你|他他|她她|们们|在在|有有|和和|就就|都都|也也|不不|很很|会会|能能|要要|中中|个个个)')
for k, v in items:
    m = DUP.findall(v)
    if m:
        add('07_叠字', k, f'{m} | {v[:90]!r}')

# ---------- 8. 同 EN 不同 ZH（句子级一词多译） ----------
byen = collections.defaultdict(set)
for k, v in items:
    byen[i2[k][0]].add(v)
multi = {en: zs for en, zs in byen.items() if len(zs) > 1}
for k, v in items:
    if i2[k][0] in multi:
        add('08_同EN多译', k, f'EN:{i2[k][0][:70]!r} 候选ZH:{sorted(multi[i2[k][0]])[:4]}')

# ---------- 9. 引号风格 ----------
for k, v in items:
    styles = []
    if '「' in v or '」' in v: styles.append('「」')
    if '“' in v or '”' in v: styles.append('“”')
    if "'" in v and LEFT.search(v): styles.append("'")
    if '"' in v and LEFT.search(v): styles.append('"')
    if len(styles) > 1:
        add('09_引号混用', k, f'{styles} | {v[:90]!r}')

# ---------- 10. 省略号风格 ----------
for k, v in items:
    if re.search(r'\.\.\.', v) and '…' in v:
        add('10_省略号混用', k, v[:90])
    elif re.search(r'(?<![.])\.\.(?![.])', v):
        add('10_省略号混用', k, v[:90])

# ---------- 11. 花括号标签一致性 ----------
def braces(s): return sorted(re.findall(r'\{([^{}]{0,12})\}', s))
for k, v in items:
    be, bz = braces(i2[k][0]), braces(v)
    if set(be) != set(bz):
        add('11_标签不一致', k, f'EN={be} ZH={bz} | ZH:{v[:90]!r}')

# ---------- 12. 前后空格 / 多余空格 ----------
for k, v in items:
    if v != v.strip():
        add('12_首尾空白', k, repr(v))
    if '  ' in v:
        add('12_首尾空白', k, repr(v[:90]))

# ---------- 13. 中英混排空格 ----------
for k, v in items:
    if re.search(rf'[{CJK}][A-Za-z0-9]|[A-Za-z0-9][{CJK}]', v):
        add('13_中英无空格', k, v[:90])

# ---------- 输出 ----------
summary = []
for cat in sorted(findings):
    rows = findings[cat]
    p = os.path.join(OUT, cat + '.tsv')
    with open(p, 'w', encoding='utf-8') as f:
        f.write('key\tdetail\n')
        for k, det in rows:
            f.write(f'{k}\t{det}\n'.replace('\n\t', '\t'))
    summary.append((cat, len(rows)))
    print(f'{len(rows):6d}  {cat}')
json.dump({c: [{'key': k, 'detail': det} for k, det in findings[c]] for c in findings},
          open(os.path.join(OUT, 'mech_all.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total findings:', sum(n for _, n in summary))
