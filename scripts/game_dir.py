#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""game_dir.py — 游戏目录自动定位 + 备份/还原（路线 A/B 共用，纯 stdlib，可嵌入 EXE）。

定位顺序（任一命中即返回）：
  1) --game-dir 显式指定（玩家手动）
  2) 环境变量 FALLOUT_SHELTER_DIR
  3) Steam libraryfolders.vdf 解析出的各库 -> steamapps/common/Fallout Shelter
  4) 每个就绪盘符下的 Steam/SteamLibrary 等库根
  5) 常见路径：D:/SteamGames 等

找不到 -> 返回 None，由上层让玩家拖入/粘贴目录。

比对方（fallout-shelter-zh-cn-patch）强：
  * 更全的库根来源（每个盘符 + FALLOUT_SHELTER_DIR）
  * 内置**备份/还原**（data.unity3d -> .bak.v5，--restore 一键还原）—— 对方完全没做备份。

判定是否为游戏目录：存在 <dir>/FalloutShelter_Data/data.unity3d。
"""
import os
import sys
import re
import shutil
import hashlib
import glob

GAME_FOLDER = "Fallout Shelter"
BUNDLE_REL = os.path.join("FalloutShelter_Data", "data.unity3d")


# ---------------- 判定 ----------------
def is_game_dir(path):
    """path 为游戏安装根目录（含 FalloutShelter_Data/data.unity3d）。"""
    if not path:
        return False
    return os.path.isfile(os.path.join(path, BUNDLE_REL))


def has_bundle_in(path):
    """候选可能是 安装根 / FalloutShelter_Data 子目录 / 直接是 data.unity3d 文件。返回归一化安装根。"""
    if not path:
        return None
    p = path.strip().strip('"').strip()
    if os.path.isfile(p):
        p = os.path.dirname(p)                      # 直接给了 data.unity3d？取父
    if os.path.basename(p).lower() == "falloutshelter_data":
        p = os.path.dirname(p)                      # 给了 _Data 目录？升到安装根
    return p if is_game_dir(p) else None


# ---------------- 库根收集 ----------------
def _get_steam_library_folders():
    """返回 Steam 安装根 + 所有 libraryfolders.vdf 里声明的额外库根 + 各盘 SteamLibrary/Steam。"""
    roots = []
    steam_roots = [
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        os.environ.get("ProgramFiles", r"C:\Program Files"),
    ]
    vdf_roots = []
    for base in steam_roots:
        steam_root = os.path.join(base, "Steam")
        if os.path.isdir(steam_root):
            roots.append(steam_root)
            vdf = os.path.join(steam_root, "steamapps", "libraryfolders.vdf")
            if os.path.isfile(vdf):
                try:
                    vdf_roots += _parse_libraryfolders_vdf(vdf)
                except Exception:
                    pass
    roots.extend(x for x in vdf_roots if x not in roots)

    # 每个就绪盘符下的常见 Steam 库
    for drive in _list_drives():
        for rel in ("Steam", "SteamLibrary", "SteamGames", "SteamLibrary-alt"):
            cand = os.path.join(drive, rel)
            if os.path.isdir(cand) and cand not in roots:
                roots.append(cand)
    # 常见手动路径
    for extra in ("D:\\SteamGames", "D:\\SteamLibrary", "E:\\SteamGames", "E:\\SteamLibrary"):
        if os.path.isdir(extra) and extra not in roots:
            roots.append(extra)
    return roots


def _parse_libraryfolders_vdf(vdf_path):
    """轻量解析：抓所有 "path" "...." 行（含 \\\\ 转义还原），去重。"""
    out = []
    try:
        with open(vdf_path, "r", errors="ignore") as f:
            for line in f:
                m = re.search(r'"path"\s+"([^"]+)"', line)
                if m:
                    p = m.group(1).replace("\\\\", "\\")
                    if os.path.isdir(p):
                        out.append(p)
    except Exception:
        pass
    return out


def _list_drives():
    drives = []
    if os.name == "nt":
        import string
        for L in string.ascii_uppercase:
            d = f"{L}:\\"
            if os.path.exists(d):
                drives.append(d)
    else:
        # Linux/WSL 下模拟：/mnt/[a-z] 盘
        for d in glob.glob("/mnt/[a-z]"):
            drives.append(f"{os.path.basename(d).upper()}:\\")
    return drives or [os.path.splitdrive(os.getcwd())[0]]


# ---------------- 通用候选 ----
def _collect_candidates():
    cands = []
    env = os.environ.get("FALLOUT_SHELTER_DIR")
    if env:
        cands.append(env)
    for root in _get_steam_library_folders():
        cands.append(os.path.join(root, "steamapps", "common", GAME_FOLDER))
        cands.append(os.path.join(root, "common", GAME_FOLDER))
        # 部分库直接放 Steam
        cands.append(os.path.join(root, "steamapps", "common"))
    return [c for c in cands if c]


# ---------------- 主入口 ----------------
def find_game_dir(explicit=None):
    """返回归一化游戏安装根，找不到返回 None。explicit 若给出则优先（并校验）。"""
    if explicit:
        got = has_bundle_in(explicit)
        if got:
            return got
        return None
    for c in _collect_candidates():
        got = has_bundle_in(c)
        if got:
            return got
    return None


# ---------------- 备份 / 还原 ----------------
BAK_SUFFIX = ".bak.v5"

def backup_bundle(game_dir, progress=None):
    """备份 data.unity3d -> data.unity3d.bak.v5（若 .bak 尚不存在才做，避免覆盖用户手动备份）。

    返回 (backup_path, created_bool)。"""
    src = os.path.join(game_dir, BUNDLE_REL)
    if not os.path.isfile(src):
        raise FileNotFoundError(f"未找到 {src}")
    bak = src + BAK_SUFFIX
    if os.path.exists(bak):
        if progress: progress(f"备份已存在，跳过：{bak}")
        return bak, False
    if progress:
        size = os.path.getsize(src)
        progress(f"备份 data.unity3d ({size/1e6:.0f} MB) → data.unity3d.bak.v5 …")
    shutil.copy2(src, bak)
    if progress: progress(f"备份完成：{bak}")
    return bak, True


def restore_bundle(game_dir, progress=None):
    """用 .bak.v5 还原 data.unity3d。成功返回 (restored_path, True)，无备份则返回 (None, False)。"""
    src = os.path.join(game_dir, BUNDLE_REL)
    bak = src + BAK_SUFFIX
    if not os.path.isfile(bak):
        raise FileNotFoundError(f"找不到备份 {bak}，无法还原（可能尚未打过汉化或备份被删）。")
    if progress: progress(f"正在还原 …")
    shutil.copy2(bak, src)
    if progress: progress(f"已还原原版 data.unity3d")
    return src, True


def bundle_md5(game_dir):
    src = os.path.join(game_dir, BUNDLE_REL)
    if not os.path.isfile(src):
        return None
    h = hashlib.md5()
    with open(src, "rb") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk: break
            h.update(chunk)
    return h.hexdigest()


# ---------------- CLI ----------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="游戏目录定位 + 备份/还原")
    ap.add_argument("--find", action="store_true", help="定位游戏目录并打印")
    ap.add_argument("--backup", metavar="DIR", help="备份指定游戏目录的 data.unity3d")
    ap.add_argument("--restore", metavar="DIR", help="用 .bak.v5 还原")
    ap.add_argument("--md5", metavar="DIR", help="打印 data.unity3d 的 md5")
    ap.add_argument("--explicit", metavar="DIR", help="显式游戏目录（配合 --find）")
    a = ap.parse_args()

    if a.md5:
        print(bundle_md5(a.md5) or "未找到 data.unity3d")
        sys.exit(0)
    if a.backup:
        p = find_game_dir(a.backup)
        if not p: print("游戏目录无效"); sys.exit(1)
        bp, created = backup_bundle(p, progress=print)
        print(f"backup: {bp} created={created}")
        sys.exit(0)
    if a.restore:
        p = find_game_dir(a.restore)
        if not p: print("游戏目录无效"); sys.exit(1)
        sp, ok = restore_bundle(p, progress=print)
        print(f"restored: {sp} ok={ok}")
        sys.exit(0)
    p = find_game_dir(a.explicit)
    if p:
        print(f"游戏目录: {p}")
        print(f"data.unity3d: {os.path.join(p, BUNDLE_REL)}")
    else:
        print("未自动找到游戏目录。")
        sys.exit(1)