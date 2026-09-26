#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_fix_list.py — 生成「剩余待审修订清单」fix_list.tsv（编号与《待审_剩余一词多译_20260925.md》一致）。

每行: 编号 | 状态 | EN专名 | 标准写法 | 异译 | key | 当前中文 | 建议中文 | 处理方式
已落地的 4 项（Outfit→装备 / Vault-Tec→避难所科技 / Pet Carrier→宠物笼子 / Living Quarters→宿舍）已统一，不在清单内。
"""
import csv
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "fix_list.tsv")

RULES = [
    (1, "Alpha Deathclaw", "领头死爪", "阿尔法死爪", "领头死爪", None, None),
    (1, "Alpha Deathclaw", "领头死爪", "首领死爪", "领头死爪", None, None),
    (1, "Alpha Deathclaw", "领头死爪", "死爪头领", "领头死爪", None, None),
    (2, "Protectron", "保护者", "保护者机器人", "保护者", None, None),
    (3, "Feral Ghoul", "狂尸鬼", "尸鬼攻击", "狂尸鬼攻击", r"^Objective_SurviveGhoulNoCasualties", None),
    (4, "Radroach", "辐射蟑螂", "辐射小强", "辐射蟑螂", None, None),
    (5, "Athletics Room", "体操房", "运动室", "体操房", r"^Room_Dojo$", None),
    (5, "Athletics Room", "体操房", "体操室", "体操房", r"^Tutorial_Tip_15$", None),
    (6, "Boss", "首领", "头目", "首领", r"^QuestLoc_INS_QL1_MajorPlayers_1_CombatInit8$", None),
    (7, "Perception", "观察力", "感知", "观察力", r"^QuestLoc_ENC_QL2_Defective_3_Room5_Question_Line2$", None),
    (8, "Luck", "运气", "幸运值", "运气值", r"^Message_TutorialPopup_16_Body$", None),
    (9, "Stimpak+RadAway", "治疗针/消辐宁", "治疗用品", "{治疗针和消辐宁}", r"^Message_TutorialPopup_15_Body", None),
    (10, "Nuka-Cola Quantum", "量子核子可乐", "你的可乐", "你的量子核子可乐", r"^QuestLoc_OneGhoulCustomer_Conversation_1_Team_2$", None),
    (10, "Nuka-Cola Quantum", "量子核子可乐", "那些可乐", "那些量子核子可乐", r"^QuestLoc_OneGhoulCustomer_Conversation_1_Team_3$", None),
    (11, "Caps", "瓶盖", "花钱玩游戏", "花瓶盖玩游戏", r"^QuestLoc_TheDeBuggers_Conversation_2_NPCEnd_2$", None),
    (12, "Giddyup Buttercup", "骑乘小马", "玩具马", "骑乘小马", r"^Junk_Name_GiddyupButtercup$", None),
    (13, "Legendary", "传奇级", "传说级", "传奇级", r"^Weapon_Name_Rifle_Legendary$", None),
    (14, "Nuka-Cola Bottler", "核子可乐装瓶室", "核子可乐装瓶厂", "核子可乐装瓶室", r"^Shop_SeasonPass_NewVegasA_Blurb$", None),
    (15, "Diner", "餐厅", "食堂", "餐厅", r"^QuestLoc_GameShowGauntletH_Conversation_3_Team_2$", None),
    (16, "Decorations", "装饰品", "普通装饰", "普通装饰品", r"^Stats_Common_Decorations$", None),
    (17, "Mr. Handy", "巧手先生", "巧手先生机器人", "巧手先生", None, None),
    (18, "Wasteland", "废土", "荒地", "废土", r"^QuestLoc_HumansLikeUs_QuestLongDescription$", None),
    (19, "Agility", "敏捷", "敏捷性", "敏捷", r"^Stats_Average_Agility$", None),
    (20, "Alien", "外星", "异形", "外星", None, None),
    (21, "Combat Armor", "战斗装甲", "格斗护甲", "战斗装甲", None, None),
    (22, "Daily Quest", "每日任务", "日常任务", "每日任务", r"^QuestList_DailyQuest$", None),
    (23, "Baby(UI层)", "婴儿", "宝贝", "婴儿", r"^(Baby_NewBabyArrived|Message_DwellerBorn)$", None),
    (26, "Ultracite Factory/Plant（映射反了）", "FACTORY=车间/PLANT=工厂", "辐射极琉矿武器",
     "", r"^Room_UltraciteWeaponFactory_[23]$", None),
]


def main():
    rows = list(csv.reader(open(os.path.join(ROOT, "data", "en_zh_pairs.tsv"),
                                encoding="utf-8", newline=""), dialect="excel-tab"))[1:]
    out, seen = [], set()
    for num, en, std, bad, good, kre, enre in RULES:
        for k, e, z in rows:
            if bad not in z or (num, k) in seen:
                continue
            if kre and not re.search(kre, k):
                continue
            if enre and not re.search(enre, e, re.I):
                continue
            if good == "":
                new, how = "(改档位映射：_2→车间, _3→工厂)", "manual"
            elif good.startswith("{"):
                new, how = z.replace(bad, good.strip("{}")), "manual"
            else:
                new, how = z.replace(bad, good), "auto"
            if new == z:
                continue
            seen.add((num, k))
            out.append((num, "待审", en, std, bad, k, z, new, how))
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, dialect="excel-tab")
        w.writerow(["编号", "状态", "EN专名", "标准写法", "异译", "key", "当前中文", "建议中文", "处理方式"])
        w.writerows(out)
    auto = sum(1 for r in out if r[8] == "auto")
    print("待审修订项 %d 条（机械可替换 %d，人工 %d）-> %s" % (len(out), auto, len(out) - auto, OUT))
    for num, c in sorted(Counter(r[0] for r in out).items(), key=lambda x: int(x[0])):
        print("  #%2s: %d" % (num, c))


if __name__ == "__main__":
    main()
