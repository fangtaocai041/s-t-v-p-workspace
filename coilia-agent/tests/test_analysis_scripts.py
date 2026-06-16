"""分析脚本测试 — 覆盖 6 个 scripts/ 分析工具的核心函数。

使用 --example 模式，无需外部数据文件。
不修改任何脚本的接口，保证另一对话框兼容。
"""

import json
import sys
import unittest
from pathlib import Path

# Add project root to path
_proj = str(Path(__file__).resolve().parent.parent)
if _proj not in sys.path:
    sys.path.insert(0, _proj)

import scripts.literature_search as ls
import scripts.migration_analysis as ma
import scripts.genetics_analysis as ga
import scripts.feeding_analysis as fa
import scripts.stock_assessment as sa
import scripts.early_life_analysis as ela


# ══════════════════════════════════════════════════════════════
# literature_search.py 测试
# ══════════════════════════════════════════════════════════════

class TestLiteratureSearch(unittest.TestCase):
    """测试文献搜索脚本的核心功能。"""

    def test_search_coilia_example_returns_papers(self):
        """search_coilia(use_example=True) 返回论文列表。"""
        papers, _ = ls.search_coilia("", use_example=True)
        self.assertGreater(len(papers), 0)
        self.assertTrue(all(hasattr(p, 'title') for p in papers))

    def test_search_example_has_doi(self):
        """示例论文包含 DOI 字段。"""
        papers, _ = ls.search_coilia("", use_example=True)
        with_doi = [p for p in papers if p.doi]
        self.assertGreater(len(with_doi), 0)

    def test_deduplicate_no_duplicates(self):
        """去重后无重复条目。"""
        papers, _ = ls.search_coilia("", use_example=True)
        deduped = ls.deduplicate(papers)
        keys = [p.dedup_key() for p in deduped]
        self.assertEqual(len(keys), len(set(keys)))

    def test_classify_papers_all_themes(self):
        """示例论文覆盖 5 个研究方向。"""
        papers, _ = ls.search_coilia("", use_example=True)
        classified = ls.classify_papers(papers)
        themes = set(p.theme for p in classified)
        for expected in ["migration", "genetics", "stock", "feeding", "early_life"]:
            self.assertIn(expected, themes)

    def test_format_json_valid(self):
        """format_json 输出有效 JSON。"""
        papers, _ = ls.search_coilia("", use_example=True)
        out = ls.format_json(papers)
        parsed = json.loads(out)
        self.assertIn("species", parsed)
        self.assertIn("papers", parsed)
        self.assertEqual(parsed["species"], "Coilia nasus")

    def test_list_species_contains_coilia(self):
        """list_species 输出包含 Coilia nasus。"""
        out = ls.list_species()
        self.assertIn("Coilia nasus", out)
        self.assertIn("P₂", out)

    def test_empty_papers_deduplicate(self):
        """空列表去重不抛异常。"""
        result = ls.deduplicate([])
        self.assertEqual(result, [])


# ══════════════════════════════════════════════════════════════
# migration_analysis.py 测试
# ══════════════════════════════════════════════════════════════

class TestMigrationAnalysis(unittest.TestCase):
    """测试洄游分析脚本的核心功能。"""

    def test_analyze_migration_example_returns_profile(self):
        """analyze_migration(use_example=True) 返回 MigrationProfile。"""
        profile, barriers = ma.analyze_migration(use_example=True)
        self.assertIsInstance(profile, ma.MigrationProfile)
        self.assertGreater(profile.total_days, 0)

    def test_migration_has_habitat_breakdown(self):
        """洄游履历包含淡水/半咸水/海水分期。"""
        profile, _ = ma.analyze_migration(use_example=True)
        total = profile.freshwater_days + profile.brackish_days + profile.marine_days
        self.assertAlmostEqual(total, profile.total_days, delta=1)

    def test_migration_confidence_high(self):
        """示例数据 (50 点) 产生高置信度。"""
        profile, _ = ma.analyze_migration(use_example=True)
        self.assertEqual(profile.confidence, "high")

    def test_barrier_assessment(self):
        """水利工程影响评估返回预期格式。"""
        _, barriers = ma.analyze_migration(use_example=True)
        self.assertGreater(len(barriers), 0)
        for b in barriers:
            self.assertIn("barrier", b)
            self.assertIn("impact", b)

    def test_list_params(self):
        """list_params 输出包含 Sr/Ca 阈值。"""
        out = ma.list_params()
        self.assertIn("freshwater", out)
        self.assertIn("marine", out)

    def test_empty_otolith_data(self):
        """空数据返回默认 MigrationProfile。"""
        profile = ma.analyze_otolith([], growth_rate=3.0)
        self.assertEqual(profile.total_days, 0)


# ══════════════════════════════════════════════════════════════
# genetics_analysis.py 测试
# ══════════════════════════════════════════════════════════════

class TestGeneticsAnalysis(unittest.TestCase):
    """测试群体遗传学分析脚本的核心功能。"""

    def test_analyze_genetics_example_returns_populations(self):
        """analyze_genetics(use_example=True) 返回群体统计。"""
        pops, hap, fst = ga.analyze_genetics(use_example=True)
        self.assertGreater(len(pops), 0)
        self.assertIsNotNone(hap)
        self.assertIsNotNone(fst)

    def test_genetics_two_populations(self):
        """示例数据包含两个群体。"""
        pops, _, _ = ga.analyze_genetics(use_example=True)
        self.assertEqual(len(pops), 2)

    def test_genetics_has_ho_he(self):
        """每个位点有 Ho 和 He 值。"""
        pops, _, _ = ga.analyze_genetics(use_example=True)
        for pop in pops:
            for locus in pop.loci:
                self.assertGreaterEqual(locus.ho, 0)
                self.assertGreaterEqual(locus.he, 0)

    def test_haplotype_diversity_range(self):
        """单倍型多样性 Hd 在 0-1 范围内。"""
        _, hap, _ = ga.analyze_genetics(use_example=True)
        if hap:
            self.assertGreaterEqual(hap.haplotype_diversity, 0)
            self.assertLessEqual(hap.haplotype_diversity, 1)

    def test_fst_calculated(self):
        """群体间 Fst 被计算。"""
        _, _, fst = ga.analyze_genetics(use_example=True)
        self.assertIsNotNone(fst)
        self.assertGreater(fst, 0)

    def test_empty_genotypes(self):
        """空基因型数据不抛异常。"""
        pop = ga.analyze_population({}, "empty")
        self.assertEqual(pop.n_individuals, 0)


# ══════════════════════════════════════════════════════════════
# feeding_analysis.py 测试
# ══════════════════════════════════════════════════════════════

class TestFeedingAnalysis(unittest.TestCase):
    """测试食性分析脚本的核心功能。"""

    def test_analyze_feeding_example_returns_results(self):
        """analyze_feeding(use_example=True) 返回胃含物+同位素结果。"""
        stomach, isotope = fa.analyze_feeding(use_example=True)
        self.assertGreater(len(stomach), 0)

    def test_feeding_has_iri(self):
        """胃含物分析包含 IRI 值。"""
        stomach, _ = fa.analyze_feeding(use_example=True)
        for item in stomach:
            if "iri" in item:
                self.assertGreater(item["iri"], 0)

    def test_feeding_json_output(self):
        """JSON 输出格式有效。"""
        stomach, isotope = fa.analyze_feeding(use_example=True)
        out = fa.format_json_feeding(stomach, isotope)
        parsed = json.loads(out)
        self.assertIn("stomach_content", parsed)

    def test_feeding_has_multiple_prey(self):
        """胃含物有种数 > 1。"""
        stomach, _ = fa.analyze_feeding(use_example=True)
        self.assertGreaterEqual(len(stomach), 2)


# ══════════════════════════════════════════════════════════════
# stock_assessment.py 测试
# ══════════════════════════════════════════════════════════════

class TestStockAssessment(unittest.TestCase):
    """测试资源评估脚本的核心功能。"""

    def test_assess_stock_example_returns_cpue(self):
        """assess_stock(use_example=True) 返回 CPUE + MSY。"""
        cpue, msy = sa.assess_stock(use_example=True)
        self.assertGreater(len(cpue.records), 0)

    def test_assess_has_msy(self):
        """MSY 估算返回正值。"""
        _, msy = sa.assess_stock(use_example=True)
        if msy:
            self.assertGreater(msy.msy, 0)
            self.assertGreater(msy.b_msy, 0)

    def test_cpue_json_format(self):
        """JSON 输出包含 cpue_trends。"""
        cpue, msy = sa.assess_stock(use_example=True)
        out = sa.format_json_stock(cpue, msy)
        parsed = json.loads(out)
        self.assertIn("cpue_trends", parsed)
        self.assertIn("species", parsed)

    def test_stock_has_recommendations(self):
        """输出包含管理建议。"""
        cpue, msy = sa.assess_stock(use_example=True)
        out = sa.format_json_stock(cpue, msy)
        parsed = json.loads(out)
        self.assertIn("recommendations", parsed)
        self.assertGreater(len(parsed["recommendations"]), 0)


# ══════════════════════════════════════════════════════════════
# early_life_analysis.py 测试
# ══════════════════════════════════════════════════════════════

class TestEarlyLifeAnalysis(unittest.TestCase):
    """测试早期资源分析脚本的核心功能。"""

    def test_analyze_early_life_example(self):
        """analyze_early_life(use_example=True) 返回统计+产卵场。"""
        stats, grounds = ela.analyze_early_life(use_example=True)
        self.assertIsInstance(stats, ela.LarvalStats)
        self.assertGreater(len(grounds), 0)

    def test_larval_stats_years_8(self):
        """示例数据覆盖 2018-2025 共 8 年。"""
        stats, _ = ela.analyze_early_life(use_example=True)
        self.assertEqual(len(stats.years), 8)
        self.assertEqual(stats.years[0], 2018)
        self.assertEqual(stats.years[-1], 2025)

    def test_larval_trend_increasing(self):
        """示例数据呈上升趋势 (模拟禁捕后恢复)。"""
        stats, _ = ela.analyze_early_life(use_example=True)
        self.assertEqual(stats.trend, "increasing")

    def test_spawning_ground_scores(self):
        """产卵场适宜性评分在 0-1 之间。"""
        _, grounds = ela.analyze_early_life(use_example=True)
        for g in grounds:
            self.assertGreaterEqual(g.suitability_score, 0)
            self.assertLessEqual(g.suitability_score, 1)

    def test_temperature_suitability(self):
        """水温适宜性函数边界情况。"""
        self.assertEqual(ela.calc_temperature_suitability(21), 1.0)    # 最优
        self.assertEqual(ela.calc_temperature_suitability(15), 0.0)    # 低于下限
        self.assertEqual(ela.calc_temperature_suitability(30), 0.0)    # 高于上限
        self.assertAlmostEqual(ela.calc_temperature_suitability(19), 0.5, places=2)  # 中间

    def test_empty_larval_data(self):
        """空仔鱼数据返回默认 LarvalStats。"""
        stats = ela.analyze_larval_resources([])
        self.assertEqual(stats.years, [])
        self.assertEqual(stats.mean_density, 0)
        # 默认 confidence 为 'medium'（dataclass 默认值）
        self.assertEqual(stats.confidence, "medium")


if __name__ == "__main__":
    unittest.main()
