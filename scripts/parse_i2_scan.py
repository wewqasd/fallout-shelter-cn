#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描式 I2 term 解析器：用 langcnt+values+尾部+nextkey 特征验证"""
import UnityPy, sys, struct, re, json

def get_big(env, pid):
    best=None
    for obj in env.objects:
        if obj.type.name=='MonoBehaviour' and obj.path_id==pid:
            if best is None or obj.byte_size>best.byte_size: best=obj
    return best

LANG_NAMES = ["en","es","fr","it","de","ru"]

def is_printable_ascii(b):
    return bool(b) and all(32 <= c < 127 for c in b)

def try_parse_langcnt(raw, pos, n, expect_langcnt):
    """尝试从 pos 解析 [langcnt][values][tail2][nextkey]，成功返回 nextkey 位置"""
    if pos+4 > n: return None
    langcnt = struct.unpack_from('<i', raw, pos)[0]
    if not (1 <= langcnt <= 40): return None
    if expect_langcnt is not None and langcnt != expect_langcnt: return None
    p = pos + 4
    vals = []
    for _ in range(langcnt):
        if p+4 > n: return None
        ln = struct.unpack_from('<i', raw, p)[0]
        if ln < 0 or ln > 100000 or p+4+ln > n: return None
        vals.append(raw[p+4:p+4+ln].decode('utf-8','replace'))
        p += 4 + ln
        p = (p + 3) // 4 * 4
    # 两个尾部数组 [count][count×int]
    for _ in range(2):
        if p+4 > n: return None
        c = struct.unpack_from('<i', raw, p)[0]
        if not (0 <= c <= 200) or p+4+c*4 > n: return None
        p += 4 + c*4
    # 下一个 key：p 处是 key 长度前缀，必须是合理 ASCII key
    if p+4 > n: return None
    nklen = struct.unpack_from('<i', raw, p)[0]
    if not (1 <= nklen <= 300) or p+4+nklen > n: return None
    nk = raw[p+4:p+4+nklen]
    if not is_printable_ascii(nk): return None
    return (p, langcnt, vals)  # p = 下一个 key 长度前缀位置

def parse_all(raw):
    n = len(raw)
    fk = raw.find(b'Achievement_Xbox_Completed_01')
    pos = fk - 4
    terms = []
    LANG_COUNT = None
    while pos + 16 <= n:
        klen = struct.unpack_from('<i', raw, pos)[0]
        if not (1 <= klen <= 300): break
        keyb = raw[pos+4:pos+4+klen]
        if not is_printable_ascii(keyb): break
        key = keyb.decode('ascii')
        key_end = pos + 4 + klen
        align = (key_end + 3) // 4 * 4
        # 从 align 开始扫描找 langcnt（跳过 flags/category）
        found = None
        scan_start = align
        scan_end = min(scan_start + 200, n)  # langcnt 不会太远
        for cand in range(scan_start, scan_end):
            res = try_parse_langcnt(raw, cand, n, LANG_COUNT)
            if res:
                found = res
                break
        if not found:
            print(f"  [STOP] 未找到 langcnt @{align}, key={key}, terms={len(terms)}")
            break
        nextpos, lc, vals = found
        if LANG_COUNT is None: LANG_COUNT = lc
        terms.append((key, vals))
        pos = nextpos
        if len(terms) % 3000 == 0:
            print(f"  ...{len(terms)} terms @{pos}/{n} ({pos/n*100:.1f}%)")
    return terms, pos, LANG_COUNT

def main(path, pid=20854):
    env = UnityPy.load(path)
    obj = get_big(env, pid)
    raw = obj.get_raw_data()
    n = len(raw)
    terms, end, lc = parse_all(raw)
    print(f"\n=== I2 LanguageSource (path={pid}) ===")
    print(f"原始大小: {n} 字节")
    print(f"语言数: {lc} ({LANG_NAMES})")
    print(f"term 数: {len(terms)}")
    print(f"term 区结束: {end}/{n} ({end/n*100:.2f}%)")
    print(f"剩余: {n-end} 字节")
    if terms:
        print(f"首个: {terms[0][0]}")
        print(f"末尾: {terms[-1][0]}")
    from collections import Counter
    chars = Counter(); nonempty = Counter()
    for key, vals in terms:
        for i,v in enumerate(vals):
            if i < len(LANG_NAMES):
                chars[LANG_NAMES[i]] += len(v)
                if v.strip(): nonempty[LANG_NAMES[i]] += 1
    print("\n=== 各语言 ===")
    for lg in LANG_NAMES:
        print(f"  {lg}: {chars[lg]:>8}字符, 非空 {nonempty[lg]}/{len(terms)}")
    with open("/home/wangqiang/fallout_work/i2_terms.json","w",encoding="utf-8") as f:
        json.dump([{"key":k,"vals":v} for k,v in terms], f, ensure_ascii=False)
    print("\n已保存 i2_terms.json")

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv)>1 else "/home/wangqiang/FalloutShelter/FalloutShelter_Data/data.unity3d"
    main(p)
