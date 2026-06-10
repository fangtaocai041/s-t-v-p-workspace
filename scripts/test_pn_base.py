"""Pn Test Base — Pn 智能体共享测试基类.

所有 Pn 项目 (P₁ porpoise, P₂ coilia, P₃ culter, P₄ ...) 继承此类,
只需覆盖 SPECIES_CONFIG 和 research_themes 即可获得完整测试集。

用法 (在 Pn 项目的 tests/ 中):
    from scripts.test_pn_base import PnAdapterTestBase, PnOrchestratorTestBase

    class TestMyAdapter(PnAdapterTestBase):
        PROJECT_NAME = "my-agent"
        SPECIES = "Species name"

    class TestMyOrchestrator(PnOrchestratorTestBase):
        RESEARCH_THEMES = {"theme_id": {"label": "...", "keywords": [...]}}
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ensure D:\Reasonix is on path
_reasonix = str(Path(__file__).resolve().parent.parent)  # D:\Reasonix\scripts → D:\Reasonix
if _reasonix not in sys.path:
    sys.path.insert(0, _reasonix)


# ═══════════════════════════════════════════════════════════════
# IProjectAdapter 接口合规测试 (所有 Pn 共用)
# ═══════════════════════════════════════════════════════════════

class PnAdapterTestBase(unittest.TestCase):
    """IProjectAdapter 接口合规测试基类.

    子类覆盖:
        ADAPTER_CLASS — adapter 类
        PROJECT_NAME  — project_name 期望值 (如 "coilia-agent")
        SPECIES       — 物种学名 (如 "Coilia nasus")
        ROLE          — 角色 (如 "P₂ · 刀鲚专研")
        SEARCH_QUERY  — 默认查询词
    """

    ADAPTER_CLASS = None      # 子类必须设置
    PROJECT_NAME = ""
    SPECIES = ""
    ROLE = ""
    SEARCH_QUERY = "研究"

    @classmethod
    def setUpClass(cls):
        if cls.ADAPTER_CLASS is None:
            raise unittest.SkipTest("ADAPTER_CLASS not configured")
        cls.adapter = cls.ADAPTER_CLASS()

    # ── search() ──

    def test_search_returns_dict(self):
        r = self.adapter.search(self.SEARCH_QUERY)
        self.assertIsInstance(r, dict)

    def test_search_has_species(self):
        r = self.adapter.search(self.SEARCH_QUERY)
        self.assertIn("species_scientific", r)
        self.assertEqual(r["species_scientific"], self.SPECIES)

    def test_search_has_query(self):
        q = "测试查询"
        r = self.adapter.search(q)
        self.assertIn(q, r.get("query", ""))

    def test_search_has_phase(self):
        r = self.adapter.search(self.SEARCH_QUERY)
        self.assertIn("phase", r)

    def test_search_has_theme(self):
        r = self.adapter.search(self.SEARCH_QUERY)
        self.assertIn("theme", r)

    def test_search_has_variants(self):
        r = self.adapter.search(self.SEARCH_QUERY)
        self.assertIn("species_variants", r)
        self.assertGreater(len(r["species_variants"]), 0)

    # ── health() ──

    def test_health_returns_dict(self):
        h = self.adapter.health()
        self.assertIsInstance(h, dict)

    def test_health_has_required_fields(self):
        h = self.adapter.health()
        for field in ("project", "role", "status"):
            self.assertIn(field, h, f"health() 缺少字段: {field}")

    def test_health_is_healthy(self):
        h = self.adapter.health()
        self.assertEqual(h["status"], "HEALTHY")

    def test_health_project_name(self):
        h = self.adapter.health()
        self.assertEqual(h["project"], self.PROJECT_NAME)

    # ── info() ──

    def test_info_returns_dict(self):
        i = self.adapter.info()
        self.assertIsInstance(i, dict)

    def test_info_has_species(self):
        i = self.adapter.info()
        self.assertIn("species", i)
        self.assertGreater(len(i["species"]), 0)

    def test_info_has_themes(self):
        i = self.adapter.info()
        self.assertIn("research_themes", i)
        self.assertGreater(len(i["research_themes"]), 0)

    def test_info_has_capabilities(self):
        i = self.adapter.info()
        self.assertIn("capabilities", i)
        self.assertGreater(len(i["capabilities"]), 0)

    def test_info_has_search_protocol(self):
        i = self.adapter.info()
        self.assertIn("search_protocol", i)
        self.assertIn("Unified Search Protocol", i["search_protocol"])

    # ── project_name ──

    def test_project_name_value(self):
        self.assertEqual(self.adapter.project_name, self.PROJECT_NAME)

    # ── IProjectAdapter 类型检查 ──

    def test_adapter_is_instance(self):
        from scripts.adapter_protocol import IProjectAdapter
        self.assertIsInstance(self.adapter, IProjectAdapter)

    def test_three_required_methods(self):
        for method in ("search", "health", "info"):
            self.assertTrue(
                callable(getattr(self.adapter, method, None)),
                f"缺少方法: {method}"
            )


# ═══════════════════════════════════════════════════════════════
# Orchestrator 路由 + 分析测试 (模板 — 子类扩展)
# ═══════════════════════════════════════════════════════════════

class PnOrchestratorTestBase(unittest.TestCase):
    """Pn Orchestrator 测试基类.

    子类覆盖:
        ORCHESTRATOR_CLASS — orchestrator 类
        SPECIES_CONFIG     — 物种配置 dict
        RESEARCH_THEMES    — {theme_id: {label, keywords}}
        THEME_PHASE_MAP    — {theme_id: expected_phase}
        AGENT_ID           — 如 "P₂"
        AGENT_NAME         — 如 "coilia-agent · 刀鲚专研"
    """

    ORCHESTRATOR_CLASS = None
    SPECIES_CONFIG = {}
    RESEARCH_THEMES = {}
    THEME_PHASE_MAP = {}
    AGENT_ID = ""
    AGENT_NAME = ""

    @classmethod
    def setUpClass(cls):
        if cls.ORCHESTRATOR_CLASS is None:
            raise unittest.SkipTest("ORCHESTRATOR_CLASS not configured")
        cls.orch = cls.ORCHESTRATOR_CLASS()

    # ── 物种配置 ──

    def test_agent_id(self):
        r = self.orch.run("测试")
        self.assertEqual(r["agent_id"], self.AGENT_ID)

    def test_agent_name(self):
        r = self.orch.run("测试")
        self.assertEqual(r["agent_name"], self.AGENT_NAME)

    def test_species_scientific(self):
        r = self.orch.run("测试")
        self.assertEqual(r["species_scientific"],
                         self.SPECIES_CONFIG["species_scientific"])

    def test_species_chinese(self):
        r = self.orch.run("测试")
        self.assertGreater(len(r["species_chinese"]), 0)

    def test_ocr_variants(self):
        r = self.orch.run("测试")
        self.assertGreater(len(r["species_variants"]), 0)

    def test_search_protocol_reference(self):
        r = self.orch.run("测试")
        self.assertIn("search_protocol", r)
        self.assertEqual(r["search_protocol"], "Unified Search Protocol v1.0")

    # ── 主题路由 (子类可通过 key 测试) ──

    def _assert_route(self, query: str, expected_theme: str, expected_phase: str):
        """辅助: 验证关键词路由到正确主题."""
        r = self.orch.run(query)
        self.assertEqual(r["theme_id"], expected_theme,
                         f"'{query}' 应路由到 '{expected_theme}', "
                         f"实际到 '{r['theme_id']}'")
        if expected_phase:
            self.assertEqual(r["phase"], expected_phase)

    def test_default_route(self):
        """无关键词匹配时回到 literature_review"""
        r = self.orch.run("泛泛查询")
        self.assertEqual(r["theme_id"], "all")
        self.assertEqual(r["phase"], "literature_review")

    # ── 搜索分析 (子类扩展) ──

    def _assert_analysis(self, theme_id: str, expected_title: str,
                         min_findings: int = 1):
        """辅助: 验证领域分析器返回正确结构."""
        r = self.orch.analyze(theme_id, {"papers": [{"title": "T"}]})
        self.assertIn("analysis_title", r)
        self.assertEqual(r["analysis_title"], expected_title)
        self.assertIn("findings", r)
        self.assertGreaterEqual(len(r["findings"]), min_findings)
        return r

    def test_analyze_empty_papers(self):
        """空搜索结果处理"""
        r = self.orch.analyze("all", {"papers": []})
        self.assertEqual(r["papers_found"], 0)

    def test_analyze_default(self):
        """默认文献分析"""
        r = self.orch.analyze("all", {"papers": [{"title": "T"}]})
        self.assertIn("findings", r)


# ═══════════════════════════════════════════════════════════════
# 协议引用 + 配置验证测试 (所有 Pn 共用)
# ═══════════════════════════════════════════════════════════════

class PnProtocolTestBase(unittest.TestCase):
    """跨项目协议引用测试基类.

    测试:
      - D:/Reasonix 层共享模块可导入
      - Unified Search Protocol 文档存在
      - STV 架构文档存在
      - agent.yaml 有效
      - SKILL.md 存在且引用 Unified Search Protocol

    子类覆盖:
        PROJECT_ROOT — 项目根路径 Path
    """

    PROJECT_ROOT: Path = None

    @property
    def _reasonix(self):
        return str(Path(__file__).resolve().parent.parent)  # D:\Reasonix

    def test_import_adapter_protocol(self):
        sys.path.insert(0, self._reasonix)
        from scripts.adapter_protocol import IProjectAdapter
        self.assertTrue(hasattr(IProjectAdapter, "search"))
        self.assertTrue(hasattr(IProjectAdapter, "health"))
        self.assertTrue(hasattr(IProjectAdapter, "info"))

    def test_import_shared_types(self):
        sys.path.insert(0, self._reasonix)
        from scripts.shared_types import VerificationStatus, ContradictionType
        self.assertTrue(hasattr(VerificationStatus, "VERIFIED"))

    def test_unified_search_doc_exists(self):
        doc = Path(self._reasonix) / "cognitive-search-engine" / "docs" \
              / "UNIFIED_SEARCH_PROTOCOL.md"
        self.assertTrue(doc.is_file(), f"协议文档不存在: {doc}")

    def test_stv_architecture_doc_exists(self):
        doc = Path(self._reasonix) / "cognitive-search-engine" / "docs" \
              / "STV_TRIANGLE_ARCHITECTURE.md"
        self.assertTrue(doc.is_file(), f"架构文档不存在: {doc}")

    def test_unified_search_impl_exists(self):
        impl = Path(self._reasonix) / "cognitive-search-engine" / "src" \
               / "unified_search.py"
        self.assertTrue(impl.is_file(), f"搜索实现不存在: {impl}")

    def test_agent_yaml_valid(self):
        if self.PROJECT_ROOT is None:
            self.skipTest("PROJECT_ROOT not configured")
        import yaml
        cfg_path = self.PROJECT_ROOT / "config" / "agent.yaml"
        self.assertTrue(cfg_path.is_file(), f"agent.yaml 不存在: {cfg_path}")
        with open(cfg_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.assertIn("agent", cfg)

    def test_skill_md_exists(self):
        if self.PROJECT_ROOT is None:
            self.skipTest("PROJECT_ROOT not configured")
        skill = self.PROJECT_ROOT / "src" / "skills" / "search-literature" \
                / "SKILL.md"
        self.assertTrue(skill.is_file(), f"SKILL.md 不存在: {skill}")

    def test_skill_mentions_unified_protocol(self):
        if self.PROJECT_ROOT is None:
            self.skipTest("PROJECT_ROOT not configured")
        skill = self.PROJECT_ROOT / "src" / "skills" / "search-literature" \
                / "SKILL.md"
        content = skill.read_text(encoding="utf-8")
        self.assertIn("Unified Search Protocol", content,
                      "SKILL.md 应引用 Unified Search Protocol")
