#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_mech2.py — 第二轮机械扫描：语序对调 / 否定丢失 / 量词范围丢失 / 性别指代。
输出到 审校/语义审校_20260927/mech2/
"""
import json, re, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, 'mech2')
os.makedirs(OUT, exist_ok=True)

d = json.load(open(f'{ROOT}/data/translations.json', encoding='utf-8'))
i2 = json.load(open(f'{ROOT}/data/i2_dump.json', encoding='utf-8'))
F = collections.defaultdict(list)


def add(cat, key, detail):
    F[cat].append({'key': key, 'detail': detail})


# ============ A. 并列/术语语序对调 ============
# 用「表自身」构建 EN 术语 -> ZH 术语 词典（只取名称类 key，短且唯一）
NAME_PREFIX = ('Weapon_Name_', 'Outfit_Name_', 'Room_', 'Pet_Name_', 'Junk_Name_',
               'Theme_Name_', 'Title_', 'UnlockRoom_')
term = {}
for k, v in d.items():
    if not k.startswith(NAME_PREFIX):
        continue
    en = i2[k][0].strip()
    zh = v.strip()
    if 4 <= len(en) <= 28 and 1 < len(zh) <= 12 and '\n' not in en and '\n' not in zh:
        if en.lower() not in term or len(zh) < term[en.lower()][1]:
            term[en.lower()] = (zh, len(zh))
# 手工补充常见专名（英文 -> 中文）
term.update({
    'stimpak': ('治疗针', 3), 'stimpaк': ('治疗针', 3), 'radaway': ('消辐宁', 3),
    'caps': ('瓶盖', 2), 'vault': ('避难所', 3), 'raiders': ('掠夺者', 3),
    'deathclaw': ('死爪', 2), 'ghoul': ('尸鬼', 2), 'mutant': ('变种人', 3),
    'brotherhood of steel': ('钢铁兄弟会', 5), 'ncr': ('NCR', 3), 'minutemen': ('义勇军', 3),
    'super mutant': ('超级变种人', 5), 'mole rat': ('鼹鼠', 2), 'radroach': ('辐射蟑螂', 4),
    'weapons': ('武器', 2), 'outfits': ('装备', 2), 'junk': ('杂物', 2), 'pets': ('宠物', 2),
})
terms_sorted = sorted(term.items(), key=lambda kv: -len(kv[0]))


_treg = [(t, zh, re.compile(r'(?<![a-z0-9])' + re.escape(t) + r'(?![a-z0-9])')) for t, (zh, _l) in terms_sorted]


def find_terms(en):
    low = ' ' + en.lower() + ' '
    hits = []
    used = [False] * len(low)
    for t, zh, rgx in _treg:
        if t not in low:
            continue
        for m in rgx.finditer(low):
            if any(used[m.start():m.end()]):
                continue
            for i in range(m.start(), m.end()):
                used[i] = True
            hits.append((m.start(), t, zh))
    return sorted(hits)


for k, v in d.items():
    en = i2[k][0]
    if len(en) < 8 or len(en) > 400 or len(v) < 4:
        continue
    hits = find_terms(en)
    if len(hits) < 2:
        continue
    pos = []
    ok = True
    for off, t, zh in hits:
        found = [m.start() for m in re.finditer(re.escape(zh), v)]
        if not found:
            ok = False
            break
        pos.append((off, found[0], t, zh))
    if not ok or len(pos) < 2:
        continue
    en_ord = [p[2] for p in sorted(pos, key=lambda x: x[0])]
    zh_ord = [p[2] for p in sorted(pos, key=lambda x: x[1])]
    if en_ord != zh_ord:
        add('A_语序对调', k, f'EN顺序={en_ord} ZH顺序={zh_ord} | EN:{en[:110]!r} ZH:{v[:110]!r}')


# ============ B. 否定丢失 ============
NEG_EN = re.compile(r"\b(not|no|never|none|nothing|nobody|cannot|can't|don't|doesn't|didn't|won't|isn't|aren't|without|unless|neither|nor|refuse|fail)\b", re.I)
NEG_ZH = re.compile(r'[不没无未别勿否莫何必免]|拒绝|禁止|停止|取消')
for k, v in d.items():
    en = i2[k][0]
    if len(en) < 10 or len(v) < 3:
        continue
    if NEG_EN.search(en) and not NEG_ZH.search(v):
        add('B_否定丢失', k, f'EN:{en[:110]!r} ZH:{v[:110]!r}')


# ============ C. 范围/限定词丢失 ============
LIM = [('only', '只|仅|唯一|才'), ('unless', '除非'), ('at least', '至少'), ('before', '之前|以前|先'),
       ('after', '之后|以后|后'), ('every', '每'), ('all ', '所有|全部|全|一切|都'),
       ('never', '从不|绝不|永不|从未'), ('must', '必须|得|要'), ('first', '首先|先|第一')]
for k, v in d.items():
    en = i2[k][0]
    if len(en) < 14 or len(v) < 3:
        continue
    for w, zhre in LIM:
        if re.search(r'\b' + w.strip() + r'\b', en, re.I) and not re.search(zhre, v):
            add('C_限定词丢失', k, f'[{w.strip()}] EN:{en[:110]!r} ZH:{v[:110]!r}')
            break


# ============ D. 性别指代 ============
def zh_pron(s):
    return len(re.findall(r'她', s)), len(re.findall(r'(?<!其)他(?!们)', s))
for k, v in d.items():
    en = i2[k][0]
    if len(en) < 6:
        continue
    she = len(re.findall(r'\b(she|her|hers|herself)\b', en, re.I))
    he = len(re.findall(r'\b(he|him|his|himself)\b', en, re.I))
    zshe, zhe = zh_pron(v)
    if she and not he and zhe and not zshe:
        add('D_性别指代', k, f'EN 指女性(she×{she}) 但 ZH 用「他」×{zhe} | EN:{en[:100]!r} ZH:{v[:100]!r}')
    elif he and not she and zshe and not zhe:
        add('D_性别指代', k, f'EN 指男性(he×{he}) 但 ZH 用「她」×{zshe} | EN:{en[:100]!r} ZH:{v[:100]!r}')


for cat in sorted(F):
    with open(os.path.join(OUT, cat + '.tsv'), 'w', encoding='utf-8') as f:
        f.write('key\tdetail\n')
        for r in F[cat]:
            f.write(f"{r['key']}\t{r['detail']}\n")
    print(f'{len(F[cat]):6d}  {cat}')
json.dump(F, open(os.path.join(OUT, 'mech2_all.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total', sum(len(x) for x in F.values()), ' 术语词典', len(term))
