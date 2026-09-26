#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_fixes.py — 落地用户已确认的 4 项专名统一，并同步三张表。

决策：
  1) Outfit        -> 装备     （原「服装」全改）
  2) Vault-Tec     -> 避难所科技（原「避难所科技公司」全改）
  3) Pet Carrier   -> 宠物笼子 （原「宠物箱」「宠物笼」全改）
  4) Living Quarters -> 宿舍   （原「居住区」全改）

写回格式与仓库现况字节一致：JSON = ensure_ascii=False, indent=1 + 末尾换行；
translations.tsv = 「key<TAB>首行 + 续行（空行=换行）」块格式；en_zh_pairs.tsv 由 make_pairs.py 重新生成。
"""
import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DRY = "--dry" in sys.argv

# (说明, key 正则或 None, EN 正则或 None, 待替换串, 替换为)
RULES = [
    ("Outfit -> 装备", None, r"(?<![A-Za-z])Outfits?(?![A-Za-z])", "服装", "装备"),
    ("Vault-Tec -> 避难所科技", None, None, "避难所科技公司", "避难所科技"),
    ("Pet Carrier -> 宠物笼子(宠物箱)", None, None, "宠物箱", "宠物笼子"),
    ("Pet Carrier -> 宠物笼子(宠物笼)", None, None, "宠物笼", "宠物笼子"),
    ("Living Quarters -> 宿舍", None, None, "居住区", "宿舍"),
]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")


def save_tsv(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        for k, v in obj.items():
            parts = v.split("\n")
            f.write(k + "\t" + parts[0] + "\n")
            for p in parts[1:]:
                f.write(p + "\n")


def main():
    jpath = os.path.join(ROOT, "data", "translations.json")
    tpath = os.path.join(ROOT, "data", "translations.tsv")
    cn = load_json(jpath)
    en = {k: v[0] for k, v in load_json(os.path.join(ROOT, "data", "i2_dump.json")).items()}
    orig = dict(cn)
    changed = []
    for desc, kre, enre, bad, good in RULES:
        # 先处理「宠物笼」时避开已生成的「宠物笼子」
        for k, z in list(cn.items()):
            if bad not in z:
                continue
            if kre and not re.search(kre, k):
                continue
            if enre and not re.search(enre, en.get(k, ""), re.I):
                continue
            if bad == "宠物笼":
                new = re.sub(r"宠物笼(?!子)", good, z)
            else:
                new = z.replace(bad, good)
            if new != z:
                cn[k] = new
                changed.append((desc, k, en.get(k, "")[:60], z[:60], new[:60]))
    print(f"命中修订 {len(changed)} 条（去重 key {len(set(c[1] for c in changed))} 个）")
    from collections import Counter
    for d, c in Counter(c[0] for c in changed).items():
        print(f"  {d}: {c} 条")
    if DRY:
        for row in changed[:10]:
            print("   ", row)
        return
    # 校验替换后无残留
    for desc, kre, enre, bad, good in RULES:
        left = [k for k, z in cn.items() if bad in z
                and (not enre or re.search(enre, en.get(k, ""), re.I))]
        if bad == "宠物笼":
            left = [k for k in left if re.search(r"宠物笼(?!子)", cn[k])]
        if left:
            print(f"!! 残留 {bad}: {len(left)} 条，例 {left[:3]}")

    save_json(jpath, cn)
    save_tsv(tpath, cn)
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "make_pairs.py")],
                   cwd=ROOT, check=True)
    print("已写回 translations.json / translations.tsv / en_zh_pairs.tsv")
    print(f"值发生变化的 key: {sum(1 for k in cn if cn[k] != orig[k])}")


if __name__ == "__main__":
    main()
