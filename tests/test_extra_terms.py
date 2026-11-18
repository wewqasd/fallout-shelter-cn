#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_extra_terms.py — 新增词条（data/extra_terms.json）写包逻辑的离线回归测试。

不依赖游戏原包：用合成的最小 I2 blob 验证
  1) 新增 term 会被插入且 term 计数同步 +N；
  2) 新增 term 的值、LC 槽位正确，可被 parse_terms 重新读出；
  3) 尾部（footer）字节原样保留、最后一条原 term 不变；
  4) 幂等：对产物再跑一遍，字节完全一致且不再新增。

用法: python tests/test_extra_terms.py
"""
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from fs_cn import patcher  # noqa: E402

ANCHOR = "Achievement_Xbox_Completed_01".encode()
LC = 6


def term_bytes(key, vals, fc=b"\x00" * 8):
    tail = struct.pack("<i", LC) + b"\x00" * (4 * LC)
    tail += struct.pack("<i", LC) + b"\x00" * (4 * LC)
    return patcher.rebuild_term(key.encode() if isinstance(key, str) else key,
                               fc, vals, len(vals), tail)


def make_blob(terms, footer=b"FOOTER-DATA"):
    """合成 blob：52B 头部填充 + term 计数 + terms + footer。"""
    body = b"".join(term_bytes(k, v) for k, v in terms)
    header = b"\x00" * 52
    blob = header + struct.pack("<i", len(terms)) + body + footer
    return blob


def main():
    base_terms = [
        (ANCHOR.decode(), ["Made 25 choices", "es", "fr", "it", "de", "ru"]),
        ("Ghoul_Name", ["Feral Ghoul", "es", "fr", "it", "de", "ru"]),
        ("Ghoul_Name_Plural", ["Feral Ghouls", "es", "fr", "it", "de", "ru"]),
    ]
    blob = make_blob(base_terms)
    terms, last_pos, lc, first = patcher.parse_terms(blob)
    assert len(terms) == 3, terms
    assert struct.unpack_from("<i", blob, first - 4)[0] == 3

    translations = {"Ghoul_Name": "狂尸鬼", "Ghoul_Name_Plural": "狂尸鬼"}
    extra = {"QuestMeleeScorched_Name": "近战辐尸人",
             "QuestMeleeScorched_Name_Plural": "近战辐尸人",
             "_注释": "应被忽略"}

    new, patched, fallback, added = patcher.rebuild_i2_table(
        blob, terms, first, last_pos, lc, translations, extra_terms=extra)
    assert added == 2, added
    assert patched == 2, patched
    assert struct.unpack_from("<i", new, first - 4)[0] == 5

    t2, last2, lc2, first2 = patcher.parse_terms(new)
    assert len(t2) == 5, len(t2)
    by = {t[0].decode(): t for t in t2}
    assert by["QuestMeleeScorched_Name"][2] == ["近战辐尸人"] * LC
    assert by["QuestMeleeScorched_Name_Plural"][2] == ["近战辐尸人"] * LC
    assert by["Ghoul_Name"][2] == ["狂尸鬼"] * LC
    assert "_注释" not in by, "以 _ 开头的注释键不应写入包内"
    # 最后一条原 term 不变、footer 原样
    assert t2[-1][0].decode() == "Ghoul_Name_Plural", t2[-1][0]
    assert new[-(len(blob) - last_pos):] == blob[last_pos:]

    # 幂等：再跑一遍，字节一致、不再新增
    new2, _p, _f, added2 = patcher.rebuild_i2_table(
        new, t2, first2, last2, lc2, translations, extra_terms=extra)
    assert added2 == 0, added2
    assert new2 == new, "二次重建应逐字节一致"

    print("OK: 新增词条插入 / 计数 / 尾部 / 幂等 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
