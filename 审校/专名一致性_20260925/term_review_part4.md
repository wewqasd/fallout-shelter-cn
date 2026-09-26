# 专名一致性审校 · 第 4 片（物品/消耗品）

数据：`data/en_zh_pairs.tsv`（14064 条）；工具：`审校/专名一致性_20260925/show_term.py`（只读）。
说明：命中数为全库 EN 侧匹配（含大小写/连字符/空格/复数变体）的条目数；写法计数按条目计。基准优先级：①《辐射4》/《辐射76》官中；②本库主体来源（盛大代理安卓版官中）；③库内多数写法。

### Stimpak
- 结论：一词多译
- 命中条目数：59（含 `Stimpak` 18 / `Stimpaks` / `Stimpacks` / `StimPack` 等变体）
- 写法：治疗针×56；治疗用品×3
- 证据：`Generic_Stimpack` | `STIMPAK` | `治疗针`；`Objective_CraftStimpack` | `Craft 1 Stimpak` | `打造1个治疗针`；`Message_TutorialPopup_15_Body` | `use RadAway and Stimpaks` | `配备武器，装备和治疗用品`
- 建议：统一为「治疗针」；56/59 已统一，3 条把 RadAway 与 Stimpak 一并意译成「治疗用品」，丢失了专名指向。

### RadAway
- 结论：一词多译
- 命中条目数：46（含 `rad-away`/`Radaway` 拼写变体）
- 写法：消辐宁×43；治疗用品×3
- 证据：`Generic_Radaway` | `RADAWAY` | `消辐宁`；`Message_RadAway_NoRad` | `No radiation, RadAway use is not required` | `没有辐射伤害，不需要使用消辐宁。`；`Message_TutorialPopup_15_Body` | `use RadAway and Stimpaks` | `配备武器，装备和治疗用品`
- 建议：统一为「消辐宁」；43/46 已统一，剩余 3 条与 Stimpak 同源（同一句合并意译），一并回改。

### Rad-X
- 结论：存疑
- 命中条目数：0
- 写法：唯一（无命中）
- 证据：无（已尝试 `Rad-X`、`Rad X`、`RadX`、`rad-x` 四种拼写，并检索中文「抗辐宁」，均为 0 条）
- 建议：统一为「抗辐宁」（仅作新增条目基准）；本库未收录 Rad-X 条目，无法判定库内一致性，故不计入本片一词多译。

### Fusion Core
- 结论：一致
- 命中条目数：12
- 写法：聚变核心×12
- 证据：`QuestLoc_INS_QL3_Betrayal_2_QuestObjective1` | `Steal some Fusion Cores` | `偷走一些聚变核心`；`QuestLoc_INS_QL1_MajorPlayers_3_QuestShortDesc` | `in exchange for Fusion Cores` | `换取聚变核心`；`QuestLoc_DuoofDestructionGlowingOnex2_QuestShortDescription` | `the old Fusion Core factory` | `旧聚变核心工厂`
- 建议：统一为「聚变核心」；库内 12/12 唯一，与《辐射4》官中「核融合核心」用词不同，属来源差异·非错误。

### Power Armor
- 结论：一致
- 命中条目数：46
- 写法：动力装甲×46
- 证据：`Outfit_Name_EnclavePowerArmor` | `Enclave Power Armor` | `英克雷动力装甲`；`Outfit_Name_PaladinDansesPowerArmor` | `Paladin Danse's Power Armor` | `圣骑士丹斯的动力装甲`；`MrHandyDialog_Wasteland_97` | `An old suit of Power Armor` | `一套旧的动力装甲`
- 建议：统一为「动力装甲」；46/46 唯一，与《辐射4》官中一致。

### Pip-Boy
- 结论：一致
- 命中条目数：35（含无连字符写法 `Pip Boy` 1 条）
- 写法：哔哔小子×35
- 证据：`Controls_Xbox_Quest_PipBoy` | `Pip-Boy` | `哔哔小子`；`Message_TutorialPopup_04_Body` | `the ribbon icon in the Pip-Boy menu` | `哔哔小子菜单里的缎带图标`；`QuestLoc_AlienBotQuest04_Conversation_3_PC1_2` | `here's my Pip Boy` | `这是我的哔哔小子`
- 建议：统一为「哔哔小子」；35/35 唯一，与《辐射4》官中一致。

### Nuka-Cola
- 结论：一词多译
- 命中条目数：137（含无连字符写法 `Nuka Cola` 4 条）
- 写法：核子可乐×136；可乐×1
- 证据：`CurieDialog_Nuka Cola_01` | `drinking Nuka-Cola` | `饮用核子可乐`；`Encounter_Random_Message78` | `an old Nuka-Cola factory` | `一个旧核子可乐工厂`；`QuestLoc_OneGhoulCustomer_Conversation_1_Team_3` | `hang on to that Nuka-Cola Quantum` | `我该拿着那些可乐`
- 建议：统一为「核子可乐」；136/137 已统一，仅 1 条对话口语省略为「可乐」；线索中的「核可乐」全库 0 条，已无残留。

### Nuka-Cola Quantum
- 结论：一词多译
- 命中条目数：78（含无连字符写法 `Nuka Cola Quantum` 4 条）
- 写法：量子核子可乐×77；可乐×1
- 证据：`Generic_NukaColaQuantum` | `NUKA-COLA QUANTUM` | `量子核子可乐`；`Help_Page31_Title` | `NUKA-COLA QUANTUM` | `量子核子可乐`；`QuestLoc_OneGhoulCustomer_Conversation_1_Team_3` | `that Nuka-Cola Quantum` | `那些可乐`
- 建议：统一为「量子核子可乐」；77/78 已统一，剩余 1 条与 Nuka-Cola 是同一条对话，一并回改。

### Bottle Cap
- 结论：一致
- 命中条目数：11（`Bottle Cap`/`Bottle Caps`/`bottlecaps`）
- 写法：瓶盖×11
- 证据：`QuestLoc_MondayNightBrawl_Conversation_1_Team_3` | `we'd have ZERO CAPS` | `那我们估计只能得零个瓶盖`；`Encounter_Random_Message140` | `Bottle Caps accepted as currency everywhere` | `瓶盖成了通用的货币`；`QuestLoc_DiplomaticMission_Conversation_1_Team_1` | `Precious, precious bottlecaps` | `宝贝又珍贵的瓶盖`
- 建议：统一为「瓶盖」；11/11 唯一，与《辐射4》官中一致，无「盖子」等其他写法。

### Caps
- 结论：一词多译
- 命中条目数：131
- 写法：瓶盖×128；钱×1；瓶改×1；漏译×1
- 证据：`Help_Page13_Title` | `CAPS` | `瓶盖`；`QuestLoc_TheDeBuggers_Conversation_2_NPCEnd_2` | `some people will pay Caps to play games` | `有些人会花钱玩游戏`；`QuestLoc_DogGone_QuestLongDescription` | `BRING GUNZ, CAPS` | `记住必许带上枪，瓶改和次的`
- 建议：统一为「瓶盖」；128/131 已统一，「钱」1 条为意译漏失应回改，「瓶改」1 条是配合原文满篇错字字条的刻意错字（建议保留），另 1 条 `worth your weight in caps` 整句漏译。

### Lunchbox
- 结论：一致
- 命中条目数：49（含 `Lunch Box`/`Lunchboxes` 变体）
- 写法：午餐盒×49
- 证据：`Generic_Lunchbox` | `LUNCHBOX` | `午餐盒`；`LunchBox_ContentTitle` | `EACH LUNCHBOX CONTAINS:` | `每个午餐盒包括：`；`Help_Page16_Title` | `LUNCHBOXES` | `午餐盒`
- 建议：统一为「午餐盒」；49/49 唯一，无「饭盒/便当盒」等写法。

### Giddyup Buttercup
- 结论：一词多译
- 命中条目数：7
- 写法：骑乘小马×6；玩具马×1
- 证据：`Junk_Name_GiddyupButtercup` | `Giddyup Buttercup` | `玩具马`；`QuestLoc_MyMetalPony_QuestObjective_1` | `Find a Giddyup Buttercup.` | `寻找骑乘小马。`；`MrHandyDialog_Wasteland_69` | `A Giddyup Buttercup. Such an elegant steed.` | `一匹“骑乘小马”，真是优雅的坐骑。`
- 建议：统一为「骑乘小马」；6/7 为库内主体写法且沿用了官译口径，`Junk_Name_GiddyupButtercup` 的「玩具马」属描述性泛化，建议回改。

### Teddy Bear
- 结论：一致
- 命中条目数：5
- 写法：泰迪熊×5
- 证据：`Junk_Name_TeddyBear` | `Teddy Bear` | `泰迪熊`；`QuestLoc_MonsterUndertheBed_QuestShortDescription` | `teddy bear-stealing monster` | `偷泰迪熊的怪兽`；`QuestLoc_S2_QL2_Q3_Req_Question2_Answer1` | `Here's a teddy bear.` | `给，泰迪熊一只`
- 建议：统一为「泰迪熊」；5/5 唯一。

## 附：已知线索复核（越出本片 13 名，仅给证据）

- **Vault-Tec**：命中 106 条 → 「避难所科技」×97、「避难所科技公司」×6、EN 有而中文未落译名 ×3。→ **一词多译确认**：`AlienDrone_campaign_Text` | `Vault-Tec is thankful for all the Overseers` | `避难所科技公司感谢所有监督者` 对比 `Message_Intro_01` | `Vault-Tec has selected you` | `避难所科技已将您选作`。建议保留「避难所科技」，改掉「避难所科技公司」(6)。
- **Ultracite**：命中 70 条 → 「辐射极琉矿」×70，中文「超铀」全库 0 条。→ **库内一致，线索不成立**：本库用的是「辐射极琉矿（矿场/武器工坊/武器/矿石）」这一整套，如 `Junk_Name_Ultracite` | `Ultracite` | `辐射极琉矿`、`Room_UltraciteMining` | `ULTRACITE MINE` | `辐射极琉矿矿场`。非错误，无需改动；若上游曾要求「超铀」，则是来源口径变更而非本库不一致。
- **核可乐 / 核子可乐**：中文「核可乐」全库 0 条、「核子可乐」136 条 + 「量子核子可乐」77 条。→ **已统一，无残留**（本片仅剩「可乐」1 条口语省略）。

## 本片确认的一词多译清单
Stimpak -> 保留 治疗针，改掉 治疗用品(3)
RadAway -> 保留 消辐宁，改掉 治疗用品(3)
Nuka-Cola -> 保留 核子可乐，改掉 可乐(1)
Nuka-Cola Quantum -> 保留 量子核子可乐，改掉 可乐(1)
Caps -> 保留 瓶盖，改掉 钱(1)
Giddyup Buttercup -> 保留 骑乘小马，改掉 玩具马(1)
