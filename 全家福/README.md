# Agent 全家福 · 谱系图

本对话（`fallout_shelter_hanhua` 汉化项目，根会话 `session-124f2d98-88a2-4082-adbe-bc828d43dc39`）
里派出去的全部子 Agent 的谱系与集体照。

## 产物

| 文件 | 说明 |
|---|---|
| [agent全家福_谱系图.png](agent全家福_谱系图.png) | **PNG 海报**（2000×2000，离线可看，适合分享） |
| [agent全家福_谱系图.html](agent全家福_谱系图.html) | **交互版**：每个 Agent 悬停显示会话 id / 起止时间 / 耗时 / 上下文体积 / 结果 |
| `_genealogy_raw.json` | 从 DSH 会话留档提取的原始谱系数据 |

## 复现

```bash
python3 collect_genealogy.py     # 读 ~/.dsh/sessions 下的会话留档 → _genealogy_raw.json
python3 build_poster.py          # → agent全家福_谱系图.html
python3 build_poster_png.py      # → agent全家福_谱系图.png（需要 PIL + 微软雅黑/文泉驿）
```

`collect_genealogy.py [project-slug] [root-session-id]` 可指定别的项目/会话，默认就是本项目。

## 数据来源与口径

DSH 把每个 Agent 存成独立会话目录：

```
~/.dsh/sessions/--home-wangqiang-fallout_shelter_hanhua--/
├── session-<root-id>/session.v4.jsonl.zstd     # 根会话：主控事件流
└── <child-uuid>/session.v4.jsonl.zstd          # 每个子 Agent 自己的会话
```

- **谱系边**：子会话头里的 `parentSession` → 根会话，`delegationDepth: 1`、`origin: "subagent"`。
  本图谱系只有两层（主控 → 275 个子 Agent），**没有二级嵌套**。
- **归属批次**：根会话事件流里的 `tool-workflow/agent-start`（`runId` / `phase` / `label` / `childId`）
  与 `tool-workflow/agent-end`（`outcome`）按 run 内时间顺序配对，得到每个 Agent 的起止与结果。
- **专项子 Agent**：`subagent/catalog` 里存在、但不在任何 `agent-start` 中的 5 个（中文标签），
  是走 `subagent` 工具而非 workflow 派的，按 `childId` 去重后单独成组。
- **上下文体积**：子会话 `.zstd` 文件字节数（压缩后），仅作投入量参考。

## 这一批 Agent 的构成（273 位）

| 批次 | 人数 | 角色 | 时间窗 | 跨度 |
|---|---|---|---|---|
| 试点审校 | 8 | 初审·准确性 ×4、初审·流畅度 ×4 | 09-27 01:32 → 01:37 | 6 min |
| 审校A段 | 80 | 40 × 2 视角 | 09-27 01:38 → 02:32 | 54 min |
| 审校B段 | 78 | 39 × 2 视角 | 09-27 01:38 → 02:31 | 53 min |
| 长文本专审 | 14 | 长文本专审 | 09-27 01:41 → 02:04 | 23 min |
| 对抗复核 | 88 | 对抗复核（验证初审结论） | 09-27 02:33 → 03:20 | 48 min |
| 专项审校 | 5 | 专名分类（阵营机器人／生物／系统房间／人物／物品消耗品） | — | 3 min |

- 合计子 Agent 累计工时 **17.9 h**，整体墙钟跨度 **47.3 h**（含人工裁决等空档）
- **260/273 正常完成**；13 个首轮 `failed`，后由主控补跑，最终每个批次都有完整产出
  （PNG 里以红圈标出）
- 根会话累计 **23 个用户回合**、主控 **874 次工具调用**（bash 589 / ask_user_question 150 /
  write 35 / edit 34 / job_output 15 / web_search 11 / read 7 / present 7）
