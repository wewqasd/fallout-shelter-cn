#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gui.py — 辐射避难所 一键汉化 GUI（EXE 主程序，fs_cn 包）。

功能：
  1) 自动定位游戏目录（game_dir 的多源扫描）；找不到则让玩家浏览选择
  2) 「一键汉化」：先提醒备份 data.unity3d -> data.unity3d.bak.v5，再跑版本自适应手术
  3) 实时进度（跑在后台线程，queue 回主线程刷新）
  4) 「一键还原」：从 .bak.v5 还原原版
  5) 内置自检汇报：写入条数 / 缺译保留原文 / 警告 / 字体 / 残留

入口：源码 python -m fs_cn.gui；EXE 由 tools/build_exe.spec 打包。
（仅 Windows/Tk 用；纯 stdlib，无额外依赖。）
"""
import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from . import __version__
from .patcher import patch_bundle
from .resources import load_default_resources
from .game_dir import find_game_dir, backup_bundle, restore_bundle

# Windows 控制台编码兼容：selfcheck 输出中文时，cp1252 等旧编码会抛
# UnicodeEncodeError（GitHub Actions runner / cmd 默认非 UTF-8）——兜底 replace。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except Exception:
        pass


class App:
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.game_dir = tk.StringVar()
        self.status = tk.StringVar(value="就绪")
        self.busy = False

        root.title(f"辐射避难所 一键汉化 v{__version__}")
        root.geometry("640x520")
        root.minsize(560, 440)

        pad = {"padx": 10, "pady": 4}

        # 游戏目录
        frm_dir = tk.Frame(root)
        frm_dir.pack(fill="x", **pad)
        tk.Label(frm_dir, text="游戏目录:").pack(side="left")
        self.ent_dir = tk.Entry(frm_dir, textvariable=self.game_dir, width=40)
        self.ent_dir.pack(side="left", fill="x", expand=True)
        tk.Button(frm_dir, text="浏览", command=self.browse).pack(side="left", padx=(6, 0))
        tk.Button(frm_dir, text="自动定位", command=self.auto_find).pack(side="left", padx=(6, 0))

        # 引导提示
        tk.Label(root, justify="left", fg="#b03a2e", anchor="w",
                 text="请选择 Fallout Shelter 游戏安装文件夹（含 FalloutShelter_Data 子文件夹）",
                 font=("Microsoft YaHei", 9, "bold")).pack(fill="x", **pad)

        # 按钮
        frm_btn = tk.Frame(root)
        frm_btn.pack(fill="x", **pad)
        self.btn_patch = tk.Button(frm_btn, text="一键汉化", width=14,
                                   command=lambda: threading.Thread(target=self.do_patch, daemon=True).start())
        self.btn_patch.pack(side="left")
        self.btn_restore = tk.Button(frm_btn, text="一键还原", width=14,
                                     command=lambda: threading.Thread(target=self.do_restore, daemon=True).start())
        self.btn_restore.pack(side="left", padx=(10, 0))
        tk.Label(frm_btn, textvariable=self.status, fg="#555", anchor="w").pack(side="left", fill="x", expand=True, padx=(10, 0))

        # 进度区
        self.txt = scrolledtext.ScrolledText(root, height=18, state="disabled", font=("Consolas", 10))
        self.txt.pack(fill="both", expand=True, **pad)

        self.hint = tk.Label(
            root, justify="left", fg="#666", anchor="w",
            text="提示：汉化会先备份 data.unity3d → data.unity3d.bak.v5；\n"
                 "若游戏更新导致汉化失效，可点「一键还原」恢复原版后重跑。",
            font=("Microsoft YaHei", 9))
        self.hint.pack(fill="x", side="bottom", **pad)

        self.log(f"辐射避难所 一键汉化工具 v{__version__}\n")
        self.auto_find()

        self.root.after(80, self._drain)
        # 拦截窗口关闭：汉化进行中先确认，然后强制结束进程
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------- UI 辅助 ----------------
    def _on_close(self):
        """窗口 X 关闭：汉化中先确认；随后 destroy + 强制退出进程。

        为什么强制退出：tkinter + PyInstaller windowed 下 mainloop 返回后
        Tcl/Tk 资源与后台线程可能让解释器挂起不退出（任务管理器残留、
        2GB 内存不释放）。os._exit 绕过清理直接结束进程，内存全部归还 OS。
        """
        if self.busy and not messagebox.askyesno(
                "汉化进行中", "汉化仍在进行，确定现在退出？\n"
                "（中断的汉化可能不完整，原版备份 data.unity3d.bak.v5 可一键还原）",
                parent=self.root):
            return
        try:
            self.root.destroy()
        except Exception:
            pass
        os._exit(0)

    def log(self, msg):
        self.txt.configure(state="normal")
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def _set_busy(self, busy):
        self.busy = busy
        self.btn_patch.configure(state="disabled" if busy else "normal")
        self.btn_restore.configure(state="disabled" if busy else "normal")

    def _drain(self):
        try:
            while True:
                msg = self.q.get_nowait()
                self.log(msg)
        except queue.Empty:
            pass
        self.root.after(80, self._drain)

    def _err(self, msg):
        self.q.put(f"\n[错误] {msg}")

    def browse(self):
        d = filedialog.askdirectory(
            title="请选择 Fallout Shelter 游戏安装文件夹（含 FalloutShelter_Data 子文件夹）")
        if d:
            self.game_dir.set(d)

    def auto_find(self):
        g = find_game_dir(None)
        if g:
            self.game_dir.set(g)
            self.log(f"自动定位到游戏目录：{g}")
        else:
            self.log("未自动定位到游戏目录。\n请点「浏览」，选择 Fallout Shelter 游戏安装文件夹"
                     "（含 FalloutShelter_Data 子文件夹）。")

    # ---------------- 操作 ----------------
    def do_patch(self):
        if self.busy: return
        g = self.game_dir.get().strip()
        if not g or not find_game_dir(g):
            self._err("游戏目录无效（未找到 FalloutShelter_Data\\data.unity3d）。\n"
                      "请点「浏览」，选择 Fallout Shelter 游戏安装文件夹（含 FalloutShelter_Data 子文件夹）。")
            return
        self._set_busy(True)
        self.log("\n===== 开始汉化 =====")
        self.q.put(f"游戏目录：{g}")

        # 1) 备份提醒 + 备份
        ok = messagebox.askyesno(
            "备份 data.unity3d",
            "汉化前将备份原版 data.unity3d → data.unity3d.bak.v5。\n"
            "若后续想还原原版（如游戏更新），点「一键还原」即可。\n\n继续汉化？",
            parent=self.root)
        if not ok:
            self._set_busy(False)
            self.log("已取消。")
            return
        try:
            bak, created = backup_bundle(g, progress=lambda m: self.q.put(str(m)))
        except Exception as e:
            self._set_busy(False)
            self._err(str(e)); self.log("汉化中止：备份失败。"); return

        # 2) 手术
        try:
            cn, font = load_default_resources()
            bundle = os.path.join(g, "FalloutShelter_Data", "data.unity3d")
            result = patch_bundle(
                src=bundle, out=bundle,      # 原地改写（已备份到 .bak.v5）
                translations=cn, font_bytes=font,
                allow_unmatched=False, validate=True, packer="lz4",
                progress=lambda m: self.q.put(str(m)),
            )
        except ValueError as e:
            self._set_busy(False)
            self._err(str(e))
            self.log("\n汉化中止：结构校验失败或表有包无（游戏可能已大改）。\n"
                     f"原版仍备份在 data.unity3d.bak.v5，可点「一键还原」。")
            return
        except Exception as e:
            self._set_busy(False)
            self._err(str(e)); self.log("\n汉化失败（详细信息见上）。原版已备份，可「一键还原」。"); return

        self._set_busy(False)
        self.q.put(f"\n===== 汉化完成 =====")
        self.q.put(f"写入 {result['patched_terms']} 条 | 缺译保留原文 {result['fallback']} 条"
                   f" | 字体 {result['fonts']} | 静态标签 {result['static_labels']}")
        if result.get("warnings"):
            self.q.put(f"自适应警告 {result['warnings']} 条（换行/按键标记，不影响使用）")
        self.q.put("现在可从 Steam 启动游戏。启动失败/想还原 → 点「一键还原」。")
        # 释放汉化期间的占用（UnityPy 对象树等），减少关闭前的驻留内存
        try:
            import gc
            del cn, font
            gc.collect()
        except Exception:
            pass

    def do_restore(self):
        if self.busy: return
        g = self.game_dir.get().strip()
        if not g or not find_game_dir(g):
            self._err("游戏目录无效。"); return
        if not messagebox.askyesno("一键还原", f"确认从\n{g}\\FalloutShelter_Data\\data.unity3d.bak.v5\n还原原版？", parent=self.root):
            return
        self._set_busy(True)
        self.log("\n===== 还原原版 =====")
        try:
            p, ok = restore_bundle(g, progress=lambda m: self.q.put(str(m)))
            self.q.put(f"已还原：{p}")
            self.q.put("现在可从 Steam 启动游戏（原版）。")
        except Exception as e:
            self._err(str(e))
        finally:
            self._set_busy(False)


def main():
    import argparse
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--selfcheck", nargs="?", const="", metavar="BUNDLE_DIR",
                    help="无头自检：加载内嵌资源+UnityPy；若给 BUNDLE_DIR 则对其内 data.unity3d 做一次性汉化（原地）")
    a, rest = ap.parse_known_args()
    if a.selfcheck is not None:
        selfcheck(a.selfcheck)
        os._exit(0)          # selfcheck 后强制退出（防 windowed 残留）
    root = tk.Tk()
    App(root)
    root.mainloop()
    os._exit(0)              # 任一出口都强制结束进程，内存归还 OS


def selfcheck(bundle_dir):
    """自检模式（EXE 无头验证用）：验证内嵌资源 + UnityPy + 可选真patch。"""
    import hashlib
    print("== FalloutShelterCN.exe 自检 ==")
    print(f"版本: {__version__}")
    print(f"frozen={getattr(sys, 'frozen', False)} meipass={getattr(sys, '_MEIPASS', 'N/A')}")
    # 1) 资源
    cn, font = load_default_resources()
    print(f"资源: translations={len(cn)} font={len(font)}B  font_md5={hashlib.md5(font).hexdigest()[:12]}")
    # 2) UnityPy (含 Boost)
    import UnityPy
    import UnityPy.UnityPyBoost as boost
    print(f"UnityPy={getattr(UnityPy, '__file__', '?')}  Boost={getattr(boost, '__file__', '?')}")
    # 3) 可选真 patch
    if bundle_dir:
        b = os.path.join(bundle_dir, "FalloutShelter_Data", "data.unity3d")
        if not os.path.isfile(b):
            print(f"[错误] 未找到 {b}"); sys.exit(2)
        print(f"对 {b} 做一次汉化（原地）…")
        r = patch_bundle(src=b, out=b, translations=cn, font_bytes=font,
                         allow_unmatched=False, validate=True, packer="lz4",
                         progress=lambda m: print("  ", m, flush=True))
        print("RESULT:", r)
    print("自检通过 ✓")


if __name__ == "__main__":
    main()