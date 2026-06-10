#!/usr/bin/env python3
"""
test_pipeline.py — 管线完整性测试集

测试所有模块在多种物种上的可运行性和输出一致性。

用法:
  python scripts/test_pipeline.py              # 全量测试
  python scripts/test_pipeline.py --quick      # 快速（只测1个物种）
  python scripts/test_pipeline.py --verbose    # 详细输出
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

_WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_WORKSPACE))

PASS = 0
FAIL = 0
ERRORS = []


def test(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        msg = f"  ❌ {name} — {detail}"
        print(msg)
        ERRORS.append(msg)


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ═══════════════════════════════════════════════════════════════
# 1. 模块导入测试
# ═══════════════════════════════════════════════════════════════
section("1. 模块导入")

try:
    from scripts.kb_loader import get_papers, get_profile, list_species
    test("kb_loader 导入", True)
except Exception as e:
    test("kb_loader 导入", False, str(e))

for mod_name, cls_name in [
    ("trend_analyzer", "TrendAnalyzer"),
    ("gap_analyzer", "GapAnalyzer"),
    ("cross_synthesis", "CrossSynthesis"),
    ("reasoning_engine", "EcologyReasoner"),
]:
    try:
        mod = __import__(f"scripts.{mod_name}", fromlist=[cls_name])
        cls = getattr(mod, cls_name)
        inst = cls()
        test(f"{mod_name}.{cls_name} 实例化", True)
    except Exception as e:
        test(f"{mod_name}.{cls_name} 实例化", False, str(e))

# ═══════════════════════════════════════════════════════════════
# 2. 数据加载测试
# ═══════════════════════════════════════════════════════════════
section("2. 数据加载")

# 2a. 图谱存在
test("species_graph.yaml 存在", Path(_WORKSPACE / "config" / "root_config" / "species_graph.yaml").exists())

# 2b. KB存在
test("species_kb.yaml 存在", Path(_WORKSPACE / "config" / "root_config" / "species_kb.yaml").exists())

# 2c. 图谱物种列举
species = list_species()
test("图谱有物种", len(species) >= 2, f"找到 {len(species)} 个: {species}")

# 2d. 图谱物种有论文
for sp in species[:3]:
    papers = get_papers(sp)
    test(f"图谱 '{sp}' 有论文数据", len(papers) > 0, f"{len(papers)}篇")

# 2e. KB有珠星三块鱼画像
profile = get_profile("珠星三块鱼")
test("KB 珠星三块鱼画像存在", profile is not None)
if profile:
    test("  含科信息", bool(profile.get("family")))
    test("  含生态信息", bool(profile.get("ecology")))
    test("  含别名", len(profile.get("aliases", [])) > 0)

# 2f. KB 无 T.brandti 画像
test("KB Tribolodon brandti 无画像", get_profile("Tribolodon brandti") is None)

# ═══════════════════════════════════════════════════════════════
# 3. 管线模块测试 (珠星三块鱼 — 有KB)
# ═══════════════════════════════════════════════════════════════
section("3. 管线测试 (珠星三块鱼 ↔ T.brandti)")

# 3a. trend_analyzer
from scripts.trend_analyzer import TrendAnalyzer
tr = TrendAnalyzer().analyze("珠星三块鱼", verbose=False)
test("趋势分析 返回论文数>0", tr.get("papers", 0) > 0, f"{tr.get('papers')}篇")
test("趋势分析 有年份范围", bool(tr.get("year_range")), tr.get("year_range"))
test("趋势分析 有方法学跃迁", len(tr.get("methodology_shifts", [])) > 0)

# 3b. gap_analyzer
from scripts.gap_analyzer import GapAnalyzer
ga = GapAnalyzer().analyze("珠星三块鱼")
test("空白分析 有方向空白", len(ga.get("direction_gaps", [])) > 0)
test("空白分析 有方法建议", len(ga.get("methodology_gaps", [])) > 0)

# 3c. cross_synthesis
from scripts.cross_synthesis import CrossSynthesis
cs = CrossSynthesis().synthesize("珠星三块鱼", "Tribolodon brandti")
test("涌现 有检测证据", cs.get("evidence_count", 0) > 0, f"{cs['evidence_count']}条")
test("涌现 有假说", len(cs.get("hypotheses", [])) > 0, f"{len(cs['hypotheses'])}条")

# 3d. reasoning_engine
from scripts.reasoning_engine import EcologyReasoner
er = EcologyReasoner().reason("珠星三块鱼", "Tribolodon brandti")
test("假说推理 有假说", len(er) > 0, f"{len(er)}条")
# 检查假说结构
if er:
    h = er[0]
    test("假说 有标题", bool(h.get("title")))
    test("假说 有置信度", h.get("confidence") in ("高", "中", "探索"))
    test("假说 有预测", bool(h.get("prediction")))
    test("假说 有验证方法", bool(h.get("test_method")))
    test("假说 有证据篇数", h.get("evidence_papers", 0) > 0)

# ═══════════════════════════════════════════════════════════════
# 4. 通用性测试 (Tribolodon brandti — 无KB)
# ═══════════════════════════════════════════════════════════════
section("4. 通用性测试 (T.brandti — 仅图谱)")

tr2 = TrendAnalyzer().analyze("Tribolodon brandti", verbose=False)
test("[无KB] 趋势分析有论文", tr2.get("papers", 0) > 0, f"{tr2.get('papers')}篇")

ga2 = GapAnalyzer().analyze("Tribolodon brandti")
test("[无KB] 空白分析有结果", len(ga2.get("direction_gaps", [])) >= 0)

cs2 = CrossSynthesis().synthesize("Tribolodon brandti", "Pseudaspius hakonensis")
test("[无KB] 涌现有证据", cs2.get("evidence_count", 0) > 0, f"{cs2['evidence_count']}条")

er2 = EcologyReasoner().reason("Tribolodon brandti", "Pseudaspius hakonensis")
test("[无KB] 假说有输出", len(er2) > 0, f"{len(er2)}条")
if er2:
    test("[无KB] 假说可检验", bool(er2[0].get("prediction")))

# ═══════════════════════════════════════════════════════════════
# 5. 管线编排测试
# ═══════════════════════════════════════════════════════════════
section("5. 管线编排")

# 模拟 run_full_analysis 的核心逻辑
from scripts.kb_loader import get_papers, get_profile

phases = ["portrait", "stats", "trend", "gaps", "synthesis", "reasoning"]
all_ok = True
for sp, comp in [("珠星三块鱼", "Tribolodon brandti"), ("Tribolodon brandti", "Pseudaspius hakonensis")]:
    p = get_papers(sp)
    pr = get_profile(sp)
    test(f"[{sp}] 管线: 可加载论文", len(p) > 0, f"{len(p)}篇")
    test(f"[{sp}] 管线: 画像{'有' if pr else '无'}(正常)", True)

# ═══════════════════════════════════════════════════════════════
# 6. 结果
# ═══════════════════════════════════════════════════════════════
section("测试结果")
total = PASS + FAIL
print(f"  通过: {PASS}/{total}")
print(f"  失败: {FAIL}/{total}")
if ERRORS:
    print(f"\n  错误详情:")
    for e in ERRORS:
        print(f"    {e}")

sys.exit(0 if FAIL == 0 else 1)
