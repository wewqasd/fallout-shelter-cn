#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 data.unity3d 提取 I2 LanguageSource 全量转储（key → 6 语言列表），
与 fs_cn.patcher 的 parse_terms 同逻辑，输出 data/i2_dump.json 同格式。

用法: python scripts/extract_i2.py <data.unity3d> <out.json>
"""
import UnityPy, struct, json, sys, os

ANCHOR = b"Achievement_Xbox_Completed_01"

def iskey(b): return bool(b) and all(32 <= c < 127 for c in b)

def try_parse_langcnt(raw, pos, n, expect=None, need_key=True):
    if pos + 4 > n: return None
    lc = struct.unpack_from('<i', raw, pos)[0]
    if not (1 <= lc <= 40): return None
    if expect is not None and lc != expect: return None
    p = pos + 4
    for _ in range(lc):
        if p + 4 > n: return None
        ln = struct.unpack_from('<i', raw, p)[0]
        if ln < 0 or ln > 100000 or p + 4 + ln > n: return None
        p += 4 + ln; p = (p + 3) // 4 * 4
    for _ in range(2):
        if p + 4 > n: return None
        c = struct.unpack_from('<i', raw, p)[0]
        if not (0 <= c <= 5000) or p + 4 + c * 4 > n: return None
        p += 4 + c * 4
    if need_key:
        if p + 4 > n: return None
        nk = struct.unpack_from('<i', raw, p)[0]
        if not (1 <= nk <= 300) or p + 4 + nk > n: return None
        if not iskey(raw[p + 4:p + 4 + nk]): return None
    return lc

def parse_terms(raw):
    n = len(raw); fk = raw.find(ANCHOR)
    if fk < 0: return [], None, None
    pos = fk - 4
    terms = []; LC = None
    while pos + 16 <= n:
        klen = struct.unpack_from('<i', raw, pos)[0]
        if not (1 <= klen <= 300): break
        keyb = raw[pos + 4:pos + 4 + klen]
        if not iskey(keyb): break
        align = (pos + 4 + klen + 3) // 4 * 4
        found = None
        for cand in range(align, min(align + 200, n)):
            if try_parse_langcnt(raw, cand, n, LC, need_key=True) is not None: found = cand; break
        if found is None:
            for cand in range(align, min(align + 200, n)):
                if try_parse_langcnt(raw, cand, n, LC, need_key=False) is not None: found = cand; break
        if found is None:
            print("  解析停止 @", len(terms)); break
        langcnt = struct.unpack_from('<i', raw, found)[0]
        if LC is None: LC = langcnt
        p = found + 4; vals = []
        for _ in range(langcnt):
            ln = struct.unpack_from('<i', raw, p)[0]; p += 4
            vals.append(raw[p:p + ln].decode('utf-8', 'replace')); p += ln; p = (p + 3) // 4 * 4
        for _ in range(2):
            c = struct.unpack_from('<i', raw, p)[0]; p += 4; p += c * 4
        terms.append((keyb.decode('ascii'), vals))
        pos = p
    return terms, LC, pos

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_ROOT, "build", "原版存档", "20260902_data.unity3d")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(_ROOT, "data", "i2_dump.json")
    env = UnityPy.load(src)
    best = None
    for o in env.objects:
        if o.type.name != 'MonoBehaviour': continue
        raw = o.get_raw_data()
        if ANCHOR in raw and (best is None or len(raw) > len(best[1])):
            best = (o, raw)
    assert best, "未找到 I2 LanguageSource（锚点缺失）"
    obj, raw = best
    terms, LC, end = parse_terms(raw)
    print(f"I2: pid={obj.path_id} file={obj.assets_file.name} terms={len(terms)} LC={LC} end={end}/{len(raw)}", flush=True)
    d = {k: v for k, v in terms}
    assert len(d) == len(terms), f"重复键! {len(d)} != {len(terms)}"
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f"已保存: {out} ({len(d)} 键)", flush=True)

main()
