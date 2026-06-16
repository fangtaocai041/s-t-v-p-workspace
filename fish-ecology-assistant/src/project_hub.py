"""
ProjectHub — 道生万物 · 统一项目中枢

  道生一，一生二，二生三，三生万物。
  Dao begets One, One begets Two, Two begets Three, Three begets the Myriad.

道 (Dao) — 外界。用户的研究问题，真实世界的生态学疑问。
  物种从哪里来？往哪里去？资源如何变化？—— 一切始于外部世界的发问。

一 (One) — 命令。用户输入进入模型项目的那一刻。
  一个查询字符串，一道指令，一次意图的投射。
  "检索珠星三块鱼" — 道化为形，进入系统。

二 (Two) — 对立。太极生两仪，矛盾与统一。
  S (fish · 知识供给 · 静态) ↔ V (cognitive · 搜索验证 · 动态)
  知识是凝滞的过去，验证是流动的当下。阴阳相推，而生变化。

三 (Three) — 三角。矛盾统一的闭合结构。
  fish(S/V0) + cognitive(V/V1) + eon-core(Coordinator)
  三角形是最小的封闭图形——两点只能对峙，三点才能围合出空间。
  密闭三元组：缺一则结构崩塌。

万物 (Myriad) — 一切事物。无限衍生。
  porpoise(P₁) + coilia(P₂) + conflict(C) + P₃, P₄, P₅ ...
  不是一万个物种，不是一万个项目——而是一切可能的输出。
  论文、分析报告、声学检测、种群评估、冲突裁决……无穷尽也。

铁律:
  - 道在外，不在内。系统的意义来自外部世界的问题。
  - 三角形密闭: 三元素缺一不可。少一个角，结构崩塌。
  - 万物开放: 三角不依赖任何衍生。衍生缺失，三角照样运转。
  - 道 → 一 → 二 → 三 → 万物：单向流动，不可逆。


用法:
  from src.project_hub import get_hub

  hub = get_hub()
  hub.cognitive.search("Ochetobius elongatus")    # 二: 阴阳之阳(动)
  hub.porpoise.health()                            # 万物: P₁
  hub.is_triangle_complete()                       # 三: 结构完整性
  result = hub.search_species("珠星三块鱼")         # 一→二→三
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════
# 三 · Triangle Core (sealed set of 3)
# ═══════════════════════════════════════════════════════

@dataclass
class TriangleMember:
    """三角之一角 — 密闭集合的元素。"""
    key: str
    name: str
    symbol: str          # "S/V0" | "V/V1" | "Coordinator"
    pole: str            # "Yin" | "Yang" | "Synthesis"
    role: str
    directory: str
    adapter_module: str
    adapter_class: str
    factory: str = "get_adapter"


TRIANGLE: List[TriangleMember] = [
    TriangleMember(
        key="fish",
        name="fish-ecology-assistant",
        symbol="S/V0",
        pole="Yin",
        role="知识供给 (Knowledge) — 多流域物种库, 矛盾分析, 可信度评分. 阴: 凝滞的过去, 静态的知识.",
        directory="fish-ecology-assistant",
        adapter_module="src/adapter.py",
        adapter_class="FishEcologyAdapter",
    ),
    TriangleMember(
        key="cognitive",
        name="cognitive-search-engine",
        symbol="V/V1",
        pole="Yang",
        role="搜索验证 (Validation) — BDI+ReAct多源搜索, OCR变体, 引用回溯, 三角验证. 阳: 流动的当下, 动态的求证.",
        directory="cognitive-search-engine",
        adapter_module="src/adapter.py",
        adapter_class="CognitiveSearchAdapter",
    ),
    TriangleMember(
        key="eon",
        name="eon-core",
        symbol="Coordinator",
        pole="Synthesis",
        role="协调内核 (Coordinator) — 10层同心架构, DAG拓扑, Samsara评控, 健康监控. 合: 阴阳交汇, 矛盾统一.",
        directory="eon-core",
        adapter_module="src/adapter.py",
        adapter_class="EonCoreAdapter",
    ),
]


# ═══════════════════════════════════════════════════════
# 万物 · Myriad Things (open set, P₁..Pₙ)
# ═══════════════════════════════════════════════════════

@dataclass
class DerivedMember:
    """万物之一物 — 开放集合的元素。三角赋能而生。"""
    key: str
    name: str
    symbol: str          # "P₁" | "P₂" | "C" | "Pₙ"
    role: str
    directory: str
    adapter_module: str
    adapter_class: str
    factory: str = "get_adapter"


DERIVED: List[DerivedMember] = [
    DerivedMember(
        key="porpoise",
        name="porpoise-agent",
        symbol="P₁",
        role="江豚专研 — NBHF声学, 栖息地建模, 种群评估. 三角赋能: 知识+验证→声学保育.",
        directory="porpoise-agent",
        adapter_module="src/adapter.py",
        adapter_class="PorpoiseAdapter",
    ),
    DerivedMember(
        key="coilia",
        name="coilia-agent",
        symbol="P₂",
        role="刀鲚专研 — 耳石微化学, 洄游生态, 资源评估. 三角赋能: 知识+验证→耳石+洄游.",
        directory="coilia-agent",
        adapter_module="src/adapter.py",
        adapter_class="CoiliaAdapter",
    ),
    DerivedMember(
        key="conflict",
        name="conflict-arbiter",
        symbol="C",
        role="冲突仲裁 — 多源保护级别冲突检测, 加权裁决. 三角赋能: 矛盾分析→司法裁决.",
        directory="conflict-arbiter",
        adapter_module="src/adapter.py",
        adapter_class="ConflictArbiterAdapter",
    ),
]


# ═══════════════════════════════════════════════════════
# ProjectHub — 道→一→二→三→万物
# ═══════════════════════════════════════════════════════

class ProjectHub:
    """道生万物架构 · 统一项目中枢。

    道 (Dao)
      └─ 一 (One): 用户命令 → fish-ecology-assistant
           └─ 二 (Two): Yin(fish·知识) ↔ Yang(cognitive·验证)
                └─ 三 (Three): Triangle Core — 密闭三元组
                     └─ 万物 (Myriad): P₁, P₂, C, Pₙ...

    访问:
      hub.cognitive  — 二之Yang (V/V1 验证引擎)
      hub.eon        — 三之Synthesis (Coordinator)
      hub.porpoise   — 万物之P₁ (江豚)
      hub.coilia     — 万物之P₂ (刀鲚)
      hub.conflict   — 万物之C (仲裁)

    状态:
      hub.is_triangle_complete()  — 三是否完整?
      hub.health_all()             — 三 + 万物 完整健康
    """

    def __init__(self) -> None:
        self._root = Path(__file__).resolve().parent.parent
        self._workspace = self._root.parent
        self._loaded: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}

        self._triangle_map: Dict[str, TriangleMember] = {m.key: m for m in TRIANGLE}
        self._derived_map: Dict[str, DerivedMember] = {m.key: m for m in DERIVED}

        # 预加载二之Yang (cognitive 是必需的阴阳之一极)
        self._ensure_triangle("cognitive")

    # ── 三 · Triangle ──

    @property
    def fish(self):
        """一之势能，二之Yin — 知识供给 (self)。"""
        return self

    @property
    def cognitive(self):
        """二之Yang — 搜索验证引擎。"""
        return self._ensure_triangle("cognitive")

    @property
    def eon(self):
        """三之Synthesis — 协调内核。"""
        return self._ensure_triangle("eon")

    # ── 万物 · Myriad ──

    @property
    def porpoise(self):
        """万物之P₁ — 江豚专研。"""
        return self._ensure_derived("porpoise")

    @property
    def coilia(self):
        """万物之P₂ — 刀鲚专研。"""
        return self._ensure_derived("coilia")

    @property
    def conflict(self):
        """万物之C — 冲突仲裁。"""
        return self._ensure_derived("conflict")

    # ── 三角完整性 ──

    @property
    def triangle_members(self) -> List[str]:
        return ["fish", "cognitive", "eon"]

    @property
    def derived_members(self) -> List[str]:
        return [m.key for m in DERIVED]

    def is_triangle_complete(self) -> bool:
        """三是否完整? 密闭三元组铁律。"""
        if self._ensure_triangle("cognitive") is None:
            return False
        eon_ok = self._ensure_triangle("eon") is not None
        if not eon_ok:
            eon_cfg = self._workspace / "eon-core" / "config" / "taiji.yaml"
            eon_ok = eon_cfg.is_file()
        return eon_ok

    def triangle_status(self) -> Dict[str, Any]:
        """三之详细状态。"""
        status = {}
        for m in TRIANGLE:
            adapter = self._loaded.get(m.key)
            available = adapter is not None or m.key == "fish"
            if m.key == "eon" and not available:
                eon_cfg = self._workspace / "eon-core" / "config" / "taiji.yaml"
                available = eon_cfg.is_file()
            status[m.key] = {
                "symbol": m.symbol,
                "pole": m.pole,
                "name": m.name,
                "role": m.role,
                "available": available,
            }
            if m.key in self._errors:
                status[m.key]["error"] = self._errors[m.key]
        return status

    @property
    def eon_config(self) -> Dict[str, Any]:
        """eon-core 的 taiji.yaml 配置。"""
        try:
            import yaml
            cfg = self._workspace / "eon-core" / "config" / "taiji.yaml"
            if cfg.is_file():
                return yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
        return {}

    # ── 道→一→二→三→万物: 搜索闭环 ──

    def search_species(self, name: str, mode: str = "kb_first",
                       group: str = "full", limit: int = 10) -> Dict[str, Any]:
        """一→二→三: 用户命令 → Yin/Yang → Triangle Core.

        道: 用户的研究问题 ("珠星三块鱼是什么?")
        一: 命令进入系统 (此方法被调用)
        二: Yin(fish·KB) ↔ Yang(cognitive·搜索)
        三: Triangle闭环 (搜索→验证→写回)
        """
        orch = self._get_orchestrator()
        if orch is None:
            return {"stage": "error", "error": "一之载体 (orchestrator) 不可用"}

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
                "path": "道→一→Yin(fish·KB)",
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
                "path": "道→一→Yin(fish·KB)",
            }

        return self._run_full_search(name, group, limit)

    def _run_full_search(self, name: str, group: str, limit: int,
                         kb_result: Any = None) -> Dict[str, Any]:
        """二之运动: Yin(知识) → Yang(验证)。"""
        cog = self._ensure_triangle("cognitive")
        if cog is None:
            return {"stage": "error", "error": "二之Yang (cognitive) 不可用 — 阴阳失衡"}

        try:
            full_result = cog.search(name, mode="adaptive")
            return {
                "stage": "full_search",
                "kb_found": kb_result.found if kb_result else False,
                "full_result": full_result,
                "path": "道→一→二(Yin+Yang)→三(Triangle)",
            }
        except Exception as e:
            try:
                # 使用 importlib 直接加载避免 src 命名空间冲突
                import importlib.util as _iu
                _cog_src = self._workspace / "cognitive-search-engine" / "src" / "search_coordinator.py"
                if _cog_src.is_file():
                    _spec = _iu.spec_from_file_location("_cog_search", str(_cog_src))
                    if _spec and _spec.loader:
                        _mod = _iu.module_from_spec(_spec)
                        _spec.loader.exec_module(_mod)
                        result = _mod.search(name, group=group, limit=limit)
                        return {
                            "stage": "full_search",
                            "kb_found": kb_result.found if kb_result else False,
                            "full_result": result,
                            "path": "道→一→二(Yin+Yang)→三(Triangle)",
                        }
                raise RuntimeError("cognitive-search-engine not loadable")
            except Exception as e2:
                return {"stage": "error", "error": f"搜索失败: {e} / {e2}"}

    # ── 三→万物: 三角赋能衍生 ──

    def delegate_to(self, subsystem: str, task: str,
                    **kwargs) -> Optional[Dict[str, Any]]:
        """三→万物: 三角赋能衍生项目。

        Args:
            subsystem: "porpoise" | "coilia" | "conflict"
            task: 任务描述
        """
        adapter = self._ensure_derived(subsystem) or self._ensure_triangle(subsystem)
        if adapter is None:
            return None
        try:
            return adapter.search(task, **kwargs)
        except Exception as e:
            logger.warning(f"委托 {subsystem} 失败: {e}")
            return None

    # ── 健康 ──

    def health_all(self) -> Dict[str, Any]:
        """三 + 万物 的完整健康。"""
        return {
            "philosophy": "道生一，一生二，二生三，三生万物",
            "one": {"name": "fish-ecology-assistant", "status": "HEALTHY"},
            "two": {
                "yin": {"name": "fish-ecology-assistant", "pole": "Yin", "status": "HEALTHY"},
                "yang": {
                    "name": "cognitive-search-engine",
                    "pole": "Yang",
                    "status": "HEALTHY" if self._loaded.get("cognitive") else "DEGRADED",
                },
            },
            "three": self.triangle_status(),
            "triangle_complete": self.is_triangle_complete(),
            "myriad": self._derived_status(),
        }

    def _derived_status(self) -> Dict[str, Any]:
        status = {}
        for m in DERIVED:
            adapter = self._loaded.get(m.key)
            s = "AVAILABLE" if adapter is not None else "DORMANT"
            status[m.key] = {
                "symbol": m.symbol,
                "name": m.name,
                "status": s,
                "role": m.role,
            }
        return status

    def capabilities(self) -> Dict[str, Any]:
        return {
            "philosophy": "道→一→二→三→万物",
            "triangle": {
                m.key: {
                    "symbol": m.symbol,
                    "pole": m.pole,
                    "role": m.role,
                    "available": m.key == "fish" or self._loaded.get(m.key) is not None,
                }
                for m in TRIANGLE
            },
            "myriad": {
                m.key: {
                    "symbol": m.symbol,
                    "role": m.role,
                    "available": self._loaded.get(m.key) is not None,
                }
                for m in DERIVED
            },
        }

    # ── 道生万物 · 全图 ──

    @staticmethod
    def relationship_map() -> str:
        """道→一→二→三→万物 完整 ASCII 图。"""
        return r"""
              道 生 一，一 生 二，二 生 三，三 生 万 物
        Dao → One → Two → Three → the Myriad Things

                        ┌──────────┐
                        │   道 Dao  │  外界 · 用户的研究问题
                        │   Way     │  "珠星三块鱼是什么?"
                        └────┬─────┘
                             │ 生 (begets)
                             ▼
                        ┌──────────┐
                        │  一  One  │  命令进入系统
                        │  Unity    │  fish-ecology-assistant
                        └────┬─────┘
                             │ 生 (begets)
                ┌────────────┴────────────┐
                ▼                         ▼
        ┌─────────────┐          ┌─────────────┐
        │  二 Yin · 阴 │◄─对立─►│  二 Yang · 阳 │  太极生两仪
        │  fish · S/V0 │  统一   │cognitive·V/V1│  矛盾与统一
        │  知识 · 静态  │         │  验证 · 动态  │
        └──────┬──────┘          └──────┬──────┘
               │                        │
               └──────────┬─────────────┘
                          │ 生 (begets)
                          ▼
        ┌─────────────────────────────────────┐
        │           三  Three                  │
        │        Triangle Core · 密闭三元组    │
        │                                     │
        │  ┌─────────┐ ┌─────────┐ ┌───────┐ │
        │  │fish·Yin │ │cog·Yang │ │eon·合 │ │
        │  │  S/V0   │ │  V/V1   │ │Coord  │ │
        │  └─────────┘ └─────────┘ └───────┘ │
        └──────────────────┬──────────────────┘
                           │ 生 (begets)
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │porpoise │ │ coilia  │ │conflict │
        │   P₁    │ │   P₂    │ │    C    │
        │ 江豚专研│ │ 刀鲚专研│ │ 冲突仲裁│
        └─────────┘ └─────────┘ └─────────┘
              │            │
              ▼            ▼
          P₃, P₄, P₅ ... 万物 Myriad
          论文 · 报告 · 声学 · 种群 · 裁决 · ......
          非一万种，而是一切可能。
        """

    # ── 内部 ──

    def _get_orchestrator(self) -> Any:
        from .orchestrator import get_orchestrator
        return get_orchestrator()

    def _ensure_triangle(self, key: str) -> Any:
        if key == "fish":
            return self
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
            self._errors[key] = f"三角之{info.symbol}({info.pole})不可用"
        return adapter

    def _ensure_derived(self, key: str) -> Any:
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
        import importlib.util, sys
        proj_dir = self._workspace / directory
        adapter_file = proj_dir / adapter_module
        if not adapter_file.is_file():
            if not required:
                return None
            return None
        proj_str = str(proj_dir)
        if proj_str not in sys.path:
            sys.path.insert(0, proj_str)
        try:
            spec = importlib.util.spec_from_file_location(
                f"_hub_{directory}_{id(self) % 10000}", str(adapter_file))
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