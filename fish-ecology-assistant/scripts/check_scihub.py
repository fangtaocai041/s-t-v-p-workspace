#!/usr/bin/env python3
"""
Sci-Hub 域名可用性检测 + ACCESS_GUIDE.md 自动更新 (鱼类生态学版)

用法:
    python scripts/check_scihub.py          # 仅检测，打印报告
    python scripts/check_scihub.py --update # 检测并更新 ACCESS_GUIDE.md
"""

import re
import sys
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from pathlib import Path

KNOWN_DOMAINS = [
    "https://sci-hub.se",
    "https://sci-hub.st",
    "https://sci-hub.ru",
    "https://sci-hub.ee",
    "https://sci-hub.ren",
    "https://sci-hub.shop",
]

TOOL_DOMAINS = {
    "Library Genesis": "https://libgen.is",
    "Anna's Archive": "https://annas-archive.org",
}

ACCESS_GUIDE_PATH = Path(__file__).resolve().parent.parent / ".reasonix" / "handbooks" / "ACCESS_GUIDE.md"


def check_domain(url: str, timeout: int = 8) -> tuple[bool, str]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return True, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        return True, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)[:80]


def check_all() -> dict:
    results = {}
    print("=" * 60)
    print("  Sci-Hub 域名可用性检测 (鱼类生态学版)")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("\n[Sci-Hub 域名]")
    for url in KNOWN_DOMAINS:
        alive, msg = check_domain(url)
        print(f"  {'✅ 存活' if alive else '❌ 失效'}  {url}  ({msg})")
        results[url] = {"alive": alive, "msg": msg}
    print("\n[同行工具]")
    for name, url in TOOL_DOMAINS.items():
        alive, msg = check_domain(url)
        print(f"  {'✅ 存活' if alive else '❌ 失效'}  {name}  {url}")
        results[name] = {"alive": alive}
    return results


def update_guide(results: dict) -> str:
    if not ACCESS_GUIDE_PATH.exists():
        return f"❌ 文件不存在: {ACCESS_GUIDE_PATH}"
    content = ACCESS_GUIDE_PATH.read_text(encoding="utf-8")
    alive_domains = [url for url in KNOWN_DOMAINS if results[url]["alive"]]
    new_line = "| **Sci-Hub** | 通过 DOI 获取付费论文 | " + " / ".join(
        [d.replace("https://", "") for d in alive_domains]
    ) + " | 🏴"
    old = r"\| \*\*Sci-Hub\*\* \|.*\| 🏴.*"
    if re.search(old, content):
        content = re.sub(old, new_line, content, count=1)
    content = re.sub(r"\n\n<!-- auto-check:.*?-->", "", content, flags=re.DOTALL)
    content = content.rstrip() + f"\n\n<!-- auto-check: {datetime.now().strftime('%Y-%m-%d %H:%M')} | alive: {len(alive_domains)}/{len(KNOWN_DOMAINS)} -->\n"
    ACCESS_GUIDE_PATH.write_text(content, encoding="utf-8")
    return f"✅ 已更新 ({len(alive_domains)}/{len(KNOWN_DOMAINS)} 存活)"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sci-Hub 域名检测")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    results = check_all()
    sci_alive = sum(1 for url in KNOWN_DOMAINS if results[url]["alive"])
    print(f"\n📊 Sci-Hub {sci_alive}/{len(KNOWN_DOMAINS)} 存活")
    if args.update:
        print(update_guide(results))
    else:
        print("\n💡 使用 --update 自动更新 ACCESS_GUIDE.md")


if __name__ == "__main__":
    main()
