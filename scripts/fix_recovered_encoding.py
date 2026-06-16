#!/usr/bin/env python3
"""
编码检测 + 修复脚本 — 扫描恢复目录中的文件，自动检测编码并转成 UTF-8。

背景: Windows File Recovery (winfr) 恢复的文件可能因为扇区覆盖/混编
导致 GBK/UTF-8 互读乱码。此脚本批量检测并修复。

用法:
    python scripts/fix_recovered_encoding.py                        # 交互式选择
    python scripts/fix_recovered_encoding.py --dry-run              # 只报告不修改
    python scripts/fix_recovered_encoding.py --scan C:\Recovered_Reasonix  # 指定路径
    python scripts/fix_recovered_encoding.py --fix                  # 执行修复
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ── 常见中文字符编码映射 ──
# 检测逻辑: 尝试多种编码读取，选匹配度最高的
ENCODINGS_TO_TRY = ["utf-8", "gbk", "gb2312", "gb18030", "big5", "shift_jis", "latin-1", "cp1252"]

# 文件扩展名白名单 — 只处理文本文件
TEXT_EXTENSIONS = {
    ".md", ".py", ".txt", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini",
    ".csv", ".xml", ".html", ".htm", ".css", ".js", ".ts", ".jsx", ".tsx",
    ".sh", ".bat", ".ps1", ".cmd", ".env", ".gitignore", ".dockerignore",
    ".editorconfig", ".md", ".rst", ".tex", ".bib", ".sql", ".log",
}

# 跳过大于 10MB 的文件
MAX_FILE_SIZE = 10 * 1024 * 1024

# 恢复目录
RECOVERY_DIRS = [
    "C:/Recovered_Reasonix",
    "C:/Recovered_Reasonix_All",
]


def detect_encoding(filepath: Path) -> Tuple[str, float, bytes]:
    """检测文件编码。返回 (编码, 置信度, 原始字节)。"""
    raw = filepath.read_bytes()
    if len(raw) == 0:
        return ("empty", 1.0, raw)

    results: List[Tuple[str, float]] = []

    for enc in ENCODINGS_TO_TRY:
        try:
            decoded = raw.decode(enc)
            # 计算"干净"比例 — 成功解码的字符占比
            clean_ratio = len(decoded) / len(raw)
            # 检查是否包含常见的乱码特征
            mojibake_score = 0
            # GBK 读 UTF-8 的典型乱码特征: å\x9f\xa5 这类连续高位字节
            if enc in ("latin-1", "cp1252", "iso-8859-1"):
                # 检查是否有中文字符本该出现的位置出现高位 Latin 字符
                high_chars = sum(1 for c in decoded if ord(c) > 127)
                if high_chars > len(decoded) * 0.3:
                    mojibake_score = 0.3  # 降低置信度
            results.append((enc, clean_ratio - mojibake_score))
        except (UnicodeDecodeError, UnicodeError):
            results.append((enc, 0.0))

    # 选最佳编码
    results.sort(key=lambda x: x[1], reverse=True)
    best_enc, best_score = results[0]

    # 惩罚 fallback 编码: latin-1/cp1252 永远不报错，须降权
    if best_enc in ("latin-1", "cp1252", "iso-8859-1"):
        # 检查 utf-8 是否也能解码（即使有替换）
        utf8_ok = any(e == "utf-8" and s > 0.8 for e, s in results)
        if utf8_ok:
            # 取 utf-8 的得分
            utf8_score = next(s for e, s in results if e == "utf-8")
            if utf8_score >= best_score * 0.95:
                best_enc = "utf-8"
                best_score = utf8_score
                return (best_enc, best_score, raw)

    # 特殊检测: 如果 UTF-8 不是最佳但文件中含中文字符
    if best_enc != "utf-8" and best_score < 0.9:
        # 尝试用 UTF-8 带替换方式读取，看中文是否乱码
        utf8_decoded = raw.decode("utf-8", errors="replace")
        replacement_count = utf8_decoded.count("\ufffd")
        total_chars = len(utf8_decoded)
        if replacement_count / max(total_chars, 1) > 0.05:
            # UTF-8 读取有太多替换字符 — 可能是 GBK 编码
            for gbk_enc in ["gbk", "gb2312", "gb18030"]:
                try:
                    gbk_decoded = raw.decode(gbk_enc)
                    # 检查GBK解码后是否包含中文字符且没有 \ufffd
                    has_chinese = any("\u4e00" <= c <= "\u9fff" for c in gbk_decoded)
                    if has_chinese and "\ufffd" not in gbk_decoded:
                        return (gbk_enc, 0.95, raw)
                except UnicodeDecodeError:
                    continue

    return (best_enc, best_score, raw)


def check_is_text(raw: bytes) -> bool:
    """快速检查是否为文本文件（非二进制）。"""
    if len(raw) == 0:
        return True
    # 检查前 8KB 中是否有 NULL 字节
    sample = raw[:8192]
    null_ratio = sample.count(b"\x00") / max(len(sample), 1)
    return null_ratio < 0.1


def fix_encoding(filepath: Path, dry_run: bool = False) -> Dict:
    """检测并修复单个文件的编码。"""
    result: Dict = {
        "path": str(filepath),
        "status": "ok",
        "original_enc": "unknown",
        "target_enc": "utf-8",
        "changes": False,
    }

    ext = filepath.suffix.lower()
    if ext not in TEXT_EXTENSIONS:
        result["status"] = "skipped_binary"
        return result

    if filepath.stat().st_size > MAX_FILE_SIZE:
        result["status"] = "skipped_too_large"
        return result

    raw = filepath.read_bytes()
    if not check_is_text(raw):
        result["status"] = "skipped_binary"
        return result

    enc, confidence, _ = detect_encoding(filepath)

    result["original_enc"] = enc
    result["confidence"] = confidence

    if enc == "empty":
        result["status"] = "empty"
        return result

    if enc == "utf-8" and confidence > 0.9:
        result["status"] = "already_utf8"
        return result

    if confidence < 0.3:
        result["status"] = "low_confidence"
        return result

    # 解码并重新编码为 UTF-8
    try:
        content = raw.decode(enc)
    except (UnicodeDecodeError, UnicodeError) as e:
        result["status"] = "decode_failed"
        result["error"] = str(e)
        return result

    # 检查是否有实际变化
    utf8_bytes = content.encode("utf-8")
    if utf8_bytes == raw:
        result["status"] = "same_utf8"
        return result

    result["changes"] = True
    result["original_size"] = len(raw)
    result["new_size"] = len(utf8_bytes)

    if not dry_run:
        filepath.write_bytes(utf8_bytes)
        result["status"] = "fixed"

    return result


def scan_directory(root: Path, dry_run: bool = False) -> List[Dict]:
    """扫描目录下的所有文本文件进行编码修复。"""
    results: List[Dict] = []
    total = 0
    fixed = 0
    skipped = 0

    # 跳过 .git 和二进制目录
    skip_dirs = {".git", "__pycache__", "node_modules", ".playwright-mcp",
                 ".reasonix", ".venv", "venv", ".git"}

    for filepath in root.rglob("*"):
        # 跳过目录
        if filepath.is_dir():
            continue

        # 检查是否在跳过目录中
        rel_parts = filepath.relative_to(root).parts
        if any(part in skip_dirs for part in rel_parts):
            continue

        ext = filepath.suffix.lower()
        if ext not in TEXT_EXTENSIONS:
            continue

        total += 1
        result = fix_encoding(filepath, dry_run=dry_run)
        results.append(result)

        if result["status"] == "fixed":
            fixed += 1
            print(f"  🔧 {filepath.name:40s} {result['original_enc']} → utf-8")
        elif dry_run and result.get("changes"):
            print(f"  📋 {filepath.name:40s} {result['original_enc']} → utf-8 (需修复)")
        elif result["status"] not in ("already_utf8", "same_utf8", "skipped_binary"):
            skipped += 1

    print()
    print(f"  总计: {total} 文件 | 已修复: {fixed} | 无需处理: {total - fixed - skipped} | 跳过: {skipped}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="编码检测 + 修复 — 扫描恢复目录中的乱码文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --scan C:\\Recovered_Reasonix --dry-run  # 只检测不修复
  %(prog)s --scan C:\\Recovered_Reasonix --fix       # 检测并修复
  %(prog)s --scan-all --dry-run                       # 扫描全部恢复目录
        """,
    )
    parser.add_argument("--scan", type=str, default="",
                        help="指定扫描路径")
    parser.add_argument("--scan-all", action="store_true",
                        help="扫描全部已知恢复目录")
    parser.add_argument("--dry-run", action="store_true",
                        help="只报告不修改")
    parser.add_argument("--fix", action="store_true",
                        help="执行修复（默认只报告）")

    args = parser.parse_args()

    # 确定扫描路径
    scan_paths: List[Path] = []
    if args.scan:
        scan_paths.append(Path(args.scan))
    elif args.scan_all:
        for d in RECOVERY_DIRS:
            p = Path(d)
            if p.exists():
                scan_paths.append(p)
    else:
        # 交互模式
        available = [d for d in RECOVERY_DIRS if Path(d).exists()]
        if not available:
            print("❌ 未找到恢复目录。请用 --scan 指定路径。")
            return 1
        print("可用的恢复目录:")
        for i, d in enumerate(available, 1):
            size = sum(f.stat().st_size for f in Path(d).rglob("*") if f.is_file())
            print(f"  [{i}] {d} ({size / 1024 / 1024:.1f} MB)")
        choice = input("选择要扫描的目录编号 (1-{}): ".format(len(available))).strip()
        try:
            idx = int(choice) - 1
            scan_paths.append(Path(available[idx]))
        except (ValueError, IndexError):
            print("❌ 无效选择")
            return 1

    dry_run = not args.fix  # 默认 dry-run，除非显式 --fix
    if args.dry_run:
        dry_run = True

    for scan_root in scan_paths:
        if not scan_root.exists():
            print(f"❌ 路径不存在: {scan_root}")
            continue

        print(f"\n{'='*60}")
        print(f"  📁 扫描: {scan_root}")
        print(f"  {'🔍 仅检测 (dry-run)' if dry_run else '🔧 执行修复'}")
        print(f"{'='*60}")
        print()

        results = scan_directory(scan_root, dry_run=dry_run)

        # 输出摘要
        fixed_count = sum(1 for r in results if r["status"] == "fixed")
        need_fix = sum(1 for r in results if r.get("changes") and dry_run)
        already_utf8 = sum(1 for r in results if r["status"] in ("already_utf8", "same_utf8"))
        low_conf = sum(1 for r in results if r["status"] == "low_confidence")
        errors = sum(1 for r in results if r["status"] in ("decode_failed",))

        print(f"\n  📊 扫描完成: {scan_root}")
        print(f"     ✅ 已是 UTF-8: {already_utf8}")
        print(f"     {'📋 待修复: ' if dry_run else '🔧 已修复: '}{'N/A' if dry_run else fixed_count}")
        if dry_run:
            print(f"     📋 需修复: {need_fix} (加 --fix 执行)")
        print(f"     ⚠️  低置信度: {low_conf}")
        print(f"     ❌ 解码错误: {errors}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
