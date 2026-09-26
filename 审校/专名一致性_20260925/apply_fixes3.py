#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_fixes3.py — 落地 #27–#31 用语统一 + #42 Settlement -> 定居点。仅作用于 UI/任务目标类 key。"""
import csv, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DRY = "--dry" in sys.argv
UI = re.compile(r"^(Objective_|QuestLoc_\w*QuestObjective|QuestLoc_\w*QuestShortDesc|Achievement_|Tutorial_|Help_Page|Room_|Generic_|Notification_|QuestList_)")
# (编号, EN正则, [(旧,新)...])
RULES = [
    (27, r"Kill|Killed|Killing", [("杀死", "消灭"), ("杀了", "消灭"), ("干掉", "消灭"), ("杀掉", "消灭"), ("击毙", "消灭"), ("屠杀", "消灭")]),
    (28, r"Rescue|Rescued|Rescuing|Save|Saved|Saving", [("营救", "拯救"), ("救出", "拯救"), ("解救", "拯救"), ("救人", "拯救"), ("救援", "拯救")]),
    (29, r"Talk|Speak|Talked", [("谈谈", "交谈"), ("说话", "交谈"), ("聊天", "交谈")]),
    (30, r"Help|Helped|Helping", [("帮忙", "帮助")]),
    (31, r"Final", [("最终", "最后")]),
]
def main():
    cn = json.load(open(f"{ROOT}/data/translations.json", encoding="utf-8"))
    en = {k: v[0] for k, v in json.load(open(f"{ROOT}/data/i2_dump.json", encoding="utf-8")).items()}
    rows = []
    for num, enre, subs in RULES:
        p = re.compile(enre, re.I)
        for k, z in list(cn.items()):
            if not UI.match(k) or not p.search(en.get(k, "")):
                continue
            new = z
            for a, b in subs:
                new = new.replace(a, b)
            if new != z:
                rows.append((num, k, z, new))
    # #42 Settlement -> 定居点
    for k, z in list(cn.items()):
        if re.search(r"(?<![A-Za-z])Settlements?(?![A-Za-z])", en.get(k, ""), re.I) and "安置点" in z:
            rows.append((42, k, z, z.replace("安置点", "定居点")))
    print(f"待改 {len(rows)} 条")
    from collections import Counter
    print("  ", dict(Counter(r[0] for r in rows)))
    for num, k, z, new in rows:
        print(f"[#{num}] {k[:52]}\n     {z[:72]!r}\n  -> {new[:72]!r}")
    if DRY:
        return
    for num, k, _z, new in rows:
        cn[k] = new
    open(f"{ROOT}/data/translations.json", "w", encoding="utf-8").write(json.dumps(cn, ensure_ascii=False, indent=1) + "\n")
    with open(f"{ROOT}/data/translations.tsv", "w", encoding="utf-8") as f:
        for k, v in cn.items():
            parts = v.split("\n"); f.write(k + "\t" + parts[0] + "\n")
            for x in parts[1:]: f.write(x + "\n")
    subprocess.run([sys.executable, f"{ROOT}/scripts/make_pairs.py"], cwd=ROOT, check=True)
    print("已写回三表")
if __name__ == "__main__":
    main()
