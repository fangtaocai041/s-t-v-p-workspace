"""
ProjectHub — 多项目协调中枢

架构: 三角核心 (sealed 3) + 衍生项目 (open N)

  三角核心 (密闭三元素):
    fish-ecology-assistant     S/V0 — 知识供给
    cognitive-search-engine    V/V1 — 搜索验证
    eon-core                   Coordinator — 协调内核

  衍生项目 (开放):
    porpoise-agent    P₁ — 江豚专研
    coilia-agent      P₂ — 刀鲚专研
    conflict-arbiter  C  — 冲突仲裁
    ...               Pₙ — 可无限扩展

规则:
  - 三角核心密闭: 正好3个, 缺一不可
  - 衍生项目开放: 0到N, 三角不依赖任何衍生项目
  - 三角提供基础能力 (知识+验证+协调), 衍生项目在此基础上执行

用法:
  from src.project_hub import get_hub

  hub = get_hub()
  hub.cognitive.search("Ochetobius elongatus")
  hub.porpoise.health()
  hub.is_triangle_complete()
  result = hub.search_species("珠星三块鱼")
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════
# 三角核心 · 密闭三元素 (sealed set of 3)
# ═══════════════════════════════════════════════════════

@dataclass
class TriangleMember:
    """三角核心成员 — 密闭集合，缺一不可。"""
    key: str
    name: str
    symbol: str          # "S/V0" | "V/V1" | "Coordinator"
    role: str
    directory: str
    adapter_module: str
    adapter_class: str
    factory: str = "get_adapter"
    description: str = ""


TRIANGLE: List[TriangleMember] = [
    TriangleMember(
        key="fish",
        name="fish-ecology-assistant",
        symbol="S/V0",
        role="知识供给 — 多流域物种知识库 (Yangtze 443+), 矛盾分析, KB-First搜索, 可信度评分",
        directory="fish-ecology-assistant",
        adapter_module="src/adapter.py",
        adapter_class="FishEcologyAdapter",
        description="三角之S: 状态与知识。万物皆从此出。",
    ),
    TriangleMember(
        key="cognitive",
        name="cognitive-search-engine",
        symbol="V/V1",
        role="搜索验证 — BDI+ReAct多源搜索, OCR变体, 引用回溯, 权威评分, 三角验证(enforce_independence)",
        directory="cognitive-search-engine",
        adapter_module="src/adapter.py",
        adapter_class="CognitiveSearchAdapter",
        description="三角之V: 验证与搜索。万物经此验证。",
    ),
    TriangleMember(
        key="eon",
        name="eon-core",
        symbol="Coordinator",
        role="协调内核 — 10层同心架构, DAG拓扑路由, Samsara业力引擎(6道轮回), EventBus, WuXing健康监控",
        directory="eon-core",
        adapter_module="src/adapter.py",
        adapter_class="EonCoreAdapter",
        description="三角之Coordinator: 协调与演化。万物由此调度。",
    ),
]


# ═══════════════════════════════════════════════════════
# 万物衍生 · 开放集合 (open set, P₁..Pₙ)
# ═══════════════════════════════════════════════════════

@dataclass
class DerivedMember:
    """衍生项目成员 — 开放集合，三角不依赖。"""
    key: str
    name: str
    symbol: str          # "P₁" | "P₂" | "C" | "Pₙ"
    role: str
    directory: str
    adapter_module: str
    adapter_class: str
    factory: str = "get_adapter"
    description: str = ""


DERIVED: List[DerivedMember] = [
    DerivedMember(
        key="porpoise",
        name="porpoise-agent",
        symbol="P₁",
        role="江豚专研 — NBHF声学检测(100-180kHz), 栖息地建模, 种群评估, 26文件MoE知识库",
        directory="porpoise-agent",
        adapter_module="src/adapter.py",
        adapter_class="PorpoiseAdapter",
        description="第一衍生: 长江江豚。三角赋能声学+保育。",
    ),
    DerivedMember(
        key="coilia",
        name="coilia-agent",
        symbol="P₂",
        role="刀鲚专研 — 耳石微化学(Sr/Ca), 洄游生态, 资源评估, CPUE分析",
        directory="coilia-agent",
        adapter_module="src/adapter.py",
        adapter_class="CoiliaAdapter",
        description="第二衍生: 刀鲚(三鲜之首)。三角赋能耳石+洄游。",
    ),
    DerivedMember(
        key="conflict",
        name="conflict-arbiter",
        symbol="C",
        role="冲突仲裁 — 多源保护级别冲突检测, 中国优先加权, 时空可比性检查",
        directory="conflict-arbiter",
        adapter_module="src/adapter.py",
        adapter_class="ConflictArbiterAdapter",
        description="仲裁衍生: 多源冲突裁决。三角的司法分支。",
    ),
]


# ═══════════════════════════════════════════════════════
# ProjectHub
# ═══════════════════════════════════════════════════════

class ProjectHub:
    """三生万物架构 · 统一项目中枢。

    三角核心 (sealed 3):
      hub.cognitive  — V/V1 搜索验证引擎 [必需]
      hub.eon        — Coordinator 协调内核 [配置必需, 运行时可选]
      hub.fish       — S/V0 知识供给 [self, 始终可用]

    万物衍生 (open N):
      hub.porpoise   — P₁ 江豚专研
      hub.coilia     — P₂ 刀鲚专研
      hub.conflict   — C  冲突仲裁

    铁律:
      hub.is_triangle_complete() → 三角三元素必须全部可用
      衍生项目缺失不影响三角运转
    """

    def __init__(self) -> None:
        self._root = Path(__file__).resolve().parent.parent  # fish-ecology-assistant/
        # REASONIX_HOME 环境变量覆盖，fallback 到当前项目的上层目录
        _env_home = os.environ.get("REASONIX_HOME", "")
        self._workspace = Path(_env_home) if _env_home else self._root.parent
        self._loaded: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}

        # 三角成员索引
        self._triangle_map: Dict[str, TriangleMember] = {m.key: m for m in TRIANGLE}
        # 衍生成员索引
        self._derived_map: Dict[str, DerivedMember] = {m.key: m for m in DERIVED}

        # 预加载三角核心 (cognitive 必需, eon 尝试)
        self._ensure_triangle("cognitive")

    # ── 三角核心属性 ──

    @property
    def fish(self):
        """fish-ecology-assistant — S/V0 知识供给 (self)。始终可用。"""
        return self  # self-referential: hub.fish ≡ hub

    @property
    def cognitive(self):
        """cognitive-search-engine — V/V1 搜索验证引擎 [三角必需]。"""
        return self._ensure_triangle("cognitive")

    @property
    def eon(self):
        """eon-core — Coordinator 协调内核 [三角必需]。"""
        return self._ensure_triangle("eon")

    # ── 万物衍生属性 ──

    @property
    def porpoise(self):
        """porpoise-agent — P₁ 江豚专研 [衍生可选]。"""
        return self._ensure_derived("porpoise")

    @property
    def coilia(self):
        """coilia-agent — P₂ 刀鲚专研 [衍生可选]。"""
        return self._ensure_derived("coilia")

    @property
    def conflict(self):
        """conflict-arbiter — C 冲突仲裁 [衍生可选]。"""
        return self._ensure_derived("conflict")

    # ── 三角完整性检查 ──

    @property
    def triangle_members(self) -> List[str]:
        """三角核心成员列表 (按 S→V→Coordinator 顺序)。"""
        return ["fish", "cognitive", "eon"]

    @property
    def derived_members(self) -> List[str]:
        """万物衍生成员列表。"""
        return [m.key for m in DERIVED]

    def is_triangle_complete(self) -> bool:
        """三角三元素是否全部可用? 密闭集合铁律。"""
        return all(
            self._ensure_triangle(k) is not None
            for k in self.triangle_members
        )

    def triangle_status(self) -> Dict[str, Any]:
        """三角核心详细状态。"""
        status = {}
        for m in TRIANGLE:
            adapter = self._loaded.get(m.key)
            status[m.key] = {
                "symbol": m.symbol,
                "name": m.name,
                "role": m.role,
                "available": adapter is not None or m.key == "fish",
                "required": True,
            }
            if m.key in self._errors:
                status[m.key]["error"] = self._errors[m.key]
        return status

    @property
    def eon_config(self) -> Dict[str, Any]:
        """加载 eon-core 的 taiji.yaml 配置。"""
        try:
            import yaml
            cfg = self._workspace / "eon-core" / "config" / "taiji.yaml"
            if cfg.is_file():
                return yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
        return {}

    # ── 统一入口 ──

    def search_species(self, name: str, mode: str = "kb_first",
                       group: str = "full", limit: int = 10) -> Dict[str, Any]:
        """统一物种搜索 — 三角核心联动。

        Pipeline (三角闭环):
          S (fish KB) → V (cognitive 搜索) → S (可信度评分写回)

        Args:
            name: 物种中文名或学名
            mode: "kb_first" (默认) | "search_only" | "kb_only"
            group: 搜索引擎组
            limit: 每引擎最大结果数
        """
        orch = self._get_orchestrator()
        if orch is None:
            return {"stage": "error", "error": "三角之S (orchestrator) 不可用 — 三角破裂"}

        if mode == "kb_only":
            kb = orch.kb_first_lookup(query=name)
            return {
                "stage": "kb_check",
                "mode": "kb_only",
                "kb_found": kb.found,
                "kb_summary": kb.summary_text,
                "kb_data": {
                    "scientific": kb.scientific_name,
                    "chinese": kb.chinese_name,
                    "family": kb.family,
                    "aliases": kb.aliases,
                    "synonyms": kb.synonyms,
                },
                "triangle_used": ["S(fish)"],
            }

        if mode == "kb_first":
            kb = orch.kb_first_lookup(query=name)
            if not kb.found:
                return self._run_full_search(name, group, limit, kb)
            return {
                "stage": "kb_check",
                "mode": "kb_first",
                "kb_found": True,
                "kb_summary": kb.summary_text,
                "kb_recommendation": kb.search_recommendation,
                "kb_data": {
                    "scientific": kb.scientific_name,
                    "chinese": kb.chinese_name,
                    "family": kb.family,
                    "aliases": kb.aliases,
                    "synonyms": kb.synonyms,
                    "ecology": kb.ecology,
                    "distribution": kb.distribution,
                },
                "needs_user_decision": True,
                "triangle_used": ["S(fish)"],
            }

        return self._run_full_search(name, group, limit)

    def _run_full_search(self, name: str, group: str, limit: int,
                         kb_result: Any = None) -> Dict[str, Any]:
        """S→V: 知识库 → 搜索验证引擎。"""
        cog = self._ensure_triangle("cognitive")
        if cog is None:
            return {
                "stage": "error",
                "error": "三角之V (cognitive) 不可用 — 三角破裂",
            }

        try:
            full_result = cog.search(name, mode="adaptive")
            return {
                "stage": "full_search",
                "kb_found": kb_result.found if kb_result else False,
                "full_result": full_result,
                "triangle_used": ["S(fish)", "V(cognitive)"],
            }
        except Exception as e:
            try:
                import sys as _sys
                _cog_root = str(self._workspace / "cognitive-search-engine")
                if _cog_root not in _sys.path:
                    _sys.path.insert(0, _cog_root)
                from src.search_coordinator import search
                result = search(name, group=group, limit=limit)
                return {
                    "stage": "full_search",
                    "kb_found": kb_result.found if kb_result else False,
                    "full_result": result,
                    "triangle_used": ["S(fish)", "V(cognitive)"],
                }
            except Exception as e2:
                return {"stage": "error", "error": f"三角搜索失败: {e} / {e2}"}

    # ── 委托: 三角 → 衍生 ──

    def delegate_to(self, subsystem: str, task: str,
                    **kwargs) -> Optional[Dict[str, Any]]:
        """委托任务到衍生项目 (三角赋能衍生)。

        Args:
            subsystem: "porpoise" | "coilia" | "conflict"
            task: 任务描述
            **kwargs: 传递参数
        """
        adapter = self._ensure_derived(subsystem) or self._ensure_triangle(subsystem)
        if adapter is None:
            return None
        try:
            return adapter.search(task, **kwargs)
        except Exception as e:
            logger.warning(f"委托 {subsystem} 失败: {e}")
            return None

    # ── 健康检查 ──

    def health_all(self) -> Dict[str, Any]:
        """三角 + 万物的完整健康状态。"""
        return {
            "architecture": "三生万物",
            "triangle": self.triangle_status(),
            "triangle_complete": self.is_triangle_complete(),
            "derived": self._derived_status(),
        }

    def _derived_status(self) -> Dict[str, Any]:
        status = {}
        for m in DERIVED:
            adapter = self._loaded.get(m.key)
            s = "AVAILABLE" if adapter is not None else "NOT_AVAILABLE"
            status[m.key] = {
                "symbol": m.symbol,
                "name": m.name,
                "status": s,
                "role": m.role,
                "optional": True,
            }
            if m.key in self._errors:
                status[m.key]["error"] = self._errors[m.key]
        return status

    def capabilities(self) -> Dict[str, Any]:
        """三角能力 + 万物能力。"""
        return {
            "triangle": {
                m.key: {
                    "symbol": m.symbol,
                    "role": m.role,
                    "description": m.description,
                    "available": m.key == "fish" or self._loaded.get(m.key) is not None,
                }
                for m in TRIANGLE
            },
            "derived": {
                m.key: {
                    "symbol": m.symbol,
                    "role": m.role,
                    "description": m.description,
                    "available": self._loaded.get(m.key) is not None,
                }
                for m in DERIVED
            },
        }

    # ── 关系图 ──

    @staticmethod
    def relationship_map() -> str:
        """三生万物架构 ASCII 图。"""
        return r"""
                    三 生 万 物
               Triangle → Ten Thousand

    ┌───────────────────────────────────────────┐
    │             三 · Triangle Core             │
    │           密闭集合 · 缺一不可              │
    │                                           │
    │   ┌─────────┐  ┌─────────┐  ┌─────────┐  │
    │   │  fish   │  │cognitive│  │eon-core │  │
    │   │  S/V0   │  │  V/V1   │  │  Coord  │  │
    │   │ 知识供给 │  │ 搜索验证 │  │ 协调内核 │  │
    │   └────┬────┘  └────┬────┘  └────┬────┘  │
    │        └────────────┼────────────┘        │
    └─────────────────────┼─────────────────────┘
                          │ 赋能
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ porpoise │  │ coilia   │  │ conflict │
    │    P₁    │  │    P₂    │  │    C     │
    │ 江豚专研 │  │ 刀鲚专研 │  │ 冲突仲裁 │
    └──────────┘  └──────────┘  └──────────┘
          │               │
          ▼               ▼
      P₃, P₄ ... 万物 · 开放集合 · 无限衍生
        """

    # ── 内部: 懒加载 ──

    def _get_orchestrator(self) -> Any:
        """直接文件路径加载 orchestrator — 避免循环导入。"""
        import importlib.util, sys
        orch_file = Path(__file__).resolve().parent / "orchestrator.py"
        mod_name = f"_orch_hub_{id(self) % 10000}"
        spec = importlib.util.spec_from_file_location(mod_name, str(orch_file))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            factory = getattr(mod, "get_orchestrator", None)
            if factory:
                return factory()
        return None

    def _ensure_triangle(self, key: str) -> Any:
        """加载三角核心成员 (必需)。"""
        if key == "fish":
            return self  # self-referential
        if key in self._loaded:
            return self._loaded[key]
        info = self._triangle_map.get(key)
        if info is None:
            return None
        adapter = self._load_adapter(
            info.directory, info.adapter_module,
            info.adapter_class, info.factory,
            required=True,
        )
        if adapter is not None:
            self._loaded[key] = adapter
        else:
            self._errors[key] = f"三角之{info.symbol}不可用 — 三角破裂!"
        return adapter

    def _ensure_derived(self, key: str) -> Any:
        """加载衍生项目成员 (可选)。"""
        if key in self._loaded:
            return self._loaded[key]
        info = self._derived_map.get(key)
        if info is None:
            return None
        adapter = self._load_adapter(
            info.directory, info.adapter_module,
            info.adapter_class, info.factory,
            required=False,
        )
        if adapter is not None:
            self._loaded[key] = adapter
        return adapter

    def _load_adapter(self, directory: str, adapter_module: str,
                      adapter_class: str, factory: str,
                      required: bool = False) -> Any:
        """通用 importlib 加载器。"""
        import importlib.util, sys

        proj_dir = self._workspace / directory
        adapter_file = proj_dir / adapter_module

        if not adapter_file.is_file():
            if not required:
                return None
            logger.warning(f"三角成员不可用: {adapter_file}")
            return None

        proj_str = str(proj_dir)
        if proj_str not in sys.path:
            sys.path.insert(0, proj_str)

        for mod_key in list(sys.modules):
            if mod_key == "src" or mod_key.startswith("src."):
                del sys.modules[mod_key]

        try:
            spec = importlib.util.spec_from_file_location(
                f"_hub_{directory}_{id(self) % 10000}",
                str(adapter_file),
            )
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            sys.modules[f"_hub_{directory}"] = mod
            spec.loader.exec_module(mod)

            fn = getattr(mod, factory, None)
            if fn:
                return fn()
            cls = getattr(mod, adapter_class, None)
            if cls:
                return cls()
            return None
        except Exception as e:
            if required:
                logger.warning(f"三角成员 {directory} 加载异常: {e}")
            return None


# ═══════════════════════════════════════════════════════
# 全局单例
# ═══════════════════════════════════════════════════════

_hub: Optional[ProjectHub] = None


def get_hub() -> ProjectHub:
    global _hub
    if _hub is None:
        _hub = ProjectHub()
    return _hub


def reset_hub() -> None:
    global _hub
    _hub = None
