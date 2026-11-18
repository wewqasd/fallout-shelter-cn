#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""force_daily_objective.py — 【测试辅助，不会打进 EXE】把存档里某个每日目标强制改成
「击杀随机敌人（不用武器）」目标，用来验证「敌人名 term」相关的汉化修复。

背景：每日目标里 `RequirementKillEnemy.m_isRandom` 会在全部 `EEnemyType` 里随机，
没有对应 `_Name`/`_Name_Plural` 词条的敌人（2.7.0 起的 Scorched/Enclave/Synth 系列）
会显示内部枚举名。正常游戏里要等目标随机到这些敌人才能复现，本工具直接改存档把
`enemyTypeTarget` 钉死成指定敌人，便于一次复现/验证。

存档格式（Assembly-CSharp 反编译确认，PersistenceManager / StringCipher）：
    .sav = Base64( AES-256-CBC( JSON ) )
    passphrase = StringCipher.GeneratePassPhrase("PlayerData") = "UGxheWVy"
    key  = PBKDF2-HMAC-SHA1(passphrase, salt=IV, 1000 次, 32 字节)
    IV   = UTF-8("tu89geji340t89u2")

用法：
    pip install pycryptodome
    python tools/force_daily_objective.py "C:/Users/<你>/AppData/Local/FalloutShelter/Vault4.sav" \
        --enemy QuestMeleeScorched --level 12
    # 还原：把生成的 .sav.bak-test 覆盖回去即可（或游戏目录里自带的 .sav.bkp）

注意：**必须在游戏关闭时**改存档；工具自动备份为 `<存档>.bak-test`。
"""
import argparse
import base64
import hashlib
import json
import os
import shutil
import sys

IV = b"tu89geji340t89u2"
PASSPHRASE = b"UGxheWVy"          # GeneratePassPhrase("PlayerData")


def _crypto():
    try:
        from Crypto.Cipher import AES
    except ImportError:
        sys.exit("需要 pycryptodome：pip install pycryptodome")
    return AES


def _key():
    return hashlib.pbkdf2_hmac("sha1", PASSPHRASE, IV, 1000, 32)


def decrypt(path):
    AES = _crypto()
    raw = open(path, "rb").read()
    ct = base64.b64decode(raw)
    pt = AES.new(_key(), AES.MODE_CBC, IV).decrypt(ct)
    return pt[:-pt[-1]].decode("utf-8")


def encrypt(path, text):
    AES = _crypto()
    data = text.encode("utf-8")
    pad = 16 - len(data) % 16
    data += bytes([pad]) * pad
    ct = AES.new(_key(), AES.MODE_CBC, IV).encrypt(data)
    open(path, "wb").write(base64.b64encode(ct))


def main():
    ap = argparse.ArgumentParser(description="把存档里的每日目标改成「击杀随机敌人」，仅用于测试")
    ap.add_argument("save", help="VaultN.sav 路径（游戏需已关闭）")
    ap.add_argument("--enemy", default="QuestMeleeScorched",
                    help="EEnemyType 枚举名，默认 QuestMeleeScorched")
    ap.add_argument("--objective", default="RandomEnemyKilledUnarmed",
                    help="目标 ID，默认 RandomEnemyKilledUnarmed（每日目标池里存在）")
    ap.add_argument("--level", type=int, default=12,
                    help="incrementLevel（目标数 = base + level×增量，默认 12 → 显示 13）")
    ap.add_argument("--slot", type=int, default=0, help="替换第几个目标槽（默认 0）")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写回")
    args = ap.parse_args()

    if not os.path.isfile(args.save):
        sys.exit(f"找不到存档: {args.save}")

    text = decrypt(args.save)
    data = json.loads(text)
    om = data.get("objectiveMgr") or {}
    slots = om.get("slotArray") or []
    if not slots:
        sys.exit("存档里没有 objectiveMgr.slotArray（槽位为空），换一个存档再试")

    idx = min(max(args.slot, 0), len(slots) - 1)
    old = slots[idx].get("objective", {})
    slots[idx]["objective"] = {
        "objectiveID": args.objective,
        "requirements": [{
            "requirementID": "r1",
            "satisfied": False,
            "currentNumberEnemiesToKill": 0,
            # TryGetEnum 读的是字符串（Enum.Parse），枚举名必须完全一致
            "enemyTypeTarget": args.enemy,
            "usedWeapons": [],
        }],
        "completed": False,
        "incrementLevel": args.level,
    }
    print(f"槽位 {idx}: {old.get('objectiveID')} → {args.objective} / {args.enemy} / incLevel={args.level}")
    if args.dry_run:
        return 0

    backup = args.save + ".bak-test"
    if not os.path.exists(backup):
        shutil.copy2(args.save, backup)
        print(f"已备份: {backup}")
    encrypt(args.save, json.dumps(data, separators=(",", ":"), ensure_ascii=False))
    print("写回完成。启动游戏 → 每日报告/目标 查看效果；还原请用 .bak-test 覆盖。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
