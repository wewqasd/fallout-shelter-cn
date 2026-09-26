#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan_proper_nouns.py — 专有名词「一词多译」扫描。

输入: data/en_zh_pairs.tsv (key, EN, 中文)
输出:
  proper_noun_variants.tsv  专名 -> 多种中文写法（含出现次数与样例 key）
  same_en_multi_zh.tsv      英文完全相同但中文不同的条目对
  summary.txt               概览

方法:
  1) 从 EN 里挖专名候选：句中首字母大写词（出现≥2次的句中用法）+ 多词大写短语 + 人工白名单
  2) 对每个候选，取所有含它的条目，用「局部 n-gram 文档频率 vs 全库文档频率」反推它的中文写法
  3) 同一专名出现 ≥2 种写法即报
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))

CJK = re.compile(r"^[\u4e00-\u9fff·•‧・]+$")
TOKEN = re.compile(r"[\u4e00-\u9fff]+(?:[·•‧・][\u4e00-\u9fff]+)*")
WORD = re.compile(r"[A-Za-z][A-Za-z'’\-\.]*")
NON_WORD = re.compile(r"[^A-Za-z0-9'’\-\.]")

STOP = set("""a an the and or of to in on for with at by from is are was were be been being you your
yours we our us they them their it its he she his her i me my this that these those all any some no
not new add new add more less up down out off over under again now then here there what which who
when where why how can cannot could will would shall should may might must do does did done have has
had get got go goes going come comes coming make makes making take takes taking use uses used using
yes ok okay please level levels time times day days week weeks hour hours minute minutes second seconds
quest quests item items room rooms dweller dwellers vault vaults find found search select choose open
close save back next done cancel confirm start end play stop buy sell use equip unequip reward rewards
value values name names type types total max min count number slot slots card cards pack packs special
only also just each every both few many most other others same than too very well still even much more
left right top bottom best good great rare common legendary epic normal hard easy goal goals objective
""".split())

# 辐射系列专名白名单（保证覆盖；大小写敏感匹配由 word_match 处理）
WHITELIST = """
Vault Vaults Vault-Tec Vault Boy Overseer Dwellers Dweller Caps Bottle Cap Stimpak RadAway Rad-X
Radroach Radroaches Radscorpion Radscorpions Deathclaw Deathclaws Mirelurk Mirelurks Bloatfly Bloodbug
Stingwing Yao Guai Brahmin Mole Rat Mole Rats Ghoul Ghouls Glowing One Super Mutant Super Mutants
Raider Raiders Brotherhood of Steel Enclave NCR Minutemen Institute Synth Synths Liberty Prime
Mr. Handy Mister Handy Miss Nanny Mister Gutsy Sentry Bot Protectron Assaultron Eyebot Turret
Power Armor Pip-Boy Fusion Core Nuka-Cola Nuka-Cola Quantum Nuka Cola Nuka-World Quantum
Laser Rifle Plasma Rifle Fat Man Gatling Laser Minigun Flamer Missile Launcher Combat Shotgun
Junk Jet Alien Blaster Fire Hydrant Bat Grognak Barbarian The Unstoppables Silver Shroud
Lunchbox Mr. Handy Lucy Maximus Cooper Howard The Ghoul Hank Norm Vault 33 Vault 32 Vault 31
Deathclaw Egg Firefly Fireflies Cazador Nightkin Centaur Floater Fog Crawler Angler Hermit Crab
Giddyup Buttercup Teddy Bear Slocum's Joe Red Rocket Nuka-Cola Bottler Super-Duper Mart
Fallout Shelter Fallout Vault-Tec Workshop Theme Themes Pet Pets Dogmeat Dog Meat
Quest Bosses Season Pass Legendary Rarity Special S.P.E.C.I.A.L. SPECIAL
""".split()


def word_match(text, term):
    """term 作为独立词在 text 中匹配（大小写不敏感，保留内部标点）。"""
    pat = r"(?<![A-Za-z])" + re.escape(term).replace(r"\ ", r"\s+") + r"(?![A-Za-z])"
    return re.search(pat, text, re.IGNORECASE) is not None


def load_pairs():
    rows = []
    with open(os.path.join(ROOT, "data", "en_zh_pairs.tsv"), encoding="utf-8", newline="") as f:
        r = csv.reader(f, dialect="excel-tab")
        next(r)
        for row in r:
            if len(row) >= 3:
                rows.append((row[0], row[1], row[2]))
    return rows


def collect_terms(rows, low):
    """返回 {term: (occurrences, mid_sentence_count)}"""
    occ = Counter()
    mid = Counter()
    multi = Counter()
    for _k, en, _zh in rows:
        for m in WORD.finditer(en):
            t = m.group(0)
            occ[t] += 1
            start = m.start()
            prev = en[start - 1] if start > 0 else ""
            if start > 0 and prev not in ".!?\n":
                mid[t] += 1
        for m in re.finditer(
            r"\b[A-Z][A-Za-z'’\-]*(?:\s+(?:of|the|and|de|von|&)\s+|\s+)"
            r"[A-Z][A-Za-z'’\-]*(?:\s+(?:of|the|and|de|von|&)\s+|\s+[A-Z][A-Za-z'’\-]*)*", en):
            seq = m.group(0).strip().rstrip(".")
            if len(seq.split()) >= 2 and "\n" not in seq and not re.search(r"[.!?,:;]", seq):
                multi[seq] += 1

    terms = {}
    for t, c in occ.items():
        if len(t) < 3 or t.lower() in STOP:
            continue
        if not t[0].isupper():
            continue
        if mid.get(t, 0) >= 2 or c >= 25:
            terms[t] = (c, mid.get(t, 0))
    for s, c in multi.items():
        if c >= 2 and s not in terms:
            terms[s] = (c, 0)
    for s in WHITELIST:
        if s in terms or s.lower() in STOP:
            continue
        n = sum(1 for l in low if s.lower() in l)
        if n:
            terms[s] = (n, 0)
    return terms


def ngrams(zh, lo=2, hi=10):
    out = set()
    for seg in TOKEN.findall(zh):
        for n in range(lo, min(hi, len(seg)) + 1):
            for i in range(len(seg) - n + 1):
                g = seg[i:i + n]
                if CJK.match(g):
                    out.add(g)
    return out


def main():
    rows = load_pairs()
    print(f"载入 {len(rows)} 条 (key, EN, ZH)")
    low = [en.lower() for _k, en, _z in rows]
    global_df = Counter()
    for _k, _en, zh in rows:
        for g in ngrams(zh):
            global_df[g] += 1
    N = len(rows)
    terms = collect_terms(rows, low)
    print(f"专名候选 {len(terms)} 个")

    # 每个条目的命中专名集合（用于「干净条目」过滤）
    term_list = [t for t in terms if len(t) >= 3]
    hits = []
    for i, l in enumerate(low):
        s = {t for t in term_list if t.lower() in l and word_match(rows[i][1], t)}
        hits.append(s)
    # 最长匹配：若某专名被同条中更长的专名包含，则不计入它的条目集（消除 Rackie / Jobinson's 这类碎片）
    hits_max = []
    for s in hits:
        mx = {t for t in s if not any(o != t and t.lower() in o.lower() for o in s)}
        hits_max.append(mx)
    entry_of = defaultdict(list)
    for i, s in enumerate(hits_max):
        for t in s:
            entry_of[t].append(i)

    def related(a, b):
        return a.lower() in b.lower() or b.lower() in a.lower()

    variants_rows = []
    details = defaultdict(list)
    direct_rows = []
    for term, (c, mid_c) in sorted(terms.items(), key=lambda x: -x[1][0]):
        idx = entry_of.get(term, [])
        if len(idx) < 2:
            continue
        # 直接命中：整条 EN 就是该专名（去标点/空白后相等）
        norm = re.sub(r"[^a-z0-9]", "", term.lower())
        direct = [i for i in idx if re.sub(r"[^a-z0-9]", "", rows[i][1].lower()) == norm]
        if direct:
            zc = Counter(rows[i][2] for i in direct)
            if len(zc) >= 2:
                for z, n in zc.most_common():
                    direct_rows.append((term, len(direct), z, n))
                    for i in direct:
                        if rows[i][2] == z:
                            details[(term, z)].append(
                                (rows[i][0], rows[i][1][:70], rows[i][2][:70]))
        # 干净条目：除本专名外不含其它候选专名
        clean = [i for i in idx if not any(s != term and not related(s, term) for s in hits[i])]
        pool = clean if len(clean) >= 3 else idx
        local = Counter()
        for i in pool:
            for g in ngrams(rows[i][2]):
                if len(g) >= 2:
                    local[g] += 1
        cands = [(g, df) for g, df in local.items()
                 if df / len(pool) >= 0.6 and global_df[g] / N <= 0.02 and CJK.match(g)]
        if len(cands) < 2:
            continue
        cands.sort(key=lambda x: (-x[1], -len(x[0])))
        keep = []
        for g, df in cands:
            ov = [(k, kd) for k, kd in keep if g in k or k in g]
            if not ov:
                keep.append((g, df))
                continue
            # 重叠时：更长且出现率不显著更低者优先（避免「宝拉·普朗布金」被切成「宝拉」+「普朗布金」）
            if all(len(g) > len(k) and df >= 0.85 * kd for k, kd in ov):
                keep = [(k, kd) for k, kd in keep if (k, kd) not in ov]
                keep.append((g, df))
        keep.sort(key=lambda x: -x[1])
        if len(keep) >= 2:
            # 互斥性过滤：真正的异译在同一条目里几乎不共现；碎片/同句其它成分高度共现
            alt = []
            for a in range(len(keep)):
                for b in range(a + 1, len(keep)):
                    (g1, d1), (g2, d2) = keep[a], keep[b]
                    co = sum(1 for i in pool if g1 in rows[i][2] and g2 in rows[i][2])
                    if co <= max(1, 0.15 * min(d1, d2)):
                        alt.extend([keep[a], keep[b]])
            alt = sorted(set(alt), key=lambda x: -x[1])
            if len(alt) >= 2:
                for g, df in alt:
                    variants_rows.append((term, len(pool), g, df, round(df / len(pool), 2)))
                for g, df in alt:
                    for i in pool:
                        if g in rows[i][2]:
                            details[(term, g)].append(
                                (rows[i][0], rows[i][1][:70], rows[i][2][:70]))

    with open(os.path.join(OUT, "proper_noun_variants.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, dialect="excel-tab")
        w.writerow(["EN专名", "干净条目数", "中文写法", "该写法条目数", "占比"])
        w.writerows(variants_rows)

    with open(os.path.join(OUT, "proper_noun_direct.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, dialect="excel-tab")
        w.writerow(["EN专名", "整条命中数", "中文写法", "条数"])
        w.writerows(direct_rows)

    # 同名英文 -> 多种中文（同一 EN 串）
    byen = defaultdict(set)
    keys_byen = defaultdict(list)
    for k, en, zh in rows:
        byen[en].add(zh)
        keys_byen[en].append((k, zh))
    multi = [(en, zs) for en, zs in byen.items() if len(zs) > 1]
    multi.sort(key=lambda x: -len(x[1]))
    with open(os.path.join(OUT, "same_en_multi_zh.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, dialect="excel-tab")
        w.writerow(["EN", "译法数", "key", "中文"])
        for en, zs in multi:
            for k, zh in sorted(keys_byen[en]):
                w.writerow([en, len(zs), k, zh])

    with open(os.path.join(OUT, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(f"条目总数 {N}\n专名候选 {len(terms)}\n"
                f"一词多译专名（≥2 种写法）{len(set(r[0] for r in variants_rows))}\n"
                f"同 EN 多中文的条目组 {len(multi)}\n")
    print(f"一词多译专名: {len(set(r[0] for r in variants_rows))} 个")
    print(f"同 EN 多中文: {len(multi)} 组")
    import json
    with open(os.path.join(OUT, "_details.json"), "w", encoding="utf-8") as f:
        json.dump({f"{k[0]}||{k[1]}": v[:4] for k, v in details.items()}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
