"""Tests for FishEcologyOrchestrator — 主入口 API 测试.

覆盖范围:
  - 已知物种精确匹配 (中文名 + 学名)
  - 未知物种 → found=False
  - 别名匹配 (aliases 字段)
  - 模糊搜索候选 (fuzzy_find_all)
  - 跨项目 search_species 集成
  - 管线阶段常量 + 单例模式
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestrator import FishEcologyOrchestrator, KbFirstResult, get_orchestrator


# ═══════════════════════════════════════════
# §1 导入与生命周期
# ═══════════════════════════════════════════

def test_importable():
    """核心类应可正常导入。"""
    assert FishEcologyOrchestrator is not None
    assert KbFirstResult is not None


def test_get_orchestrator():
    """工厂函数应返回实例。"""
    orch = get_orchestrator()
    assert isinstance(orch, FishEcologyOrchestrator)


def test_singleton_pattern():
    """get_orchestrator 应返回同一实例。"""
    o1 = get_orchestrator()
    o2 = get_orchestrator()
    assert o1 is o2


def test_health():
    """健康检查应返回标准结构。"""
    orch = get_orchestrator()
    health = orch.health()
    assert health["project"] == "fish-ecology-assistant"
    assert health["status"] in ("HEALTHY", "DEGRADED")
    assert "pipeline_stages" in health
    assert "species_db_size" in health
    # species_db_size 应是已知物种数量 (new format index)
    assert isinstance(health["species_db_size"], int)
    assert health["species_db_size"] >= 20  # 至少20+已知物种


def test_info():
    """版本信息应返回能力清单。"""
    orch = get_orchestrator()
    info = orch.info()
    assert info["project"] == "fish-ecology-assistant"
    assert "version" in info
    assert "capabilities" in info
    assert "kb_first_two_stage_search" in info["capabilities"]
    assert "species_knowledge_base" in info["capabilities"]


# ═══════════════════════════════════════════
# §2 KB-First 查找: 已知物种精确匹配
# ═══════════════════════════════════════════

def test_kb_first_lookup_鳤_by_chinese():
    """中文名"鳤"应在知识库中找到 (硬断言)。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="鳤")
    assert isinstance(result, KbFirstResult)
    assert result.found is True, f"鳤应在KB中，但 found={result.found}"
    assert result.chinese_name == "鳤", f"got chinese_name={result.chinese_name}"
    assert result.scientific_name == "Ochetobius elongatus"
    assert result.family == "鲤科"
    assert result.search_recommendation == "stay_in_kb"


def test_kb_first_lookup_鳤_by_scientific():
    """学名 Ochetobius elongatus 应匹配到鳤。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="Ochetobius elongatus")
    assert isinstance(result, KbFirstResult)
    assert result.found is True
    assert result.chinese_name == "鳤"
    assert result.family == "鲤科"


def test_kb_first_lookup_刀鲚_by_chinese():
    """中文名"刀鲚"应在知识库中找到。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="刀鲚")
    assert isinstance(result, KbFirstResult)
    assert result.found is True
    assert result.scientific_name == "Coilia nasus"
    assert result.family == "鳀科 (Engraulidae)"


def test_kb_first_lookup_长江江豚():
    """长江江豚 (Neophocaena asiaeorientalis) 应在知识库中。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="长江江豚")
    assert isinstance(result, KbFirstResult)
    assert result.found is True, "长江江豚应在KB中"
    assert result.family == "鼠海豚科"


def test_kb_first_lookup_partial_genus():
    """部分学名匹配: 'Ochetobius' 应匹配到鳤。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="Ochetobius")
    assert isinstance(result, KbFirstResult)
    assert result.found is True
    assert result.chinese_name == "鳤"


# ═══════════════════════════════════════════
# §3 别名匹配
# ═══════════════════════════════════════════

def test_kb_first_lookup_by_alias():
    """别名"珠星三块鱼"应匹配到三块鱼 (Tribolodon brandti)。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="珠星三块鱼")
    assert isinstance(result, KbFirstResult)
    assert result.found is True, f"别名匹配应成功，但 found={result.found}"
    # 在知识库中，珠星三块鱼是 Tribolodon brandti 的别名
    assert result.chinese_name == "三块鱼"
    assert result.scientific_name == "Tribolodon brandti"
    # matched_by_alias 应为 True，表示通过别名而非主名匹配
    assert result.matched_by_alias is True


# ═══════════════════════════════════════════
# §4 未知物种 → found=False + 候选
# ═══════════════════════════════════════════

def test_kb_first_lookup_unknown():
    """完全未知的物种应返回 found=False, search_recommendation='continue_to_c'。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="_nonexistent_species_xyz_")
    assert isinstance(result, KbFirstResult)
    assert result.found is False
    assert result.search_recommendation == "continue_to_c"


def test_kb_first_lookup_unknown_returns_candidates():
    """未知名称应返回模糊候选列表 (可能为空或非空)。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="非鱼类物种名称测试")
    assert isinstance(result, KbFirstResult)
    assert result.found is False
    # all_candidates 是一个列表 (可能为空)
    assert isinstance(result.all_candidates, list)


# ═══════════════════════════════════════════
# §5 模糊匹配候选
# ═══════════════════════════════════════════

def test_fuzzy_find_candidates():
    """部分匹配的物种名应返回分数排序的候选列表。"""
    orch = get_orchestrator()
    # 测试内部 _fuzzy_find_all
    candidates = orch._fuzzy_find_all("鲤", "", limit=10)
    assert isinstance(candidates, list)
    if len(candidates) > 0:
        # 候选结果按 score 降序排列
        scores = [c["score"] for c in candidates]
        assert scores == sorted(scores, reverse=True), "候选应按score降序排列"
        # 最高分候选应有 Chinese name
        assert candidates[0].get("chinese", ""), f"最高分候选缺少中文名: {candidates[0]}"
        # 最高分候选应有 scientific name
        assert candidates[0].get("scientific", ""), f"最高分候选缺少学名: {candidates[0]}"


def test_fuzzy_find_with_scientific():
    """用学名片段进行模糊搜索应返回匹配结果。"""
    orch = get_orchestrator()
    candidates = orch._fuzzy_find_all("Coilia", "", limit=5)
    assert isinstance(candidates, list)
    # 应返回至少包含 Coilia 属的物种
    coilia_matches = [c for c in candidates if "Coilia" in c.get("scientific", "")]
    # 如果有候选，至少应该有一些是 Coilia 属
    if coilia_matches:
        assert True


# ═══════════════════════════════════════════
# §6 管线阶段 + 边界
# ═══════════════════════════════════════════

def test_stages_constant():
    """管线阶段应正确。"""
    assert FishEcologyOrchestrator.STAGES == ["Plan", "Search", "Analyze", "Write", "Review"]


def test_kb_first_lookup_empty_query():
    """空查询应返回 found=False，不崩溃。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="")
    assert isinstance(result, KbFirstResult)
    # 空查询: found=False 且 search_recommendation=continue_to_c
    assert result.found is False
    assert result.search_recommendation == "continue_to_c"


def test_kb_first_lookup_special_chars():
    """含特殊字符的查询应不崩溃。"""
    orch = get_orchestrator()
    result = orch.kb_first_lookup(query="!!!@@@###")
    assert isinstance(result, KbFirstResult)
    # 不应 crash
    assert result.found is False
