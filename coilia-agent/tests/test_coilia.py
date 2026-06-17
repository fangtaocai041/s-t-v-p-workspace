"""Coilia Agent (P₂) 测试 — 继承 D:/Reasonix 层共享测试基类.

每个 Pn 项目的 tests/ 只需:
  1. 继承 PnAdapterTestBase + 填 4 个变量
  2. 继承 PnOrchestratorTestBase + 填研究主题
  3. 继承 PnProtocolTestBase + 填项目路径
  4. 加物种专研分析测试
"""

import sys
import unittest
import importlib.util
from pathlib import Path

# Ensure D:\Reasonix\scripts\ is found BEFORE coilia-agent\scripts\
# (pytest may pre-add coilia-agent to sys.path, shadowing the shared scripts package)
_proj = str(Path(__file__).resolve().parent.parent)
_reasonix = str(Path(__file__).resolve().parent.parent.parent)
# Remove any existing entries for _proj and _reasonix, then re-add in correct order
_sys_path_new = []
for _p in sys.path:
    if _p not in (_proj, _reasonix):
        _sys_path_new.append(_p)
sys.path[:] = [_reasonix, _proj] + _sys_path_new

# Clear any cached 'scripts' module from earlier test collection
# (other tests may have loaded coilia-agent/scripts/ as the 'scripts' package)
for _key in list(sys.modules.keys()):
    if _key == 'scripts' or _key.startswith('scripts.'):
        del sys.modules[_key]

from scripts.test_pn_base import (
    PnAdapterTestBase,
    PnOrchestratorTestBase,
    PnProtocolTestBase,
)
from src.adapter import CoiliaAdapter
from src.agent.orchestrator import CoiliaOrchestrator


# ═══════════════════════════════════════════════════════════════
# P₂ 物种配置
# ═══════════════════════════════════════════════════════════════

P2_CONFIG = {
    "agent_id": "P₂",
    "agent_name": "coilia-agent · 刀鲚专研",
    "species_scientific": "Coilia nasus",
    "species_chinese": ["刀鲚", "长颌鲚", "长江刀鱼", "刀鱼"],
    "species_variants": [
        "Coilia nasis", "Coilia nasua", "Coilia nasas",
        "Coilia ectenes", "Coilia brachygnathus",
    ],
    "profile": {
        "research_group": "淡水渔业研究中心 刘凯研究员课题组",
    },
    "research_themes": {
        "migration": {
            "label": "洄游生态与耳石微化学",
            "keywords": ["洄游", "migration", "耳石", "otolith", "sr/ca", "微化学"],
        },
        "genetics": {
            "label": "群体遗传与种群结构",
            "keywords": ["遗传", "genetic", "dna", "微卫星", "snp", "线粒体", "基因组"],
        },
        "stock": {
            "label": "资源评估与管理",
            "keywords": ["资源", "stock", "cpue", "评估", "msy", "种群", "捕捞"],
        },
        "feeding": {
            "label": "食性与营养生态",
            "keywords": ["食性", "feeding", "营养", "稳定同位素", "胃含物"],
        },
        "early_life": {
            "label": "早期资源与繁殖",
            "keywords": ["繁殖", "spawning", "产卵", "仔鱼", "早期资源", "胚胎"],
        },
    },
    "themes_to_phases": {
        "migration": "migration_analysis",
        "genetics": "genetics_analysis",
        "stock": "stock_assessment",
        "feeding": "feeding_ecology",
        "early_life": "early_life_history",
    },
}


# ═══════════════════════════════════════════════════════════════
# 1. Adapter 测试 (IProjectAdapter 接口合规)
# ═══════════════════════════════════════════════════════════════

class TestCoiliaAdapter(PnAdapterTestBase):
    ADAPTER_CLASS = CoiliaAdapter
    PROJECT_NAME = "coilia-agent"
    SPECIES = "Coilia nasus"
    ROLE = "P₂ · 刀鲚专研"
    SEARCH_QUERY = "刀鲚研究"


# ═══════════════════════════════════════════════════════════════
# 2. Orchestrator 测试 (路由 + 分析器)
# ═══════════════════════════════════════════════════════════════

class TestCoiliaOrchestrator(PnOrchestratorTestBase):
    ORCHESTRATOR_CLASS = CoiliaOrchestrator
    SPECIES_CONFIG = P2_CONFIG
    RESEARCH_THEMES = P2_CONFIG["research_themes"]
    AGENT_ID = "P₂"
    AGENT_NAME = "coilia-agent · 刀鲚专研"

    # ── P₂ 特有: 5 个研究方向路由 ──

    def test_route_migration(self):
        self._assert_route("刀鲚洄游路线", "migration", "migration_analysis")

    def test_route_genetics(self):
        self._assert_route("刀鲚遗传多样性", "genetics", "genetics_analysis")

    def test_route_stock(self):
        self._assert_route("刀鲚资源评估", "stock", "stock_assessment")

    def test_route_feeding(self):
        self._assert_route("刀鲚食性分析", "feeding", "feeding_ecology")

    def test_route_early_life(self):
        self._assert_route("刀鲚产卵场", "early_life", "early_life_history")

    def test_route_english_keyword(self):
        self._assert_route("Coilia nasus otolith", "migration", "migration_analysis")
        self._assert_route("genetic structure", "genetics", "genetics_analysis")
        self._assert_route("stock assessment", "stock", "stock_assessment")

    # ── P₂ 特有: 5 个领域分析器 ──

    def test_analyze_migration(self):
        r = self._assert_analysis("migration", "洄游生态与耳石微化学", min_findings=4)
        self.assertIn("Sr/Ca", r["findings"][0])

    def test_analyze_genetics(self):
        r = self._assert_analysis("genetics", "群体遗传与种群结构", min_findings=3)
        self.assertIn("SNP", r["findings"][0])

    def test_analyze_stock(self):
        r = self._assert_analysis("stock", "资源评估与管理", min_findings=4)
        self.assertIn("3750t", r["findings"][1])

    def test_analyze_feeding(self):
        self._assert_analysis("feeding", "食性与营养生态", min_findings=3)

    def test_analyze_early_life(self):
        self._assert_analysis("early_life", "早期资源与繁殖", min_findings=3)

    # ── 关联物种 ──

    def test_related_species_in_info(self):
        from src.adapter import CoiliaAdapter
        i = CoiliaAdapter().info()
        related = i.get("related_species", [])
        self.assertGreaterEqual(len(related), 2)


# ═══════════════════════════════════════════════════════════════
# 3. 协议引用 + 配置验证
# ═══════════════════════════════════════════════════════════════

class TestCoiliaProtocol(PnProtocolTestBase):
    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # coilia-agent/

    def test_profile_research_group(self):
        """P₂ 课题组成员信息"""
        r = CoiliaOrchestrator().run("刀鲚")
        self.assertIn("research_group", r["profile"])
        self.assertIn("刘凯", r["profile"]["research_group"])


if __name__ == "__main__":
    unittest.main()
