#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_fixes2.py — 落地第二轮用户拍板决策（第 1~26 项）。

写回格式与仓库现况字节一致；写完重新生成 translations.tsv 与 en_zh_pairs.tsv。
用法： python3 apply_fixes2.py [--dry]
"""
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DRY = "--dry" in sys.argv

KRE = lambda p: re.compile(p)          # key 限定
ERE = lambda p: re.compile(p, re.I)    # EN 限定

# (编号, 说明, key正则|None, EN正则|None, [(查找, 替换, 是否正则)])
RULES = [
    (1, "Alpha Deathclaw -> 领头死爪", None, ERE(r"(?<![A-Za-z])Alpha Deathclaw(?![A-Za-z])"),
     [("阿尔法死爪", "领头死爪", 0), ("首领死爪", "领头死爪", 0), ("死爪头领", "领头死爪", 0)]),
    (2, "Protectron -> 保护者机器人", None, ERE(r"(?<![A-Za-z])Protectrons?(?![A-Za-z])"),
     [(r"保护者(?!机器人)", "保护者机器人", 1)]),
    (3, "Feral Ghoul -> 狂尸鬼", KRE(r"^Objective_SurviveGhoulNoCasualties"), None,
     [("尸鬼攻击", "狂尸鬼攻击", 0)]),
    (4, "Radroach -> 辐射蟑螂", None, ERE(r"(?<![A-Za-z])Radroach(?:es)?(?![A-Za-z])"),
     [("辐射小强", "辐射蟑螂", 0)]),
    (5, "Athletics Room -> 体操房", KRE(r"^Room_Dojo$"), None, [("运动室", "体操房", 0)]),
    (5, "Athletics Room -> 体操房", KRE(r"^Tutorial_Tip_15$"), None, [("体操室", "体操房", 0)]),
    (6, "Boss -> 首领", KRE(r"^QuestLoc_INS_QL1_MajorPlayers_1_CombatInit8$"), None, [("头目", "首领", 0)]),
    (7, "Perception -> 观察力", KRE(r"^QuestLoc_ENC_QL2_Defective_3_Room5_Question_Line2$"), None, [("感知", "观察力", 0)]),
    (8, "Luck -> 运气值", KRE(r"^Message_TutorialPopup_16_Body$"), None, [("幸运值", "运气值", 0)]),
    (9, "Stimpak+RadAway -> 治疗针和消辐宁", KRE(r"^Message_TutorialPopup_15_Body"), None,
     [("治疗用品", "治疗针和消辐宁", 0)]),
    (10, "Quantum 可乐 -> 量子核子可乐", KRE(r"^QuestLoc_OneGhoulCustomer_Conversation_1_Team_2$"), None,
     [("你的可乐", "你的量子核子可乐", 0)]),
    (10, "Quantum 可乐 -> 量子核子可乐", KRE(r"^QuestLoc_OneGhoulCustomer_Conversation_1_Team_3$"), None,
     [("那些可乐", "那些量子核子可乐", 0)]),
    (11, "Caps -> 花瓶盖玩游戏", KRE(r"^QuestLoc_TheDeBuggers_Conversation_2_NPCEnd_2$"), None,
     [("花钱玩游戏", "花瓶盖玩游戏", 0)]),
    (12, "Giddyup Buttercup -> 奶油小马", None, ERE(r"(?<![A-Za-z])Giddyup Buttercup(?![A-Za-z])"),
     [("玩具马", "奶油小马", 0), ("骑乘小马", "奶油小马", 0)]),
    (13, "Legendary -> 传奇级", KRE(r"^Weapon_Name_Rifle_Legendary$"), None, [("传说级", "传奇级", 0)]),
    (14, "Nuka-Cola Bottler -> 装瓶室", KRE(r"^Shop_SeasonPass_NewVegasA_Blurb$"), None,
     [("核子可乐装瓶厂", "核子可乐装瓶室", 0)]),
    (15, "Diner -> 餐厅", KRE(r"^QuestLoc_GameShowGauntletH_Conversation_3_Team_2$"), None, [("食堂", "餐厅", 0)]),
    (16, "Decorations -> 普通装饰品", KRE(r"^Stats_Common_Decorations$"), None, [("普通装饰", "普通装饰品", 0)]),
    (17, "Mr. Handy -> 巧手先生", KRE(r"^QuestLoc_CollectorsEdition_Conversation_1_Team_1$"), None,
     [("巧手先生机器人", "巧手先生", 0)]),
    (18, "Wasteland -> 废土", KRE(r"^QuestLoc_HumansLikeUs_QuestLongDescription$"), None, [("荒地", "废土", 0)]),
    (19, "Agility -> 敏捷", KRE(r"^Stats_Average_Agility$"), None, [("敏捷性", "敏捷", 0)]),
    (20, "Alien 对话 -> 外星", KRE(r"^QuestLoc_WaroftheNerds_Conversation_2_Team_3$"), None,
     [("异形耳朵", "外星耳朵", 0)]),
    (21, "Combat Armor -> 战斗装甲", KRE(r"^Outfit_Name_CombatArmor"), None, [("格斗护甲", "战斗装甲", 0)]),
    (22, "Daily Quest -> 每日任务", KRE(r"^QuestList_DailyQuest$"), None, [("日常任务", "每日任务", 0)]),
    (23, "Baby(UI) -> 婴儿", KRE(r"^(Baby_NewBabyArrived|Message_DwellerBorn)$"), None, [("宝贝", "婴儿", 0)]),
    (24, "Settler -> 定居者", None, ERE(r"(?<![A-Za-z])Settlers?(?![A-Za-z])"),
     [("安置点的人", "定居者", 0), (r"定居点的居民", "定居者", 1), ("居民", "定居者", 0)]),
    (25, "Brotherhood(单用) -> 兄弟会", None, None, [("钢铁兄弟会", "兄弟会", 0)]),   # EN 过滤在代码里特判
    (26, "Ultracite 房名档位互换", KRE(r"^Room_UltraciteWeaponFactory_2$"), None,
     [("辐射极琉矿武器工厂", "辐射极琉矿武器车间", 0)]),
    (26, "Ultracite 房名档位互换", KRE(r"^Room_UltraciteWeaponFactory_3$"), None,
     [("辐射极琉矿武器车间", "辐射极琉矿武器工厂", 0)]),
]


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_json(p, o):
    with open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps(o, ensure_ascii=False, indent=1) + "\n")


def save_tsv(p, o):
    with open(p, "w", encoding="utf-8") as f:
        for k, v in o.items():
            parts = v.split("\n")
            f.write(k + "\t" + parts[0] + "\n")
            for x in parts[1:]:
                f.write(x + "\n")


def main():
    cn = load_json(os.path.join(ROOT, "data", "translations.json"))
    dump = load_json(os.path.join(ROOT, "data", "i2_dump.json"))
    en = {k: v[0] for k, v in dump.items()}
    orig = dict(cn)
    changes = []
    for num, desc, kre, enre, subs in RULES:
        for k, z in list(cn.items()):
            if kre and not kre.search(k):
                continue
            e = en.get(k, "")
            if num == 25:                       # Brotherhood：仅 EN 单用（排除 Brotherhood of Steel）
                if not re.search(r"(?<![A-Za-z])Brotherhood(?![A-Za-z])", e) or re.search(r"Brotherhood of Steel", e, re.I):
                    continue
            elif enre and not enre.search(e):
                continue
            new = z
            for pat, rep, isre in subs:
                new = re.sub(pat, rep, new) if isre else new.replace(pat, rep)
            if new != z:
                cn[k] = new
                changes.append((num, desc, k, z, new))
    print(f"命中修订 {len(changes)} 条 / key {len(set(c[2] for c in changes))} 个")
    for num, c in Counter(c[0] for c in changes).items():
        print(f"  #{num}: {c}")
    bad = [c for c in changes if "定居点的定居者" in c[4]]
    if bad:
        print("!! 出现「定居点的定居者」:", [b[2] for b in bad])
    if DRY:
        print("\n--- 样例 ---")
        for c in changes[:12]:
            print(f"[#{c[0]}] {c[2]}\n   旧: {c[3][:80]}\n   新: {c[4][:80]}")
        return
    save_json(os.path.join(ROOT, "data", "translations.json"), cn)
    save_tsv(os.path.join(ROOT, "data", "translations.tsv"), cn)
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "make_pairs.py")], cwd=ROOT, check=True)
    print("已写回三表；值变化 key:", sum(1 for k in cn if cn[k] != orig[k]))


if __name__ == "__main__":
    main()
