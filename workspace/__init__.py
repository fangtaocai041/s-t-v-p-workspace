"""
workspace — 五项目统一入口 (Package)

无论从哪个项目目录运行 `reasonix code`，只需:
    from workspace import search_species

    result = search_species("鳤")          # → cognitive-search-engine (V1)
    result = search_species("珠星三块鱼")   # 中文名直接支持
    print(result.summary())

专精路由:
    search_species(name)          → cognitive-search-engine   文献搜索
    lookup_species(name)          → fish-ecology-assistant    知识库查询
    assess_conservation(name)     → porpoise-agent            保护评估 (江豚)
    assess_species(name, context) → coilia-agent              洄游评估 (刀鲚)
    assess_conflict(name, ...)    → conflict-arbiter          冲突仲裁 (火 🟥)
    health_check()                → 全部 5 项目              全栈健康检查

架构:
    道 (操作者) → 一 (workspace package) → 二 (project_loader) → 三 (5项目) → 万物
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════
# 自动路径配置 — 无论从哪个目录运行都能正常工作
# ═══════════════════════════════════════════════════════

# __file__ is workspace/__init__.py → parent.parent = workspace root
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# 确保工作区根目录和 scripts 在 sys.path 中
for _p in [str(_WORKSPACE_ROOT), str(_WORKSPACE_ROOT / "scripts")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# 确保所有项目目录可导入 (cognitive-search-engine 必须在最前 —
# 否则其他项目的 src/ 会遮蔽 cognitive-search-engine/src/)
for _proj in [
    "cognitive-search-engine",   # ← 必须最先，避免 src/ 命名空间被遮蔽
    "fish-ecology-assistant",
    "porpoise-agent",
    "coilia-agent",
    "conflict-arbiter",
]:
    _proj_path = str(_WORKSPACE_ROOT / _proj)
    if _proj_path in sys.path:
        sys.path.remove(_proj_path)
    sys.path.insert(0, _proj_path)

# 预加载 cognitive 核心模块，避免其他项目的 src/ 遮蔽
# 使用 importlib 直接加载，并注册到 sys.modules（dataclass 依赖此注册）
import importlib.util as _iu

def _preload_cognitive_module(rel_path: str, module_name: str):
    """用 importlib 从 cognitive-search-engine 加载模块并注册到 sys.modules。"""
    _path = _WORKSPACE_ROOT / "cognitive-search-engine" / rel_path
    _spec = _iu.spec_from_file_location(module_name, str(_path))
    if _spec and _spec.loader:
        _mod = _iu.module_from_spec(_spec)
        sys.modules[module_name] = _mod
        _spec.loader.exec_module(_mod)
        return _mod
    return None

# 必须先加载 src.__init__ — 否则 Python 的包解析器找不到正确的 src 包
_preload_cognitive_module("src/__init__.py", "src")
_cognitive_unified = _preload_cognitive_module("src/unified_search.py", "src.unified_search")
_cognitive_coordinator = _preload_cognitive_module("src/search_coordinator.py", "src.search_coordinator")

if _cognitive_unified is not None:
    _coordinated_search = _cognitive_unified.coordinated_search
    _CoordinatedSearchResult = _cognitive_unified.CoordinatedSearchResult
else:
    _coordinated_search = None
    _CoordinatedSearchResult = None

# ═══════════════════════════════════════════════════════
# 智能 src.* 模块路由 — 基于 sys.path 顺序
# ═══════════════════════════════════════════════════════
# 原 _CognitiveSrcFinder 始终路由到 cognitive-search-engine，
# 导致 porpoise-agent (src.utils) 和 coilia-agent 的导入失败。
#
# 新 _SmartSrcRouter 按 sys.path 顺序查找 src.* 模块：
# - cognitive-search-engine 排在 sys.path 最前 → 优先解析
# - src.utils 仅存在于 porpoise-agent → 正确路由到 porpoise
# - 各项目 src/ 下的模块名不重叠 → 无冲突

class _SmartSrcRouter:
    """智能 src 路由: 按 sys.path 顺序查找 src.* 模块所在的项目。"""
    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("src"):
            return None
        import importlib.util
        # 从 fullname 提取相对路径: src.world_model → world_model
        #                          src.agent.orchestrator → agent/orchestrator
        _rel = fullname.replace("src", "", 1).lstrip(".")
        if not _rel:
            _fname_parts = ("__init__.py",)
        else:
            _dir_path = _rel.replace(".", "/")
            # 先试模块文件 (xxx.py), 再试包 (xxx/__init__.py)
            _fname_parts = (f"{_dir_path}.py", f"{_dir_path}/__init__.py")

        for _p in sys.path:
            _proj_src = Path(_p) / "src"
            if not _proj_src.is_dir():
                continue
            for _fname in _fname_parts:
                _fpath = _proj_src / _fname
                if _fpath.is_file():
                    return importlib.util.spec_from_file_location(fullname, str(_fpath))
        return None

# 移除可能存在的旧 finder
sys.meta_path = [x for x in sys.meta_path if not isinstance(x, _SmartSrcRouter)
                 and getattr(x, '__class__', None) is not _SmartSrcRouter
                 and getattr(x, '__class__', None).__name__ not in ('_CognitiveSrcFinder', '_SmartSrcRouter')]
sys.meta_path.insert(0, _SmartSrcRouter())


# ═══════════════════════════════════════════════════════
# 懒加载适配器 (首次调用时才加载对应项目)
# ═══════════════════════════════════════════════════════

_adapters: Dict[str, Any] = {}


def _get_adapter(project_key: str):
    """懒加载: 获取项目适配器。"""
    if project_key in _adapters:
        return _adapters[project_key]

    from scripts.project_loader import (
        get_cognitive, get_fish, get_porpoise, get_coilia, get_conflict,
    )

    loaders = {
        "cognitive": get_cognitive,
        "fish": get_fish,
        "porpoise": get_porpoise,
        "coilia": get_coilia,
        "conflict": get_conflict,
    }

    loader = loaders.get(project_key)
    if loader is None:
        raise ValueError(f"Unknown project: {project_key}. Options: {list(loaders.keys())}")

    adapter = loader()
    if adapter is None:
        raise RuntimeError(
            f"Project '{project_key}' not found. "
            f"Expected at: {_WORKSPACE_ROOT / {'cognitive-search-engine' if project_key == 'cognitive' else project_key + '-agent' if project_key in ('porpoise', 'coilia') else 'fish-ecology-assistant'}}"
        )

    _adapters[project_key] = adapter
    return adapter


# ═══════════════════════════════════════════════════════
# 公共 API — 统一入口
# ═══════════════════════════════════════════════════════

def search_species(
    name: str,
    group: str = "standard",
    limit: int = 10,
) -> "CoordinatedSearchResult":
    """
    search_species(name) → CoordinatedSearchResult

    物种文献搜索 — 统一入口。自动路由到 cognitive-search-engine。

    支持:
      - 学名: "Ochetobius elongatus"
      - 中文名: "鳤", "珠星三块鱼"
      - 别名: "江豚"
      - OCR变体: "Ochetobibus elongatus" (自动纠正)

    管线:
      check_taxonomy() → estimate_mode() → search_streaming()
      → aggregate → classify → CN/EN → JHU priority

    用法:
      result = search_species("鳤")
      print(result.summary())
      for p in result.papers:
          print(p.get("title"))
    """
    if _coordinated_search is None:
        raise RuntimeError("cognitive-search-engine not found. Expected at: " +
                           str(_WORKSPACE_ROOT / "cognitive-search-engine"))
    result = _coordinated_search(species_name=name, group=group, limit=limit)

    # Fallback: SearchRuleEngine HTTP if MCP tools returned nothing
    if result.total_papers == 0:
        try:
            from src.rule_engine import SearchRuleEngine as _SRE
            sr = _SRE(mode="http")
            sp_id = result.scientific_name.replace(" ", "_")
            engine_res = sr.execute(sp_id)
            papers = engine_res.get("papers", [])
            if papers:
                for p in papers:
                    p.setdefault("source", "search_engine_http")
                result.papers = papers
                result.total_papers = len(papers)
                result.mode = "http_fallback"
        except Exception:
            pass

    return result


def lookup_species(name: str) -> Dict[str, Any]:
    """
    lookup_species(name) → dict

    物种知识库查询 — 委托给 fish-ecology-assistant (V0)。
    返回物种档案: 保护等级/分布/分类/已知文献/冲突裁决等。

    自动执行: 如果知识库中有保护等级数据，自动调用 conflict-arbiter
    进行中国优先的冲突检测，结果存入 conflict_verdict。
    """
    fish = _get_adapter("fish")
    result = fish.search(name, mode="lookup")

    # 自动冲突仲裁: 如果有保护等级数据
    try:
        sd = result.get("species_data", {}) or {}
        sources = _build_lookup_sources(sd)
        if len(sources) >= 2:
            conflict = _get_adapter("conflict")
            verdict = conflict.search(
                name,
                sources=sources,
                region="china",
            )
            result["conflict_verdict"] = {
                "conflict_level": verdict.get("conflict_level"),
                "consensus": verdict.get("consensus"),
                "verdict": verdict.get("verdict"),
            }
    except Exception:
        pass

    return result


def _build_lookup_sources(sd: dict) -> list:
    """从 lookup_species 的 species_data 中提取保护等级构建冲突来源。"""
    sources = []
    iucn = sd.get("iucn", sd.get("iucn_status", ""))
    if iucn:
        sources.append({"source": "iucn", "iucn": iucn})
    prot = sd.get("protection_level", "")
    if prot:
        sources.append({"source": "chinese_red_list", "protection_level": prot})
    cons = sd.get("conservation", "")
    if cons and cons not in ("", "无"):
        sources.append({"source": "provincial_protection", "protection_level": cons})
    return sources


def assess_conservation(name: str, context: str = "") -> Dict[str, Any]:
    """
    assess_conservation(name, context="") → dict

    保护评估 — 委托给 porpoise-agent (V2, P₁)。
    自动执行: 威胁矩阵 + 矛盾分析 + IUCN框架。

    适用于: 江豚 (Neophocaena asiaeorientalis) 等长江旗舰物种。
    对于其他物种会自动路由到适当的评估框架。
    """
    porpoise = _get_adapter("porpoise")
    return porpoise.search(f"assess {name} {context}")


def assess_species(name: str, context: str = "conservation") -> Dict[str, Any]:
    """
    assess_species(name, context) → dict

    物种评估 — 委托给 coilia-agent (V3, P₂)。
    专精: 耳石微化学/洄游生态/资源评估。

    适用于: 刀鲚 (Coilia nasus) 等洄游鱼类。
    """
    coilia = _get_adapter("coilia")
    return coilia.search(name, context=context)


def assess_conflict(
    species_name: str,
    sources: Optional[List[Dict[str, Any]]] = None,
    claims: Optional[List[Dict[str, Any]]] = None,
    region: str = "china",
) -> Dict[str, Any]:
    """
    assess_conflict(species_name, sources=..., claims=..., region="china") → dict

    热点冲突仲裁 — 委托给 conflict-arbiter (V4, 火 🟥)。

    检测多源保护推荐冲突 + 可信度加权仲裁 + 熔断。

    region="china": 中国保护等级为权威 (chinese_red_list weight=100)
    region="global": 常规加权仲裁

    用法:
      # 多源保护等级冲突
      sources = [
        {"source": "iucn", "iucn": "CR"},
        {"source": "chinese_red_list", "protection_level": "国家二级"},
        {"source": "provincial_protection", "protection_level": "省级重点"},
      ]
      result = assess_conflict("鳤", sources=sources)
      print(result["verdict"])

      # 文献声明冲突（带时空信息）
      claims = [
        {"claim": "种群下降30%", "source": "peer_reviewed_literature",
         "weight": 75, "value": 30,
         "time_period": {"start": 2005, "end": 2010}, "region": "长江中游"},
        {"claim": "种群稳定", "source": "survey_report",
         "weight": 60, "value": 5,
         "time_period": {"start": 2020, "end": 2025}, "region": "长江下游"},
      ]
      result = assess_conflict("鳤", claims=claims)
      # → verdict: "🟢 不同时空数据，不构成冲突。"
      
      # 无时空信息的声明（兼容旧格式）:
      result = assess_conflict("鳤", claims=old_claims)
    """
    conflict = _get_adapter("conflict")
    return conflict.search(
        species_name,
        sources=sources or [],
        claims=claims or [],
        region=region,
    )


def health_check() -> Dict[str, Any]:
    """
    health_check() → dict

    全项目健康检查 — 检查全部 5 个项目的状态。
    """
    results = {}
    for key, name in [
        ("cognitive", "cognitive-search-engine"),
        ("fish", "fish-ecology-assistant"),
        ("porpoise", "porpoise-agent"),
        ("coilia", "coilia-agent"),
        ("conflict", "conflict-arbiter"),
    ]:
        try:
            adapter = _get_adapter(key)
            results[name] = adapter.health()
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}
    return results


def full_stack_search(name: str) -> Dict[str, Any]:
    """
    full_stack_search(name) → dict

    全栈物种搜索 — WF_A 工作流:
      fish.lookup_species() → cognitive.search_species() → fish.score_credibility()

    返回: {species_profile, literature, credibility_scores}
    """
    # Step 1: 知识库查询
    profile = lookup_species(name)

    # Step 2: 文献搜索
    literature = search_species(name)

    # Step 3: 可信度评分
    fish = _get_adapter("fish")
    papers_dict = {
        "papers": literature.papers,
        "categories": literature.categories,
    }
    credibility = fish.search("score_credibility", papers=papers_dict)

    return {
        "species": name,
        "profile": profile,
        "literature": {
            "total": literature.total_papers,
            "mode": literature.mode,
            "conservation": literature.conservation,
            "scientific_name": literature.scientific_name,
            "all_variants": literature.all_variants,
        },
        "credibility": credibility,
        "workflow": "WF_A: fish→cognitive→fish",
    }


# ═══════════════════════════════════════════════════════
# 便捷别名
# ═══════════════════════════════════════════════════════

search = search_species          # 最短别名
lookup = lookup_species          # 知识库查询
assess = assess_conservation     # 保护评估
health = health_check            # 健康检查
full = full_stack_search         # 全栈搜索
conflict = assess_conflict       # 冲突仲裁 (火 🟥)


# ═══════════════════════════════════════════════════════
# f项目自主运行 → 多项目协作管线
# ═══════════════════════════════════════════════════════

def run_fish_pipeline(
    species_name: str,
    enable_literature: bool = True,
    enable_conflict: bool = True,
    enable_assessment: bool = False,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    run_fish_pipeline(species_name) → dict

    f项目自主运行 → 多项目协作管线。
    f项目 (fish-ecology-assistant) 先自主运行，再将结果传给其他项目协同。

    Phase 1 → f项目 知识库查询 (自主运行)
    Phase 2 → 木 文献搜索
    Phase 3 → 火 冲突仲裁
    Phase 4 → 金/水 领域评估
    Phase 5 → 汇总

    用法:
      from workspace import run_fish_pipeline
      result = run_fish_pipeline("鳤")
      print(result["summary"])

      # 全量模式 (含领域评估):
      result = run_fish_pipeline("鳤", enable_assessment=True)
    """
    from workspace.pipeline_fish_collab import run_fish_pipeline as _pipeline
    return _pipeline(
        species_name=species_name,
        enable_literature=enable_literature,
        enable_conflict=enable_conflict,
        enable_assessment=enable_assessment,
        verbose=verbose,
    )
