#!/usr/bin/env python3
"""
search_species.py — f项目文献检索编排器 (三步管线)

  协议: 查KB → 询问 → 调c项目 → 回写
  角色: 一之载体 — 用户命令入口，调度 Yin(知识) ↔ Yang(验证)

用法:
  # 交互模式 (查KB → 询问是否全量检索)
  python scripts/search_species.py "珠星三块鱼"

  # 自动模式 (跳过询问，直接全量检索 + 回写)
  python scripts/search_species.py "珠星三块鱼" --auto

  # 仅查KB
  python scripts/search_species.py "珠星三块鱼" --kb-only

  # 指定c项目路径
  python scripts/search_species.py "Pseudaspius hakonensis" --c-project ../cognitive-search-engine

管线:
  Step 1: 查 f项目 fish_species_kb.yaml → 已有知识摘要
  Step 2: --auto 跳过 / 否则询问是否启动 c项目全量检索
  Step 3: 调用 cognitive-search-engine/scripts/search_api.py --species "..." --format json
  Step 4: 解析结果 → 回写 fish_species_kb.yaml (追加 literature + taxonomy_log)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 项目根
FISH_ROOT = Path(__file__).resolve().parent.parent
KB_PATH = FISH_ROOT / "config" / "fish_species_kb.yaml"
DEFAULT_C_PROJECT = FISH_ROOT.parent / "cognitive-search-engine"


# ═══════════════════════════════════════════════════════
# Step 1: 查 f项目知识库
# ═══════════════════════════════════════════════════════

def load_kb() -> Dict[str, Any]:
    """
    加载物种知识库。

    优先尝试 orchestrator (新格式 fish_species_index.yaml + .md profiles)，
    失败则回退到 fish_species_kb.yaml (旧格式 flat YAML)。

    注意: 写回操作 (update_kb → save_kb) 仍使用旧格式 fish_species_kb.yaml。
          双向同步需 v6.6.0 KB 迁移计划。
    """
    try:
        # 确保项目根在 sys.path 中 (CLI 运行时 sys.path[0]=scripts/)
        _root = str(FISH_ROOT)
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from src.orchestrator import get_orchestrator
        orch = get_orchestrator()
        # 通过 health() 验证 orchestrator 可用
        h = orch.health()
        if h.get("status") == "HEALTHY" and h.get("species_db_size", 0) > 0:
            # 返回一个兼容 find_species_in_kb 的包装结构
            return {"_orchestrator": orch, "_species_db_size": h["species_db_size"]}
    except Exception:
        pass

    # Fallback: old format
    try:
        import yaml
        with open(KB_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        return {"_error": str(e)}


def find_species_in_kb(kb: Dict, query: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    在知识库中查找物种条目。

    返回: (species_dict, entry_id)
      匹配策略:
        - 新格式 (orchestrator): 通过 kb_first_lookup() 精确/别名/同义名匹配
        - 旧格式 (flat YAML): query 与 id / scientific / name / aliases / synonyms 比对
    """
    # ── 新格式: 委托 orchestrator ──
    orch = kb.get("_orchestrator")
    if orch is not None:
        result = orch.kb_first_lookup(query=query)
        if result.found:
            # 将 KbFirstResult 转换为旧格式兼容的 dict
            entry = {
                "id": result.scientific_name.lower().replace(" ", "_"),
                "scientific": result.scientific_name,
                "name": result.chinese_name,
                "family": result.family,
                "order": result.order,
                "conservation": result.conservation,
                "ecology": result.ecology,
                "aliases": list(result.aliases),
                "synonyms": list(result.synonyms),
                "distribution": dict(result.distribution),
                "matched_by_alias": result.matched_by_alias,
                "_orchestrator_summary": result.summary_text,
            }
            return entry, entry["id"]
        return None, None

    # ── 旧格式: 精确匹配 ──
    query_lower = query.lower().strip()
    species_list = kb.get("species", [])

    for s in species_list:
        sid = (s.get("id", "") or "").lower()
        sci = (s.get("scientific", "") or "").lower()
        name = (s.get("name", "") or "").lower()
        aliases = [a.lower() for a in (s.get("aliases", []) or [])]
        synonyms = [a.lower() for a in (s.get("synonyms", []) or [])]
        all_names = [sid, sci, name] + aliases + synonyms

        if query_lower in all_names or any(query_lower in n for n in all_names if n):
            return s, s.get("id", sid)

    # 中文名模糊匹配
    for s in species_list:
        chinese = (s.get("name", "") or "")
        if query in chinese or chinese in query:
            return s, s.get("id", "")

    return None, None


def kb_summary(species: Dict) -> str:
    """生成知识库摘要文本。

    优先使用 orchestrator 生成的 summary_text (新格式)，
    回退到旧格式手工组装。
    """
    # ── 新格式: orchestrator 已生成完整摘要 ──
    orch_summary = species.get("_orchestrator_summary")
    if orch_summary:
        lines = [orch_summary]
        # 追加兼容字段
        literature = species.get("literature", [])
        if literature:
            lines.append(f"   📄 已有文献: {len(literature)} 篇")
        tax_log = species.get("taxonomy_log", [])
        if tax_log:
            lines.append(f"   ⚠️ 分类变更记录: {len(tax_log)} 条")
        return "\n".join(lines)

    # ── 旧格式: 手工组装 ──
    lines = []
    name = species.get("name", "?")
    sci = species.get("scientific", "?")
    lines.append(f"📚 知识库: {name} ({sci})")

    family = species.get("family", "?")
    subfamily = species.get("subfamily", "")
    if subfamily:
        lines.append(f"   分类: {family} → {subfamily}")
    else:
        lines.append(f"   分类: {family}")

    conservation = species.get("conservation", "?")
    lines.append(f"   保护: {conservation}")

    ecology = species.get("ecology", "")
    if ecology:
        lines.append(f"   生态: {ecology}")

    dist = species.get("distribution", {})
    if dist:
        countries = dist.get("countries", [])
        basins = dist.get("basins", [])
        if countries:
            lines.append(f"   分布: {', '.join(countries[:5])}")
        if basins:
            lines.append(f"   流域: {', '.join(basins[:5])}")

    literature = species.get("literature", [])
    if literature:
        lines.append(f"   📄 已有文献: {len(literature)} 篇")
    else:
        lines.append(f"   📄 已有文献: 无")

    tax_log = species.get("taxonomy_log", [])
    if tax_log:
        lines.append(f"   ⚠️ 分类变更记录: {len(tax_log)} 条")

    synonyms = species.get("synonyms", [])
    if synonyms:
        lines.append(f"   🔄 异名: {', '.join(synonyms[:5])}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# Step 2: 询问用户 (交互模式)
# ═══════════════════════════════════════════════════════

def ask_user(kb_entry: Optional[Dict]) -> bool:
    """交互式询问是否启动 c项目全量检索。"""
    print()
    if kb_entry:
        print(kb_summary(kb_entry))
        print()
        print("是否启动 cognitive-search-engine 全量检索？")
    else:
        print("知识库中未找到该物种。是否启动 cognitive-search-engine 全量检索？")

    print("  [y] 是，启动全量检索并回写知识库")
    print("  [n] 否，仅查看知识库现有内容")
    print("  [q] 退出")
    print()

    while True:
        try:
            choice = input("> ").strip().lower()
            if choice in ("y", "yes"):
                return True
            elif choice in ("n", "no"):
                return False
            elif choice in ("q", "quit", "exit"):
                sys.exit(0)
            else:
                print("  请输入 y / n / q")
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)


# ═══════════════════════════════════════════════════════
# Step 3: 调用 c项目
# ═══════════════════════════════════════════════════════

def call_c_search(species: str, c_project: Path,
                  max_results: int = 20) -> Optional[Dict]:
    """调用 cognitive-search-engine/scripts/search_api.py。"""
    script = c_project / "scripts" / "search_api.py"
    if not script.is_file():
        print(f"❌ c项目搜索脚本不存在: {script}")
        return None

    cmd = [
        sys.executable, str(script),
        "--species", species,
        "--max", str(max_results),
        "--format", "json",
    ]
    print(f"\n🔍 调用 c项目: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(c_project),
            env={**os.environ, "PYTHONPATH": str(c_project)},
        )
        if result.returncode != 0:
            print(f"❌ c项目返回错误 (code={result.returncode}):")
            print(result.stderr[:500])
            return None

        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        print("❌ c项目搜索超时 (180s)")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ c项目返回非JSON: {e}")
        print(result.stdout[:500] if 'result' in dir() else "")
        return None
    except Exception as e:
        print(f"❌ 调用c项目失败: {e}")
        return None


# ═══════════════════════════════════════════════════════
# Step 4: 回写 f项目知识库
# ═══════════════════════════════════════════════════════

def update_kb(kb: Dict, query: str, c_result: Dict,
              dry_run: bool = False) -> Dict:
    """
    将 c项目搜索结果写回 fish_species_kb.yaml。

    更新内容:
      - literature: 追加新论文
      - taxonomy_log: 追加分类变更记录
      - 补充缺失字段 (chinese_name, family 等)
    """
    import copy
    kb = copy.deepcopy(kb)
    species_list = kb.setdefault("species", [])

    # 查找或创建条目
    entry, entry_id = find_species_in_kb(kb, query)
    if entry is None:
        # 创建新条目
        entry = {"id": c_result["species"]["scientific"].replace(" ", "_")}
        species_list.append(entry)

    # ── 补充元数据 ──
    c_species = c_result.get("species", {})
    if not entry.get("scientific"):
        entry["scientific"] = c_species.get("scientific", query)
    if not entry.get("name"):
        entry["name"] = c_species.get("chinese", query)
    if c_species.get("chinese") and not any(
        c_species["chinese"] in a for a in entry.get("aliases", [])
    ):
        entry.setdefault("aliases", [])
        if c_species["chinese"] not in entry["aliases"]:
            entry["aliases"].append(c_species["chinese"])

    # 异名 (从 variants 获取)
    existing_synonyms = set(s.lower() for s in entry.get("synonyms", []))
    for v in c_species.get("variants", []):
        if not v.startswith("⚠️") and v.lower() not in existing_synonyms:
            entry.setdefault("synonyms", [])
            entry["synonyms"].append(v)
            existing_synonyms.add(v.lower())

    # ── 处理分类学不一致 ──
    tax_gap = c_result.get("taxonomy_discrepancy")
    if tax_gap:
        tax_log_entries = entry.setdefault("taxonomy_log", [])
        existing_dates = {t.get("detected_at", "") for t in tax_log_entries}
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in existing_dates:
            tax_log_entries.append({
                "detected_at": today,
                "field": tax_gap.get("field", ""),
                "c_project_value": tax_gap.get("c_project_value", ""),
                "f_project_value": tax_gap.get("f_project_value", ""),
                "note": tax_gap.get("note", ""),
                "evidence": tax_gap.get("evidence", []),
                "source": "P3_cross_project_search (auto-detected by search_api.py)",
            })
            # 更新 family 字段
            if tax_gap.get("field") == "family":
                entry["family"] = tax_gap["c_project_value"]

    # ── 追加文献 ──
    existing_lit = entry.setdefault("literature", [])
    existing_dois = {
        (p.get("doi") or "").lower().strip()
        for p in existing_lit
    }

    new_count = 0
    for paper in c_result.get("papers", []):
        doi = (paper.get("doi") or "").lower().strip()
        if doi and doi in existing_dois:
            continue
        # 跳过无 DOI 且无标题的低质量条目
        if not doi and not paper.get("title"):
            continue

        lit_entry = {
            "doi": paper.get("doi", ""),
            "title": paper.get("title", ""),
            "year": paper.get("year"),
            "journal": paper.get("journal", ""),
            "authors": paper.get("authors", [])[:5],
            "category": paper.get("category", "unclassified"),
            "source": paper.get("_source", "c_project"),
            "added_at": datetime.now().strftime("%Y-%m-%d"),
        }
        existing_lit.append(lit_entry)
        if doi:
            existing_dois.add(doi)
        new_count += 1

    # ── 记录变更说明 ──
    change_log = entry.setdefault("change_log", [])
    change_log.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action": "P3_cross_project_search",
        "query": query,
        "new_papers": new_count,
        "total_papers": len(existing_lit),
        "taxonomy_updated": bool(tax_gap),
    })

    if not dry_run:
        save_kb(kb)

    return kb, new_count, bool(tax_gap)


def save_kb(kb: Dict) -> None:
    """写回 fish_species_kb.yaml (保留格式)。"""
    try:
        import yaml
        # 备份
        backup = KB_PATH.with_suffix(".yaml.bak")
        if KB_PATH.exists():
            backup.write_text(KB_PATH.read_text(encoding="utf-8"), encoding="utf-8")

        with open(KB_PATH, "w", encoding="utf-8") as f:
            yaml.dump(kb, f, allow_unicode=True, default_flow_style=False,
                      sort_keys=False, width=120)
        print(f"✅ 知识库已更新: {KB_PATH}")
        print(f"   备份: {backup}")
    except Exception as e:
        print(f"❌ 保存知识库失败: {e}")


# ═══════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="f项目文献检索编排器 — 查KB → 询问 → c检索 → 回写",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/search_species.py "珠星三块鱼"           # 交互模式
  python scripts/search_species.py "珠星三块鱼" --auto    # 自动全量+回写
  python scripts/search_species.py "珠星三块鱼" --kb-only # 仅查KB
  python scripts/search_species.py "Ochetobius elongatus" --dry-run
        """,
    )
    parser.add_argument("species", help="物种名 (学名/中文名/异名)")
    parser.add_argument("--auto", action="store_true",
                        help="跳过询问，直接全量检索+回写")
    parser.add_argument("--kb-only", action="store_true",
                        help="仅查看知识库，不调用c项目")
    parser.add_argument("--dry-run", action="store_true",
                        help="不写入知识库 (预览模式)")
    parser.add_argument("--max", type=int, default=20,
                        help="c项目每个查询最大结果数 (默认20)")
    parser.add_argument("--c-project", type=str,
                        default=str(DEFAULT_C_PROJECT),
                        help=f"c项目路径 (默认: {DEFAULT_C_PROJECT})")
    parser.add_argument("--json", action="store_true",
                        help="输出JSON格式")

    args = parser.parse_args()
    c_project = Path(args.c_project).resolve()

    # ── Step 1: 查KB ──
    kb = load_kb()
    if "_error" in kb:
        print(f"❌ 加载知识库失败: {kb['_error']}")
        sys.exit(1)

    entry, entry_id = find_species_in_kb(kb, args.species)

    if args.json and args.kb_only:
        result = {"kb_found": entry is not None}
        if entry:
            result["kb_entry"] = {
                "id": entry.get("id"),
                "scientific": entry.get("scientific"),
                "name": entry.get("name"),
                "family": entry.get("family"),
                "literature_count": len(entry.get("literature", [])),
                "aliases": entry.get("aliases", []),
                "synonyms": entry.get("synonyms", []),
                "taxonomy_log": entry.get("taxonomy_log", []),
            }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if entry:
        print(kb_summary(entry))
    else:
        # 尝试部分匹配
        print(f"🔍 知识库中未找到精确匹配 '{args.species}'")
        # 列出可能相关的条目
        species_list = kb.get("species", [])
        candidates = []
        for s in species_list:
            name = s.get("name", "")
            sci = s.get("scientific", "")
            if args.species[:2] in name or args.species[:2] in sci:
                candidates.append(f"  - {name} ({sci})")
        if candidates:
            print("可能相关的条目:")
            for c in candidates[:5]:
                print(c)

    if args.kb_only:
        return

    # ── Step 2: 询问 ──
    if not args.auto:
        if not ask_user(entry):
            print("👋 已取消。仅查看知识库内容。")
            return

    # ── Step 3: 调用c项目 ──
    print(f"\n{'='*60}")
    print(f"🚀 启动 c项目全量检索...")
    c_result = call_c_search(args.species, c_project, args.max)
    if c_result is None or c_result.get("status") != "ok":
        print("❌ c项目搜索失败，知识库未更新。")
        sys.exit(2)

    # 打印搜索摘要
    c_stats = c_result.get("stats", {})
    papers = c_result.get("papers", [])
    print(f"\n📊 c项目搜索完成:")
    print(f"   总命中: {c_stats.get('total_raw', 0)} 篇")
    print(f"   去重后: {c_stats.get('total_merged', len(papers))} 篇")
    print(f"   耗时: {c_stats.get('elapsed_s', '?')}s")

    tax_gap = c_result.get("taxonomy_discrepancy")
    if tax_gap:
        print(f"   ⚠️ 分类学不一致: {tax_gap.get('field')} — "
              f"c={tax_gap.get('c_project_value')} vs f={tax_gap.get('f_project_value')}")

    # ── Step 4: 回写 ──
    print(f"\n📝 回写知识库...")
    updated_kb, new_count, tax_updated = update_kb(
        kb, args.species, c_result, dry_run=args.dry_run
    )

    if args.dry_run:
        print("🔍 [DRY-RUN] 未实际写入。预览:")
        print(f"   新增论文: {new_count} 篇")
        print(f"   分类更新: {'是' if tax_updated else '否'}")
    else:
        print(f"\n✅ 完成!")
        print(f"   新增论文: {new_count} 篇")
        if tax_updated:
            print(f"   分类学信息已更新")
        print(f"   知识库文件: {KB_PATH}")

    if args.json:
        print(json.dumps({
            "status": "ok",
            "kb_found": entry is not None,
            "new_papers": new_count,
            "taxonomy_updated": tax_updated,
            "dry_run": args.dry_run,
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
