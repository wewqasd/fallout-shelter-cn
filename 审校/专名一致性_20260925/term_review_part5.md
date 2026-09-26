# 专名一致性审校 · 第 5 片（系统/房间/机制）

数据：`data/en_zh_pairs.tsv`（14064 条）；工具：`审校/专名一致性_20260925/show_term.py`（只读）。
说明：命中数为全库 EN 侧匹配（含大小写/连字符/空格变体）的条目数；写法计数按条目计。基准优先级：①《辐射4》/《辐射76》官中；②本库主体来源（盛大代理安卓版官中）；③库内多数写法。本片 15 个专名均有命中（无 0 条项）。

### Vault-Tec
- 结论：一词多译
- 命中条目数：104（仅连字符写法 `Vault-Tec` 命中；`Vault Tec`/`VaultTec` 均 0 条）
- 写法：避难所科技×96；避难所科技公司×6；中文未落译名×2
- 证据：`VaultTecWindow_Title` | `VAULT-TEC` | `避难所科技公司`；`Tutorial_Tip_45` | `Vault-Tec. We'll be there!` | `避难所科技。我们会与你们同在！`；`QuestLoc_AlienBotQuest04_Conversation_3_NPCStart_2` | `Vault-Tec Personnel identified.` | `确认避难所科技公司人员身份。`
- 建议：统一为「避难所科技」；《辐射4/76》官中即为「避难所科技」，库内 96/104 已统一，「公司」后缀集中在赛季文案与 1 条单行标题，属多余增益。

### SPECIAL
- 结论：一致
- 命中条目数：54
- 写法：保留英文缩写 SPECIAL×27；写作 S.P.E.C.I.A.L.×1；意译为「属性」或省略×4；英文小写形容词 special 的常规译法（特殊/特别等）×22
- 证据：`Special_Title` | `SPECIAL` | `SPECIAL属性`；`Message_Tutorial_23` | `{TRAIN} your Dwellers to {INCREASE} their {SPECIAL} stats.` | `{训练}您的居民，{增加}他们的{S.P.E.C.I.A.L.}属性。`；`Help_Page02_Title` | `DWELLERS SPECIAL` | `居民属性`
- 建议：统一保留英文「SPECIAL」；属性缩写全库未译成中文，14 条「特殊」全部对应英文小写形容词 special（如 `A Special Brand`→`一个特殊的品牌`），与该缩写不混用，故不计多译。

### Legendary
- 结论：一词多译
- 命中条目数：51
- 写法：传奇×48（含「传奇级」14、「传奇级别」9）；传说级×1；形容词义意译（神奇/顶级秘密）×2
- 证据：`LunchBox_Content_Card2` | `Legendary Weapon (1.7%)` | `传奇武器 (1.7%)`；`Weapon_Name_Rifle_Legendary` | `Legendary Rifle` | `传说级步枪`；`Room_Upgrade_Not_Enough_Dwellers_LegendaryWeapons` | `craft Legendary Weapons` | `打造传奇武器`
- 建议：统一为「传奇」；《辐射4/76》官中作「传奇」，库内 48/49 已统一，仅 1 条武器名写作「传说级」；「传奇级/传奇级别」是同写法加缀，不计多译。

### Theme
- 结论：一致
- 命中条目数：53
- 写法：主题×51（其中「外观主题」6 条，对应 `Exterior Theme`）；句意省略/口语意译×2
- 证据：`Generic_Theme` | `THEME` | `主题`；`Theme_ShortName_Exterior` | `Exterior Theme` | `外观主题`；`Shop_SeasonPass_Description` | `a Vault Exterior THEME, a Weapon Workshop THEME` | `避难所外观主题、武器工坊主题`
- 建议：统一为「主题」；51/53 一致，未落译的 2 条分别是 UI 省略（`Notification_Crafting_Theme_End`）与口语比喻（`Speech_Conversation_NPC2_Topic11_Response2`），不构成专名多译。

### Pet
- 结论：一致
- 命中条目数：77
- 写法：宠物×58；宠物笼/宠物笼子×13（英文实为 `Pet Carrier`，属另一词条）；动词/习语义（抚摸、pet project）×6
- 证据：`Generic_Pet` | `PET` | `宠物`；`LunchBox_Content_Card2` | `Common Pet (2.3%)` | `普通宠物 (2.3%)`；`PetCarrier_ContentRedeemTitle2` | `Bundle of 5 Pet Carriers` | `5个宠物笼`
- 建议：统一为「宠物」；作宠物/动物名词的 58 条全库唯一（宠物箱/笼类属 `Pet Carrier`，另计）。

### Weight Room
- 结论：一致
- 命中条目数：4
- 写法：举重房×4
- 证据：`Room_Gym` | `WEIGHT ROOM` | `举重房`；`Room_Gym_Build` | `Build a WEIGHT ROOM?` | `建造一个举重房？`；`Tutorial_Tip_10` | `The Weight Room will allow you to train a Dweller's Strength.` | `举重房可以让您训练居民的力量（S）。`
- 建议：统一为「举重房」；4/4 唯一，线索中的「健身房」在本库对应的是 `FITNESS ROOM`（`Room_SuperRoom2`→`健身房`），并非 Weight Room 的第二译法。

### Athletics Room
- 结论：一词多译
- 命中条目数：4
- 写法：体操房×2；运动室×1；体操室×1
- 证据：`Room_Dojo` | `ATHLETICS ROOM` | `运动室`；`Room_Dojo_Build` | `Build an ATHLETICS ROOM?` | `建造一间体操房？`；`Tutorial_Tip_15` | `The Athletics Room will allow you to train a Dweller's Agility.` | `体操室可以让您训练居民的敏捷性（A）。`
- 建议：统一为「体操房」；同一房间的标题（运动室）与建造确认句（体操房）自相矛盾，教学提示又作「体操室」，是本片最硬的一处不一致。

### Armory
- 结论：一致
- 命中条目数：6
- 写法：军械库×6
- 证据：`Room_Armory` | `ARMORY` | `军械库`；`Tutorial_Tip_11` | `The Armory room will allow you to train a Dweller's Perception.` | `军械库可以让您训练居民的观察力（P）。`；`Weapon_Description_BOSAssaultRifle_Enhanced` | `Fresh out of the BOS armory` | `刚从兄弟会军械库出来`
- 建议：统一为「军械库」；6/6 唯一（含 2 条小写 armory 的普通名词用法），与《辐射4》官中一致。

### Classroom
- 结论：一致
- 命中条目数：4
- 写法：教室×4
- 证据：`Room_ClassRoom` | `CLASSROOM` | `教室`；`Room_ClassRoom_Build` | `Build a CLASSROOM?` | `建造一间教室？`；`Tutorial_Tip_14` | `The Classroom will allow you to train a Dweller's Intelligence.` | `教室可以让您训练一个居民的智力（I）。`
- 建议：统一为「教室」；4/4 唯一。

### Lounge
- 结论：一致
- 命中条目数：4
- 写法：会客室×4
- 证据：`Room_Bar` | `LOUNGE` | `会客室`；`Room_Bar_Build` | `Build a LOUNGE?` | `建造一个会客室？`；`Tutorial_Tip_13` | `The Lounge will allow you to train a Dweller's Charisma.` | `会客室可以让您训练一个居民的魅力（C）。`
- 建议：统一为「会客室」；4/4 唯一，未受英文 key `Room_Bar` 影响改用「酒吧」，与前几轮训练房命名口径一致。

### Game Room
- 结论：一致
- 命中条目数：4
- 写法：棋牌室×4
- 证据：`Room_Casino` | `GAME ROOM` | `棋牌室`；`Room_Casino_Build` | `Build a GAME ROOM?` | `建造一个棋牌室？`；`Tutorial_Tip_17` | `The Game Room will allow you to train a Dweller's Luck.` | `棋牌室可以让您训练一个居民的运气（L）。`
- 建议：统一为「棋牌室」；4/4 唯一。

### Weapon Workshop
- 结论：一致
- 命中条目数：9
- 写法：武器工坊×9
- 证据：`Room_WeaponFactory` | `WEAPON WORKSHOP` | `武器工坊`；`Room_WeaponFactory_Build` | `Build a WEAPON WORKSHOP?` | `建造武器工坊？`；`Notification_Crafting_Weapon_End` | `One of your Weapon Workshops has made a Weapon!` | `武器工坊制成了一件武器！`
- 建议：统一为「武器工坊」；9/9 唯一（含 `Ultracite Weapon Workshop`→`辐射极琉矿武器工坊`）；「武器车间/武器工厂」分别对应英文 `WEAPON FACTORY`/`WEAPON PLANT`，属三级房名的另一词条。

### Outfit Workshop
- 结论：一致
- 命中条目数：2
- 写法：装备工坊×2
- 证据：`Room_OutfitFactory` | `OUTFIT WORKSHOP` | `装备工坊`；`Room_OutfitFactory_Build` | `Build an OUTFIT WORKSHOP?` | `建造一个装备工坊？`
- 建议：统一为「装备工坊」；2/2 唯一，与 `Outfit Factory/Plant`→「装备车间/装备工厂」配套。

### Nuka-Cola Bottler
- 结论：一词多译
- 命中条目数：3
- 写法：核子可乐装瓶室×2；核子可乐装瓶厂×1
- 证据：`Room_NukaColaPlant` | `NUKA-COLA BOTTLER` | `核子可乐装瓶室`；`Room_NukaColaPlant_Build` | `Build a NUKA-COLA BOTTLER?` | `建造一个核子可乐装瓶室？`；`Shop_SeasonPass_NewVegasA_Blurb` | `NEW Nuka-Cola Bottler THEME` | `全新核子可乐装瓶厂主题`
- 建议：统一为「核子可乐装瓶室」；房间标题与建造句 2 条一致且为库内多数，赛季通行证文案的「装瓶厂」应跟随（英文 `NUKA-COLA PLANT`→「核子可乐工厂」是三级房名的另一词条）。

### Nuclear Reactor
- 结论：一致
- 命中条目数：2
- 写法：核电站×2
- 证据：`Room_Energy2` | `NUCLEAR REACTOR` | `核电站`；`Room_Energy2_Build` | `Build a NUCLEAR REACTOR?` | `建造核电站？`；`QuestLoc_PoweredUp_QuestObjective_1` | `Search the nuclear power plant for Paula Plumbkin.` | `前往核电站寻找宝拉·普朗布金。`
- 建议：统一为「核电站」；2/2 唯一，升级房名 `ADVANCED REACTOR`/`SUPER REACTOR`→「高级核电站/超级核电站」同口径，剧情文本 `nuclear power plant` 亦作「核电站」。

## 本片确认的一词多译清单
Vault-Tec -> 保留 避难所科技，改掉 避难所科技公司(6)
Legendary -> 保留 传奇，改掉 传说级(1)
Athletics Room -> 保留 体操房，改掉 运动室(1)、体操室(1)
Nuka-Cola Bottler -> 保留 核子可乐装瓶室，改掉 核子可乐装瓶厂(1)
