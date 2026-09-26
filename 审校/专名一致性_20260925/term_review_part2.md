# 专名一致性审校 · 第 2 片：阵营 / 组织 / 机器人

数据：`data/en_zh_pairs.tsv`（14064 条）；工具：`审校/专名一致性_20260925/show_term.py`。
「命中条目数」= 工具输出值（专名按单词边界匹配，不含复数形态；括号内为含复数形态的补充统计）。
基准优先级：①《辐射4》/《辐射76》官方中文；②库主体来源（盛大代理安卓版《辐射避难所》官中）；③库内多数写法。
说明：`Mr. Handy` 与 `Mister Handy` 为同一机器人的两种英文写法，已合并统计；`Sentry Bot` 精确拼写命中 0 条，改用 `Sentry Bots` / `Sentry` 补查（见该条）。

### Brotherhood of Steel
- 结论：一致
- 命中条目数：40
- 写法：钢铁兄弟会×40（唯一）
- 证据：`Outfit_Description_BOSUniform` | The official garb of the Brotherhood of Steel. | 钢铁兄弟会的正式服装。
- 证据：`QuestLoc_ClearingAPath_QuestObjective_1` | Clear a path for the Brotherhood of Steel squad at the factory. | 为工厂里的钢铁兄弟会小队清空道路。
- 证据：`QuestLoc_GameShowGauntletA_Conversation_3_Team_1` | Brotherhood of Steel. | 钢铁兄弟会。
- 建议：统一为「钢铁兄弟会」；全库 40/40 唯一，无「钢铁会/兄弟会骑士团」等异写，保持现状即可。

### Enclave
- 结论：一致
- 命中条目数：111
- 写法：英克雷×111（唯一）
- 证据：`Theme_Name_EnclaveCafeteria` | Enclave Cafeteria | 英克雷食堂
- 证据：`QuestLoc_ENC_QL1_LoveOfGold_4_QuestObjective1` | Deal with the Enclave Remnants' leader | 对付英克雷残部首领
- 证据：`Weapon_Name_EnclavePlasmaRifle` | Enclave Plasma Rifle | 英克雷等离子步枪
- 建议：统一为「英克雷」；111/111 唯一，且无「飞地」（已核 0 条）等直译异写，保持现状即可。

### Raiders
- 结论：一致
- 命中条目数：185（含单数 Raider 共 312）
- 写法：掠夺者×185（唯一；含单数 312 条亦全部为「掠夺者」）
- 证据：`QuestLoc_PowertothePeople_QuestShortDescription` | Rescue Overseer Mogabe from Rubarb's Raiders. | 从鲁巴布的掠夺者手中救出监督者莫加比。
- 证据：`QuestLoc_JackAintBack_QuestLongDescription` | The Overseer's son got married to a Raider, but she sold him to Slavers! | 监督者的儿子和一个掠夺者结婚了，但她把他卖给了奴隶贩子！
- 证据：`QuestLoc_ASpecialBrand_QuestLongDescription` | Last night, we ended up partying with Raiders at an old Warehouse. | 昨晚，我们在旧仓库和掠夺者们一起开了个派对。
- 建议：统一为「掠夺者」；312 条单复数文本全含「掠夺者」，无「劫掠者/土匪/匪帮」异写（已核 0 条），保持现状即可。

### Minutemen
- 结论：一致
- 命中条目数：14（含单数 Minuteman 共 20）
- 写法：义勇军×14（唯一；单数 Minuteman 6 条中 5 条作「义勇军民兵…」）
- 证据：`Theme_ShortName_Minutemen` | Minutemen | 义勇军
- 证据：`QuestLoc_INS_QL1_MajorPlayers_1_QuestObjective2` | Rescue the Minutemen Commander | 营救义勇军指挥官
- 证据：`Tutorial_Tip_86` | You can craft Minutemen and Brotherhood of Steel Themes in the Theme Workshop. | 您可以在主题工坊中打造义勇军和钢铁兄弟会的主题。
- 建议：统一为「义勇军」；14/14 唯一且无「民兵」「义勇兵」竞争写法，单数条「义勇军民兵制服」式并称属冗余但非异名，可选精简。

### Church of the Children of Atom
- 结论：存疑
- 命中条目数：2
- 写法：原子之子的教会×1；未译略去×1
- 证据：`QuestLoc_SavingDaylight_QuestLongDescription` | We need to stop Confessor Alvarado and the Church of the Children of Atom before they detonate their 20-megaton nuclear device | 我们需要赶在神父阿尔瓦拉多和原子之子的教会引爆那枚2000万吨级的核装置之前阻止他们
- 证据：`QuestLoc_SpringForwardFallBack_QuestLongDescription` | Our investigation has indicated that a local chapter of the Church of the Children of Atom was responsible for the recent toxic spraying attacks. | 我们必须去找他们的领袖忏悔者阿尔瓦拉多，叫他停止这些攻击，否则后果自负。（该组织名未译出）
- 证据：`QuestLoc_GameShowGauntletG_Conversation_4_Team_2` | Children of Atom. | 原子之子。
- 建议：统一为「原子之子的教会」；有效样本仅 1 条（另一条整句译写略去组织名），无竞争写法，与库内「原子之子」（Children of Atom 14 条中 13 条）一致，属证据不足而非多译。

### Overseer
- 结论：存疑
- 命中条目数：189（含复数 Overseers 共 198）
- 写法：监督者×187；首领×1；未译略去×1
- 证据：`Overseer` | Overseer | 监督者
- 证据：`QuestLoc_ExtremePrejudice_QuestShortDescription` | Take out a hostile Vault Overseer. | 拿下一个敌对避难所的首领。
- 证据：`QuestLoc_DeathRevealed_QuestLongDescription` | In Vault 672, we met Dwellers from Vault 144 who are familiar with Death… their Overseer contacted us | 我们遇到了来自144号避难所、熟悉“死亡”的居民……（未保留「监督者」）
- 建议：统一为「监督者」；187/189（99%）已统一为「监督者」，1 条短描述泛化为「首领」（同一任务长描述仍作「监督者」）、1 条整句译写略去，属语境改写而非独立译名，故记存疑可回改第一条。

### Mr. Handy / Mister Handy
- 结论：一致
- 命中条目数：34（Mr. Handy）+ 17（Mister Handy）= 51
- 写法：巧手先生×50（其中 `QuestLoc_SignalFailure_Conversation_1_NPCStart_2` 加引号作「‘巧手’先生」）；保留英文未译×1
- 证据：`Mr_Handy_Name` | Mr. Handy | 巧手先生
- 证据：`MrHandyDialog_Generic_08` | I am a Mister Handy model robot. The pride of General Atomics International! | 我是巧手先生型机器人，通用原子国际的骄傲！
- 证据：`Shop_SeasonPass_NewVegasB_Premium_Description` | Victor (Mr. Handy equivalent character) | 维克托（Mr. Handy同等角色）
- 建议：统一为「巧手先生」；两种英文写法合并后 50/51 为「巧手先生」（含 4 条复数 Mr. Handys 亦同），唯一例外是保留英文的译注式写法，属漏译应回改。

### Miss Nanny
- 结论：一致
- 命中条目数：2
- 写法：巧手小姐×2（唯一，均作「居里巧手小姐」）
- 证据：`Shop_SeasonPass_InstitutePremium_Blurb` | Exclusive CURIE MISS NANNY and NICK VALENTINE | 专属居里巧手小姐和尼克·瓦伦坦
- 证据：`Shop_SeasonPass_Institute_Premium_Description` | new Curie Miss Nanny | 全新居里巧手小姐
- 建议：统一为「巧手小姐」；2 条均作「居里巧手小姐」，与库内「巧手先生」（Mr. Handy）命名成对，无「保姆小姐/南尼小姐」异写（已核 0 条），但样本仅 2 条，后续新增文本需按此对齐。

### Sentry Bot
- 结论：存疑
- 命中条目数：0（精确拼写）；改用 `Sentry Bots` / `Sentry` 命中 1
- 写法：铁卫兵×1（唯一）
- 证据：`Weapon_Description_HuntingRifle_ArmorPiercing` | Most people don't hunt Sentry Bots. You're not most people. | 大多数人不会猎捕铁卫兵。但你不是大多数人。
- 建议：统一为「铁卫兵」；精确拼写 `Sentry Bot` 全库 0 条，仅复数 `Sentry Bots` 1 条作「铁卫兵」（与《辐射4》官中一致），无「哨兵/哨戒机器人」异写（已核 0 条），因样本过少记存疑。

### Protectron
- 结论：一致
- 命中条目数：6（含复数 Protectrons 共 9）
- 写法：保护者×4；保护者机器人×2（命名条目 `Protectron_Name` 与 `VictorDialog_Wasteland_42`，即同词加类别后缀）
- 证据：`Protectron_Name` | Protectron | 保护者机器人
- 证据：`Encounter_Progression_Repeatable_JunkLocation9` | If I can fix a Protectron's laser arm, I could blast it open. | 要是能修好保护者的激光手臂，就能把门轰开。
- 证据：`VictorDialog_Wasteland_42` | Look at this poor Protectron all in pieces. | 瞧这可怜的保护者机器人，零件散了一地。
- 建议：统一为「保护者」；词根 9/9 全为「保护者」，命名条目加「机器人」后缀属同词变体而非异名（与「突袭者头部」体例相同），如需严格对齐可把命名条目改为「保护者」。

### Assaultron
- 结论：一致
- 命中条目数：4
- 写法：突袭者×4（唯一，均作「突袭者头部」）
- 证据：`Weapon_Name_AssaultronHead` | Assaultron Head | 突袭者头部
- 证据：`Weapon_Name_AssaultronHead_Enhanced` | Enhanced Assaultron Head | 强化的突袭者头部
- 证据：`Weapon_Name_AssaultronHead_Rusty` | Rusty Assaultron Head | 生锈的突袭者头部
- 建议：统一为「突袭者」；4/4 唯一，全库仅出现在「Assaultron Head」武器名中，无「突击者/突袭机器人」异写（已核 0 条），保持现状即可。

## 本片确认的一词多译清单
（本片 12 个专名未发现确认的一词多译项；`Overseer` 的「首领」1 条、`Church of the Children of Atom` 的 1 条漏译、`Sentry Bot` 的样本不足均已按「存疑」计入正文，不计入本清单。）
