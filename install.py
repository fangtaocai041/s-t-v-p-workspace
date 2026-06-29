"""
SanShengWanWu Workspace Installer
==================================
Clone and setup all 9 projects for the Reasonix fish ecology agent ecosystem.

Usage:
    python install.py              # Clone all 9 projects
    python install.py --check      # Verify existing installation
    python install.py --gitee      # Use Gitee (faster in China)
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

PROJECTS = {
    "eon-core": {
        "url": "https://github.com/fangtaocai041/eon-core.git",
        "gitee": "https://gitee.com/caifangtao/eon-core.git",
        "role": "Coordinator",
        "required": True,
    },
    "cognitive-search-engine": {
        "url": "https://github.com/fangtaocai041/cognitive-search-engine.git",
        "gitee": "https://gitee.com/caifangtao/cognitive-search-engine.git",
        "role": "Verification (V/V1)",
        "required": True,
    },
    "fish-ecology-assistant": {
        "url": "https://github.com/fangtaocai041/fish-ecology-assistant.git",
        "gitee": "https://gitee.com/caifangtao/fish-ecology-assistant.git",
        "role": "Knowledge Supply (S/V0)",
        "required": True,
    },
    "infrastructure": {
        "url": "https://github.com/fangtaocai041/infrastructure.git",
        "gitee": None,
        "role": "Cross-cutting",
        "required": True,
    },
    "conflict-arbiter": {
        "url": "https://github.com/fangtaocai041/conflict-arbiter.git",
        "gitee": "https://gitee.com/caifangtao/conflict-arbiter.git",
        "role": "Conflict Arbitration (C)",
        "required": False,
    },
    "porpoise-agent": {
        "url": "https://github.com/fangtaocai041/porpoise-agent.git",
        "gitee": "https://gitee.com/caifangtao/porpoise-agent.git",
        "role": "Porpoise (P1)",
        "required": False,
    },
    "coilia-agent": {
        "url": "https://github.com/fangtaocai041/coilia-agent.git",
        "gitee": "https://gitee.com/caifangtao/coilia-agent.git",
        "role": "Coilia (P2)",
        "required": False,
    },
    "culter-agent": {
        "url": "https://github.com/fangtaocai041/culter-agent.git",
        "gitee": "https://gitee.com/caifangtao/culter-agent.git",
        "role": "Culter (P3)",
        "required": False,
    },
    "san-sheng-wanwu-core": {
        "url": "https://github.com/fangtaocai041/san-sheng-wanwu-core.git",
        "gitee": None,
        "role": "Meta-project",
        "required": False,
    },
}

DEPS = ["pyyaml>=6.0", "networkx>=3.0"]


def run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                          text=True, cwd=cwd, timeout=60)
        return r.returncode, r.stdout + r.stderr
    except Exception as e:
        return 1, str(e)


def main():
    p = argparse.ArgumentParser(description="SanShengWanWu Installer")
    p.add_argument("--check", action="store_true")
    p.add_argument("--dir", default=".", help="Install directory")
    p.add_argument("--gitee", action="store_true", help="Use Gitee mirrors")
    args = p.parse_args()

    print("=" * 50)
    print("SanShengWanWu Workspace Installer")
    print("=" * 50)

    # Python check
    v = sys.version_info
    if (v.major, v.minor) < (3, 11):
        print(f"[FAIL] Python {v.major}.{v.minor} < 3.11 required")
        sys.exit(1)
    print(f"[OK] Python {v.major}.{v.minor}")

    # Git check
    code, _ = run("git --version")
    if code != 0:
        print("[FAIL] git not found")
        sys.exit(1)
    print("[OK] git ready")

    root = Path(args.dir).resolve()

    if args.check:
        print("\nVerifying projects...")
        for name in ["eon-core", "cognitive-search-engine",
                     "fish-ecology-assistant", "infrastructure"]:
            exists = (root / name / "src").exists()
            print(f"  {'[OK]' if exists else '[MISSING]'} {name}")
        return

    # Install deps
    print("\nInstalling Python dependencies...")
    deps_str = " ".join(f'"{d}"' for d in DEPS)
    run(f"{sys.executable} -m pip install {deps_str} -q")

    # Clone projects
    root.mkdir(parents=True, exist_ok=True)
    failed = []
    for name, info in PROJECTS.items():
        dest = root / name
        if dest.exists():
            print(f"  [SKIP] {name} exists")
            continue

        url = info["gitee"] if args.gitee and info["gitee"] else info["url"]
        print(f"  Cloning {name} ({info['role']})...")
        code, out = run(f"git clone {url} {dest}")
        if code != 0:
            print(f"  [FAIL] {name}")
            if info["required"]:
                failed.append(name)
        else:
            print(f"  [OK] {name}")

    if failed:
        print(f"\n[FAIL] Required projects failed: {failed}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("Installation complete!")
    print()
    print("Quick start:")
    print("  cd fish-ecology-assistant")
    print("  python -c \"from src.orchestrator import lookup_term; print(lookup_term('MSY'))\"")
    print()
    print("  cd cognitive-search-engine")
    print("  python -m pytest tests/")
    print("=" * 50)


if __name__ == "__main__":
    main()
