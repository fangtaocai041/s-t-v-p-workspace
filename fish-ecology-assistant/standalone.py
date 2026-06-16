#!/usr/bin/env python3
"""
fish-ecology-assistant 独立启动脚本 (零 Reasonix 依赖)

用法:
    python standalone.py health           # 健康检查
    python standalone.py lookup 鳤         # 查询物种
    python standalone.py search 刀鲚       # 全文搜索
    python standalone.py serve            # 启动 REST API (需 pip install fastapi uvicorn)
    python standalone.py migrate          # YAML → SQLite 迁移
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fish_ecology_assistant.db import KnowledgeDB, get_db


def cmd_health():
    db = get_db()
    if db.count() == 0:
        db.init_from_yaml()
    print(f"✅ HEALTHY — {db.count()} species in SQLite")
    db.close()


def cmd_migrate():
    db = KnowledgeDB()
    count = db.init_from_yaml()
    print(f"✅ Migrated {count} species")
    db.close()


def cmd_lookup(query: str):
    db = get_db()
    if db.count() == 0:
        db.init_from_yaml()
    s = db.lookup(query)
    if s:
        print(f"🐟 {s['chinese']} ({s['scientific']})")
        print(f"   科: {s['family']}  |  保护: {s['conservation']}  |  状态: {s['status']}")
        print(f"   流域: {s['basins']}")
        print(f"   别名: {', '.join(s['aliases'])}" if s['aliases'] else "   别名: 无")
        print(f"   文献: {s['literature_count']} 篇")
        if s['literature_count'] > 0:
            papers = db.get_literature(s['id'])
            for p in papers[:5]:
                print(f"     - {p['title'][:60]}... ({p['year']})")
    else:
        print(f"❌ 未找到: {query}")
    db.close()


def cmd_search(query: str, limit: int = 10):
    db = get_db()
    if db.count() == 0:
        db.init_from_yaml()
    results = db.search(query, limit)
    print(f"🔍 \"{query}\" → {len(results)} 结果")
    for r in results:
        print(f"  {r['chinese']:8s} {r['scientific']:30s} {r['conservation']}")
    db.close()


def cmd_serve():
    try:
        from fish_ecology_assistant.api import main
        main()
    except ImportError:
        print("❌ pip install fastapi uvicorn")
        sys.exit(1)


def cmd_list():
    db = get_db()
    if db.count() == 0:
        db.init_from_yaml()
    for s in db.list_all():
        print(f"  {s['chinese']:8s} {s['scientific']:35s} {s['conservation']:4s} {s['literature_count']}篇")
    db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python standalone.py [health|lookup|search|serve|migrate|list]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "health":
        cmd_health()
    elif cmd == "migrate":
        cmd_migrate()
    elif cmd == "lookup":
        cmd_lookup(sys.argv[2] if len(sys.argv) > 2 else "鳤")
    elif cmd == "search":
        cmd_search(sys.argv[2] if len(sys.argv) > 2 else "", int(sys.argv[3]) if len(sys.argv) > 3 else 10)
    elif cmd == "serve":
        cmd_serve()
    elif cmd == "list":
        cmd_list()
    else:
        print(f"未知命令: {cmd}")
