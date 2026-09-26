# 专名一致性审校 · 第 1 片：生物 / 敌人

数据：`data/en_zh_pairs.tsv`（14064 条）；工具：`审校/专名一致性_20260925/show_term.py`。
「命中条目数」= 工具输出值（专名按单词边界、不含复数形态；括号内为含复数形态的补充统计）。
基准优先级：①《辐射4》/《辐射76》官方中文；②库主体来源（盛大代理安卓版《辐射避难所》官中）；③库内多数写法。

### Deathclaw
- 结论：一致
- 命中条目数：109（含复数 158）
- 写法：死爪×109（唯一）
- 证据：`Deathclaw_Name` | Deathclaw | 死爪
- 证据：`Emergency_Deathclaw` | DEATHCLAW ATTACK | 死爪袭击
- 证据：`CurieDialog_Wasteland_3` | The offensive capabilities of this Deathclaw are quite advanced. | 这只死爪的攻击能力相当先进。
- 建议：统一为「死爪」；库内 109 条（含复数 158 条）全部为「死爪」，零条「死亡爪」，属来源差异·非错误（安卓官中=死爪，FO4 官中=死亡爪，本库主体为安卓版），保持现状即可。

### Alpha Deathclaw
- 结论：一词多译
- 命中条目数：23（含复数 27）
- 写法：领头死爪×19；阿尔法死爪×2；首领死爪×1；死爪头领×1
- 证据：`QuestLoc_12PointBuck_QuestObjective_1` | Kill the Alpha Deathclaw. | 杀死领头死爪。
- 证据：`QuestLoc_NVB_QL3_Stripper_4_QuestObjective1` | Defeat the Alpha Deathclaw | 击败阿尔法死爪
- 证据：`QuestLoc_HighSteaks_QuestObjective_1` | Kill the Alpha Deathclaw and harvest its meat. | 杀死死爪头领，取得它的肉。
- 建议：统一为「领头死爪」；领头死爪 19/23 为库内多数且为安卓官中写法，阿尔法/首领/头领 4 条为直译或近义改写（阿尔法系 FO4 风格前缀，但 FO4 全称作「阿尔法死亡爪」，与本库「死爪」词根不合），建议回改。

### Radroach
- 结论：一词多译
- 命中条目数：44
- 写法：辐射蟑螂×42；辐射小强×1；蟑螂（女王）×1
- 证据：`Encounter_Message_Creature4` | a disgusting Radroach. | 一只令人讨厌的辐射蟑螂。
- 证据：`Objective_KillRadroaches` | Kill a Radroach | 消灭1只辐射小强
- 证据：`QuestLoc_RadroachRoundup_Conversation_2_NPCStart_4` | At any rate, have you killed the Radroach Queen yet? | 无论如何，你们杀死了蟑螂女王吗？
- 建议：统一为「辐射蟑螂」；「辐射小强」为口语异名（另有 `Objective_KillRadroaches_Plural` 亦作「辐射小强」，共 2 条），「蟑螂女王」漏译前缀（同库 `QuestLoc_RadroachRoundup_Conversation_1_Team_3` 作「辐射蟑螂女王」，应回改）。

### Radscorpion
- 结论：存疑
- 命中条目数：52（含复数 81）
- 写法：辐射蝎×51；蝎子×1
- 证据：`Emergency_Radscorpions` | RADSCORPION ATTACK | 辐射蝎袭击
- 证据：`QuestLoc_PetPeeve_Conversation_1_NPCStart_1` | First those Raiders kill my Radscorpion pets, now you've killed Glowy! | 先是掠夺者们杀死了我的宠物蝎子，现在你又杀死了“绿绿”！
- 建议：统一为「辐射蝎」；仅 1 条对话把 Radscorpion 泛化省略为「蝎子」（同句为宠物口语语境，不构成独立译名），主体 51/52 一致，故不计入一词多译，但若要严格统一可回改该条。

### Mirelurk
- 结论：一致
- 命中条目数：12（含复数 14）
- 写法：泥沼蟹×12（唯一；子类统一作 泥沼蟹猎杀者／泥沼蟹之王）
- 证据：`Encounter_Message_Creature15` | a barnacle-encrusted Mirelurk. | 一只结满藤壶的泥沼蟹。
- 证据：`Encounet_Progression_Creature35` | I hope I can handle this Mirelurk Hunter! It's coming at me fast! | 希望我能搞定这个泥沼蟹猎杀者，它正朝我飞奔过来！
- 证据：`QuestLoc_GameShowGauntletB_Conversation_3_Team_3` | Mirelurk King. | 泥沼蟹之王。
- 建议：统一为「泥沼蟹」；全库写法唯一，与 FO4 官中一致，无需改动。

### Bloatfly
- 结论：一致
- 命中条目数：5
- 写法：巨大苍蝇×5（唯一）
- 证据：`Encounter_Message_Creature3` | a Bloatfly, buzzing dangerously close. | 一只巨大苍蝇，危险地嗡嗡叫着靠近。
- 证据：`Encounter_Victory_Creature3` | I killed the Bloatfly and it exploded into a thousand pieces. Disgusting. | 我杀死了巨大苍蝇，炸成了一堆碎块。好恶心。
- 建议：统一为「巨大苍蝇」；5/5 唯一且与来源一致，无需改动。

### Bloodbug
- 结论：存疑
- 命中条目数：0
- 写法：唯一（无）
- 证据：`-` | 尝试拼写 Bloodbug / Blood Bug / Blood Fly 均为 0 命中；全库无「吸血虫」「吸血」字样，该词条未进入本库
- 建议：暂按《辐射4》官中定为「吸血虫」；本库 0 命中，无库内证据可判（若后续库版本或 DLC 文本引入该生物，直接沿用「吸血虫」）。

### Stingwing
- 结论：存疑
- 命中条目数：0
- 写法：唯一（无）
- 证据：`-` | 尝试拼写 Stingwing / Sting Wing / StingWing 均为 0 命中；全库无「刺翼」「翼虫」字样，该词条未进入本库
- 建议：暂定为「刺翼虫」；本库 0 命中，无库内证据可判（中文资料亦见简作「刺翼」，正式译名建议以《辐射76》官中为准）。

### Feral Ghoul
- 结论：一词多译
- 命中条目数：28（含复数 59）
- 写法：狂尸鬼×25；尸鬼×3（其中 2 条为 Feral Ghoul attack 目标文案，1 条为 Non-Feral 语境属正确）
- 证据：`Encounet_Progression_Creature11` | This Feral Ghoul is out of its mind! It's lunging at me! | 这只狂尸鬼一定是疯了！它正朝我扑过来！
- 证据：`Objective_SurviveGhoulNoCasualties` | Survive {0} Feral Ghoul attack with no casualties | 在没有人员伤亡的情况下撑过了{0}次尸鬼攻击
- 证据：`QuestLoc_RadiationLeak_Conversation_1_NPCStart_1` | Wait! We're not Feral! We're friendly! | 等等！我们不是狂尸鬼！我们很友好！
- 建议：统一为「狂尸鬼」；主体（含 狂尸鬼漫游者×5、狂尸鬼掠夺者×5）均为「狂尸鬼」，`Objective_SurviveGhoulNoCasualties(_Plural)` 两条「尸鬼攻击」与 `Emergency_Ghouls`「狂尸鬼袭击」自相矛盾，应回改；`QuestLoc_LittleRedRadiumHood_QuestLongDescription` 的 Non-Feral Ghoul=「温顺的尸鬼」属合理区分，保留。

### Ghoul
- 结论：一致
- 命中条目数：73（含复数 166）
- 写法：尸鬼×73（唯一；不含 feral 的 42 条单独出现全部为「尸鬼」）
- 证据：`CurieDialog_Wasteland_24` | Those Ghouls were so aggressive! Are they what people call “feral”? | 那些尸鬼攻击性太强了！它们就是人们所说的“狂尸鬼”吗？
- 证据：`QuestLoc_HouseWarming_3_Question4` | It's a Ghoul party, alright… but why are they attacking us? Are they feral? | 这确实是场尸鬼派对，没错……但他们为什么要攻击我们？
- 建议：统一为「尸鬼」；单独出现无一例外为「尸鬼」，与 Feral Ghoul=「狂尸鬼」构成合理区分（另注：EN「zombie」6 条译为「僵尸」，不属本专名）。

### Super Mutant
- 结论：一词多译
- 命中条目数：30（含复数 39）
- 写法：超级变种人×21；巨兽×8（Super Mutant Behemoth 子类，属合理区分）；变种人×1
- 证据：`Encounter_Message_Creature24` | a Super Mutant. | 一个超级变种人。
- 证据：`Weapon_Description_AlienDisintegrator_Rusty` | This hunk of junk can still bissect a super mutant. | 这堆破烂仍然可以将变种人拦腰斩断。
- 证据：`Encounter_Message_Creature27` | a gigantic Super Mutant Behemoth. | 一个硕大的巨兽。
- 建议：统一为「超级变种人」；21 条作「超级变种人」（子类大师/霸王），仅 1 条作「变种人」，属漏译前缀，应回改；`Behemoth` 一律作「巨兽」（FO4 官中同）不计入多译。

### Brahmin
- 结论：一致
- 命中条目数：20
- 写法：双头牛×20（唯一）
- 证据：`CurieDialog_Wasteland_43` | I just met a group of traders with an enormous Brahmin. It is a wonderful creature! | 我刚遇到一群商人，带着一头巨大的双头牛。真是一只奇妙的生物！
- 证据：`Encounter_Message_Repeatable_JunkLocation11` | a Caravan Merchant chasing after a panicked Brahmin. | 一名大篷车商人正在追逐一头受惊的双头牛。
- 建议：统一为「双头牛」；全库唯一，与 FO4 官中一致，无需改动。

### Mole Rat
- 结论：一致
- 命中条目数：51（含复数 87）
- 写法：鼹鼠×46（唯一）；鼹鼠人×5（均为 EN「Mole Rat Man」人名，非生物）
- 证据：`CurieDialog_Wasteland_20` | A Mole rat. What a fascinating specimen! | 一只鼹鼠。多么迷人的样本！
- 证据：`Emergency_Molerat` | MOLE RAT ATTACK | 鼹鼠袭击
- 证据：`QuestLoc_TheMoleRatMan_QuestName` | The Mole Rat Man | 鼹鼠人
- 建议：统一为「鼹鼠」；生物名 46/46 唯一，「鼹鼠人」为角色名「Mole Rat Man」且库内统一（5 条），属合理区分，保留。

## 本片确认的一词多译清单
Alpha Deathclaw -> 保留 领头死爪，改掉 阿尔法死爪(2)/首领死爪(1)/死爪头领(1)
Radroach -> 保留 辐射蟑螂，改掉 辐射小强(2)/蟑螂女王(1)
Feral Ghoul -> 保留 狂尸鬼，改掉 尸鬼(2)
Super Mutant -> 保留 超级变种人，改掉 变种人(1)
