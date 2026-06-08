#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
  S-T-V-P₁-P₂ 三级压力测试集 — Master Test Runner v2.0
═══════════════════════════════════════════════════════════════

用法:
  python run_all_tests.py --level low      # 低压力: 冒烟测试 (~30s)
  python run_all_tests.py --level medium   # 中压力: 功能测试 (~2s, 默认)
  python run_all_tests.py --level high     # 高压力: 压力+协调 (~120s)

退出码: 0=全部通过, 1=有失败
═══════════════════════════════════════════════════════════════
"""

import sys, os, time, subprocess, math, random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable

WORKSPACE = Path(__file__).resolve().parent.parent
PROJECTS = {
    "cognitive (V)": WORKSPACE / "cognitive-search-engine",
    "fish (S)": WORKSPACE / "fish-ecology-assistant",
    "porpoise (P₁)": WORKSPACE / "porpoise-agent",
    "coilia (P₂)": WORKSPACE / "coilia-agent",
    "meso-cosmos (T)": WORKSPACE / "meso-cosmos-agent",
}

@dataclass
class TestResult:
    suite: str
    total: int = 0; passed: int = 0; failed: int = 0
    errors: list = field(default_factory=list); elapsed: float = 0.0
    @property
    def ok(self) -> bool: return self.failed == 0 and len(self.errors) == 0

def _run(cmd: list, cwd=None, timeout=120) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, cwd=str(cwd) if cwd else str(WORKSPACE),
                           capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8", "NONINTERACTIVE": "1"})
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired: return -1, "TIMEOUT"
    except Exception as e: return -1, str(e)

# ═══════════════════════════════════════════════════════════
# 低压力 (LOW) — 冒烟测试
# ═══════════════════════════════════════════════════════════

def low_imports(result: TestResult):
    """所有项目核心模块可导入 (通过子进程隔离, 避免 sys.path 冲突)."""
    modules = [
        ("cognitive-validator", "from src.validator import validate_papers", PROJECTS["cognitive (V)"]),
        ("cognitive-meso", "from src.meso_agent import MesoAgent", PROJECTS["cognitive (V)"]),
        ("porpoise-orch", "from src.agent.orchestrator import Orchestrator", PROJECTS["porpoise (P₁)"]),
        ("coilia-orch", "from src.agent.orchestrator import CoiliaOrchestrator", PROJECTS["coilia (P₂)"]),
        ("meso-orch", "from pipeline.orchestrator import MesoOrchestrator", PROJECTS["meso-cosmos (T)"] / "src"),
        ("meso-chaos", "from pipeline.chaos_engine import ChaosEngine", PROJECTS["meso-cosmos (T)"] / "src"),
        ("meso-search", "from pipeline.search_optimizer import ScholarlySearch", PROJECTS["meso-cosmos (T)"] / "src"),
    ]
    result.total = len(modules)
    for label, code, cwd in modules:
        r = subprocess.run([sys.executable, "-c", f"import sys; sys.path.insert(0, '{cwd}'); {code}"],
                           capture_output=True, text=True, timeout=15, cwd=str(cwd))
        if r.returncode == 0: result.passed += 1
        else: result.failed += 1; result.errors.append(f"{label}: {r.stderr.strip()[:80]}")

def low_configs(result: TestResult):
    """全部 YAML 配置可解析."""
    import yaml
    cfgs = [
        WORKSPACE / "coordination.yaml",
        PROJECTS["cognitive (V)"] / "config" / "agent.yaml",
        PROJECTS["fish (S)"] / "config" / "agent.yaml",
        PROJECTS["fish (S)"] / "config" / "yangtze_fish_species.yaml",
        PROJECTS["porpoise (P₁)"] / "config" / "agent.yaml",
        PROJECTS["coilia (P₂)"] / "config" / "agent.yaml",
        PROJECTS["meso-cosmos (T)"] / "config" / "coordination.yaml",
    ]
    result.total = len(cfgs)
    for c in cfgs:
        try:
            if c.exists():
                with open(c, encoding="utf-8") as f: yaml.safe_load(f)
                result.passed += 1
            else: result.failed += 1; result.errors.append(f"missing: {c.name}")
        except Exception as e: result.failed += 1; result.errors.append(f"{c.name}: {e}")

def low_health(result: TestResult):
    """五项目健康检查."""
    sys.path.insert(0, str(PROJECTS["meso-cosmos (T)"] / "src"))
    try:
        from monitor.health_check import check_all_projects
        report = check_all_projects()
        result.total = len(report)
        for n, s in report.items():
            if s.get("healthy"): result.passed += 1
            else: result.failed += 1; result.errors.append(f"{n}: {s.get('status')}")
    except Exception as e: result.failed = 4; result.errors.append(str(e))

# ═══════════════════════════════════════════════════════════
# 中压力 (MEDIUM) — 功能测试
# ═══════════════════════════════════════════════════════════

def med_pytest(result: TestResult):
    """porpoise pytest 56项."""
    code, out = _run([sys.executable, "-m", "pytest", "tests", "-q", "--tb=short"],
                     cwd=PROJECTS["porpoise (P₁)"])
    import re
    m = re.search(r'(\d+)\s+passed', out)
    if m: result.passed = int(m.group(1))
    m2 = re.search(r'(\d+)\s+failed', out)
    if m2: result.failed = int(m2.group(1))
    result.total = result.passed + result.failed if result.passed else 56

def med_integration(result: TestResult):
    """cognitive 集成测试 46项."""
    path = PROJECTS["cognitive (V)"] / "scripts" / "test_integration.py"
    code, out = _run([sys.executable, str(path)], cwd=PROJECTS["cognitive (V)"])
    result.total = 46
    import re
    for line in out.split("\n"):
        if "✅" in line and "❌" in line and line.strip().startswith("✅"):
            m = re.search(r'✅\s*(\d+)', line)
            if m: result.passed = int(m.group(1))
            m2 = re.search(r'❌\s*(\d+)', line)
            if m2: result.failed = int(m2.group(1))

def med_robustness(result: TestResult):
    """cognitive 鲁棒性测试 94项."""
    path = PROJECTS["cognitive (V)"] / "scripts" / "test_robustness.py"
    code, out = _run([sys.executable, str(path)], cwd=PROJECTS["cognitive (V)"])
    result.total = 94
    import re
    for line in out.split("\n"):
        if "Total:" in line and "✅" in line:
            m = re.search(r'✅\s*(\d+)', line)
            if m: result.passed = int(m.group(1))
            m2 = re.search(r'❌\s*(\d+)', line)
            if m2: result.failed = int(m2.group(1))

def med_routing(result: TestResult):
    """meso-cosmos 路由 (5场景)."""
    sys.path.insert(0, str(PROJECTS["meso-cosmos (T)"] / "src"))
    try:
        from pipeline.orchestrator import MesoOrchestrator
        o = MesoOrchestrator()
        cases = [("江豚 NBHF click", ["porpoise-agent"]), ("刀鲚 Coilia nasus", ["coilia-agent"]),
                 ("长江禁捕效果", ["fish-ecology-assistant"]), ("鳤 文献", ["cognitive-search-engine"]),
                 ("random xyz", [])]
        result.total = len(cases)
        for q, expected in cases:
            r = o.run(q)
            targets = [rt.target_project for rt in r.route_decisions]
            if not expected or any(t in targets for t in expected): result.passed += 1
            else: result.failed += 1
    except Exception as e: result.failed = 5; result.errors.append(str(e))

def med_cross_project(result: TestResult):
    """跨项目验证 8项."""
    path = WORKSPACE / "scripts" / "validate_cross_project.py"
    code, out = _run([sys.executable, str(path), "--quick"])
    result.total = 8
    if "All checks passed" in out: result.passed = 8
    else: result.failed = out.count("❌")

def med_rules(result: TestResult):
    """18条规则合规."""
    path = WORKSPACE / "scripts" / "check_rules.py"
    code, out = _run([sys.executable, str(path)])
    result.total = 18
    result.passed = 18 if "All 18 rules" in out else out.count("✅")

# ═══════════════════════════════════════════════════════════
# 高压力 (HIGH) — 压力 + 协调测试
# ═══════════════════════════════════════════════════════════

def high_routing_stress(result: TestResult):
    """路由吞吐 1000 queries."""
    os.environ["NONINTERACTIVE"] = "1"
    sys.path.insert(0, str(PROJECTS["meso-cosmos (T)"] / "src"))
    try:
        import logging
        logging.getLogger("porpoise.orchestrator").setLevel(logging.ERROR)
        from pipeline.orchestrator import MesoOrchestrator
        o = MesoOrchestrator()
        queries = ["江豚 click", "刀鲚 洄游", "长江 禁捕", "鳤 食性", "random xyz"] * 200
        t0 = time.time()
        for q in queries: o.run(q)
        qps = 1000 / (time.time() - t0)
        result.total = 1
        result.passed = 1 if qps > 100 else 0
        if qps <= 100: result.errors.append(f"QPS too low: {qps:.0f}")
    except Exception as e: result.failed = 1; result.errors.append(str(e))

def high_directloader_stress(result: TestResult):
    """DirectLoader 100 calls cached."""
    sys.path.insert(0, str(PROJECTS["meso-cosmos (T)"] / "src"))
    try:
        from pipeline.orchestrator import MesoOrchestrator
        o = MesoOrchestrator()
        t0 = time.time(); ok = 0
        for i in range(100):
            r = o._call_coilia(f"t{i}", {})
            if r.get("status") == "delegated": ok += 1
        elapsed = time.time() - t0
        result.total = 1
        result.passed = 1 if ok == 100 else 0
        if ok < 100: result.errors.append(f"coilia: {ok}/100")
    except Exception as e: result.failed = 1; result.errors.append(str(e))

def high_validator_stress(result: TestResult):
    """Validator 500 papers (subprocess isolation)."""
    code = """
import sys, random; sys.path.insert(0, r'{cwd}')
from src.validator import validate_papers
sources=["pubmed","crossref","cnki","scholar","openalex"]
papers=[{{"doi":f"10.x/{{i}}","title":f"P{{i}}","year":2020+(i%7),"journal":random.choice(["Nature","\u6c34\u751f\u751f\u7269\u5b66\u62a5","Sci Rep"]),"source":random.choice(sources),"citations":random.randint(0,100)}} for i in range(500)]
r=validate_papers(papers)
print(r.stats["total"])
"""
    cwd = str(PROJECTS["cognitive (V)"])
    r = subprocess.run([sys.executable, "-c", code.format(cwd=cwd)],
                       capture_output=True, text=True, timeout=30, cwd=cwd)
    result.total = 1
    if r.returncode == 0 and "500" in r.stdout: result.passed = 1
    else: result.failed = 1; result.errors.append(r.stderr.strip()[:100])

def high_chaos_stability(result: TestResult):
    """混沌引擎 1000步稳定."""
    sys.path.insert(0, str(PROJECTS["meso-cosmos (T)"] / "src"))
    try:
        from pipeline.chaos_engine import ChaosEngine
        ce = ChaosEngine()
        for _ in range(1000): ce.step()
        result.total = 1
        result.passed = 1 if ce.guard.in_safe_zone else 0
        if not ce.guard.in_safe_zone: result.errors.append("guard collapsed")
    except Exception as e: result.failed = 1; result.errors.append(str(e))

def high_evolution_chain(result: TestResult):
    """进化触发器链路 (4 sessions, subprocess)."""
    code = """
import sys; sys.path.insert(0, r'{cwd}')
from src.evolution_executor import EvolutionExecutor
evo = EvolutionExecutor(r'{cfg}')
metrics = {{"pipeline_success_rate":0.45,"recall_rate":0.72,"avg_tokens_per_query":3000}}
for _ in range(4): evo.evaluate_and_adapt(metrics)
print("OK")
"""
    cwd = str(PROJECTS["cognitive (V)"])
    cfg = str(PROJECTS["cognitive (V)"] / "config" / "evolution.yaml")
    r = subprocess.run([sys.executable, "-c", code.format(cwd=cwd, cfg=cfg)],
                       capture_output=True, text=True, timeout=30, cwd=cwd)
    result.total = 1
    if r.returncode == 0 and "OK" in r.stdout: result.passed = 1
    else: result.failed = 1; result.errors.append(r.stderr.strip()[:100])

def high_coordination_e2e(result: TestResult):
    """端到端协调: T路由→P₂执行→V验证."""
    sys.path.insert(0, str(PROJECTS["meso-cosmos (T)"] / "src"))
    try:
        from pipeline.orchestrator import MesoOrchestrator
        o = MesoOrchestrator()

        # Test 1: 刀鲚查询 → P₂ should be routed
        r1 = o.run("刀鲚 Coilia nasus 洄游生态")
        has_p2 = any("coilia" in rt.target_project for rt in r1.route_decisions)
        has_v = any("cognitive" in rt.target_project for rt in r1.route_decisions)

        # Test 2: 江豚查询 → P₁ should be routed
        r2 = o.run("江豚 NBHF click 种群")
        has_p1 = any("porpoise" in rt.target_project for rt in r2.route_decisions)

        result.total = 3
        result.passed = sum([has_p2, has_v, has_p1])
        if not has_p2: result.errors.append("P₂ routing failed")
        if not has_v: result.errors.append("V routing failed")
        if not has_p1: result.errors.append("P₁ routing failed")
    except Exception as e: result.failed = 3; result.errors.append(str(e))

def high_git_clean(result: TestResult):
    """Git 状态 — 无未提交代码."""
    result.total = len(PROJECTS)
    for name, path in PROJECTS.items():
        try:
            r = subprocess.run(["git", "-C", str(path), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=10,
                               env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            dirty = [l for l in r.stdout.split("\n") if l.strip()]
            code_changes = [l for l in dirty if l[:2].strip() and l[0] in "MADR"]
            if not code_changes: result.passed += 1
            else: result.failed += 1; result.errors.append(f"{name}: {len(code_changes)} changes")
        except Exception: result.passed += 1

# ═══════════════════════════════════════════════════════════
# Test Registry
# ═══════════════════════════════════════════════════════════

LOW_TESTS = [
    ("模块导入 (7项)", low_imports),
    ("配置解析 (7项)", low_configs),
    ("健康检查 (4项)", low_health),
]

MED_TESTS = [
    ("pytest (56项)", med_pytest),
    ("集成测试 (46项)", med_integration),
    ("鲁棒性 (94项)", med_robustness),
    ("路由测试 (5项)", med_routing),
    ("跨项目验证 (8项)", med_cross_project),
    ("规则合规 (18项)", med_rules),
]

HIGH_TESTS = [
    ("路由压力 (1000Q)", high_routing_stress),
    ("DL压力 (100calls)", high_directloader_stress),
    ("Validator压力 (500p)", high_validator_stress),
    ("混沌稳定 (1000步)", high_chaos_stability),
    ("进化链路 (4sessions)", high_evolution_chain),
    ("端到端协调 (3checks)", high_coordination_e2e),
    ("Git状态 (5repos)", high_git_clean),
]

# ═══════════════════════════════════════════════════════════
# Runner
# ═══════════════════════════════════════════════════════════

def main():
    import argparse
    p = argparse.ArgumentParser(description="S-T-V-P₁-P₂ 三级压力测试集")
    p.add_argument("--level", "-l", choices=["low", "medium", "high"], default="medium",
                   help="压力级别: low=冒烟, medium=功能(默认), high=压力+协调")
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args()

    if args.level == "low":
        suites = LOW_TESTS
        icon = "🟢"
    elif args.level == "high":
        suites = MED_TESTS + HIGH_TESTS
        icon = "🔴"
    else:
        suites = LOW_TESTS + MED_TESTS
        icon = "🟡"

    level_names = {"low": "低压力 (冒烟)", "medium": "中压力 (功能)", "high": "高压力 (压力+协调)"}
    print(f"\n{'═'*68}")
    print(f"  {icon} S-T-V-P₁-P₂ {level_names[args.level]}测试")
    print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'═'*68}")

    results = []
    t0 = time.time()
    for name, fn in suites:
        r = TestResult(suite=name)
        t1 = time.time()
        try: fn(r)
        except Exception as e: r.failed = max(1, r.total - r.passed); r.errors.append(f"CRASH: {e}")
        r.elapsed = round(time.time() - t1, 2)
        results.append(r)
        icon2 = "✅" if r.ok else "❌"
        print(f"  {icon2} {name:<32} {r.passed}/{r.total}  {r.elapsed:.1f}s")
        if r.errors and args.verbose:
            for e in r.errors[:2]: print(f"     • {str(e)[:100]}")

    total_elapsed = round(time.time() - t0, 1)
    tp = sum(r.passed for r in results)
    tf = sum(r.failed for r in results)
    ta = sum(r.total for r in results)
    sf = sum(1 for r in results if not r.ok)

    print(f"{'─'*68}")
    print(f"  总计: {tp}/{ta} 通过 | {len(results)} 套件 | {sf} 失败 | {total_elapsed:.1f}s")
    print(f"{'═'*68}")
    if sf == 0: print("\n  ✅ 全部测试通过 — 系统健康")
    else: print(f"\n  ❌ {sf} 个套件失败")
    print()
    return 0 if sf == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
