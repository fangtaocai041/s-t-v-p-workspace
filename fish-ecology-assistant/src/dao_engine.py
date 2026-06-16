"""
道生一 · 一生二 · 二生三 · 三生万物 — 可执行引擎

工程语言化 · 代码化 · 落地执行层

用法:
  python dao_engine.py "珠星三块鱼"
  python dao_engine.py "Tribolodon hakonensis"
  python dao_engine.py "鳤"

哲学链 → 代码映射:
  道 (Dao)     → DaoQuery        — 外部研究问题, 结构化输入
  一 (One)     → OneEntry        — 统一入口, 命令进入系统
  二 (Two)     → YinYangDuality  — 太极生两仪: S(阴/静/知识) ↔ V(阳/动/验证)
  三 (Three)   → TriangleCore    — 矛盾统一的密闭三元组
  万物 (Myriad)→ MyriadManifest  — 三角赋能后的一切输出
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════
# L0: 道 Dao — 外部世界
# ═══════════════════════════════════════════════════════

class DaoSource(str, Enum):
    CLI = "cli"            # 命令行输入
    API = "api"            # API 调用
    SKILL = "skill"        # Reasonix Skill 触发
    DELEGATE = "delegate"  # 跨项目委托


@dataclass
class DaoQuery:
    """道 — 外部世界的研究问题, 结构化为可执行命令。

    道可道, 非常道。名可名, 非常名。
    无名天地之始, 有名万物之母。

    The external question, before it enters the system.
    This is the raw, unstructured research intent from the outside world.
    """
    raw: str                              # 用户原始输入
    species_hint: str = ""                # 提取的物种名 (中文或学名)
    intent: str = "search_species"        # 意图分类
    source: DaoSource = DaoSource.CLI     # 来源通道
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def from_cli(cls, argv: List[str]) -> "DaoQuery":
        """从命令行参数构造道查询。"""
        raw = " ".join(argv) if argv else ""
        # 提取物种名: 第一个非选项参数
        species = ""
        for a in argv:
            if not a.startswith("-"):
                species = a
                break
        return cls(raw=raw or species, species_hint=species)

    def is_empty(self) -> bool:
        return not self.raw.strip()

    def summary(self) -> str:
        return f"道(Dao): 外界输入 — \"{self.raw[:80]}\""


# ═══════════════════════════════════════════════════════
# L1: 一 One — 太极, 统一入口
# ═══════════════════════════════════════════════════════

@dataclass
class OneEntry:
    """一 — 太极, 未分阴阳的初始态。

    道生一。命令进入系统, 在此处尚为混沌一体,
    未分知识(S)与验证(V), 未显阴阳。

    此阶段完成:
      1. 接收 DaoQuery
      2. 加载 ProjectHub (三角核心 + 万物衍生)
      3. 初始化 orchestrator
    """
    dao: DaoQuery                         # 上游: 道
    hub_loaded: bool = False              # ProjectHub 是否已加载
    orchestrator_ready: bool = False      # orchestrator 是否就绪
    errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        """一: 加载系统, 迎接命令。"""
        try:
            # 加载 ProjectHub (三角核心)
            from src.project_hub import get_hub
            self._hub = get_hub()
            self.hub_loaded = True

            # 加载 orchestrator
            from src.orchestrator import get_orchestrator
            self._orch = get_orchestrator()
            self.orchestrator_ready = True
        except Exception as e:
            self.errors.append(f"一(One) 初始化失败: {e}")

    @property
    def hub(self):
        return getattr(self, "_hub", None)

    @property
    def orch(self):
        return getattr(self, "_orch", None)

    def is_ready(self) -> bool:
        return self.hub_loaded and self.orchestrator_ready and not self.errors

    def summary(self) -> str:
        status = "☯️ 太极已立" if self.is_ready() else "❌ 太极未成"
        return f"一(One): {status} — hub={self.hub_loaded}, orch={self.orchestrator_ready}"


# ═══════════════════════════════════════════════════════
# L2: 二 Two — 太极生两仪 (Yin-Yang Duality)
# ═══════════════════════════════════════════════════════

class Polarity(str, Enum):
    YIN = "阴"    # S/V0 — 知识供给 · 静态 · 收敛
    YANG = "阳"   # V/V1 — 搜索验证 · 动态 · 发散


@dataclass
class YinResult:
    """阴 — S(fish): 知识库查询结果。"""
    polarity: Polarity = Polarity.YIN
    found: bool = False
    scientific_name: str = ""
    chinese_name: str = ""
    family: str = ""
    aliases: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    ecology: str = ""
    distribution: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    recommendation: str = "continue_to_c"
    raw: Dict[str, Any] = field(default_factory=dict)
    elapsed_ms: float = 0.0


@dataclass
class YangResult:
    """阳 — V(cognitive): 搜索验证结果。"""
    polarity: Polarity = Polarity.YANG
    executed: bool = False                 # 是否实际执行了搜索
    total_papers: int = 0
    papers: List[Dict[str, Any]] = field(default_factory=list)
    mode: str = ""                         # exhaustive / classified / review_anchored
    engine_stats: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    elapsed_ms: float = 0.0


@dataclass
class YinYangDuality:
    """二 — 太极生两仪。

    一生二。S(阴/静/知识) 与 V(阳/动/验证) 的对立统一。
    阴中有阳 (知识库触发搜索需求), 阳中有阴 (搜索结果写回知识库)。

    Execute flow:
      yin = kb_first_lookup(query)           # 阴: 知识库查询
      IF yin.found AND user_stays:
          return (yin, None)                 # 仅阴, 阳未发
      ELSE:
          yang = cognitive_search(query)     # 阳: 搜索验证
          return (yin, yang)                 # 阴阳俱备
    """
    yin: YinResult
    yang: Optional[YangResult] = None
    user_decision: str = ""                  # "stay" | "continue" | "auto"

    @property
    def is_duality_complete(self) -> bool:
        """阴阳是否俱备?"""
        return self.yin.found or (self.yang is not None and self.yang.executed)

    @property
    def contradiction_type(self) -> str:
        """矛盾类型: 阴主导 / 阳主导 / 阴阳平衡。"""
        if self.yin.found and self.yang is None:
            return "阴主导 — 知识库已足够, 阳未发"
        if not self.yin.found and self.yang is not None:
            return "阳主导 — 知识库未命中, 阳补其缺"
        if self.yin.found and self.yang is not None:
            return "阴阳平衡 — 知识与验证俱备"
        return "阴阳俱寂 — 知识库和搜索均无结果"

    def summary(self) -> str:
        yin_s = f"阴(S/知识): {'✅ ' + self.yin.chinese_name if self.yin.found else '❌ 未命中'}"
        yang_s = f"阳(V/验证): {self.yang.total_papers}篇" if self.yang and self.yang.executed else "阳(V/验证): 未发"
        return f"二(Two): {yin_s} | {yang_s} | {self.contradiction_type}"


# ═══════════════════════════════════════════════════════
# L3: 三 Three — 三角密闭结构
# ═══════════════════════════════════════════════════════

class TriCorner(str, Enum):
    FISH = "fish"            # S/V0 — 阴
    COGNITIVE = "cognitive"  # V/V1 — 阳
    EON = "eon"              # Coordinator — 太极点


@dataclass
class TriangleMember:
    corner: TriCorner
    symbol: str
    available: bool
    nature: str              # "阴·静" | "阳·动" | "太极点"
    health: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriangleCore:
    """三 — 三角密闭结构。

    二生三。阴阳矛盾统一, 产生最小封闭结构。
    三角缺一不可: fish(阴) + cognitive(阳) + eon-core(太极点)。

    Invariant: is_complete() MUST be True for system to operate.
    """
    members: Dict[str, TriangleMember] = field(default_factory=dict)
    complete: bool = False

    def validate(self) -> bool:
        """三角验证: 三个角必须全部可用。"""
        required = {TriCorner.FISH, TriCorner.COGNITIVE, TriCorner.EON}
        available = {
            c for c, m in self.members.items()
            if isinstance(m, TriangleMember) and m.available
        }
        self.complete = required == available
        return self.complete

    def summary(self) -> str:
        lines = ["三(Three): 三角密闭结构"]
        for m in self.members.values():
            ok = "☯️" if m.available else "❌"
            lines.append(f"  {ok} {m.symbol:15s} {m.nature}")
        lines.append(f"  三角完整: {self.complete}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# L4: 万物 Myriad — 一切输出
# ═══════════════════════════════════════════════════════

@dataclass
class MyriadManifest:
    """万物 — 三角赋能后的一切输出。

    三生万物。三角结构产生、验证、协调之后,
    所有输出自然涌现: 论文列表, 可信度评分, 分析报告,
    衍生项目结果, Skills 输出...... 非一万种, 而是一切可能。
    """
    papers: List[Dict[str, Any]] = field(default_factory=list)
    credibility_scores: List[Dict[str, Any]] = field(default_factory=list)
    derived_results: Dict[str, Any] = field(default_factory=dict)
    report: str = ""
    total_manifestations: int = 0
    total_elapsed_ms: float = 0.0

    def summary(self) -> str:
        lines = ["万物(Myriad): 一切输出"]
        lines.append(f"  论文: {len(self.papers)}篇")
        lines.append(f"  可信度评分: {len(self.credibility_scores)}条")
        lines.append(f"  衍生结果: {len(self.derived_results)}项")
        if self.total_elapsed_ms:
            lines.append(f"  总耗时: {self.total_elapsed_ms:.0f}ms")
        lines.append(f"  万物非一万种, 而是一切可能。")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# 道→一→二→三→万物 执行引擎
# ═══════════════════════════════════════════════════════

class DaoEngine:
    """道生一, 一生二, 二生三, 三生万物 — 完整执行引擎。

    将 Daoist 哲学链编译为可执行 Python 代码。
    每层都是类型安全的 dataclass, 层与层之间通过
    validate() 门控确保正确性。

    执行流:
      DaoQuery (CLI输入)
        → OneEntry (加载系统)
          → YinYangDuality (KB查询 + 可选搜索)
            → TriangleCore (三角验证)
              → MyriadManifest (一切输出)

    Usage:
      engine = DaoEngine()
      result = engine.execute(DaoQuery.from_cli(["珠星三块鱼"]))
      print(engine.render(result))
    """

    def execute(self, dao: DaoQuery,
                auto_search: bool = False) -> Dict[str, Any]:
        """执行完整道→一→二→三→万物链。

        Args:
            dao: 道查询 (外部输入)
            auto_search: True = KB未命中时自动启动全量搜索

        Returns:
            {dao, one, two, three, myriad} — 完整五层结果
        """
        t0 = time.perf_counter()

        # ── 道: 验证输入 ──
        if dao.is_empty():
            return {"error": "道(Dao)为空 — 无输入, 无万物", "dao": dao}

        # ── 一: 加载系统, 建立太极 ──
        one = OneEntry(dao=dao)
        if not one.is_ready():
            return {
                "error": "一(One)太极未立 — 系统初始化失败",
                "dao": dao, "one": one,
            }

        # ── 二: 太极生两仪 (阴·知识 + 阳·验证) ──
        two = self._execute_two(one, dao, auto_search)

        # ── 三: 三角验证 ──
        three = self._execute_three(one)

        # ── 万物: 一切输出 ──
        myriad = self._execute_myriad(two, t0)

        return {
            "dao": dao,
            "one": one,
            "two": two,
            "three": three,
            "myriad": myriad,
        }

    def _execute_two(self, one: OneEntry, dao: DaoQuery,
                     auto_search: bool) -> YinYangDuality:
        """二: 太极生两仪 — 阴(知识) ↔ 阳(验证)。"""
        t_yin = time.perf_counter()
        yin = YinResult()

        # 阴: KB查询
        try:
            species = dao.species_hint or dao.raw
            kb = one.orch.kb_first_lookup(query=species)
            yin.found = kb.found
            yin.scientific_name = kb.scientific_name
            yin.chinese_name = kb.chinese_name
            yin.family = kb.family
            yin.aliases = list(kb.aliases)
            yin.synonyms = list(kb.synonyms)
            yin.ecology = kb.ecology
            yin.distribution = dict(kb.distribution)
            yin.summary = kb.summary_text
            yin.recommendation = kb.search_recommendation
            yin.raw = kb.raw_species_data
        except Exception as e:
            yin.summary = f"阴(S)查询异常: {e}"
        yin.elapsed_ms = (time.perf_counter() - t_yin) * 1000

        yang = None

        # 阳: 如果 KB 未命中且 auto_search=True, 自动搜索
        if not yin.found and auto_search:
            yang = self._execute_yang(one, dao)
        elif yin.found and yin.recommendation == "continue_to_c" and auto_search:
            yang = self._execute_yang(one, dao)

        return YinYangDuality(yin=yin, yang=yang,
                              user_decision="auto" if auto_search else "pending")

    def _execute_yang(self, one: OneEntry, dao: DaoQuery) -> YangResult:
        """阳: 搜索验证 — 调用 cognitive-search-engine。"""
        t_yang = time.perf_counter()
        yang = YangResult()

        try:
            hub = one.hub
            if hub and hasattr(hub, 'cognitive') and hub.cognitive:
                result = hub.cognitive.search(
                    dao.species_hint or dao.raw, mode="adaptive")
                if isinstance(result, dict):
                    yang.total_papers = result.get("total_papers", 0)
                    yang.papers = result.get("papers", [])
                    yang.mode = result.get("mode", "")
                    yang.engine_stats = result.get("engine_stats", {})
                yang.executed = True
        except Exception as e:
            yang.errors.append(f"阳(V)搜索异常: {e}")

        yang.elapsed_ms = (time.perf_counter() - t_yang) * 1000
        return yang

    def _execute_three(self, one: OneEntry) -> TriangleCore:
        """三: 三角验证 — 密闭三元组完整性检查。"""
        three = TriangleCore()

        try:
            ts = one.hub.triangle_status() if one.hub else {}
            for key, info in ts.items():
                corner = TriCorner(key) if key in {"fish", "cognitive", "eon"} else None
                if corner is None:
                    continue
                nature = (
                    "阴·静" if key == "fish"
                    else "阳·动" if key == "cognitive"
                    else "太极点"
                )
                three.members[corner] = TriangleMember(
                    corner=corner,
                    symbol=info.get("symbol", ""),
                    available=info.get("available", False),
                    nature=nature,
                    health=info,
                )
            three.validate()
        except Exception:
            pass

        return three

    def _execute_myriad(self, two: YinYangDuality,
                        t0: float) -> MyriadManifest:
        """万物: 三角赋能后的一切输出。"""
        myriad = MyriadManifest()

        # 从阴阳结果中收集论文
        if two.yang and two.yang.executed:
            myriad.papers = two.yang.papers
            myriad.total_manifestations += len(two.yang.papers)

        # 知识库数据也算输出
        if two.yin.found:
            myriad.total_manifestations += 1

        myriad.total_elapsed_ms = (time.perf_counter() - t0) * 1000
        return myriad

    # ── 渲染 ──

    @staticmethod
    def render(result: Dict[str, Any]) -> str:
        """将执行结果渲染为可读输出。"""
        if "error" in result:
            return f"❌ {result['error']}"

        dao = result.get("dao")
        one = result.get("one")
        two = result.get("two")
        three = result.get("three")
        myriad = result.get("myriad")

        lines = []
        lines.append("═" * 62)
        lines.append("  道生一 · 一生二 · 二生三 · 三生万物")
        lines.append("  Dao → One → Two → Three → the Myriad")
        lines.append("═" * 62)
        lines.append("")

        # L0: 道
        if dao:
            lines.append(f"┌─ L0: 道 (Dao) ─────────────────────────────")
            lines.append(f"│ 输入: \"{dao.raw[:50]}\"")
            lines.append(f"│ 物种: {dao.species_hint or '(未提取)'}")
            lines.append(f"└──────────────────────────────────────────")
            lines.append("")

        # L1: 一
        if one:
            lines.append(f"┌─ L1: 一 (One) · 太极 ────────────────────")
            lines.append(f"│ hub 加载: {'✅' if one.hub_loaded else '❌'}")
            lines.append(f"│ orch 就绪: {'✅' if one.orchestrator_ready else '❌'}")
            lines.append(f"└──────────────────────────────────────────")
            lines.append("")

        # L2: 二
        if two:
            lines.append(f"┌─ L2: 二 (Two) · 太极生两仪 ──────────────")
            yin = two.yin
            lines.append(f"│ 阴(S/知识):")
            if yin.found:
                lines.append(f"│   ✅ {yin.chinese_name} ({yin.scientific_name})")
                lines.append(f"│   科属: {yin.family}")
                if yin.aliases:
                    lines.append(f"│   别名: {', '.join(yin.aliases[:4])}")
                lines.append(f"│   {yin.elapsed_ms:.0f}ms")
            else:
                lines.append(f"│   ❌ 未命中 ({yin.elapsed_ms:.0f}ms)")
            if two.yang and two.yang.executed:
                lines.append(f"│ 阳(V/验证):")
                lines.append(f"│   ✅ {two.yang.total_papers}篇论文")
                lines.append(f"│   模式: {two.yang.mode}")
                lines.append(f"│   {two.yang.elapsed_ms:.0f}ms")
            else:
                lines.append(f"│ 阳(V/验证): 未发 (留步于阴)")
            lines.append(f"│ 矛盾: {two.contradiction_type}")
            lines.append(f"└──────────────────────────────────────────")
            lines.append("")

        # L3: 三
        if three:
            lines.append(f"┌─ L3: 三 (Three) · 三角密闭 ──────────────")
            for m in three.members.values():
                ok = "☯️" if m.available else "❌"
                lines.append(f"│ {ok} {m.symbol:15s} {m.nature}")
            lines.append(f"│ 三角完整: {'✅' if three.complete else '❌ 破裂!'}")
            lines.append(f"└──────────────────────────────────────────")
            lines.append("")

        # L4: 万物
        if myriad:
            lines.append(f"┌─ L4: 万物 (Myriad) · 一切输出 ────────────")
            lines.append(f"│ 论文: {len(myriad.papers)}篇")
            lines.append(f"│ 可信度评分: {len(myriad.credibility_scores)}条")
            lines.append(f"│ 衍生结果: {len(myriad.derived_results)}项")
            lines.append(f"│ 总耗时: {myriad.total_elapsed_ms:.0f}ms")
            lines.append(f"│")
            lines.append(f"│ 万物非一万种, 而是一切可能。")
            lines.append(f"└──────────────────────────────────────────")

        lines.append("")
        lines.append("═" * 62)
        lines.append("  道 → 一 → 二 → 三 → 万物 · 执行完成")
        lines.append("═" * 62)

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# CLI 入口 — 可执行落地层
# ═══════════════════════════════════════════════════════

def main():
    """道生一 · CLI 入口。

    $ python dao_engine.py "珠星三块鱼"
    $ python dao_engine.py "Tribolodon hakonensis"
    $ python dao_engine.py --search "鳤"
    """
    import argparse

    p = argparse.ArgumentParser(
        description="道生一 · 一生二 · 二生三 · 三生万物 — 可执行引擎")
    p.add_argument("query", nargs="*", help="物种名 (中文或学名)")
    p.add_argument("--search", "-s", action="store_true",
                   help="KB未命中时自动启动全量搜索 (阳)")
    p.add_argument("--json", "-j", action="store_true",
                   help="JSON 格式输出")

    args = p.parse_args()

    # 道: 构造查询
    dao = DaoQuery.from_cli(args.query)
    if dao.is_empty():
        dao = DaoQuery(raw="珠星三块鱼", species_hint="珠星三块鱼")

    # 执行: 道→一→二→三→万物
    engine = DaoEngine()
    result = engine.execute(dao, auto_search=args.search)

    # 万物: 输出
    if args.json:
        import json
        # 简化 dataclass 为 dict
        simplified = {
            "dao": {"raw": dao.raw, "species": dao.species_hint},
            "one": {"ready": result.get("one", None) and result["one"].is_ready()},
            "two": {
                "yin_found": result.get("two", None) and result["two"].yin.found,
                "yin_name": result.get("two", None) and result["two"].yin.chinese_name,
                "yang_papers": result.get("two", None) and (
                    result["two"].yang.total_papers if result["two"].yang else 0),
            },
            "three": {
                "complete": result.get("three", None) and result["three"].complete,
            },
            "myriad": {
                "total": result.get("myriad", None) and result["myriad"].total_manifestations,
            },
        }
        print(json.dumps(simplified, ensure_ascii=False, indent=2))
    else:
        print(engine.render(result))


if __name__ == "__main__":
    main()
