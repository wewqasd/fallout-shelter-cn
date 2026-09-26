# Lead 独立核查发现（不经分片代理，全部由 Lead 直接比对数据得出）

数据来源：`data/en_zh_pairs.tsv`（14064 条，key / EN / 中文）。
证据均为可直接 grep 的 key。

## 1. Outfit（装备类别名）— 一词多译，规模最大

| 写法 | 条数 |
|---|---|
| 装备 | 88 |
| 服装 | 25 |

同词直证（EN 完全相同或同模板）：

| key | EN | ZH |
|---|---|---|
| `Objective_CollectOutfit` | Collect 1 Outfit | 收集1件**装备** |
| `Objective_CraftOutfits` | Craft 1 Outfit | 打造1件**装备** |
| `Objective_Outfits` | Equip 1 Dweller with an Outfit | 给一个居民穿上**装备** |
| `Objective_CollectOutfitsOnQuests` | Collect an Outfit on a Quest | 在任务中收集1件**服装** |
| `Objective_CraftLegendaryOutfits` | Craft 1 Legendary Outfit | 打造1件传奇**服装** |
| `Inventory_Title_Outfits` | OUTFITS | **装备**（分类标题） |
| `Outfit_Name_PiperSpecial` | Piper's Outfit | 派普**服装** |
| `Notification_Crafting_Outfit_End` | One of your Outfit Workshops has made an Outfit! | **装备**工坊制成了一件**装备**！ |

说明：`装备` 同时还是 Gear/Equipment 的译名，但上表前 6 行 EN 都是 Outfit，属同一英文词的两种译法。
建议：物品类别统一为 **装备**（与 `Inventory_Title_Outfits`、任务目标一致），仅具体人名服装（`Outfit_Name_*`）可保留「服装」，或全部统一。

## 2. 其它类别词/系统词

| EN | 写法 A（条数） | 写法 B（条数） | 直证 key（B 侧） |
|---|---|---|---|
| Perception（SPECIAL 属性） | 观察力（17） | 感知（1） | `QuestLoc_ENC_QL2_Defective_3_Room5_Question_Line2`：`<Thanks to your PERCEPTION…>` → 「凭借你的**感知**」 |
| Luck（SPECIAL 属性） | 运气（Special_Luck、Stats_Average_Luck=居民平均运气） | 幸运值（1） | `Message_TutorialPopup_16_Body`：`high Luck SPECIAL` → 「**幸运值**（L）高的居民」 |
| Protectron | 保护者（5，对话） | 保护者机器人（4，含 `Protectron_Name`） | `Protectron_Name`：Protectron → 保护者机器人 |
| Mr. Handy | 巧手先生（56） | 巧手先生机器人（1） | `QuestLoc_CollectorsEdition_Conversation_1_Team_1`：`Mr. Handy robots` → 巧手先生机器人 |
| Diner（房间/店铺） | 餐厅（24） | 食堂（1） | `QuestLoc_GameShowGauntletH_Conversation_3_Team_2`：`Cambridge Campus Diner.` → 「剑桥校园**食堂**」 |
| Living Quarters | 宿舍（27） | 居住区（5） | `Theme_ShortName_LivingQuarters`：`Living Quarters Theme` → 「**居住区**主题」；`Shop_SeasonPass_NewVegasB_Blurb` |
| Decorations | 装饰品（7） | 装饰（1） | `Stats_Common_Decorations`：`Common Decorations` → 「普通**装饰**」（其余 `Stats_*_Decorations` 均作装饰品） |
| Boss | 首领（68） | 头目（2） | `QuestLoc_INS_QL1_MajorPlayers_1_CombatInit8`：`That's gotta be the boss.` → 「那肯定是个**头目**」 |
| Legendary（稀有度） | 传奇级（14） | 传说级（1） | `Weapon_Name_Rifle_Legendary`：`Legendary Rifle` → 「**传说级**步枪」 |
| Wasteland | 废土（385） | 荒地（1） | `QuestLoc_HumansLikeUs_QuestLongDescription`：`over the Wasteland` → 「不远的**荒地**上」 |
| Rarity 前缀 | 普通级/稀有级（`Stats_*`） | 普通/稀有（`Stats_Common_Decorations`=普通装饰、`Stats_Rare_*`=稀有级） | 同上 |

## 3. 已核查后**排除**的疑似项（避免误报）

| 疑似 | 结论 |
|---|---|
| 死亡爪 / 死爪 | 库内「死亡爪」0 条，「死爪」109 条 → 一致。差异属来源口径（安卓=死爪 / FO4=死亡爪），非库内多译 |
| 超级突变体 / 超级变种 | 「超级突变体」0 条 → 一致 |
| 监管者 / 督导者 | 0 条 → 一致（监督者 198） |
| 盖子 / 核可乐 / 饭盒 / 血量 等 | 均为 0 条 → 历史统一轮次已生效 |
| 废料 / 材料 | EN 分别是 junk pile / material 的普通名词，非物品类别 Junk（杂物）→ 非多译 |
| 智慧 / 感知（属性外语境） | 智慧对应 wisdom/intelligence 的日常义；已单列 Perception 那 1 条 |
| 幸运大转盘 / 幸运38号顶层公寓 | 是 SPIN-TO-WIN WHEEL / Lucky 38 的固有译名，非 Luck 属性 → 非多译 |
| 敏捷性（`Stats_Average_Agility`=居民平均敏捷性） | 与 Special_Agility=敏捷 属词形差异，建议一并统一为「敏捷」 |

## 4. 术语沿革备查（git）

- `a624ce2` Ultracite 全库 70 条 → 超铀；随后 `bb2351a`（专有名词全量考据 483 处）改为 **辐射极琉矿**。
- 现值：`辐射极琉矿` 70 条、`超铀` 0 条 → 库内一致；「Ultracite 应作超铀」的旧结论已被后续考据覆盖，无需回改。
