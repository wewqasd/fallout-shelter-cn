#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建 cjk_font_v6_pua.ttf（PUA 手柄按键图标版）:
- 基底 build/cjk_font_v5_official.ttf（国服官方思源黑体 Noto Sans SC，upem 1000，TrueType glyf）
- 新增 16 个 PUA 字形 E000-E00F（对应 ReplaceButtonImages 的 16 个标记 [A]~[DD]）:
    E000=[A] E001=[B] E002=[X] E003=[Y] E004=[LT] E005=[RT] E006=[LB] E007=[RB]
    E008=[CV] E009=[MN] E00A=[L] E00B=[R] E00C=[DL] E00D=[DR] E00E=[DU] E00F=[DD]
- 设计语言照搬 v4 uniFF00（实心圆盘 + 镂空内容，二次贝塞尔 0.9142，实心 CW / 镂空 CCW）
- 字母轮廓借自 DejaVuSans（v4 借 •/™ 同工艺），双字母并排，方向键 = 三角箭头
- 运行时机制: 译文中的 PUA 字符绕过 ReplaceButtonImages（只认 [XX] 标记），直接由本字体渲染
"""
import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 仓库根
sys.path.insert(0, os.path.join(_ROOT, ".pylibs"))
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

BASE = os.path.join(_ROOT, "assets", "cjk_font_v5_official.ttf")   # 基底字体（已归档，需自行准备）
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUT = os.path.join(_ROOT, "assets", "cjk_font_v6_pua.ttf")

UPEM = 1000
KQ = 0.9142                      # 二次贝塞尔圆弧常数（v4 已真机验证）
CX, CY, R = 500, 480, 360        # 圆盘中心 / 半径（0.72em，顶 840 底 120）
ADV = 1000                       # 字宽 = 全宽

# 标记 → PUA 码位（顺序对齐 ReplaceButtonImages 的 FF00-FF0F）
MARKERS = ["A", "B", "X", "Y", "LT", "RT", "LB", "RB", "CV", "MN", "L", "R", "DL", "DR", "DU", "DD"]
CP = {m: 0xE000 + i for i, m in enumerate(MARKERS)}
SINGLE = {"A", "B", "X", "Y", "L", "R"}            # 盘内单字母
DOUBLE = {"LT": "LT", "RT": "RT", "LB": "LB", "RB": "RB", "CV": "CV", "MN": "MN"}
ARROW = {"DL": (230, 480), "DR": (770, 480), "DU": (500, 730), "DD": (500, 230)}
ARROW_TRI = {  # 指向性三角（镂空），尖点 = 上述坐标
    "DL": [(690, 700), (690, 260), (230, 480)],
    "DR": [(310, 700), (310, 260), (770, 480)],
    "DU": [(290, 310), (710, 310), (500, 730)],
    "DD": [(290, 690), (710, 690), (500, 230)],
}


def add_circle(pen, cx, cy, r, cw=True):
    Kk = KQ * r
    E, S, W, N = (cx + r, cy), (cx, cy - r), (cx - r, cy), (cx, cy + r)
    NE, SE, SW, NW = (cx + Kk, cy + Kk), (cx + Kk, cy - Kk), (cx - Kk, cy - Kk), (cx - Kk, cy + Kk)
    pen.moveTo(E)
    if cw:
        pen.qCurveTo(SE, S); pen.qCurveTo(SW, W); pen.qCurveTo(NW, N); pen.qCurveTo(NE, E)
    else:
        pen.qCurveTo(NE, N); pen.qCurveTo(NW, W); pen.qCurveTo(SW, S); pen.qCurveTo(SE, E)
    pen.closePath()


def poly(pen, pts, hole=False):
    pts = list(pts)
    area = 0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        area += x1 * y2 - x2 * y1
    is_cw = area < 0
    if (hole and is_cw) or ((not hole) and (not is_cw)):
        pts = list(reversed(pts))
    pen.moveTo(pts[0])
    for p in pts[1:]:
        pen.lineTo(p)
    pen.closePath()


def borrow_letter(dv, dv_cmap, ch, pen, s, cx, cy):
    """DejaVu 字母轮廓缩放 s、bbox 中心对齐 (cx,cy) 原样写入 pen。
    绕向说明: 盘画成 CCW(+1)，字母外轮廓原生 CW(-1) → 字母笔画区 winding=0 即镂空，
    字母自身计数器(如 A 的三角孔)原生 CCW(+1) → winding=2 保持实心，nonzero 规则下无需反转。"""
    src = dv_cmap[ord(ch)]
    rec = RecordingPen()
    dv["glyf"][src].draw(rec, dv["glyf"])          # 解析组件
    bp = BoundsPen(None)
    rec.replay(bp)
    (x0, y0, x1, y1) = bp.bounds
    dx = cx - (x0 + x1) / 2 * s
    dy = cy - (y0 + y1) / 2 * s
    rec.replay(TransformPen(pen, (s, 0, 0, s, dx, dy)))


def main():
    font = TTFont(BASE)
    go = font.getGlyphOrder()
    dv = TTFont(DEJAVU)
    dv_cap = 1493.0                                 # DejaVu 大写字高（实测全 1493）
    s1 = 430.0 / dv_cap                             # 单字母: 高 430
    s2 = 270.0 / dv_cap                             # 双字母: 高 270

    for m in MARKERS:
        cp = CP[m]
        name = f"uni{cp:04X}"
        pen = TTGlyphPen(None)
        add_circle(pen, CX, CY, 360, cw=False)      # 盘走 CCW，字母原生 CW 即成镂空（见 borrow_letter 注释）
        if m in SINGLE:
            borrow_letter(dv, dv.getBestCmap(), m, pen, s1, CX, CY)
        elif m in DOUBLE:
            a, b = DOUBLE[m]
            # 双字母并排：总宽 = wA*s2 + GAP + wB*s2，整体居中
            GAP = 90
            bp = BoundsPen(None)
            rec = RecordingPen(); dv["glyf"][dv.getBestCmap()[ord(a)]].draw(rec, dv["glyf"]); rec.replay(bp)
            wa = (bp.bounds[2] - bp.bounds[0]) * s2
            rec = RecordingPen(); dv["glyf"][dv.getBestCmap()[ord(b)]].draw(rec, dv["glyf"])
            bp2 = BoundsPen(None); rec.replay(bp2)
            wb = (bp2.bounds[2] - bp2.bounds[0]) * s2
            total = wa + GAP + wb
            borrow_letter(dv, dv.getBestCmap(), a, pen, s2, CX - total / 2 + wa / 2, CY)
            borrow_letter(dv, dv.getBestCmap(), b, pen, s2, CX + total / 2 - wb / 2, CY)
        else:                                        # 方向键三角
            # 盘是 CCW，镂空三角必须反向(CW)：hole=False 强制 CW（鞋带面积<0）
            poly(pen, ARROW_TRI[m], hole=False)
        if name not in go:
            go.append(name)
        g = pen.glyph()
        bp = BoundsPen(None)
        g.draw(bp, font["glyf"])
        lsb = int(bp.bounds[0]) if bp.bounds else 0
        font["glyf"][name] = g
        font["hmtx"][name] = (ADV, lsb)
        print(f"  {name} = [{m}]  lsb={lsb}")

    # cmap: (3,1) format4 + (3,10) format12 都挂上
    n_cmap = 0
    for st in font["cmap"].tables:
        if (st.platformID, st.platEncID) in ((3, 1), (3, 10)):
            for m in MARKERS:
                st.cmap[CP[m]] = f"uni{CP[m]:04X}"
            n_cmap += 1
    print(f"cmap 子表已加: {n_cmap}")

    font.setGlyphOrder(go)
    font["glyf"].setGlyphOrder(go)
    # vmtx: 抄一个既有 CJK 字形的 (advanceHeight, offset)
    if "vmtx" in font:
        ref = font["vmtx"]["uniFF01"] if "uniFF01" in font["vmtx"].metrics else next(iter(font["vmtx"].metrics.values()))
        for m in MARKERS:
            font["vmtx"][f"uni{CP[m]:04X}"] = ref
        print("vmtx 已补充:", ref)
    font.save(OUT)
    print("saved:", OUT)

    # ---- 验证 ----
    f2 = TTFont(OUT)
    base = TTFont(BASE)
    cm = f2.getBestCmap()
    ok_cmap = all(CP[m] in cm for m in MARKERS)
    same_ff = all(
        f2["glyf"][f"uniFF{i:02X}"].compile(f2, [f"uniFF{i:02X}"]) ==
        base["glyf"][f"uniFF{i:02X}"].compile(base, [f"uniFF{i:02X}"])
        for i in range(0, 16) if f"uniFF{i:02X}" in base["glyf"]
    )
    # 绕向检查: 实心盘 CW（鞋带面积<0），镂空存在
    from fontTools.pens.areaPen import AreaPen
    for m in MARKERS:
        ap = AreaPen(glyphset=f2.getGlyphSet())
        f2.getGlyphSet()[f"uni{CP[m]:04X}"].draw(ap)
        # 无断言（总面积含盘+洞），只确认轮廓可解算
    print(f"验证: PUA cmap 全部存在={ok_cmap}  FF00-FF0F 字形与基底一致={same_ff}")
    print("upem:", f2['head'].unitsPerEm, " glyph数:", f2['maxp'].numGlyphs)


if __name__ == "__main__":
    main()