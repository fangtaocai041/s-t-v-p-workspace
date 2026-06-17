"""CoiliaAgent — P₂ 鲚属专研 · 领域分析引擎.

P₂ 不搜索。搜索由 cognitive-search-engine 统一执行 (Unified Search Protocol)。
P₂ 做三件事:
  1. 物种约束: 告诉搜索系统 "搜 <当前物种>，N 个研究方向"
  2. 阶段路由: 根据关键词匹配到专属研究方向
  3. 领域分析: 对搜索结果做 P₂ 特有的专研分析

物种配置由 SpeciesRegistry 统一管理 (config/species/*.yaml)。
搜索协议参见:
  cognitive-search-engine/docs/UNIFIED_SEARCH_PROTOCOL.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add D:/Reasonix to sys.path for shared protocols
_reasonix = str(Path(__file__).resolve().parent.parent.parent.parent)  # D:\Reasonix
if _reasonix not in sys.path:
    sys.path.insert(0, _reasonix)

from src.agent.species_registry import SpeciesRegistry, get_registry


# ── 向后兼容 ─────────────────────────────────────────────
# 旧代码引用 SPECIES_CONFIG 时返回默认物种配置 (coilia_nasus)
def _get_default_config() -> Dict[str, Any]:
    cfg = get_registry().default()
    return {
        "agent_id": "P₂",
        "agent_name": "coilia-agent · 鲚属专研",
        "species_scientific": cfg.get("species_scientific", "Coilia nasus"),
        "species_chinese": cfg.get("species_chinese", []),
        "species_variants": cfg.get("species_variants", []),
        "profile": cfg.get("profile", {}),
        "research_themes": cfg.get("research_themes", {}),
    }


SPECIES_CONFIG = _get_default_config()


# ── Cognitive enhancement (from porpoise-agent BDI pattern) ──
try:
    from src.agent.cognitive_analyzer import CognitiveAnalyzer, CognitiveResult
    _HAS_COGNITIVE = True
except ImportError:
    _HAS_COGNITIVE = False
    CognitiveAnalyzer = None  # type: ignore
    CognitiveResult = None    # type: ignore

# ── 领域分析引擎 ─────────────────────────────────────

# ── ReAct cognitive loop (cross-pollination from porpoise-agent) ──
try:
    from src.agent.react_loop import CoiliaReActLoop, ReActState
    _HAS_REACT = True
except ImportError:
    _HAS_REACT = False
    CoiliaReActLoop = None
    ReActState = None

class CoiliaOrchestrator:
    """P₂ 鲚属专研 — 领域分析引擎。

    Step 1: run(question)
      → 路由到研究方向
      → 返回搜索参数 (物种 + 约束)

    Step 2: analyze(theme, search_results)
      → 对搜索结果做 P₂ 专研分析
      → 返回领域分析报告

    支持多物种: 通过 species_id 指定 (默认 coilia_nasus)。
    """

    def __init__(self, species_id: str = None):
        registry = get_registry()
        if species_id is None:
            species_id = registry.default_id()
        self.species_id = species_id
        raw = registry.get(species_id)
        if raw is None:
            raw = registry.default()
        self.config = {
            "agent_id": "P₂",
            "agent_name": f"coilia-agent · {raw.get('species_chinese', [species_id])[0]}专研",
            "species_scientific": raw.get("species_scientific", "Coilia nasus"),
            "species_chinese": raw.get("species_chinese", []),
            "species_variants": raw.get("species_variants", []),
            "profile": raw.get("profile", {}),
            "research_themes": raw.get("research_themes", {}),
        }

    def run_with_react(self, question: str) -> dict:
        """Execute full ReAct cognitive cycle for domain analysis.
        
        Adopted from porpoise-agent's Think→Act→Observe→Reflect pattern.
        This is the RECOMMENDED method — combines script algorithms with
        cognitive reasoning for higher quality analysis.
        """
        if not _HAS_REACT:
            return self.run(question)
        
        loop = CoiliaReActLoop(max_iterations=3)
        result = loop.run(question)
        return {
            "mode": "react_cognitive",
            "agent": self.config.get("agent_id", "P2"),
            "result": result,
            "iterations": result.get("iterations", 0),
            "state": result.get("state", "unknown"),
        }

    # ── Keyword routing ──
    # ── Step 1: 搜索请求 ──

    def run(self, question: str) -> dict:
        """路由 → 返回搜索参数 (遵循 Unified Search Protocol)."""
        theme_id, theme = self._route(question)
        return {
            "agent_id": self.config["agent_id"],
            "agent_name": self.config["agent_name"],
            "species_scientific": self.config["species_scientific"],
            "species_chinese": self.config["species_chinese"],
            "species_variants": self.config["species_variants"],
            "query": question,
            "theme": theme["label"] if theme else "全部",
            "theme_id": theme_id,
            "phase": self._theme_to_phase(theme_id),
            "profile": self.config["profile"],
            # 搜索遵循 Unified Search Protocol v1.0:
            #   1. 精确名搜索 2. 宽网补漏 3. OCR变体 4. 合并去重 5. 分类 6. 输出
            #   参见: cognitive-search-engine/docs/UNIFIED_SEARCH_PROTOCOL.md
            "search_protocol": "Unified Search Protocol v1.0",
        }


    # ── BDI Cognitive Analysis (cross-pollination from porpoise-agent) ──

    def analyze_with_cognition(self, question: str, theme_id: str = "",
                               search_results: dict | None = None,
                               depth: str = "standard") -> dict | None:
        """Execute BDI cognitive analysis cycle.

        Upgraded from porpoise-agent's BDI+ReAct+Reflexion pattern.
        Perceive (gather beliefs) → Deliberate (form intentions) →
        Execute (run analysis) → Reflect (self-critique) → Refine (iterate).

        This is the RECOMMENDED analysis method — it produces higher quality,
        self-critiqued results compared to the legacy _analyze_* methods.
        """
        if not _HAS_COGNITIVE:
            # Fallback to legacy analysis
            return self.analyze(theme_id, search_results or {}, use_scripts=True)

        analyzer = CognitiveAnalyzer(self.config)
        result: CognitiveResult = analyzer.analyze(
            question=question,
            theme_id=theme_id or self._route(question)[0],
            search_results=search_results,
            depth=depth,
        )

        return {
            "mode": "cognitive_bdi",
            "state": result.state.value,
            "question": result.question,
            "theme_id": result.theme_id,
            "findings": result.findings,
            "belief_confidence": result.belief.confidence,
            "reflection": {
                "strengths": result.reflection.strengths if result.reflection else [],
                "weaknesses": result.reflection.weaknesses if result.reflection else [],
                "missing_evidence": result.reflection.missing_evidence if result.reflection else [],
                "needs_reanalysis": result.reflection.needs_reanalysis if result.reflection else False,
            } if result.reflection else None,
            "sources_used": result.sources_used,
            "triangles_engaged": result.triangles_engaged,
            "iterations": analyzer.iteration_count,
        }

    def _route(self, question: str):
        """关键词匹配 → (theme_id, theme_config)."""
        q = question.lower()
        for tid, theme in self.config["research_themes"].items():
            if any(kw in q for kw in theme["keywords"]):
                return tid, theme
        return "all", None

    def _theme_to_phase(self, theme_id: str) -> str:
        PHASE_MAP = {
            "migration": "migration_analysis",
            "genetics": "genetics_analysis",
            "stock": "stock_assessment",
            "feeding": "feeding_ecology",
            "early_life": "early_life_history",
        }
        return PHASE_MAP.get(theme_id, "literature_review")

    # ── Step 2: 领域分析 ──

    def analyze(self, theme_id: str, search_results: dict,
                use_scripts: bool = False) -> dict:
        """搜索结果 → 鲚属专研分析.

        两种模式:
          - use_scripts=False (默认): 使用内置硬编码发现 (适合文献综述)
          - use_scripts=True: 调用 scripts/ 真实算法生成分析 (适合数据分析)

        Args:
            theme_id: 研究方向 ID (migration/genetics/stock/feeding/early_life)
            search_results: 搜索结果 (含 papers 列表)
            use_scripts: 是否调用 scripts/ 真实算法
        """
        papers = search_results.get("papers", search_results.get("items", []))

        # 按研究方向分派
        handler = {
            "migration": self._analyze_migration,
            "genetics": self._analyze_genetics,
            "stock": self._analyze_stock,
            "feeding": self._analyze_feeding,
            "early_life": self._analyze_early_life,
        }.get(theme_id, self._analyze_literature)

        result = handler(papers)

        # 可选: 集成 scripts/ 真实算法结果
        if use_scripts:
            script_name = {
                "migration": "migration_analysis",
                "genetics": "genetics_analysis",
                "stock": "stock_assessment",
                "feeding": "feeding_analysis",
                "early_life": "early_life_analysis",
            }.get(theme_id)
            if script_name:
                script_result = self.call_analysis_script(script_name)
                if script_result is not None:
                    result["script_analysis"] = script_result

        return result

    # ── 脚本集成 (增量添加, 不改已有方法) ──

    SCRIPTS = {
        "literature_search": {
            "module": "scripts.literature_search",
            "func": "search_coilia",
            "kwargs": {"query": "", "use_example": True},
        },
        "migration_analysis": {
            "module": "scripts.migration_analysis",
            "func": "analyze_migration",
            "kwargs": {"use_example": True},
        },
        "genetics_analysis": {
            "module": "scripts.genetics_analysis",
            "func": "analyze_genetics",
            "kwargs": {"use_example": True},
        },
        "feeding_analysis": {
            "module": "scripts.feeding_analysis",
            "func": "analyze_feeding",
            "kwargs": {"use_example": True},
        },
        "stock_assessment": {
            "module": "scripts.stock_assessment",
            "func": "assess_stock",
            "kwargs": {"use_example": True},
        },
        "early_life_analysis": {
            "module": "scripts.early_life_analysis",
            "func": "analyze_early_life",
            "kwargs": {"use_example": True},
        },
    }

    def call_analysis_script(self, script_name: str, **overrides) -> dict | None:
        """调用 scripts/ 目录下的真实分析算法.

        通过模块+函数名动态导入并调用，返回结构化结果。
        脚本不可用时返回 None（不抛异常）。

        Args:
            script_name: 脚本标识 (例如 "migration_analysis")
            **overrides: 覆盖默认参数的键值对

        Returns:
            dict 或 None (脚本不可用时)
        """
        spec = self.SCRIPTS.get(script_name)
        if not spec:
            return None

        _reasonix = str(Path(__file__).resolve().parent.parent.parent.parent)
        if _reasonix not in sys.path:
            sys.path.insert(0, _reasonix)

        try:
            import importlib
            mod = importlib.import_module(spec["module"])
            func = getattr(mod, spec["func"])

            kwargs = dict(spec["kwargs"])
            kwargs.update(overrides)
            result = func(**kwargs)
            return self._script_result_to_dict(script_name, result)
        except (ImportError, AttributeError, Exception):
            return None

    def _script_result_to_dict(self, script_name: str, result) -> dict:
        """将脚本的返回值转换为可序列化的 dict。"""
        import dataclasses
        if result is None:
            return {"script": script_name, "status": "empty"}

        # 处理 dataclass → dict
        def _to_dict(obj):
            if dataclasses.is_dataclass(obj):
                return {f.name: _to_dict(getattr(obj, f.name))
                        for f in dataclasses.fields(obj)}
            if isinstance(obj, (list, tuple)):
                return [_to_dict(v) for v in obj]
            if isinstance(obj, dict):
                return {k: _to_dict(v) for k, v in obj.items()}
            if hasattr(obj, '__dict__'):
                return {k: _to_dict(v) for k, v in obj.__dict__.items()
                        if not k.startswith('_')}
            return obj

        return {
            "script": script_name,
            "status": "ok",
            "data": _to_dict(result),
        }

    def _analyze_literature(self, papers: list) -> dict:
        return {
            "analysis_title": "文献检索",
            "papers_found": len(papers),
            "findings": [
                f"搜索到 {len(papers)} 篇 {self.config['species_chinese'][0]} 相关文献",
            ],
        }

    def _analyze_migration(self, papers: list) -> dict:
        return {
            "analysis_title": "洄游生态与耳石微化学",
            "papers_found": len(papers),
            "findings": [
                "耳石微化学分析: Sr/Ca 比值 0.5-4.5 μmol/mol 范围",
                "洄游模式: 春季溯河→长江中下游产卵→秋季降海",
                "关键栖息地: 长江口崇明段、靖江段",
                "LA-ICP-MS 线扫描分辨率: 10μm/点",
            ],
        }

    def _analyze_genetics(self, papers: list) -> dict:
        return {
            "analysis_title": "群体遗传与种群结构",
            "papers_found": len(papers),
            "findings": [
                "遗传标记: 微卫星(SSR) + 线粒体 COI/D-loop + SNP",
                "群体结构: 长江/钱塘江/瓯江群体遗传分化",
                "有效群体大小 (Ne): 建议采用 LD 法估算",
            ],
        }

    def _analyze_stock(self, papers: list) -> dict:
        profile = self.config["profile"]
        return {
            "analysis_title": "资源评估与管理",
            "papers_found": len(papers),
            "findings": [
                "评估方法: CPUE 标准化 + 剩余产量模型 (Schaefer/Fox)",
                f"历史峰值: {profile.get('historical_peak', '未知')}",
                f"当前状态: {profile.get('current_status', '未知')}",
                "保护建议: 延长春季禁渔、保护产卵场、减少兼捕",
            ],
        }

    def _analyze_feeding(self, papers: list) -> dict:
        return {
            "analysis_title": "食性与营养生态",
            "papers_found": len(papers),
            "findings": [
                "碳氮稳定同位素分析不同生活史阶段食性转变",
                "长江口 vs 鄱阳湖食性比较",
                "仔鱼食性: 浮游动物为主",
            ],
        }

    def _analyze_early_life(self, papers: list) -> dict:
        return {
            "analysis_title": "早期资源与繁殖",
            "papers_found": len(papers),
            "findings": [
                "产卵场: 长江中下游干流、鄱阳湖",
                "产卵期: 4-6月 (水温18-25°C)",
                "仔鱼资源量年际波动与水文条件相关",
            ],
        }
