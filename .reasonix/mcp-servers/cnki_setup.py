#!/usr/bin/env python3
"""
CNKI MCP 服务器安装脚本 — 第 20 个 MCP

安装 CNKICrawlerMCP (基于 https://github.com/Mangofang/CNKICrawlerMCP)

用法:
    python cnki_setup.py install
    python cnki_setup.py test
"""

import subprocess
import sys
from pathlib import Path

CNKI_DIR = Path(__file__).resolve().parent / "cnki"


def install():
    """克隆 CNKI MCP 并安装。"""
    if (CNKI_DIR / "pyproject.toml").exists():
        print("✅ CNKI MCP 已安装")
        return

    print("📥 克隆 CNKICrawlerMCP...")
    subprocess.run(
        ["git", "clone", "https://github.com/Mangofang/CNKICrawlerMCP.git", str(CNKI_DIR)],
        check=True,
    )

    print("📦 安装依赖...")
    subprocess.run(
        [sys.executable, "-m", "venv", str(CNKI_DIR / "venv")],
        check=True,
    )
    pip = str(CNKI_DIR / "venv" / "Scripts" / "pip.exe")
    subprocess.run([pip, "install", "-e", str(CNKI_DIR)], check=True)

    print("✅ CNKI MCP 安装完成")
    print(f"   重启 Reasonix 后可用，共 20 个 MCP 服务器")


def test():
    """测试 CNKI MCP 是否可用。"""
    python = CNKI_DIR / "venv" / "Scripts" / "python.exe"
    if not python.exists():
        print("❌ 请先运行 install")
        return
    result = subprocess.run(
        [str(python), "-c", "import cnki_mcp; print('OK')"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print("✅ CNKI MCP 可用")
    else:
        print(f"❌ 错误: {result.stderr}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("用法: python cnki_setup.py install | test")
