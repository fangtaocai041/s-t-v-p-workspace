#!/usr/bin/env python3
"""
规则2: 操作前必须备份 — MCP配置 / .git目录 / 关键文件 / 项目目录。

用法:
    python scripts/backup.py --mcp                # 备份 MCP 配置
    python scripts/backup.py --git <project>      # 备份指定项目的 .git 目录
    python scripts/backup.py --file <path>        # 备份单个文件
    python scripts/backup.py --all                # 全量备份
    python scripts/backup.py --list               # 列出已有备份
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKUP_ROOT = ROOT / ".reasonix" / "backups"
MCP_SOURCE = Path.home() / ".reasonix"


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def backup_mcp() -> Path:
    """备份 MCP 配置到 .reasonix/backups/mcp_<timestamp>/"""
    ts = timestamp()
    dest = BACKUP_ROOT / f"mcp_{ts}"
    dest.mkdir(parents=True, exist_ok=True)

    config_file = MCP_SOURCE / "config.json"
    if config_file.exists():
        shutil.copy2(config_file, dest / "config.json")

    mcp_servers = MCP_SOURCE / "mcp-servers"
    if mcp_servers.exists():
        shutil.copytree(mcp_servers, dest / "mcp-servers", dirs_exist_ok=True)

    print(f"✅ MCP 配置已备份到: {dest}")
    return dest


def backup_git(project: str) -> Path:
    """备份子项目的 .git 目录（创建 git bundle）。"""
    ts = timestamp()
    dest = BACKUP_ROOT / f"git_{project}_{ts}"
    dest.mkdir(parents=True, exist_ok=True)

    import subprocess

    proj_root = ROOT / project
    git_dir = proj_root / ".git"
    if not git_dir.exists():
        print(f"⚠️  {project} 没有 .git 目录")
        return dest

    # 用 git bundle 打包
    bundle_file = dest / f"{project}.bundle"
    result = subprocess.run(
        ["git", "-C", str(proj_root), "bundle", "create", str(bundle_file), "--all"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"✅ {project} git bundle 已创建: {bundle_file}")
    else:
        print(f"❌ git bundle 创建失败: {result.stderr}")

    return dest


def backup_file(filepath: str) -> Path:
    """备份单个文件。"""
    ts = timestamp()
    dest = BACKUP_ROOT / f"file_{ts}"
    dest.mkdir(parents=True, exist_ok=True)

    src = Path(filepath)
    if not src.is_absolute():
        src = ROOT / src
    if src.exists():
        shutil.copy2(src, dest / src.name)
        print(f"✅ 文件已备份: {dest / src.name}")
    else:
        print(f"❌ 文件不存在: {src}")

    return dest


def backup_all() -> None:
    """全量备份: MCP 配置 + 全部子项目 git + 关键配置。"""
    print("═══ 全量备份 ═══\n")
    backup_mcp()

    projects = [
        "fish-ecology-assistant", "cognitive-search-engine", "eon-core",
        "porpoise-agent", "coilia-agent", "culter-agent", "conflict-arbiter",
    ]
    for proj in projects:
        git_dir = ROOT / proj / ".git"
        if git_dir.exists():
            backup_git(proj)

    # 备份关键配置文件
    for cfg in ["coordination.yaml", "VERSION.yaml", "RULES.md"]:
        p = ROOT / cfg
        if p.exists():
            backup_file(str(p))

    print(f"\n✅ 全量备份完成 → {BACKUP_ROOT}")


def list_backups() -> None:
    """列出已有备份。"""
    if not BACKUP_ROOT.exists():
        print("暂无备份")
        return
    for d in sorted(BACKUP_ROOT.iterdir(), reverse=True):
        size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        print(f"  {d.name:40s}  {size // 1024} KB")


def main() -> int:
    parser = argparse.ArgumentParser(description="操作前备份工具")
    parser.add_argument("--mcp", action="store_true", help="备份 MCP 配置")
    parser.add_argument("--git", type=str, metavar="PROJECT", help="备份指定项目的 .git")
    parser.add_argument("--file", type=str, metavar="PATH", help="备份单个文件")
    parser.add_argument("--all", action="store_true", help="全量备份")
    parser.add_argument("--list", action="store_true", help="列出已有备份")
    args = parser.parse_args()

    if args.list:
        list_backups()
        return 0
    if args.all:
        backup_all()
        return 0
    if args.mcp:
        backup_mcp()
    if args.git:
        backup_git(args.git)
    if args.file:
        backup_file(args.file)
    if not any([args.mcp, args.git, args.file, args.all]):
        parser.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
