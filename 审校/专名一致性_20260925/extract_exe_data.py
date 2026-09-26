#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_exe_data.py — 从 PyInstaller 单文件 EXE 中抽出内嵌的 data/*.json 与字体，
核对「出厂 EXE 内嵌译文」与当前翻译表是否同一版。

用法: python extract_exe_data.py <exe> <输出目录>
"""
import os
import struct
import sys
import zlib

MAGIC = b"MEI\014\013\012\013\016"
TARGETS = ("data\\translations.json", "data\\i2_dump.json", "assets\\noto_sans_sc_cn.ttf")


def main():
    exe, outdir = sys.argv[1], sys.argv[2]
    raw = open(exe, "rb").read()
    pos = raw.rfind(MAGIC)
    if pos < 0:
        print("未找到 PyInstaller cookie")
        return 1
    pkg_len, toc_pos, toc_len, pyver = struct.unpack("!IIII", raw[pos + 8:pos + 24])
    arch = len(raw) - pkg_len
    print(f"cookie@{pos} pkg_len={pkg_len} toc_len={toc_len} abi={pyver} archive_base={arch}")
    os.makedirs(outdir, exist_ok=True)
    for name in TARGETS:
        p = raw.find(name.encode("ascii"))
        if p < 0:
            print(f"  [缺失] {name}")
            continue
        off, csize, usize, flag, typ = struct.unpack("!IIIBc", raw[p - 14:p])
        blob = raw[arch + off:arch + off + csize]
        data = zlib.decompress(blob) if flag == 1 else blob
        ok = (len(data) == usize)
        dest = os.path.join(outdir, name.replace("\\", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        print(f"  {name}: off={off} csize={csize} usize={usize} flag={flag} typ={typ!r} "
              f"解出={len(data)} 尺寸{'一致' if ok else '不一致!'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
