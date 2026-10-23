#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compare_exe.py — 逐成员对比两个 PyInstaller onefile EXE，定位 md5 差异来源。

用途：验证「本地构建 vs GitHub Actions 构建」是否只差在环境因素（系统 DLL、
内嵌的构建机绝对路径），而不是业务内容（翻译表、字体、我们自己的模块）。

用法：
    python tools/compare_exe.py A.exe B.exe [-v] [--json out.json]

输出：
  1. PE 头 TimeDateStamp / Checksum（PyInstaller 默认写入构建时刻）
  2. CArchive 成员集合与逐成员 sha256：相同 / 不同 / 单边
  3. PYZ.zlib 内部逐模块 sha256，并对有差异的模块抓取内嵌的绝对路径

零依赖（仅标准库），可跨平台读取 Windows 产物。
"""
from __future__ import annotations

import hashlib
import json
import marshal
import re
import struct
import sys
import zlib

COOKIE_MAGIC = b"MEI\014\013\012\013\016"
COOKIE_FMT = "!8sIIII64s"
COOKIE_LEN = struct.calcsize(COOKIE_FMT)
TOC_FMT = "!IIIIBc"
TOC_LEN = struct.calcsize(TOC_FMT)
PYZ_MAGIC = b"PYZ\0"


# ---------------------------------------------------------------- PE 头
def pe_header_info(path: str) -> dict:
    """读 PE 头里的 TimeDateStamp 与 Checksum（PyInstaller 会重写这两处）。"""
    with open(path, "rb") as fp:
        mz = fp.read(0x40)
        if mz[:2] != b"MZ":
            return {}
        e_lfanew = struct.unpack_from("<I", mz, 0x3C)[0]
        fp.seek(e_lfanew)
        pe = fp.read(4 + 20 + 68)
        if pe[:4] != b"PE\0\0":
            return {}
        ts = struct.unpack_from("<I", pe, 8)[0]
        # COFF(20B) 之后是 OptionalHeader，其 Checksum 在偏移 64
        checksum = struct.unpack_from("<I", pe, 4 + 20 + 64)[0]
    return {"timestamp": ts, "checksum": checksum}


# ------------------------------------------------------- CArchive (PKG)
def _find_cookie(fp) -> int:
    fp.seek(0, 2)
    end = fp.tell()
    chunk = 1 << 20
    pos = end
    while pos >= len(COOKIE_MAGIC):
        start = max(pos - chunk, 0)
        fp.seek(start)
        buf = fp.read(pos - start)
        i = buf.rfind(COOKIE_MAGIC)
        if i != -1:
            return start + i
        pos = start + len(COOKIE_MAGIC) - 1
    return -1


def parse_carchive(path: str) -> dict:
    """解析 onefile EXE 尾部的 CArchive，返回 cookie 信息与 TOC。"""
    with open(path, "rb") as fp:
        cookie_off = _find_cookie(fp)
        if cookie_off < 0:
            raise SystemExit(f"{path}: 找不到 CArchive cookie")
        fp.seek(cookie_off)
        cookie = fp.read(COOKIE_LEN)
        _magic, alen, toc_off, toc_len, pyvers, pylib = struct.unpack(COOKIE_FMT, cookie)
        end_off = cookie_off + COOKIE_LEN
        start_off = end_off - alen

        fp.seek(start_off + toc_off)
        data = fp.read(toc_len)

        toc = {}
        pos = 0
        while pos < len(data):
            (entry_len, offset, dlen, ulen, cflag, typ) = struct.unpack_from(TOC_FMT, data, pos)
            pos += TOC_LEN
            name_len = entry_len - TOC_LEN
            name = data[pos : pos + name_len].rstrip(b"\0").decode("utf-8")
            pos += name_len
            toc[name] = {
                "offset": offset,
                "clen": dlen,
                "ulen": ulen,
                "cflag": cflag,
                "type": typ.decode("ascii", "replace"),
            }

        return {
            "path": path,
            "pe": pe_header_info(path),
            "pyvers": pyvers,
            "pylib": pylib.rstrip(b"\0").decode("utf-8", "replace"),
            "archive_len": alen,
            "start_off": start_off,
            "toc": toc,
            "_fp_path": path,
        }


def extract_member(arc: dict, name: str) -> bytes:
    e = arc["toc"][name]
    with open(arc["path"], "rb") as fp:
        fp.seek(arc["start_off"] + e["offset"])
        data = fp.read(e["clen"])
    return zlib.decompress(data) if e["cflag"] else data


def hash_members(arc: dict) -> dict:
    """逐成员抽取并算 sha256（大文件只算一次）。"""
    out = {}
    with open(arc["path"], "rb") as fp:
        for name, e in arc["toc"].items():
            fp.seek(arc["start_off"] + e["offset"])
            data = fp.read(e["clen"])
            if e["cflag"]:
                data = zlib.decompress(data)
            out[name] = {
                "sha256": hashlib.sha256(data).hexdigest(),
                "type": e["type"],
                "ulen": len(data),
            }
    return out


# -------------------------------------------------------------- PYZ
def parse_pyz(blob: bytes) -> dict:
    """解析 PYZ（PyInstaller 的 ZlibArchive）：返回 name -> (offset, length)。"""
    if blob[:4] != PYZ_MAGIC:
        raise SystemExit("PYZ magic 不匹配")
    toc_off = struct.unpack_from("!i", blob, 8)[0]
    toc = marshal.loads(blob[toc_off:])
    out = {}
    for name, entry in toc:
        # entry = (typecode, offset, length)
        _typ, off, ln = entry[0], entry[1], entry[2]
        out[name] = (off, ln)
    return out


def hash_pyz_modules(blob: bytes) -> dict:
    out = {}
    for name, (off, ln) in parse_pyz(blob).items():
        raw = blob[off : off + ln]
        try:
            code = zlib.decompress(raw)
        except zlib.error:
            code = raw
        out[name] = hashlib.sha256(code).hexdigest()
    return out


_PATH_RE = re.compile(rb"(?:[A-Za-z]:[\\/]|\\\\[A-Za-z0-9_.\-]+[\\/])[^\x00\"'<>|\r\n]{2,220}")


def paths_in(blob: bytes, limit: int = 12) -> list[str]:
    seen, out = set(), []
    for m in _PATH_RE.finditer(blob):
        s = m.group(0).decode("utf-8", "replace")
        key = s
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= limit:
            break
    return out


# ------------------------------------------------------------ 对比
def compare(a_path: str, b_path: str, verbose: bool = False) -> dict:
    A, B = parse_carchive(a_path), parse_carchive(b_path)
    ha, hb = hash_members(A), hash_members(B)

    only_a = sorted(set(ha) - set(hb))
    only_b = sorted(set(hb) - set(ha))
    common = sorted(set(ha) & set(hb))
    same = [n for n in common if ha[n]["sha256"] == hb[n]["sha256"]]
    diff = [n for n in common if ha[n]["sha256"] != hb[n]["sha256"]]

    report = {
        "a": {"path": a_path, "pe": A["pe"], "pyvers": A["pyvers"], "pylib": A["pylib"],
              "members": len(ha), "archive_len": A["archive_len"]},
        "b": {"path": b_path, "pe": B["pe"], "pyvers": B["pyvers"], "pylib": B["pylib"],
              "members": len(hb), "archive_len": B["archive_len"]},
        "identical": same,
        "differing": [{"name": n, "type": ha[n]["type"], "ulen": ha[n]["ulen"],
                       "sha_a": ha[n]["sha256"][:16], "sha_b": hb[n]["sha256"][:16]} for n in diff],
        "only_a": [{"name": n, "ulen": ha[n]["ulen"], "type": ha[n]["type"]} for n in only_a],
        "only_b": [{"name": n, "ulen": hb[n]["ulen"], "type": hb[n]["type"]} for n in only_b],
    }

    # PYZ 内部逐模块
    pyz_name = next((n for n, e in A["toc"].items() if e["type"] == "z"), None)
    if pyz_name and pyz_name in B["toc"]:
        ma = hash_pyz_modules(extract_member(A, pyz_name))
        mb = hash_pyz_modules(extract_member(B, pyz_name))
        d_mods = sorted(n for n in set(ma) & set(mb) if ma[n] != mb[n])
        report["pyz"] = {
            "member": pyz_name,
            "modules_a": len(ma),
            "modules_b": len(mb),
            "modules_same": len([n for n in set(ma) & set(mb) if ma[n] == mb[n]]),
            "modules_diff": d_mods,
            "modules_only_a": sorted(set(ma) - set(mb)),
            "modules_only_b": sorted(set(mb) - set(ma)),
        }
        if verbose and d_mods:
            # 抓差异模块里内嵌的绝对路径，验证是否为构建机路径差异
            rep = {}
            for name in d_mods[:40]:
                off, ln = parse_pyz(extract_member(A, pyz_name))[name]
                blob_a = extract_member(A, pyz_name)[off : off + ln]
                off_b, ln_b = parse_pyz(extract_member(B, pyz_name))[name]
                blob_b = extract_member(B, pyz_name)[off_b : off_b + ln_b]
                pa, pb = paths_in(zlib.decompress(blob_a)), paths_in(zlib.decompress(blob_b))
                rep[name] = {"a_paths": pa, "b_paths": pb}
            report["pyz"]["path_evidence"] = rep
    return report


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("-")]
    verbose = "-v" in argv or "--verbose" in argv
    json_out = None
    if "--json" in argv:
        json_out = argv[argv.index("--json") + 1]
        args = [a for a in args if a != json_out]
    if len(args) != 2:
        print(__doc__)
        return 2

    r = compare(args[0], args[1], verbose)

    print("=" * 74)
    print("PE 头")
    for k in ("a", "b"):
        pe = r[k]["pe"]
        print(f"  {k}: TimeDateStamp={pe.get('timestamp')}  Checksum=0x{pe.get('checksum', 0):08x}")
    print(f"  Python 版本魔数 {r['a']['pyvers']} vs {r['b']['pyvers']}；"
          f"pylib {r['a']['pylib']!r} vs {r['b']['pylib']!r}")
    print(f"  CArchive 长度 {r['a']['archive_len']} vs {r['b']['archive_len']}")
    print("=" * 74)
    print(f"CArchive 成员：A={r['a']['members']} B={r['b']['members']}；"
          f"完全相同 {len(r['identical'])}，内容不同 {len(r['differing'])}，"
          f"仅 A {len(r['only_a'])}，仅 B {len(r['only_b'])}")
    if r["differing"]:
        print("\n-- 内容不同的成员 --")
        for d in r["differing"]:
            print(f"  [{d['type']}] {d['name']}  ({d['ulen']} B)  {d['sha_a']} ≠ {d['sha_b']}")
    if r["only_a"]:
        print("\n-- 仅 A 有 --")
        for d in r["only_a"]:
            print(f"  [{d['type']}] {d['name']}  ({d['ulen']} B)")
    if r["only_b"]:
        print("\n-- 仅 B 有 --")
        for d in r["only_b"]:
            print(f"  [{d['type']}] {d['name']}  ({d['ulen']} B)")

    if "pyz" in r:
        p = r["pyz"]
        print("\n" + "=" * 74)
        print(f"PYZ 内部：A={p['modules_a']} 模块 B={p['modules_b']}；"
              f"字节相同 {p['modules_same']}，不同 {len(p['modules_diff'])}")
        if p["modules_diff"]:
            print(f"-- 不同的模块（{len(p['modules_diff'])}）--")
            for n in p["modules_diff"]:
                print(f"  {n}")
        for side in ("modules_only_a", "modules_only_b"):
            if p[side]:
                print(f"-- 仅 {side[-1].upper()} 有：{p[side]}")

    if json_out:
        with open(json_out, "w", encoding="utf-8") as fp:
            json.dump(r, fp, ensure_ascii=False, indent=1)
        print(f"\nJSON 已写入 {json_out}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
