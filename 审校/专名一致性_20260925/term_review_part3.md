# 专名一致性审校 · 第 3 片：人物 / NPC

数据源：`data/en_zh_pairs.tsv`（14064 条）
工具：`审校/专名一致性_20260925/show_term.py`
说明：中文候选 n-gram 含同句噪声，下表仅采信逐条明细；「命中条目数」取 `show_term.py` 的英文专名词边界匹配数。
人名规范：名与姓之间用间隔号「·」；带·/不带·、全名/简称混用在此逐条记录。

### Mr. House
- 结论：一致
- 命中条目数：28
- 写法：豪斯先生×28（唯一）
- 证据：
  - `Outfit_Name_MrHousesSuit` | EN: "Mr. House's Suit" | ZH: 「豪斯先生的西装」
  - `QuestLoc_HouseWarming_1_QuestShortDesc` | EN: "Deliver Mr. House's party invitation to Maximus." | ZH: 「把豪斯先生的派对请柬送给马克西姆斯。」
  - `QuestLoc_HouseWarming_4_QuestObjective3` | EN: "Check in with Mr. House" | ZH: 「向豪斯先生报告」
- 建议：统一为「豪斯先生」；全库 28 条无第二种写法，另 4 条赛季名「豪斯常胜」属同一音译（House），无需改动。

### Preston Garvey
- 结论：一致
- 命中条目数：10
- 写法：普雷斯顿·加维×9；普雷斯顿（省略姓氏的简称）×1
- 证据：
  - `QuestLoc_ASettlerNeedsYourHelp_Conversation_1_NPCStart_2` | EN: "Preston Garvey, Commonwealth Minutemen." | ZH: 「我叫普雷斯顿·加维，联邦义勇军民兵组织的成员。」
  - `QuestLoc_GameShowGauntletE_Conversation_1_Team_2` | EN: "Preston Garvey." | ZH: 「普雷斯顿·加维。」
  - `QuestLoc_FollowingHisFirstSteps_QuestShortDescription` | EN: "Search for clues to Preston Garvey's location." | ZH: 「寻找有关普雷斯顿下落的相关线索。」
- 建议：统一为「普雷斯顿·加维」；仅 1 条短描述用简称「普雷斯顿」，建议补全为「普雷斯顿·加维」（另 5 条 EN 仅作 "Preston" 的条目用简称属正常）。

### Confessor Alvarado
- 结论：一词多译
- 命中条目数：9
- 写法：神父阿尔瓦拉多×6；忏悔者阿尔瓦拉多×2；未译出人名×1
- 证据：
  - `QuestLoc_ESterisComing_QuestLongDescription` | EN: "Confessor Alvarado has agreed to put a stop to radioactive spraying…" | ZH: 「忏悔者阿尔瓦拉多已同意停止喷洒辐射物质……」
  - `QuestLoc_SavingDaylight_QuestObjective_1` | EN: "Stop Confessor Alvarado's Plans." | ZH: 「停止神父阿尔瓦拉多的计划。」
  - `QuestLoc_SpringForwardFallBack_QuestObjective_1` | EN: "Talk to Confessor Alvarado." | ZH: 「和神父阿尔瓦拉多交谈。」
- 补充证据：`QuestLoc_SpringForwardFallBack_QuestLongDescription` 亦作「忏悔者阿尔瓦拉多」；`QuestLoc_SavingDaylight_Conversation_1_NPCEnd_2` 单独出现称谓时译作「神父」；`QuestLoc_TheSixthSun_QuestLongDescription` 整句漏译人名。
- 建议：统一为「神父阿尔瓦拉多」；称谓已确认两译并存（复核线索成立），且库内孤立称谓处亦用「神父」，取多数写法。

### Paula Plumbkin
- 结论：一致
- 命中条目数：35
- 写法：宝拉·普朗布金×32；宝拉（省略姓氏的简称）×3
- 证据：
  - `QuestLoc_AThirstforAdventure_Conversation_1_Team_1` | EN: "Have you seen Paula Plumbkin?" | ZH: 「你有见过宝拉·普朗布金吗？」
  - `QuestLoc_Overrun_QuestObjective_1` | EN: "Search Vault 909 for Paula Plumbkin." | ZH: 「前往909号避难所寻找宝拉·普朗布金。」
  - `QuestLoc_PaulasinaPickle_QuestLongDescription` | EN: "The Feral Ghouls … dragged Paula Plumbkin to an abandoned building." | ZH: 「旧核子可乐工厂里的狂尸鬼把宝拉拖到了一处废弃建筑里。」
- 建议：统一为「宝拉·普朗布金」；全名 32 条全部带间隔号，无·写法混用，3 条为对话内自然简称，可不改。

### Rackie Jobinson
- 结论：一致
- 命中条目数：98
- 写法：罗基·杰宾森×93；省略人名（仅「棒球衫」）×5；另全库 3 条英文作 "Jobinson's Jersey"，其中 2 条为「罗基·杰宾森」、1 条为「杰宾森」（缺名字）
- 证据：
  - `Outfit_Name_JobinsonsJersey` | EN: "Rackie Jobinson's Jersey" | ZH: 「罗基·杰宾森的棒球衫」
  - `QuestLoc_HerestoYouRackieJobinson_QuestName` | EN: "Here's to You, Rackie Jobinson" | ZH: 「为了你，罗基·杰宾森。」
  - `QuestLoc_TheSearchforJobinsonsJersey_QuestlineName` | EN: "The Search for Jobinson's Jersey!" | ZH: 「寻找杰宾森的棒球衫！」
- 建议：统一为「罗基·杰宾森」；音译全库唯一且均带间隔号，仅任务线名 `QuestLoc_TheSearchforJobinsonsJersey_QuestlineName` 漏掉「罗基·」，建议补全（5 条省略人名属上下文指代，可不改）。

### Maximus
- 结论：一致
- 命中条目数：10
- 写法：马克西姆斯×10（唯一）
- 证据：
  - `QuestLoc_OBrother_Conversation04_NPC02` | EN: "Name's Maximus." | ZH: 「我叫马克西姆斯。」
  - `QuestLoc_HouseWarming_1_Question5` | EN: "I'm Brother Maximus." | ZH: 「我是马克西姆斯兄弟。」
  - `Shop_SeasonPass_NewVegasA_Premium_Description` | EN: "Maximus' Jacket" | ZH: 「马克西姆斯夹克」
- 建议：统一为「马克西姆斯」；单名无需间隔号，全库无「马克西姆」等异写（已核 0 条）。

### Lucy
- 结论：一致
- 命中条目数：5
- 写法：露西×5（唯一）
- 证据：
  - `QuestLoc_PierIntoFuture_Conversation02_NPC01` | EN: "My name's Lucy!" | ZH: 「我叫露西！」
  - `Outfit_Name_LucysVaultSuit` | EN: "Lucy's Vault Suit" | ZH: 「露西的避难所制服」
  - `Outfit_Name_LucysYellowDress` | EN: "Lucy's Yellow Dress" | ZH: 「露西的黄裙子」
- 建议：统一为「露西」；单名无需间隔号，无「露茜/露希」异写（已核 0 条）。

### The Ghoul
- 结论：一致
- 命中条目数：9
- 写法：尸鬼×9（唯一）
- 证据：
  - `Outfit_Name_RottedDuster` | EN: "The Ghoul's Coat" | ZH: 「尸鬼大衣」
  - `Encounet_Progression_NPC3` | EN: "The Ghoul is ugly, but not feral." | ZH: 「这尸鬼长得丑，但还没狂化。」
  - `QuestLoc_GhoulInBlack_Answer01_NPC01` | EN: "They're after the Ghoul!" | ZH: 「他们要找那个尸鬼！」
- 建议：统一为「尸鬼」；角色名与通名（Ghoul/狂尸鬼）同形，全库无第二种角色名译法，暂无需改动。

### Hank
- 结论：一致
- 命中条目数：1
- 写法：汉克×1（唯一）
- 证据：
  - `Outfit_Name_HanksPowerArmor` | EN: "Hank's Power Armor" | ZH: 「汉克的动力装甲」
- 建议：统一为「汉克」；全库仅 1 条且无异写（已核「汉克斯/汉柯」为 0 条），样本偏少，如后续版本新增文本需复查。

### Norm
- 结论：存疑
- 命中条目数：0
- 写法：无（0 命中，无法判定）
- 证据：无（`Norm` / `Norman` / `Norma` 英文匹配与「诺姆」「诺曼」中文串全库均 0 条）
- 建议：暂不统一；本次导出文本未收录该人物，需改用其它拼写/新增资源复核后再定译名。

### Vault Boy
- 结论：一致
- 命中条目数：1
- 写法：避难所小子×1（唯一）
- 证据：
  - `Tutorial_Header` | EN: "Vault Boy!" | ZH: 「避难所小子！」
- 建议：统一为「避难所小子」；已核 `VaultBoy` / `Vault-Boy` / 「避难所男孩」「避难所少年」均 0 条，「哔哔小子」属 Pip-Boy，另一专名不冲突。

### Three Dog
- 结论：一致
- 命中条目数：22
- 写法：三狗×22（唯一）
- 证据：
  - `QuestLoc_DogsofWar_QuestObjective_1` | EN: "Talk to Three Dog." | ZH: 「和三狗交谈。」
  - `QuestLoc_RunThreeDogRun_QuestName` | EN: "Run, Three Dog, Run!" | ZH: 「跑，三狗，快跑！」
  - `Outfit_Name_Threedog` | EN: "Three Dog's Outfit" | ZH: 「三狗服装」
- 建议：统一为「三狗」；全库无「三犬/三条狗」等异写（已核 0 条）。

## 本片确认的一词多译清单
Confessor Alvarado -> 保留 神父阿尔瓦拉多，改掉 忏悔者阿尔瓦拉多(2)
