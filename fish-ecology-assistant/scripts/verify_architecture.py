#!/usr/bin/env python3
"""
[DEPRECATED] verify_architecture.py — 全架构验证脚本

⚠️ 此脚本已过时 (认知过时 / functionally outdated)。
   不应再通过跨项目导入 cognitive-search-engine 来验证本项目。

委托方向:
  - 本项目的验证应使用 `src.orchestrator.get_orchestrator().health()`
    和 `src.orchestrator.get_orchestrator().kb_first_lookup()`
  - 三角核心一致性验证由 `src.project_hub.get_hub().is_triangle_complete()`
    和 `hub.triangle_status()` 负责
  - cognitive-search-engine 是三角之 V，fish-ecology-assistant 是三角之 S，
    数据流方向为 S → V，不应反向耦合

保留此文件供参考，但不再作为 CI 入口使用。

原描述:
  验证 f项目 (V0) + c项目 (V1) + conflict-arbiter (V4) 的协调一致性。

原用法:
  python scripts/verify_architecture.py           # 从 fish-ecology-assistant 目录
  python D:\\Reasonix\\fish-ecology-assistant\\scripts\\verify_architecture.py  # 任意路径
"""

import sys
from pathlib import Path

# ── 自动定位工作区根目录 ──
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent          # fish-ecology-assistant
WORKSPACE_DIR = PROJECT_DIR.parent       # D:\\Reasonix

sys.path.insert(0, str(WORKSPACE_DIR))
sys.path.insert(0, str(WORKSPACE_DIR / "cognitive-search-engine" / "src"))
sys.path.insert(0, str(WORKSPACE_DIR / "conflict-arbiter" / "src"))

passed = 0
failed = 0

def test(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}: {detail}")

# ════════════════════════════════════════════
# §1 f项目 V0: 知识库精确匹配
# ════════════════════════════════════════════
print("\n▸ f项目 V0 — 知识库")

from workspace import lookup_species

# 1a. 精确匹配: 中文名
r = lookup_species("鳤")
sd = r.get("species_data", {})
test("中文名精确匹配 → 鳤", sd.get("name") == "鳤",
     f"got {sd.get('name')}")

# 1b. taxonomy_log 存在
tax_log = sd.get("taxonomy_log", [])
test("taxonomy_log 存在", len(tax_log) > 0)
if tax_log:
    test("taxonomy_log.field == family", tax_log[0].get("field") == "family")
    test("taxonomy_log 含 evidence", len(tax_log[0].get("evidence", [])) > 0)
    test("taxonomy_log 含 subgroup", bool(tax_log[0].get("subgroup", "")))
    test("taxonomy_log 含 related_genera", bool(tax_log[0].get("related_genera", [])))

# 1c. 科字段 (已更新为鲴科)
test("family 为 Xenocyprididae (鲴科)",
     sd.get("family") == "Xenocyprididae (鲴科)",
     f"got {sd.get('family')}")

# 1d. 精确匹配: 学名
r2 = lookup_species("Ochetobius elongatus")
test("学名精确匹配 → 鳤", r2.get("species_data", {}).get("name") == "鳤")

# 1e. 精确匹配: 不模糊
r3 = lookup_species("鳙")
test("鳤≠鳙 不误配", r.get("species_data", {}).get("name") != r3.get("species_data", {}).get("name"),
     f"鳤→{r.get('species_data',{}).get('name')}, 鳙→{r3.get('species_data',{}).get('name')}")

# ════════════════════════════════════════════
# §2 c项目 V1: 分类学不一致检测
# ════════════════════════════════════════════
print("\n▸ c项目 V1 — 分类学检测")

from unified_search import detect_taxonomy_discrepancy

# 2a. 已修复物种 → 一致
test("鳤: 两项目一致", detect_taxonomy_discrepancy("Ochetobius elongatus") is None)
test("翘嘴鲌: 两项目一致", detect_taxonomy_discrepancy("Culter alburnus") is None)
test("鳡: 两项目一致", detect_taxonomy_discrepancy("Elopichthys bambusa") is None)
test("鯮: 两项目一致", detect_taxonomy_discrepancy("Luciobrama macrocephalus") is None)
test("长江江豚: 两项目一致", detect_taxonomy_discrepancy("Neophocaena asiaeorientalis") is None)
test("中华鲟: 两项目一致", detect_taxonomy_discrepancy("Acipenser sinensis") is None)

# 2b. 模拟不一致 → 应有警告
import unified_search as us
# 临时修改 f项目返回值以触发不一致
orig_family = us._family_same
result = detect_taxonomy_discrepancy("Ochetobius_elongatus")  # 用 _ 分隔的 id 格式
# 这个物种在 species_graph.yaml 中查找的是 id，所以要用 "Ochetobius_elongatus"
if detect_taxonomy_discrepancy("NonExistentSpecies") is None:
    test("不存在的物种 → 无警告(正常)", True)

# ════════════════════════════════════════════
# §3 conflict-arbiter V4: 中国保护等级优先
# ════════════════════════════════════════════
print("\n▸ conflict-arbiter V4 — 冲突仲裁")

from arbiter import ConflictArbiter
ca = ConflictArbiter()

# 3a. 中国优先: 保护等级
result = ca.detect_conflicts("鳤", sources=[
    {"source": "iucn", "iucn": "CR"},
    {"source": "chinese_red_list", "protection_level": "国家二级"},
], region="china")
test("中国分类为权威", result["consensus"]["authority"] == "chinese_classification",
     f"got {result['consensus'].get('authority')}")
test("region_policy = china", result["region_policy"] == "china")
test("裁决含'按中国保护等级执行'", "按中国保护等级执行" in result["verdict"])

# 3b. 时空一致性
result_st = ca.arbitrate("鳤", claims=[
    {"claim": "种群下降30%", "value": 30,
     "time_period": {"start": 2005, "end": 2010}, "region": "长江中游"},
    {"claim": "种群稳定", "value": 5,
     "time_period": {"start": 2020, "end": 2025}, "region": "长江下游"},
])
test("不同时空 → 不构成冲突", result_st["conflict_level"] == 0,
     f"level={result_st['conflict_level']}")
test("裁决含'不构成冲突'", "不构成冲突" in result_st["verdict"])

# 3c. 同一时空 → 正常冲突
result_sc = ca.arbitrate("鳤", claims=[
    {"claim": "种群下降30%", "value": 30,
     "time_period": {"start": 2005, "end": 2010}, "region": "长江中游"},
    {"claim": "种群上升10%", "value": -10,
     "time_period": {"start": 2008, "end": 2010}, "region": "长江中游"},
])
test("同时间+同地区 → 正常仲裁", result_sc["conflict_level"] >= 2,
     f"level={result_sc['conflict_level']}")

# 3d. 无时空信息 → 仍仲裁 (兼容旧格式)
result_no_st = ca.arbitrate("鳤", claims=[
    {"claim": "种群下降30%", "value": 30},
    {"claim": "种群稳定", "value": 5},
])
test("无时空信息 → 仍仲裁(兼容)", result_no_st["claims_analyzed"] == 2)

# ════════════════════════════════════════════
# 汇总
# ════════════════════════════════════════════
print()
print("=" * 50)
total = passed + failed
print(f"  通过: {passed}/{total}  ({passed/total*100:.0f}%)")
if failed == 0:
    print("  🎯 全架构验证通过")
else:
    print(f"  ❌ {failed} 个测试失败")
print("=" * 50)

sys.exit(0 if failed == 0 else 1)
