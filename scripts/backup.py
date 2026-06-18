#!/usr/bin/env python3
"""
backup.py — Reasonix 工作区一键备份

备份所有 git 仓库推送 + 关键配置文件 + MCP 二进制 + Zotero 数据库。

用法:
    python scripts/backup.py                    # 备份到默认位置
    python scripts/backup.py --repo-only        # 只推送 git
    python scripts/backup.py --dest D:\backup   # 指定备份目录
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
BACKUP_DIR = Path(os.environ.get("REASONIX_BACKUP_DIR", str(WORKSPACE.parent / "Reasonix_backup")))
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")


def log(msg):
    print(f"  [{TIMESTAMP[:8]}] {msg}")


# ── 1. Git 推送 ──

REPOS = [
    ("D:/Reasonix", "github (fangtaocai041/s-t-v-p-workspace)"),
    ("D:/Reasonix/fish-ecology-assistant", "gitee (caifangtao/fish-ecology-assistant)"),
    ("D:/Reasonix/san-sheng-wanwu-core", "github (fangtaocai041/san-sheng-wanwu-core)"),
    ("D:/Reasonix/cognitive-search-engine", "github"),
    ("D:/Reasonix/eon-core", "github"),
    ("D:/Reasonix/porpoise-agent", "github"),
    ("D:/Reasonix/coilia-agent", "github"),
    ("D:/Reasonix/culter-agent", "github"),
    ("D:/Reasonix/conflict-arbiter", "github"),
    ("D:/Reasonix/infrastructure", "github (new)"),
]


def git_push_all():
    """推送所有 git 仓库到远程。"""
    log("=== Pushing all git repos ===")
    for repo_path, remote in REPOS:
        path = Path(repo_path)
        if not (path / ".git").exists():
            log(f"  ⚠️  NOT A REPO: {repo_path}")
            continue
        try:
            r = subprocess.run(
                ["git", "-C", str(path), "push"],
                capture_output=True, text=True, timeout=30,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
            )
            if r.returncode == 0:
                log(f"  ✅ {repo_path} → {remote}")
            else:
                err = r.stderr.strip()[-100:] if r.stderr else ""
                log(f"  ⚠️  {repo_path}: {err}")
        except Exception as e:
            log(f"  ❌ {repo_path}: {e}")


# ── 2. 配置文件备份 ──

CONFIG_FILES = [
    (WORKSPACE / ".env", "API keys"),
    (Path.home() / ".reasonix" / "config.json", "Reasonix desktop config"),
    (WORKSPACE / ".reasonix" / "mcp-servers" / "cnki" / "CNKICrawlerMCP.exe", "CNKI MCP binary"),
    (Path("D:/ZoteroData/zotero.sqlite"), "Zotero library (53MB)"),
]


def backup_configs():
    """备份关键配置文件到 BACKUP_DIR。"""
    log(f"=== Backing up configs to {BACKUP_DIR} ===")
    dest = BACKUP_DIR / TIMESTAMP
    dest.mkdir(parents=True, exist_ok=True)

    for src, label in CONFIG_FILES:
        if src.exists():
            try:
                if src.suffix == ".exe":
                    shutil.copy2(src, dest / src.name)
                else:
                    shutil.copy2(src, dest / src.name)
                size = src.stat().st_size
                log(f"  ✅ {label} ({size // 1024}KB)")
            except Exception as e:
                log(f"  ❌ {label}: {e}")
        else:
            log(f"  ➖ {label}: not found")


# ── 3. 数据目录备份 ──

DATA_DIRS = [
    WORKSPACE / "data",
    WORKSPACE / "fish-ecology-assistant" / "data",
    WORKSPACE / "san-sheng-wanwu-core" / "data",
]


def backup_data():
    """备份数据文件。"""
    log("=== Backing up data files ===")
    for d in DATA_DIRS:
        if d.exists():
            for f in d.glob("*"):
                if f.is_file() and f.suffix in (".db", ".sqlite", ".txt", ".csv"):
                    try:
                        dest = BACKUP_DIR / TIMESTAMP / "data"
                        dest.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, dest / f.name)
                        log(f"  ✅ {f.parent.name}/{f.name}")
                    except Exception as e:
                        log(f"  ❌ {f.name}: {e}")


# ── 主流程 ──

def main():
    import argparse
    p = argparse.ArgumentParser(description="Reasonix workspace backup")
    p.add_argument("--repo-only", action="store_true", help="Only git push")
    p.add_argument("--dest", type=str, default="", help="Backup directory")
    args = p.parse_args()

    if args.dest:
        global BACKUP_DIR
        BACKUP_DIR = Path(args.dest)

    log(f"Backup started — workspace: {WORKSPACE}")
    log(f"Backup destination: {BACKUP_DIR / TIMESTAMP}")

    if not args.repo_only:
        backup_configs()
        backup_data()
        log(f"Backup size: {sum(f.stat().st_size for f in (BACKUP_DIR / TIMESTAMP).rglob('*') if f.is_file()) // 1024}KB")

    git_push_all()
    log("Backup complete.")


if __name__ == "__main__":
    main()
