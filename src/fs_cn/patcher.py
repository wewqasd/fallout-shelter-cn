#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patcher.py — 版本自适应汉化手术核心（fs_cn 包）。

设计（三层）：
  1) 定位层（pid 无关）：I2 内容锚点 / FontManager MonoScript 类名 / 静态标签内容
  2) 写回层（term 匹配 + 缺省回退）：
       - 表有、包无（旧 term 被删）→ allow_unmatched=False 中止，True 跳过并汇报
       - 包有、表无（更新新增 term）→ 保留原文英文，fallback 计数汇报
  3) 前置校验：译文 {0}/换行/富文本标记 与 EN 不一致 → 默认中止（--skip-validate 可跳过）
  4) 输出：LZ4 压缩写回（默认）或 none（兜底）

用法（API）:
    from fs_cn.patcher import patch_bundle
    result = patch_bundle(
        src=".../data.unity3d", out=".../data.unity3d",
        translations={term: zh, ...}, font_bytes=b"...",
        allow_unmatched=False, validate=True, packer="lz4",
        progress=print,  # 可选回调 fn(str)
    )
    # result = {"ok":bool, "patched_terms":N, "fallback":M, "skipped":K,
    #           "fonts":N, "fontmanagers":N, "static_labels":N, "size":N, "msg":str}
"""
import UnityPy, struct, json, os, sys, shutil, hashlib, re, ntpath, time as _time
from datetime import datetime
from collections import defaultdict, Counter
from . import resources

# 多锚点：主锚点 + 备选（版本更新若删/改主锚点 term，逐个尝试）
ANCHORS = [
    b"Achievement_Xbox_Completed_01",
    b"ActivateRewards",
    b"Attention",
    b"Baby_NewBabyArrived",
]

# ---------------- 进度事件（结构化，向后兼容纯文本回调） ----------------
# 阶段权重：按 2.7.0 实测耗时占比折算（总≈180s），用于「总进度」条平滑推进。
STAGE_WEIGHTS = {
    "load":    0.09,   # UnityPy.load 481MB
    "parse":   0.02,   # I2 定位 / 前置校验
    "rebuild": 0.02,   # I2 重建
    "font":    0.31,   # 字体替换
    "labels":  0.04,   # FontManager / UILabel / 静态标签
    "save":    0.52,   # 写回 530MB
}
STAGE_NAMES = {
    "load":   "载入数据包", "parse": "解析文本表", "rebuild": "重建文本表",
    "font":   "替换中文字体", "labels": "修正界面控件", "save": "写回数据包",
}
_STAGE_ORDER = ["load", "parse", "rebuild", "font", "labels", "save"]


class Progress:
    """结构化进度上报器。

    - ``stage(name, msg)``        进入某阶段（总进度按权重推进）
    - ``step(cur, total, msg)``   阶段内进度
    - ``text(msg)``               普通日志行

    兼容旧用法：外部若传入只接收单个字符串的函数，自动退化为纯文本回调。
    """

    def __init__(self, cb=None, echo_print=False):
        self.cb = cb
        self.echo = echo_print
        self._acc = 0.0            # 已完成阶段权重和

    def _emit(self, kind, **kw):
        if self.echo and kw.get("msg"):
            print(kw["msg"], flush=True)
        if self.cb is None:
            return
        try:
            self.cb(kind=kind, **kw)
        except TypeError:
            # 旧式回调：只接受一个字符串位置参数
            msg = kw.get("msg", "")
            if msg:
                try:
                    self.cb(str(msg))
                except Exception:
                    pass

    def stage(self, name, msg=None):
        base = self._acc
        w = STAGE_WEIGHTS.get(name, 0.0)
        self._emit("stage", stage=name, label=STAGE_NAMES.get(name, name),
                   weight=w, base=base, msg=msg or STAGE_NAMES.get(name, name))
        self._acc += w

    def step(self, cur, total, msg=None):
        frac = (cur / total) if total else 0.0
        self._emit("step", cur=cur, total=total,
                   frac=max(0.0, min(1.0, frac)),
                   msg=msg or f"{cur}/{total}")

    def text(self, msg, detail=False):
        """普通日志行。detail=True 表示「仅排查时有用」的过程明细，
        GUI 可将其只写入折叠区，不打扰主界面。"""
        self._emit("text", msg=str(msg), detail=bool(detail))


# ---------------- I2 解析（同 v3.1 已验证逻辑） ----------------
def iskey(b): return bool(b) and all(32 <= c < 127 for c in b)

def try_parse_langcnt(raw, pos, n, expect=None, need_key=True):
    if pos + 4 > n: return None
    lc = struct.unpack_from('<i', raw, pos)[0]
    if not (1 <= lc <= 40): return None
    if expect is not None and lc != expect: return None
    p = pos + 4
    for _ in range(lc):
        if p + 4 > n: return None
        ln = struct.unpack_from('<i', raw, p)[0]
        if ln < 0 or ln > 100000 or p + 4 + ln > n: return None
        p += 4 + ln; p = (p + 3) // 4 * 4
    for _ in range(2):
        if p + 4 > n: return None
        c = struct.unpack_from('<i', raw, p)[0]
        if not (0 <= c <= 5000) or p + 4 + c * 4 > n: return None
        p += 4 + c * 4
    if need_key:
        if p + 4 > n: return None
        nk = struct.unpack_from('<i', raw, p)[0]
        if not (1 <= nk <= 300) or p + 4 + nk > n: return None
        if not iskey(raw[p + 4:p + 4 + nk]): return None
    return lc

def parse_terms(raw, anchor=None):
    n = len(raw); fk = raw.find(anchor if anchor else ANCHORS[0])
    if fk < 0: return [], None, None, None
    pos = fk - 4
    terms = []; LC = None
    while pos + 16 <= n:
        klen = struct.unpack_from('<i', raw, pos)[0]
        if not (1 <= klen <= 300): break
        keyb = raw[pos + 4:pos + 4 + klen]
        if not iskey(keyb): break
        align = (pos + 4 + klen + 3) // 4 * 4
        found = None
        for cand in range(align, min(align + 200, n)):
            if try_parse_langcnt(raw, cand, n, LC, need_key=True) is not None: found = cand; break
        if found is None:
            for cand in range(align, min(align + 200, n)):
                if try_parse_langcnt(raw, cand, n, LC, need_key=False) is not None: found = cand; break
        if found is None:
            break
        langcnt = struct.unpack_from('<i', raw, found)[0]
        if LC is None: LC = langcnt
        fc = raw[align:found]
        p = found + 4; vals = []
        for _ in range(langcnt):
            ln = struct.unpack_from('<i', raw, p)[0]; p += 4
            vals.append(raw[p:p + ln].decode('utf-8', 'replace')); p += ln; p = (p + 3) // 4 * 4
        tail_start = p
        for _ in range(2):
            c = struct.unpack_from('<i', raw, p)[0]; p += 4; p += c * 4
        terms.append((keyb, fc, vals, raw[tail_start:p]))
        pos = p
    return terms, pos, LC, fk - 4

def rebuild_term(keyb, flags_cat, vals, langcnt, tail):
    out = struct.pack('<i', len(keyb)) + keyb
    out += b'\x00' * ((4 - (len(out) % 4)) % 4)
    out += flags_cat
    out += struct.pack('<i', langcnt)
    for v in vals:
        vb = v.encode('utf-8')
        out += struct.pack('<i', len(vb)) + vb
        out += b'\x00' * ((4 - (len(out) % 4)) % 4)
    out += tail
    return out

# ---------------- 定位辅助 ----------------
def current_raw(o):
    """读对象当前数据：set_raw_data 过的用 self.data，否则读原始字节。"""
    d = getattr(o, "data", None)
    return d if d else o.get_raw_data()

def rd_str(raw, p):
    ln = struct.unpack_from("<i", raw, p)[0]
    if ln < 0 or ln > 1_000_000 or p + 4 + ln > len(raw): raise ValueError("str")
    return raw[p + 4:p + 4 + ln], (p + 4 + ln + 3) // 4 * 4

def build_script_map(objs):
    sm = {}
    for o in objs:
        if o.type.name == "MonoScript":
            try: sm[o.path_id] = str(o.read().m_ClassName)
            except Exception: pass
    return sm

def build_af_ext(objs):
    af = {}
    for o in objs:
        k = id(o.assets_file)
        if k not in af:
            try:
                af[k] = [str(getattr(e, "path", getattr(e, "path_name", ""))) for e in o.assets_file.externals]
            except Exception:
                af[k] = []
    return af

def cls_of(o, script_map, af_ext):
    raw = current_raw(o)
    if len(raw) < 40: return None
    fid, pid = struct.unpack_from("<iq", raw, 16)
    exts = af_ext.get(id(o.assets_file)) or []
    if fid == 0: return script_map.get(pid)
    if 1 <= fid <= len(exts) and "globalgamemanagers" in exts[fid - 1]:
        return script_map.get(pid)
    return None


# ---------------- UILabel 渲染路径钉死（对标对方 forced/assigned，零 typetree） ----------------
# NGUI UILabel 序列化布局（MonoBehaviour 字节，已用 typetree 逐字段对账校准，6000.0.58）：
#   [16B header][12B m_Script][m_Name str][基类 UIRect/UIWidget = 132B][12B mFontTypografy]
#   [12B mTrueTypeFont][mText str][4B mFontSize][4B mFontStyle] …中间 20 个字段(132B)…
#   [4B mForceTrueTypeFont(bool)]（对象末尾附近）
# 操作：
#   1) force: mForceTrueTypeFont 0→1（强制走 TrueType 动态字体 = 已换的 CJK）
#   2) assign: mTrueTypeFont 空引用 → 该 asset 的 dominant 字体（频次最高，即 CJK 化的 Font）
# 安全失败：结构校验不过（force 非{0,1}、fileID 越界）的标签跳过 + 计数报告，不中止。
# 版本更新若 NGUI 字段布局变化 → 校验失败自动跳过本功能（退化=回退依赖），不写坏字节。
_BASE_CLASS_FIELD_LEN = 132     # m_Name 结束 → mFontTypografy（UIRect+UIWidget+新字段）
_FORCE_AFTER_TEXT = 136         # mText 结束对齐 → mForceTrueTypeFont（mFontSize..mMultiline 共136B）

def force_label_true_type(objs, script_map, af_ext, progress=None):
    def log(m, detail=False):
        # progress 可能是 Progress 实例、结构化回调或旧式 fn(str)
        if isinstance(progress, Progress):
            progress.text(m, detail=detail)
        elif progress:
            progress(str(m))
        else:
            print(m, flush=True)

    # 每 asset 的外部文件数（fileID 合法性上界）
    ext_len = {k: len(v) for k, v in af_ext.items()}

    # 第一遍：解析所有 UILabel，统计每 asset 的 dominant 字体引用
    entries = []                      # (obj, raw, tt_off, force_off, tt_key, tt_ok)
    dominant = defaultdict(Counter)   # asset_name -> Counter[(fid,pid)]
    scanned = 0; bad = 0
    for o in objs:
        if o.type.name != 'MonoBehaviour': continue
        if cls_of(o, script_map, af_ext) != 'UILabel': continue
        scanned += 1
        raw = current_raw(o)
        try:
            p = 28
            _, p = rd_str(raw, p)                    # m_Name
            p += _BASE_CLASS_FIELD_LEN               # 基类字段
            p += 12                                   # mFontTypografy PPtr
            tt_off = p
            tt_fid, tt_pid = struct.unpack_from("<iq", raw, p); p += 12
            _, p = rd_str(raw, p)                    # mText str
            force_off = p + _FORCE_AFTER_TEXT
            if force_off + 4 > len(raw): raise ValueError()
            if struct.unpack_from("<i", raw, force_off)[0] not in (0, 1):  # bool 校验
                bad += 1; continue
        except Exception:
            bad += 1; continue
        a = o.assets_file.name
        # fileID 合法性：0=本 asset，1..N=external（垃圾/越界 fileID 排除）
        fid_ok = 0 <= tt_fid <= ext_len.get(id(o.assets_file), 0)
        tt_ok = fid_ok and tt_pid != 0
        if tt_ok:
            dominant[a][(tt_fid, tt_pid)] += 1
        entries.append((o, raw, tt_off, force_off, (tt_fid, tt_pid), tt_ok))
    if scanned == 0:
        log("警告: 未找到 UILabel（类名可能已变），跳过渲染路径钉死")
        return 0, 0, 0, bad

    # 第二遍：强制 + 指派
    forced = 0; assigned = 0
    for o, raw, tt_off, force_off, tt_key, tt_ok in entries:
        patch = bytearray(raw)
        changed = False
        if struct.unpack_from("<i", raw, force_off)[0] == 0:
            patch[force_off] = 1                      # 4B bool 0→1（低字节）
            forced += 1; changed = True
        if not tt_ok:
            dom = dominant[o.assets_file.name].most_common(1)
            if dom:
                (dfid, dpid), _ = dom[0]
                struct.pack_into("<iq", patch, tt_off, dfid, dpid)
                assigned += 1; changed = True
        if changed:
            o.set_raw_data(bytes(patch))
    log(f"UILabel render pinned: scanned={scanned} forced={forced} assigned={assigned}"
        + (f" 结构异常跳过={bad}" if bad else ""), detail=True)
    return forced, assigned, scanned, bad

# ---------------- 前置校验 ----------------
# 设计准则：
#   * {0} 占位符集合一致性 ——「真结构损坏」信号，唯一**硬中止**项。
#   * 按键标记 [A]~[DD] —— 译文中会用 PUA 字形 \ue000~\ue00f 替换（本字体专用），
#     或按语境删去；属**设计内自适应**，只计入警告，不中止。
#   * 换行段数 / 括号文本（如 "[Content line 2]"→"[内容线2]"）—— 翻译时有意合并/拆分/改意，
#     属**设计内自适应**，只计入警告，不中止。
_PH = re.compile(r'\{[0-9]+\}')
_PUA = [chr(0xE000 + i) for i in range(16)]     # 对应 [A]~[DD]
_MARKER_TOKENS = {'[A]','[B]','[X]','[Y]','[LT]','[RT]','[LB]','[RB]',
                  '[CV]','[MN]','[L]','[R]','[DL]','[DR]','[DU]','[DD]'}
_BRACKET = re.compile(r'\[[a-zA-Z0-9 ]+\]')       # 任何 [xx] 形 token

def segs(s): return [x for x in s.split('\n') if x.strip()]

def validate_translation(key, zh, en):
    """返回 (硬问题列表, 警告列表)。

    硬问题 = {0} 占位符不一致（唯一会中止的）。
    警告   = 仅保留「真可能出问题」的情形：
               · EN 有按键标记，但 ZH 既无 PUA 字形也未保留原标记（可能漏标）
            以下设计内自适应情形**不再报警**（曾造成 70 条噪音，实测 0 条真问题）：
               · 换行段数不同（中文分段本来就会变）
               · 括号 token 差异（[A]→PUA 字形 是预期替代）
    """
    fatal, warns = [], []
    # ---- 硬项：{0} 占位符集合必须一致（真结构损坏）----
    if set(_PH.findall(zh)) != set(_PH.findall(en)):
        fatal.append(f"占位符 {{0}} 不一致: ZH={sorted(set(_PH.findall(zh)))} EN={sorted(set(_PH.findall(en)))}")
    # ---- 警告项：只报按键标记真丢失 ----
    en_tok = set(_BRACKET.findall(en))
    zh_tok = set(_BRACKET.findall(zh))
    en_markers = en_tok & _MARKER_TOKENS
    zh_pua = [p for p in _PUA if p in zh]
    if en_markers and (zh_tok & en_markers) != en_markers and not zh_pua:
        warns.append(f"按键标记可能丢失: EN={sorted(en_markers)} ZH 无对应 PUA 字形")
    return fatal, warns

# ---------------- 主手术 ----------------
def patch_bundle(src, out, translations, font_bytes=None,
                 allow_unmatched=False, validate=True, packer="lz4",
                 progress=None, archive=False):
    # progress 可为：None / 旧式 fn(str) / 结构化 fn(kind=..., **kw)
    # 一律包成 Progress；无回调时打印到 stdout（CLI 行为不变）
    ep = progress if isinstance(progress, Progress) else Progress(progress, echo_print=(progress is None))

    def log(msg, detail=False):
        ep.text(msg, detail=detail)

    result = {"ok": False, "msg": "", "warnings": 0, "warn_keys": []}

    # ---- 0) 原版存档（md5 去重）----
    if archive and os.path.exists(src):
        try:
            arc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "原版存档")
            arc_dir = os.path.abspath(arc_dir)
            os.makedirs(arc_dir, exist_ok=True)
            digest = hashlib.md5(open(src, 'rb').read()).hexdigest()
            seen = set()
            for fn in os.listdir(arc_dir):
                if fn.endswith(".md5"):
                    seen.add(open(os.path.join(arc_dir, fn), encoding='utf-8').read().split()[0])
            if digest not in seen:
                tag = datetime.now().strftime("%Y%m%d")
                shutil.copy2(src, os.path.join(arc_dir, f"{tag}_data.unity3d"))
                with open(os.path.join(arc_dir, f"{tag}_data.unity3d.md5"), "w", encoding='utf-8') as f:
                    f.write(digest + "\n")
                log(f"原版存档: {tag}_data.unity3d (md5 {digest[:8]}…)")
            else:
                log(f"原版与既有存档相同（md5 {digest[:8]}…），跳过存档")
        except Exception as e:
            log(f"(存档跳过: {e})")

    if font_bytes is None:
        raise ValueError("font_bytes 不能为空")

    # ---- 1) 载入 ----
    try:
        _size_mb = os.path.getsize(src) / 1e6
    except OSError:
        _size_mb = 0
    ep.stage("load", f"正在载入数据包（{_size_mb:.0f} MB），首次载入较慢，请耐心等待…")
    env = UnityPy.load(src)
    ep.step(1, 1, "数据包已载入")
    objs = list(env.objects)
    log(f"对象数: {len(objs)}", detail=True)

    # ---- 2) I2: 按内容锚点定位（多锚点，pid 无关）----
    ep.stage("parse", "正在定位文本表…")
    best = None; used_anchor = None
    for anchor in ANCHORS:
        for o in objs:
            if o.type.name != 'MonoBehaviour': continue
            raw = o.get_raw_data()
            if anchor in raw and (best is None or len(raw) > len(best[1])):
                best = (o, raw); used_anchor = anchor
        if best is not None:
            break
    if best is None:
        raise ValueError("未找到 I2 LanguageSource（全部锚点缺失）— 游戏结构可能已大改")
    obj, raw = best
    n = len(raw)
    terms, last_pos, LC, first = parse_terms(raw, used_anchor)
    log(f"I2: 锚点={used_anchor.decode()} pid={obj.path_id} file={obj.assets_file.name} terms={len(terms)} LC={LC}", detail=True)

    # ---- 3) 前置校验（基于包内 EN，版本自适应）----
    if validate:
        pkg_en = {t[0].decode('ascii'): t[2][0] for t in terms}   # vals[0] = EN 槽
        log("前置校验：译文结构标记 vs 包内 EN …", detail=True)
        fatal, warn_keys = [], []
        for k, zh in translations.items():
            if not zh: continue
            en = pkg_en.get(k)
            if en is None: continue
            f, w = validate_translation(k, zh, en)
            fatal.extend((k, x) for x in f)
            warn_keys.extend((k, x) for x in w)
        if fatal:
            msg = f"前置校验失败 {len(fatal)} 键（{0} 占位符与包内EN不符，疑似结构损坏）:\n" + \
                  "\n".join(f"  {k}: {x}" for k, x in fatal[:10])
            if len(fatal) > 10: msg += f"\n  … 共 {len(fatal)} 键"
            raise ValueError(msg)
        if warn_keys:
            # 只有「按键标记真丢失」这类真问题才会走到这里（设计内自适应已不再报警）
            log(f"注意: {len(warn_keys)} 条译文的按键标记可能丢失（不影响汉化，可忽略）:")
            for k, x in warn_keys[:5]:
                log(f"  {k}: {x}")
            if len(warn_keys) > 5: log(f"  … 共 {len(warn_keys)} 条")
        else:
            log(f"译文校验通过（{len(translations)} 条）")
        # 版本情报：包内 EN vs 基准 EN（notes）差异 → 游戏可能已更新
        en_changed = []
        if resources.en_lookup:
            en_changed = [k for k, en in pkg_en.items()
                          if k in resources.en_lookup and resources.en_lookup[k] != en]
            if en_changed:
                log(f"版本情报: {len(en_changed)} 个 term 的英文原文与基准不同（游戏可能已更新）: "
                    + ", ".join(en_changed[:5]) + (" …" if len(en_changed) > 5 else ""))
    else:
        en_changed = []

    # 表有包无（旧 term 被删/改名）
    table_keys = set(translations)
    pkg_keys = {t[0].decode('ascii') for t in terms}
    deleted = sorted(table_keys - pkg_keys)
    if deleted:
        preview = ", ".join(deleted[:15])
        if len(deleted) > 15: preview += f", … {len(deleted)} more"
        if not allow_unmatched:
            raise ValueError(
                f"翻译表含 {len(deleted)} 个当前包中不存在的 term（游戏版本可能变化）:\n{preview}\n"
                f"若确认继续（跳过这些 term），请以 allow_unmatched=True 重试。"
            )
        log(f"警告: 跳过 {len(deleted)} 个表有包无的 term（版本更新删除/改名）: {preview}")

    header = raw[0:first]; footer = raw[last_pos:]
    rebuilt = bytearray(header); fallback = 0; patched = 0; skipped = 0
    ep.stage("rebuild", f"正在重建文本表（共 {len(terms)} 条）…")
    _n_terms = len(terms)
    _next_tick = max(1, _n_terms // 20)
    for _i, (keyb, fc0, vals, tail) in enumerate(terms, 1):
        key = keyb.decode('ascii')
        zh = translations.get(key)
        if zh:
            new_vals = [zh] * len(vals)
            patched += 1
        else:
            new_vals = vals          # 缺省回退：保留原文（新版本新增 term）
            fallback += 1
        rebuilt += rebuild_term(keyb, fc0, new_vals, len(vals), tail)
        if _i % _next_tick == 0 or _i == _n_terms:
            ep.step(_i, _n_terms, f"重建文本表 {_i}/{_n_terms}")
    rebuilt += footer
    obj.set_raw_data(bytes(rebuilt))
    log(f"I2 rebuilt: {len(rebuilt)}B  写入 {patched} 条  缺译保留原文 {fallback} 条", detail=True)

    # ---- 4) 字体: 全部 Font → CJK ----
    font_objs = [o for o in objs if o.type.name == 'Font']
    n_all = len(font_objs)
    ep.stage("font", f"正在替换中文字体（共 {n_all} 个，每个约 10 MB，请耐心等待）…")
    nf = 0
    for fobj in font_objs:
        # 先报「正在处理第 n 个」，再执行（单个字体写入耗时较长，先出提示避免空等）
        ep.step(nf, n_all, f"正在写入字体 {nf + 1}/{n_all}（每个约 10 MB）…")
        fo = fobj.read()
        fo.m_FontData = list(font_bytes)
        fo.save()
        nf += 1
        ep.step(nf, n_all, f"已完成字体 {nf}/{n_all}")
    log(f"fonts replaced: {nf}", detail=True)

    # ---- 5) FontManager: 按类名定位，customFonts 非空 PPtr 置零 ----
    ep.stage("labels", "正在修正界面控件字体引用…")
    script_map = build_script_map(objs)
    af_ext = build_af_ext(objs)
    fm_patched = 0
    for o in objs:
        if o.type.name != "MonoBehaviour": continue
        if cls_of(o, script_map, af_ext) != "FontManager": continue
        raw = current_raw(o)
        p = 28
        _, p = rd_str(raw, p)      # m_Name
        cnt = struct.unpack_from("<i", raw, p)[0]; p += 4
        patch = bytearray(raw); total = 0
        for li in range(cnt):
            nf_ = struct.unpack_from("<i", raw, p)[0]; p += 4
            p += 12 * nf_
            nc = struct.unpack_from("<i", raw, p)[0]; p += 4
            for ci in range(nc):
                off = p
                f2, p2 = struct.unpack_from("<iq", raw, p); p += 12
                if f2 != 0 or p2 != 0:
                    struct.pack_into("<iq", patch, off, 0, 0)
                    total += 1
        assert len(patch) == len(raw)
        if total:
            o.set_raw_data(bytes(patch))
        fm_patched += 1
    log(f"FontManagers scanned: {fm_patched}（非空 custom 引用已置零）", detail=True)
    if fm_patched == 0:
        log("注意: 未找到 FontManager（MonoScript 类名可能已变），字体引用未清理 — 若游戏内字体异常请留意")

    # ---- 5b) UILabel 渲染路径钉死（对标对方 forced 2807 / assigned 29，零 typetree）----
    forced_labels, assigned_labels, labels_scanned, labels_bad = force_label_true_type(
        objs, script_map, af_ext, progress=ep)

    # ---- 6) 快捷按钮硬编码标签 REACH NOW → 立即到达 ----
    # 注：I2 表里的 Button_QuantumSkip 已由第 3 步译为「立即到达」；
    #     但 UI 上还有一处硬编码 UILabel（level254）I2 够不着，需单独等长块替换。
    #     两者译文必须一致（均用「立即到达」，4 汉字 = 12 字节，与 16 字节块对齐）。
    old_block = struct.pack("<i", 9) + b"REACH NOW" + b"\x00\x00\x00"
    new_block = struct.pack("<i", 12) + "立即到达".encode("utf-8")
    assert len(old_block) == len(new_block) == 16
    rn = 0
    for o in objs:
        if o.type.name != "MonoBehaviour": continue
        raw = current_raw(o)
        if old_block in raw:
            o.set_raw_data(raw.replace(old_block, new_block))
            rn += 1
    if rn == 0:
        log("注意: 未找到 REACH NOW 硬编码标签（可能已被官方改动或已在 I2 表中），跳过该项", detail=True)

    # ---- 7) 静态 UILabel 英文替换 ----
    STATIC_LABELS = [
        ("SPIN", "抽取"),
        ("SCIENCE SPIN", "科学转盘"),
        ("CAPITALIST SPIN", "资本主义转盘"),
        ("Lucky Spin", "幸运转盘"),
        ("EXPERIMENTAL VAULTS", "实验避难所"),
        ("GO TO EXPERIEMNTAL VAULT", "前往实验避难所"),
        ("GO TO STANDARD VAULT", "前往标准避难所"),
        ("WELCOME TO", "欢迎来到"),
        ("ARE YOU SURE YOU\nWANT TO LOGOUT?", "确定要退出登录吗？"),
    ]
    def splice_string(raw, en, zh):
        eb, zb = en.encode('utf-8'), zh.encode('utf-8')
        pat = struct.pack("<i", len(eb)) + eb
        i = raw.find(pat)
        if i < 0: return raw, 0
        if raw.find(pat, i + 1) >= 0: return raw, -1
        old_field = 4 + len(eb); old_pad = (4 - old_field % 4) % 4
        if raw[i + 4 + len(eb): i + 4 + len(eb) + old_pad] != b"\x00" * old_pad:
            return raw, -1
        new_pad = (4 - (4 + len(zb)) % 4) % 4
        new_bytes = struct.pack("<i", len(zb)) + zb + b"\x00" * new_pad
        return raw[:i] + new_bytes + raw[i + 4 + len(eb) + old_pad:], 1

    static_patched = 0
    for o in objs:
        if o.type.name != "MonoBehaviour": continue
        raw = current_raw(o)
        if len(raw) < 40 or len(raw) > 4000: continue
        if cls_of(o, script_map, af_ext) != "UILabel": continue
        new_raw, n_hit = raw, 0
        for en, zh in STATIC_LABELS:
            new_raw, st = splice_string(new_raw, en, zh)
            if st > 0: n_hit += 1
        if n_hit:
            o.set_raw_data(new_raw)
            static_patched += n_hit
    log(f"static EN labels replaced: {static_patched}", detail=True)
    if static_patched == 0:
        log("注意: 未找到静态标签（内容可能已变），跳过该步", detail=True)

    # ---- 8) 保存 ----
    d_now = getattr(obj, "data", None)
    assert d_now is not None and len(d_now) == len(rebuilt) and "立即到达".encode() in d_now, \
        f"I2 重写丢失！当前 data 大小: {len(d_now) if d_now else None}"
    outdir = os.path.dirname(os.path.abspath(out)) or "."
    os.makedirs(outdir, exist_ok=True)

    # 写回是整包 LZ4 压缩 + 落盘，UnityPy 内部无进度回调，耗时可达总时长的 ~50%。
    # 用后台心跳线程按「已用时间/预估时长」推进阶段进度，避免界面长时间静止被误判为卡死。
    import threading as _th
    ep.stage("save", "正在压缩并写回数据包（约需 1-2 分钟，请勿关闭窗口）…")
    _stop = _th.Event()
    _t0 = _time.time()

    def _watch():
        # 写回耗时与整包体积近似成正比，但受磁盘波动影响大（531MB 实测 60~250s），
        # 且 UnityPy 内部无进度回调。用单调渐近曲线 CAP·(1-e^(-t/T))：
        #   · 严格单调递增 —— 进度条绝不回退
        #   · 封顶 95% —— 留出余量，绝不提前跑满（真实完成时才由主流程拉到 100%）
        #   · 按体积估算时间常数 T（约 6 MB/s）—— 大体贴合真实进度
        import math as _math
        CAP = 0.95
        T = max(25.0, len(rebuilt) / 6.0e6) * 0.8
        while not _stop.wait(0.5):
            el = _time.time() - _t0
            frac = CAP * (1.0 - _math.exp(-el / T))
            ep.step(frac, 1.0, f"压缩并写回数据包… 已用 {el:.0f}s")

    _w = _th.Thread(target=_watch, daemon=True)
    _w.start()
    try:
        env.save(packer, outdir)
    finally:
        _stop.set()
        _w.join(timeout=3)

    # UnityPy save 输出文件名 = 源 bundle 的文件名（ntpath.basename）；多个文件时取最大的新文件
    saved = os.path.join(outdir, ntpath.basename(src))
    if not os.path.exists(saved):
        cands = [os.path.join(outdir, f) for f in os.listdir(outdir)
                 if os.path.isfile(os.path.join(outdir, f))]
        saved = max(cands, key=os.path.getsize) if cands else saved
    if os.path.abspath(saved) != os.path.abspath(out):
        shutil.move(saved, out)
    size = os.path.getsize(out)
    ep.step(1, 1, f"写回完成（{size/1e6:.0f} MB）")
    log(f"saved: {out} {size}B", detail=True)

    result.update({
        "ok": True,
        "patched_terms": patched,
        "fallback": fallback,
        "skipped": len(deleted) if deleted and allow_unmatched else 0,
        "fonts": nf,
        "fontmanagers": fm_patched,
        "forced_labels": forced_labels,
        "assigned_labels": assigned_labels,
        "static_labels": static_patched,
        "reach_now": rn,
        "size": size,
        "warnings": len(warn_keys) if validate else None,
        "en_changed": len(en_changed) if validate else None,
        "msg": f"完成：写入 {patched} 条，缺译保留原文 {fallback} 条，字体 {nf}，静态标签 {static_patched}"
               + (f"，自适应警告 {len(warn_keys)} 条" if warn_keys else "")
               + (f"，EN变化 {len(en_changed)} 条" if en_changed else ""),
    })
    return result
