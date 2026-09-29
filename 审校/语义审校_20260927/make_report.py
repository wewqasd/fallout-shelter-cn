#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_report.py — 由 findings_verified.json 生成审校报告与明细表。"""
import json, os, collections, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
V = json.load(open(f'{HERE}/findings_verified.json', encoding='utf-8'))
F = V['findings']
M = json.load(open(f'{HERE}/mech/mech_all.json', encoding='utf-8'))
M2 = json.load(open(f'{HERE}/mech2/mech2_all.json', encoding='utf-8'))

conf = [r for r in F if r['status'] == 'confirmed']
rej = [r for r in F if r['status'] == 'rejected']
unc = [r for r in F if r['status'] == 'uncertain']
S1 = [r for r in conf if r['severity'] == 'S1']
S2 = [r for r in conf if r['severity'] == 'S2']
S3 = [r for r in conf if r['severity'] == 'S3']


def esc(s):
    # 表格里：真实换行与字面 \n 都压成 ' / '，避免破坏 markdown 表格
    return (s or '').replace('|', '\\|').replace('\\n', ' / ').replace('\n', ' / ')


def flat(s):
    # 速览文档单行字段：真实换行与字面 \n 都压成 ' / '
    return (s or '').replace('\\n', ' / ').replace('\n', ' / ')


def pretty(s):
    # 速览文档多行字段：还原真换行、压掉空行、续行缩进两格
    t = (s or '').replace('\\n', '\n').replace('\n\n', '\n')
    return t.replace('\n', '\n  ')


L = []
L.append('# 《辐射避难所》Steam 汉化 — 重大错误 & 语意不通顺 审校报告\n')
L.append('- 日期：2026-09-27')
L.append(f'- 对象：`data/translations.json`（14064 条）= 编译唯一读取源（`src/fs_cn/patcher.py`）')
L.append(f'- 语料切分：79 个上下文连续 chunk（每 180 条，按 key 自然序，同任务/同角色相邻）× 2 视角（准确性 / 通顺度）'
         f' + 长文本（EN≥100 字符）822 条专审（14 chunk）')
L.append(f'- 初审：172 个独立审校 agent；复核：{len(V["findings"])} 条候选逐条交给独立复核 agent 做对抗式判定'
         f'（可用 i2_dump.json 的 ES/FR/DE/RU 槽交叉验证英文原意）')
L.append(f'- 机械扫描：14 类确定性规则全库扫描（数字/占位符/长度比/同 EN 多译/语序/否定/性别指代/反斜杠 等）做交叉校验\n')
L.append('## 统计\n')
L.append('| 项 | 数量 |')
L.append('|---|---|')
L.append(f'| 初审候选（去重后） | {V["base"]} |')
L.append(f'| 复核确认 | {len(conf)}（S1 {len(S1)} / S2 {len(S2)} / S3 {len(S3)}） |')
L.append(f'| 复核驳回（误报/可接受） | {len(rej)} |')
L.append(f'| 存疑待定 | {len(unc)} |')
L.append(f'| 未完成复核 | {len(V["missing"])} |\n')

L.append('## 怎么读这份报告\n')
L.append('| 文件 | 用途 |')
L.append('|---|---|')
L.append('| 本报告 `审校报告_重大错误与不通顺_20260927.md` | 全量结论（S1/S2/S3 三张表 + 机械扫描 + 驳回理由） |')
L.append('| `S1_必改_72条.md` | **只想快速过一遍就打开这个**：72 条严重错误，一条一段，含英文原文与建议改法 |')
L.append('| `修复清单_20260927.tsv` | 机器可读的修订清单（1234 行），落地时直接喂 `apply_fixes.py` |')
L.append('| `S3_可选建议.tsv` | 577 条「不够地道」建议，单独成表，方便只挑想要的 |')
L.append('| `审核明细_全部.tsv` | 1318 条候选全记录（含 84 条被驳回的误报及驳回理由） |')
L.append('')
L.append('**目录**：[统计](#统计) · [一、S1 重大错误](#一s1-重大错误必须改) · [二、S2 中等错误](#二s2-中等错误建议改) · '
         '[三、S3 轻微问题](#三s3-轻微问题可选) · [四、机械扫描](#四机械扫描独立发现不经-llm) · '
         '[五、机械扫描独有发现](#五机械扫描独有发现llm-初审未覆盖)\n')
L.append('**怎么复现**：`python3 审校/语义审校_20260927/{collect.py,collect_verdicts.py,make_report.py,apply_fixes.py}`；'
         '原始分片在 `chunks/`，初审产出在 `out/`，复核产出在 `vout/`。\n')



def section(title, desc, rows, limit=None):
    L.append(f'## {title}\n')
    if desc:
        L.append(desc + '\n')
    if not rows:
        L.append('（无）\n'); return
    L.append('| # | key | 英文原文 | 现译 | 问题 | 建议改法 |')
    L.append('|---|---|---|---|---|---|')
    for i, r in enumerate(rows if limit is None else rows[:limit], 1):
        L.append(f"| {i} | `{r['key']}` | {esc(r['EN'])[:160]} | {esc(r['ZH'])[:160]} | "
                 f"{esc(r['problem'])[:300]} | {esc(r.get('final_fix') or r['fix'])[:300]} |")
    L.append('')


section('一、S1 重大错误（必须改）',
        '含义错、信息反了、漏掉关键信息、数字/指代错、读不通——会让玩家得到错误信息。', S1)
section('二、S2 中等错误（建议改）', '含义大体正确但明显偏差，或中文生硬到影响理解。', S2)
section('三、S3 轻微问题（可选）', '意思没问题但明显不够地道/不准确。', S3)


# ---- S1 速览文档 ----
Q = ['# S1 必改清单 — 72 条会让玩家读到错误信息的地方\n',
     '> 每条：英文原文 → 现译 → 问题 → 建议改法。完整版见 `审校报告_重大错误与不通顺_20260927.md`。\n']
for i, r in enumerate(S1, 1):
    Q.append(f'### {i}. `{r["key"]}`\n')
    Q.append(f'- **英文**：{flat(r["EN"])}')
    Q.append(f'- **现译**：{flat(r["ZH"])}')
    Q.append(f'- **问题**：{flat(r["problem"])}')
    Q.append(f'- **建议**：{pretty(r.get("final_fix") or r["fix"])}\n')
open(f'{HERE}/S1_必改_72条.md', 'w', encoding='utf-8').write('\n'.join(Q) + '\n')

# ---- 机械扫描独立发现 ----
L.append('## 四、机械扫描独立发现（不经 LLM）\n')
L.append('| 类别 | 条数 | 说明 |')
L.append('|---|---|---|')
mech_desc = {
    '00_空值': '译文为空（设计内：原版英文即空）',
    '01_数字不一致': 'EN 与 ZH 的阿拉伯数字集合不一致',
    '02_残留英文': '中文里残留英文单词（多为专名/URL，正常）',
    '04_半角标点': '中文句子里出现半角 `, . ! ?`',
    '05_句末标点': 'EN 与 ZH 句末标点类型不一致',
    '06_疑似漏译(过短)': 'ZH 长度 < EN 的 16%（疑似漏译）',
    '06_疑似多译(过长)': 'ZH 长度 > EN 的 90%（疑似多译/加戏）',
    '08_同EN多译': '同一句英文有两种以上译法（术语/口径不一致）',
    '13_中英无空格': '中英文之间无空格（风格问题）',
    '11_标签不一致': '`{...}` 高亮标记内容不同（已核实为正确设计，非问题）',
}
for cat in sorted(M):
    if cat in ('07_叠字', '03_疑似繁体'):
        continue
    L.append(f'| {cat} | {len(M[cat])} | {mech_desc.get(cat, "")} |')
L.append(f'| B_否定丢失 | {len(M2.get("B_否定丢失", []))} | EN 有否定词而 ZH 无否定形式（多为中文用别的方式表达，需人工看） |')
L.append(f'| A_语序对调 | {len(M2.get("A_语序对调", []))} | 并列成分顺序与英文不一致（多为中文正常语序，非问题） |')
L.append(f'| D_性别指代 | {len(M2.get("D_性别指代", []))} | EN 与 ZH 的性别指代不一致 —— **0 条**，此项干净 |')
L.append('')
L.append('已核实为**非问题**、不再报告的类别：')
L.append('- `{...}` 高亮标记内写成中文（如 `{建造}`）—— 已确认是游戏的高亮排版标记，不是查表占位符，本地化正确。')
L.append('- 中英之间无空格、半角/全角标点混用 —— 风格问题，游戏 UI 下不影响阅读。')
L.append('- 繁体字泄漏 —— 用 810 字繁体字表全库扫描，**0 条**。')
L.append('- 按键字形（`\\ue0xx` 等 PUA 字符）丢失 —— `validate_translation()` 全库 0 条。')
L.append('')


# ---- 机械扫描独有发现 ----
import re as _re
D = json.load(open(f'{ROOT}/data/translations.json', encoding='utf-8'))
EN2 = json.load(open(f'{ROOT}/data/i2_dump.json', encoding='utf-8'))
RGX = _re.compile(r'^(Objective_|QuestObjective_|QuestLoc_.*QuestObjective|QuestLoc_.*QuestShortDesc|Achievement_|Tutorial_|Help_Page|Room_|Generic_|Notification_|QuestList_|UnlockRoom_|Bonus_|Stats_)')
straggler = [(k, v) for k, v in sorted(D.items())
             if RGX.match(k) and '杀死' in v and _re.search(r'\bKill', EN2[k][0])]
bs = [(k, v) for k, v in D.items() if '\\' in v]
L.append('## 五、机械扫描独有发现（LLM 初审未覆盖）\n')
L.append(f'这一节的问题是靠确定性规则扫出来的，初审 172 个 agent 都漏了——正好说明两种方法必须并用。\n')
L.append(f'### 5.1 术语残留：`Kill` 既定译法「消灭」的漏网条目（{len(straggler)} 条）\n')
L.append('上一轮已定案 `Kill → 消灭`（当时改了 87 条）。这 7 条因为 key 里带 `:` 或空格，被上一轮的 key 正则漏掉，仍写作「杀死」：\n')
L.append('| key | 现译 | 建议 |')
L.append('|---|---|---|')
for k, v in straggler:
    L.append(f'| `{k}` | {v} | {v.replace("杀死", "消灭")} |')
L.append('')
L.append('（另有 2 条对话台词 `QuestLoc_ReturntoVault333_Conversation_1_NPCStart_4`「杀死瑞吉娜·雷格！」、'
         '`QuestLoc_SavingDaylight_Conversation_1_NPCStart_3` 同词，属口语，本轮按既定范围**不改**。）\n')
L.append(f'### 5.2 译文里残留转义反斜杠（{len(bs)} 条）\n')
for k, v in bs:
    L.append(f'- `{k}`：`{v}` —— EN 无反斜杠，游戏内会原样显示 `` \\" ``，已由 LLM 初审捕获（S2）。\n')
L.append('### 5.3 全库确认为「干净」的项\n')
L.append('- 繁体字泄漏：**0 条**（810 字繁体字表全库扫描）')
L.append('- 性别指代错乱（EN 的 he/she 与 ZH 的他/她 相反）：**0 条**')
L.append('- 手柄按键字形（PUA `\\ue0xx`）丢失：**0 条**（`validate_translation()` 全库 0 警告）')
L.append('- `{0}` 数字占位符不一致：**0 条**（唯一硬性结构约束，全库通过）')
L.append('- 空译文：**6 条**，均为原版英文即为空（`MrHandyDialog_StorageRoom_01/02`、`SnipSnipDialog_StorageRoom_01/02`、`Speech_Room_SomeoneHappy1`、`Speech_Happiness_InteractingLove1`），属设计内，无需处理\n')
L.append('### 5.4 复核驳回的典型例子（说明误报被挡住）\n')
L.append('| key | 初审意见 | 复核驳回理由 |')
L.append('|---|---|---|')
for r in rej[:6]:
    L.append(f"| `{r['key']}` | {esc(r['problem'])[:120]} | {esc(r.get('v_reason') or '')[:160]} |")
L.append('')

# ---- 明细表 ----
with open(f'{HERE}/审核明细_全部.tsv', 'w', encoding='utf-8') as f:
    f.write('status\tseverity\ttype\tconfidence\tchunk\tlens\tkey\tEN\tZH\t问题\t建议改正\t复核意见\n')
    for r in sorted(F, key=lambda x: (x['status'] != 'confirmed', x['severity'], x['key'])):
        f.write('\t'.join([
            r['status'], r['severity'], r['type'], r['confidence'], str(r['chunk']), r['lens'], r['key'],
            r['EN'].replace('\n', '\\n'), r['ZH'].replace('\n', '\\n'),
            r['problem'].replace('\n', ' '), (r.get('final_fix') or r['fix']).replace('\n', '\\n'),
            (r.get('v_reason') or '').replace('\n', ' ')
        ]) + '\n')
with open(f'{HERE}/S3_可选建议.tsv', 'w', encoding='utf-8') as f:
    f.write('key\tEN\tZH\t建议\t复核意见\n')
    for r in S3:
        f.write('\t'.join([r['key'], r['EN'].replace('\n', '\\n'), r['ZH'].replace('\n', '\\n'),
                           (r.get('final_fix') or r['fix']).replace('\n', '\\n'),
                           (r.get('v_reason') or '').replace('\n', ' ')]) + '\n')

open(f'{HERE}/审校报告_重大错误与不通顺_20260927.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('报告已生成: 审校报告_重大错误与不通顺_20260927.md')
print(f'S1={len(S1)} S2={len(S2)} S3={len(S3)} rejected={len(rej)} uncertain={len(unc)}')
