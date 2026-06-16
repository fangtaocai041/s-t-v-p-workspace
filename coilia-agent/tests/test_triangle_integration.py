"""
三角闭环集成测试 — S(fish) → V(cognitive) → P₂(analyze) → S(写回)

验证 WF_A_full_stack_search 的正确流程。
需要 D:/Reasonix 层共享模块。
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, r"D:\Reasonix")
sys.path.insert(0, r"D:\Reasonix\coilia-agent")

from src.agent.orchestrator import CoiliaOrchestrator


# ═══════════════════════════════════════════════════════════════
# Step 1: S(fish) — 知识库查询
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def fish_knowledge_base():
    """加载 fish 知识库."""
    import yaml
    kb_path = Path(r"D:\Reasonix\fish-ecology-assistant\config\fish_species_kb.yaml")
    if not kb_path.is_file():
        pytest.skip("fish_species_kb.yaml 不在预期路径")
    return yaml.safe_load(kb_path.read_text(encoding="utf-8"))


class TestTriangleStep1FishKB:
    """Step 1: S(fish) 知识库应包含 Coilia 属 + Coilia nasus（闭环已补齐）"""

    def test_coilia_genus_present(self, fish_knowledge_base):
        """知识库有 Coilia 属物种"""
        species = fish_knowledge_base.get("species", [])
        coilia = [s for s in species if "coilia" in s.get("scientific", "").lower()]
        assert len(coilia) >= 1, "知识库应包含至少一种 Coilia 属鱼类"

    def test_brachygnathus_present(self, fish_knowledge_base):
        """短颌鲚 (Coilia brachygnathus) 已在库"""
        species = fish_knowledge_base.get("species", [])
        brachy = any(
            "brachygnathus" in s.get("scientific", "").lower()
            for s in species
        )
        assert brachy, "短颌鲚应在知识库中"

    def test_nasus_present(self, fish_knowledge_base):
        """刀鲚 (Coilia nasus) 已在知识库中 — 三角闭环写回已生效"""
        species = fish_knowledge_base.get("species", [])
        nasus = any(
            "nasus" in s.get("scientific", "").lower()
            for s in species
        )
        assert nasus, "刀鲚应已在知识库中 (三角闭环 V→S 写回)"


# ═══════════════════════════════════════════════════════════════
# Step 2: V(cognitive) — P₂ 搜索请求
# ═══════════════════════════════════════════════════════════════

class TestTriangleStep2P2Search:
    """Step 2: P₂ 发出正确的搜索参数"""

    @pytest.fixture(scope="class")
    def orch(self):
        return CoiliaOrchestrator()

    def test_p2_emits_species_params(self, orch):
        """P₂.run() 返回物种约束 + OCR 变体"""
        r = orch.run("刀鲚耳石微化学")
        assert r["agent_id"] == "P₂"
        assert r["species_scientific"] == "Coilia nasus"
        assert len(r["species_variants"]) >= 3
        assert r["search_protocol"] == "Unified Search Protocol v1.0"

    def test_p2_routes_to_migration(self, orch):
        """'耳石微化学' → migration_analysis"""
        r = orch.run("耳石微化学")
        assert r["theme_id"] == "migration"
        assert r["phase"] == "migration_analysis"

    def test_p2_routes_to_genetics(self, orch):
        """'遗传结构' → genetics_analysis"""
        r = orch.run("刀鲚遗传结构")
        assert r["theme_id"] == "genetics"
        assert r["phase"] == "genetics_analysis"

    def test_p2_routes_to_stock(self, orch):
        """'资源评估' → stock_assessment"""
        r = orch.run("资源评估")
        assert r["theme_id"] == "stock"
        assert r["phase"] == "stock_assessment"


# ═══════════════════════════════════════════════════════════════
# Step 3-4: V→S 可信度评分 + P₂ 领域分析
# ═══════════════════════════════════════════════════════════════

class TestTriangleStep3And4:
    """Step 3-4: P₂ analyze 对搜索结果做专研分析"""

    @pytest.fixture(scope="class")
    def orch(self):
        return CoiliaOrchestrator()

    @pytest.fixture(scope="class")
    def sample_papers(self):
        return [
            {"title": "Otolith Sr:Ca of Coilia nasus", "year": 2023, "doi": "10.xxx"},
            {"title": "Population genetics of Coilia nasus", "year": 2024},
            {"title": "Stock assessment", "year": 2025},
        ]

    def test_analyze_counts_papers(self, orch, sample_papers):
        r = orch.analyze("migration", {"papers": sample_papers})
        assert r["papers_found"] == 3

    def test_analyze_migration_produces_4_findings(self, orch, sample_papers):
        r = orch.analyze("migration", {"papers": sample_papers})
        assert r["analysis_title"] == "洄游生态与耳石微化学"
        assert len(r["findings"]) == 4
        assert any("Sr/Ca" in f for f in r["findings"])

    def test_analyze_genetics_produces_3_findings(self, orch, sample_papers):
        r = orch.analyze("genetics", {"papers": sample_papers})
        assert len(r["findings"]) == 3
        assert any("SNP" in f for f in r["findings"])

    def test_analyze_stock_has_historical_peak(self, orch, sample_papers):
        r = orch.analyze("stock", {"papers": sample_papers})
        assert any("3750t" in f for f in r["findings"])

    def test_analyze_feeding(self, orch, sample_papers):
        r = orch.analyze("feeding", {"papers": sample_papers})
        assert r["analysis_title"] == "食性与营养生态"
        assert len(r["findings"]) >= 3

    def test_analyze_early_life(self, orch, sample_papers):
        r = orch.analyze("early_life", {"papers": sample_papers})
        assert r["analysis_title"] == "早期资源与繁殖"
        assert any("产卵场" in f for f in r["findings"])

    def test_analyze_empty(self, orch):
        r = orch.analyze("migration", {"papers": []})
        assert r["papers_found"] == 0
