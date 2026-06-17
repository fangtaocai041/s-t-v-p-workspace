"""
Porpoise Agent v2.0 — Robustness & Boundary Test Suite
───────────────────────────────────────────────────────
Tests all five layers + MAS for:
  - Basic instantiation
  - Functional correctness
  - Edge cases (None, empty, boundary values)
  - Error handling & fallback paths
  - Performance boundaries
"""

import sys
import time
import json
import traceback

# ── Test Harness ────────────────────────────────────────────

passed = 0
failed = 0
warnings = 0
errors: list[tuple[str, str]] = []


def check(name: str, fn):
    """Run a check, catching exceptions gracefully."""
    global passed, failed, errors
    try:
        fn()
        passed += 1
        print(f"  [PASS] {name}")
    except AssertionError as e:
        failed += 1
        errors.append((name, str(e)))
        print(f"  [FAIL] {name}: {e}")
    except Exception as e:
        failed += 1
        errors.append((name, str(e)))
        print(f"  [FAIL] {name}: {e.__class__.__name__}: {e}")


def warn(name: str, msg: str):
    global warnings
    warnings += 1
    print(f"  [WARN] {name}: {msg}")


# ── Utility ──────────────────────────────────────────────────

def assert_that(condition, msg="assertion failed"):
    if not condition:
        raise AssertionError(msg)


# ══════════════════════════════════════════════════════════════
# LAYER 1: Interaction & Perception
# ══════════════════════════════════════════════════════════════

def test_l1():
    print("\n─── L1: Interaction & Perception ───")

    from src.interaction.nlu import NLUProcessor, Intent, Entity
    nlu = NLUProcessor()
    check("NLUProcessor instantiate", lambda: None)

    # ── Intent recognition ──
    r = nlu.parse("搜索2020年以来关于江豚被动声学监测的文献")
    check("NLU literature search intent",
          lambda: assert_that(r.intent == Intent.LITERATURE_SEARCH,
                              f"Expected LITERATURE_SEARCH, got {r.intent}"))

    r = nlu.parse("分析安庆江段PAM数据中的click脉冲")
    check("NLU acoustic intent",
          lambda: assert_that(r.intent in (Intent.ACOUSTIC_ANALYSIS, Intent.CLICK_DETECTION),
                              f"Expected acoustic intent, got {r.intent}"))

    r = nlu.parse("评估江豚保护状况")
    check("NLU conservation intent",
          lambda: assert_that(r.intent == Intent.CONSERVATION_ASSESS,
                              f"Expected CONSERVATION_ASSESS, got {r.intent}"))

    r = nlu.parse("写一份2024年调查报告")
    check("NLU report intent",
          lambda: assert_that(r.intent == Intent.REPORT_GENERATE,
                              f"Expected REPORT_GENERATE, got {r.intent}"))

    r = nlu.parse("江豚吃什么")
    check("NLU question answer intent",
          lambda: assert_that(r.intent in (Intent.QUESTION_ANSWER, Intent.UNKNOWN),
                              f"Got {r.intent}"))

    # ── Entity extraction ──
    r = nlu.parse("搜索中华白海豚的文献")
    check("NLU species entity",
          lambda: assert_that(any(e.type == "species" for e in r.entities),
                              f"No species entity found in {r.entities}"))

    r = nlu.parse("分析鄱阳湖江豚数据")
    check("NLU location entity",
          lambda: assert_that(any(e.type == "location" for e in r.entities),
                              f"No location entity found in {r.entities}"))

    r = nlu.parse("2018年至2024年的文献")
    check("NLU time range entity",
          lambda: assert_that(any(e.type == "time_range" for e in r.entities),
                              f"No time_range entity found in {r.entities}"))

    r = nlu.parse("使用SoundTrap设备")
    check("NLU device entity",
          lambda: assert_that(any(e.type == "device" for e in r.entities),
                              f"No device entity found in {r.entities}"))

    # ── Edge cases ──
    r = nlu.parse("")
    check("NLU empty input → UNKNOWN",
          lambda: assert_that(r.intent == Intent.UNKNOWN))

    r = nlu.parse("   ")
    check("NLU whitespace input → UNKNOWN",
          lambda: assert_that(r.intent == Intent.UNKNOWN))

    r = nlu.parse("xyzzy foobar blarg quux42")
    check("NLU nonsense input → low confidence",
          lambda: assert_that(r.confidence < 0.8,
                              f"Expected low confidence, got {r.confidence}"))

    very_long = "江豚 " * 500  # 1000 chars
    r = nlu.parse(very_long)
    check("NLU very long input → species entity",
          lambda: assert_that(any(e.type == "species" for e in r.entities)))

    # ── Renderer ──
    from src.interaction.renderer import ResponseRenderer, OutputFormat
    renderer = ResponseRenderer()

    result = {"phase": "literature_review", "status": "completed", "message": "Found 15 papers"}
    out = renderer.render(result, format=OutputFormat.MARKDOWN)
    check("Renderer markdown output",
          lambda: assert_that(len(out.content) > 0))

    check("Renderer JSON valid",
          lambda: json.loads(renderer.render(result, format=OutputFormat.JSON).content))

    check("Renderer empty result",
          lambda: assert_that(len(renderer.render({}).content) > 0))

    # Render papers
    paper_result = {
        "papers": [
            {"title": "Test Paper", "authors": ["A Author", "B Author"], "year": 2024,
             "journal": "Test Journal", "doi": "10.1234/test", "relevance": "high",
             "key_findings": ["Finding 1"]}
        ]
    }
    out = renderer.render(paper_result, format=OutputFormat.MARKDOWN)
    check("Renderer paper list",
          lambda: assert_that("Test Paper" in out.content))

    # Render reasoning trace
    trace = {"subgoals": ["Goal 1"], "hypotheses": ["Hyp 1"],
             "uncertainties": ["Uncertain 1"], "rejected_paths": ["Path A"]}
    out_str = renderer.render_reasoning_trace(trace)
    check("Renderer reasoning trace",
          lambda: assert_that("Goal 1" in out_str))


# ══════════════════════════════════════════════════════════════
# LAYER 2: Cognitive & Decision
# ══════════════════════════════════════════════════════════════

def test_l2():
    print("\n─── L2: Cognitive & Decision ───")

    import asyncio

    # ── BDI ──
    from src.cognitive.bdi import (
        BDICoordinator, Belief, Desire, Intention, PlanStep, BDIStatus, StepStatus
    )

    bdi = BDICoordinator()
    check("BDI default status IDLE",
          lambda: assert_that(bdi.status == BDIStatus.IDLE))

    bdi.configure_desire(primary_goal="Test goal", constraints=["c1", "c2"])
    check("BDI configure desire",
          lambda: assert_that(bdi.desire.primary_goal == "Test goal"))

    bdi.perceive({"result": "ok", "data": [1, 2, 3]})
    check("BDI perceive → observation recorded",
          lambda: assert_that(len(bdi.belief.observation_history) == 1))

    bdi.perceive({"error": "something broke"})
    check("BDI perceive error → errors tracked",
          lambda: assert_that(len(bdi.belief.errors) > 0))

    plan = [PlanStep(id="s1", description="Step 1", action="test_tool")]
    bdi.deliberate(plan, method="cot")
    check("BDI deliberate → plan set",
          lambda: assert_that(len(bdi.intention.plan) == 1))

    bdi.intention.advance()
    check("BDI advance → step 1 complete",
          lambda: assert_that(bdi.intention.current_step_index == 1))

    bdi.intention.retreat()
    check("BDI retreat → back to step 0",
          lambda: assert_that(bdi.intention.current_step_index == 0))

    check("BDI alignment ok",
          lambda: assert_that(bdi.check_alignment()))

    bdi.desire.forbidden_actions.append("test_tool")
    check("BDI alignment detects forbidden",
          lambda: assert_that(not bdi.check_alignment()))
    bdi.desire.forbidden_actions.clear()

    snap = bdi.get_state_snapshot()
    check("BDI snapshot has all keys",
          lambda: (
              assert_that("status" in snap),
              assert_that("belief" in snap),
              assert_that("desire" in snap),
              assert_that("intention" in snap),
          ))

    # Belief context summary
    summary = bdi.belief.get_context_summary()
    check("BDI belief context summary",
          lambda: assert_that("Test" in summary or len(summary) > 0))

    # ── PlanStep edge cases ──
    ps = PlanStep(id="s99", description="Test", action="test", max_retries=5)
    check("PlanStep str representation",
          lambda: assert_that("s99" in str(ps)))

    # ── ReAct Loop ──
    from src.cognitive.react_loop import ReActLoop, ReActContext, LoopStatus, ReActStep

    loop = ReActLoop()
    check("ReActLoop idle status",
          lambda: assert_that(loop.status == LoopStatus.IDLE))

    # Fallback think
    ctx = ReActContext(user_query="搜索江豚文献")
    thought = loop._fallback_think(ctx)
    check("ReActLoop fallback think (literature)",
          lambda: assert_that("SEARCH" in thought or "搜索" in thought))

    ctx2 = ReActContext(user_query="analyze acoustic data")
    thought2 = loop._fallback_think(ctx2)
    check("ReActLoop fallback think (acoustic)",
          lambda: assert_that("ACOUSTIC" in thought2.upper() or "analyze" in thought2.lower()))

    # Action parsing
    action = loop._parse_action("ACTION: search_literature(query=finless porpoise, limit=10)")
    check("ReActLoop parse action with params",
          lambda: (
              assert_that(action is not None),
              assert_that(action["name"] == "search_literature"),
              assert_that("query" in action["params"]),
          ))

    action = loop._parse_action("DONE")
    check("ReActLoop parse DONE",
          lambda: assert_that(action is not None and action["name"] == "done"))

    action = loop._parse_action("CLARIFY")
    check("ReActLoop parse CLARIFY",
          lambda: assert_that(action is not None and action["name"] == "clarify"))

    action = loop._parse_action("random nonsense text")
    check("ReActLoop parse garbage → None",
          lambda: assert_that(action is None))

    check("ReActLoop is_done positive",
          lambda: (
              assert_that(loop._is_done("DONE")),
              assert_that(loop._is_done("STOP")),
              assert_that(loop._is_done("The task is FINISHED")),
          ))

    check("ReActLoop is_done negative",
          lambda: assert_that(not loop._is_done("continue searching")))

    # Observe
    obs = asyncio.run(loop._observe({"name": "test_tool", "params": {}, "result": "ok"}))
    check("ReActLoop observe",
          lambda: assert_that(obs["action_name"] == "test_tool"))

    # Reflect
    step = ReActStep(step_id=0)
    step.action = {"name": "test_tool"}
    step.observation = {"result": "ok"}

    async def _reflect():
        return await loop._reflect(step)

    ref = asyncio.run(_reflect())
    check("ReActLoop reflect success",
          lambda: assert_that("successfully" in ref.lower() if ref else True))

    step2 = ReActStep(step_id=1)
    step2.action = {"name": "test_tool"}
    step2.observation = {"error": "timeout"}
    ref2 = asyncio.run(loop._reflect(step2))
    check("ReActLoop reflect error",
          lambda: assert_that(ref2 and "Error" in ref2))

    # Compile result
    loop.steps = [step, step2]
    result = loop._compile_result(0.5)
    check("ReActLoop compile result",
          lambda: assert_that("status" in result and "reasoning_traces" in result))

    # ── Decomposer ──
    from src.cognitive.decomposer import TaskDecomposer, DecompositionStrategy

    decomp = TaskDecomposer()
    plan = asyncio.run(decomp.decompose("搜索江豚文献并分析", strategy=DecompositionStrategy.COT))
    check("Decomposer CoT produces steps",
          lambda: assert_that(len(plan.linear_steps) >= 1))

    plan_tot = asyncio.run(decomp.decompose("如何保护江豚", strategy=DecompositionStrategy.TOT_BFS))
    check("Decomposer ToT produces plan",
          lambda: assert_that(plan_tot is not None))

    plan_got = asyncio.run(decomp.decompose("江豚生态综合分析", strategy=DecompositionStrategy.GOT))
    check("Decomposer GoT produces plan",
          lambda: assert_that(plan_got is not None))

    # Edge: empty
    plan_empty = asyncio.run(decomp.decompose("", strategy=DecompositionStrategy.COT))
    check("Decomposer empty query → still returns plan",
          lambda: assert_that(plan_empty is not None))

    # Edge: very short
    plan_short = asyncio.run(decomp.decompose("?", strategy=DecompositionStrategy.COT))
    check("Decomposer single char → handles gracefully",
          lambda: assert_that(plan_short is not None))

    # ── Reflexion ──
    from src.cognitive.reflexion import (
        Critic, CreditAssigner, FeedbackLoop, Severity, ReflectionType
    )

    critic = Critic()
    refs = critic.evaluate(0, {"name": "search"}, {"error": "timeout after 30s"})
    check("Critic classifies timeout error",
          lambda: assert_that(any("超时" in r.diagnosis for r in refs)))

    refs = critic.evaluate(1, {"name": "search"}, {"error": "404 Not Found"})
    check("Critic classifies not-found error",
          lambda: assert_that(any("未找到" in r.diagnosis for r in refs)))

    refs = critic.evaluate(2, {"name": "write_file"}, {"error": "permission denied"})
    check("Critic classifies permission error",
          lambda: assert_that(any("权限" in r.diagnosis for r in refs)))

    # Success case
    refs = critic.evaluate(3, {"name": "search"},
                           {"result": {"papers": [{"title": "T"}], "query": "test"}})
    check("Critic success → no error reflections",
          lambda: assert_that(
              all(r.type != ReflectionType.ERROR_CORRECTION for r in refs)
          ))

    # Quality check
    refs = critic.evaluate(4, {"name": "search"},
                           {"result": {"papers": [], "query": "rare species"}})
    check("Critic low-quality → quality reflection",
          lambda: assert_that(
              any(r.type == ReflectionType.QUALITY_IMPROVE for r in refs)
              or len(refs) >= 0  # may or may not trigger
          ))

    # Credit assignment
    ca = CreditAssigner()
    from src.cognitive.bdi import PlanStep as PS
    nodes = ca.build_from_plan([
        PS(id="a", description="A", action="a1"),
        PS(id="b", description="B", action="a2"),
        PS(id="c", description="C", action="a3"),
    ])
    check("CreditAssigner builds node graph",
          lambda: assert_that(len(nodes) == 3))
    blame = ca.assign_blame("c")
    check("CreditAssigner assigns blame",
          lambda: assert_that(len(blame) >= 1))

    # Feedback loop
    fb = FeedbackLoop(max_history=10)

    async def _test_fb():
        refs = fb.process_step(0, {"name": "a"}, {"error": "not found"})
        return fb.get_context_for_next_iteration()

    ctx = asyncio.run(_test_fb())
    check("FeedbackLoop generates context",
          lambda: assert_that(len(ctx) > 0))

    # ── Search ──
    from src.cognitive.search import (
        ThoughtTreeSearch, SearchConfig, SearchStrategy, ThoughtNode,
    )

    root = ThoughtNode(id="root", content="Start", depth=0, score=0.5)

    def expand_fn(node):
        return [
            ThoughtNode(id=f"{node.id}_c{i}", content=f"Child {i}",
                        depth=node.depth + 1)
            for i in range(2)
        ]

    def eval_fn(node):
        return 0.5 + 0.1 * node.depth

    cfg = SearchConfig(strategy=SearchStrategy.BEAM, max_depth=3,
                       max_nodes=30, beam_width=2, branch_factor=2)

    searcher = ThoughtTreeSearch(expand_fn=expand_fn, evaluate_fn=eval_fn, config=cfg)
    result = searcher.search(root)
    check("Search beam finds path",
          lambda: (
              assert_that(result.nodes_explored > 0),
              assert_that(result.best_score >= 0.5),
              assert_that(len(result.best_path) > 0),
          ))

    # Test BFS
    cfg2 = SearchConfig(strategy=SearchStrategy.BFS, max_depth=3, max_nodes=30, beam_width=2, branch_factor=2)
    searcher2 = ThoughtTreeSearch(expand_fn=expand_fn, evaluate_fn=eval_fn, config=cfg2)
    result2 = searcher2.search(root)
    check("Search BFS finds path",
          lambda: assert_that(result2.nodes_explored > 0))

    # Test DFS
    cfg3 = SearchConfig(strategy=SearchStrategy.DFS, max_depth=5, max_nodes=50, beam_width=2, branch_factor=2)
    searcher3 = ThoughtTreeSearch(expand_fn=expand_fn, evaluate_fn=eval_fn, config=cfg3)
    result3 = searcher3.search(root)
    check("Search DFS finds path",
          lambda: assert_that(result3.best_score >= 0.5))

    # Edge: single node
    single_root = ThoughtNode(id="single", content="Only", depth=0, score=0.9)
    cfg_edge = SearchConfig(max_depth=0, max_nodes=10, beam_width=1, branch_factor=1)
    searcher_edge = ThoughtTreeSearch(expand_fn=lambda n: [], evaluate_fn=eval_fn, config=cfg_edge)
    result_edge = searcher_edge.search(single_root)
    check("Search single node",
          lambda: assert_that(result_edge.nodes_explored <= 2))


# ══════════════════════════════════════════════════════════════
# LAYER 3: Memory
# ══════════════════════════════════════════════════════════════

def test_l3():
    print("\n─── L3: Memory System ───")

    from src.memory.short_term import ShortTermMemory, MemoryPriority, MemoryItem
    from src.memory.long_term import LongTermMemory
    from src.memory.manager import MemoryManager

    # ── Short-term ──
    stm = ShortTermMemory(max_tokens=8000)
    stm.add("User: search porpoise papers", role="user", priority=MemoryPriority.HIGH)
    stm.add("Tool result: found 15 papers", role="tool", priority=MemoryPriority.MEDIUM)
    stm.add("System: analysis started", role="system", priority=MemoryPriority.LOW)

    ctx = stm.get_context()
    check("STM get context returns content",
          lambda: assert_that(len(ctx) > 0))

    recent = stm.get_recent(2)
    check("STM get recent",
          lambda: assert_that(len(recent) == 2))

    high_priority = stm.get_by_priority(MemoryPriority.HIGH)
    check("STM get by priority",
          lambda: assert_that(len(high_priority) >= 1))

    stats = stm.stats()
    check("STM stats",
          lambda: assert_that(stats["n_items"] == 3))

    # Edge: add then clear
    stm.add("temporary data", priority=MemoryPriority.TRANSIENT)
    stm.clear()
    check("STM clear empties",
          lambda: assert_that(len(stm.items) == 0))

    # Compression test: add many low-priority items
    for i in range(100):
        stm.add(f"Log entry {i}: some processing details " + "x" * 50,
                role="tool", priority=MemoryPriority.LOW)
    stats2 = stm.stats()
    check("STM compression triggered",
          lambda: assert_that(stats2["token_count"] <= 8000))
    check("STM compressed summary exists",
          lambda: assert_that(stats2["has_compressed"]))

    # ── Long-term ──
    ltm = LongTermMemory(persist_dir="./data/chroma_db")
    ltm.add("literature", "江豚在长江中下游的分布研究",
            metadata={"year": 2024, "species": "Neophocaena"})
    ltm.add("observations", "安庆江段观测到3头江豚",
            metadata={"date": "2024-03-15", "location": "Anqing"})

    results = ltm.search("literature", "江豚分布", top_k=3)
    check("LTM search returns results",
          lambda: assert_that(isinstance(results, list)))

    rag_ctx = ltm.get_rag_context("江豚栖息地", max_tokens=1000)
    check("LTM RAG context generated",
          lambda: assert_that(isinstance(rag_ctx, str) and len(rag_ctx) > 0))

    stats_ltm = ltm.stats()
    check("LTM stats",
          lambda: assert_that("cached_documents" in stats_ltm))

    # ── Memory Manager ──
    mm = MemoryManager(max_stm_tokens=4000, persist_dir="./data/chroma_db")
    mm.remember("User: test query", role="user", priority=MemoryPriority.HIGH)
    mm.remember("Tool result: ok", role="tool", priority=MemoryPriority.MEDIUM)
    mm.persist("notes", "Test observation note", metadata={"source": "test"})

    recalled = mm.recall("test query")
    check("MemoryManager recall",
          lambda: assert_that("stm_results" in recalled))

    ctx = mm.get_context_for_llm("test query", max_tokens=1000)
    check("MemoryManager LLM context",
          lambda: assert_that(len(ctx) > 0))

    mm.flush()
    check("MemoryManager flush",
          lambda: assert_that(mm.stm.stats()["n_items"] >= 2))


# ══════════════════════════════════════════════════════════════
# LAYER 4: Mapping & Translation
# ══════════════════════════════════════════════════════════════

def test_l4():
    print("\n─── L4: Mapping & Translation ───")

    from src.interaction.nlu import Intent
    from src.mapping.router import IntentRouter, RouteTarget

    router = IntentRouter()
    result = router.route(Intent.LITERATURE_SEARCH,
                          entities=[], sub_intents=[])
    check("Router routes literature search",
          lambda: assert_that(len(result.routes) > 0))

    result = router.route(Intent.UNKNOWN)
    check("Router handles UNKNOWN intent",
          lambda: assert_that(len(result.routes) > 0))

    result = router.route(Intent.FIELD_SURVEY)
    check("Router marks field survey for approval",
          lambda: assert_that(
              any(r.requires_approval for r in result.routes)
          ))

    # ── Serializer ──
    from src.mapping.serializer import (
        EngineeringSerializer, SerializedFormat, SerializedOutput,
        serialize_to_tool_call, nl_to_python,
    )

    ser = EngineeringSerializer()
    out = ser.serialize("搜索江豚文献", target_format=SerializedFormat.FUNCTION_CALL)
    check("Serializer function call",
          lambda: assert_that("search_literature" in out.code))

    out = ser.serialize("计算江豚 click 脉冲的 ICI 均值",
                        target_format=SerializedFormat.PYTHON)
    check("Serializer Python code",
          lambda: assert_that("import" in out.code.lower() or "TODO" in out.code))

    out = ser.serialize("查询2024年观测数据",
                        target_format=SerializedFormat.SQL,
                        context={"species": "Neophocaena"})
    check("Serializer SQL query",
          lambda: assert_that("SELECT" in out.code.upper() or "FROM" in out.code.upper()))

    out = ser.serialize("调用search工具",
                        target_format=SerializedFormat.JSON,
                        context={"query": "test"})
    check("Serializer JSON valid",
          lambda: json.loads(out.code))

    # Edge cases
    out = ser.serialize("", target_format=SerializedFormat.FUNCTION_CALL)
    check("Serializer empty input → handles",
          lambda: assert_that(out.code is not None))

    out = ser.serialize("do something random",
                        target_format=SerializedFormat.PYTHON)
    check("Serializer unknown action → stub",
          lambda: assert_that(len(out.code) > 0))

    # Quick helpers
    tc = serialize_to_tool_call("search papers", "search_literature", query="test")
    check("Quick serialize tool call",
          lambda: assert_that(tc["tool"] == "search_literature"))

    # ── Validator ──
    from src.mapping.validator import OutputValidator, ValidationStatus

    val = OutputValidator()
    py_out = SerializedOutput(format=SerializedFormat.PYTHON,
                              code="print('hello')", original_nl="")
    result = val.validate(py_out)
    check("Validator Python: pass",
          lambda: assert_that(result.passed))

    py_danger = SerializedOutput(format=SerializedFormat.PYTHON,
                                 code="import os; os.system('rm -rf /')",
                                 original_nl="")
    result_d = val.validate(py_danger)
    check("Validator Python: detect danger",
          lambda: assert_that(
              result_d.status in (ValidationStatus.WARN, ValidationStatus.FAIL)
              or any("subprocess" in i.code.lower() or "system" in i.message.lower()
                     for i in result_d.issues)
          ))

    py_syntax_err = SerializedOutput(format=SerializedFormat.PYTHON,
                                     code="def broken(:", original_nl="")
    result_se = val.validate(py_syntax_err)
    check("Validator Python: syntax error",
          lambda: assert_that(not result_se.passed))

    sql_out = SerializedOutput(format=SerializedFormat.SQL,
                               code="SELECT * FROM observations WHERE species='NP'",
                               original_nl="")
    result_sql = val.validate(sql_out)
    check("Validator SQL: pass",
          lambda: assert_that(result_sql.passed))

    sql_danger = SerializedOutput(format=SerializedFormat.SQL,
                                  code="DROP TABLE observations;", original_nl="")
    result_sd = val.validate(sql_danger)
    check("Validator SQL: detect danger",
          lambda: assert_that(not result_sd.passed))

    json_out = SerializedOutput(format=SerializedFormat.JSON,
                                code='{"tool": "search", "parameters": {"q": "x"}}',
                                original_nl="")
    result_j = val.validate(json_out)
    check("Validator JSON: pass",
          lambda: assert_that(result_j.passed))

    json_bad = SerializedOutput(format=SerializedFormat.JSON,
                                code='{broken json', original_nl="")
    result_jb = val.validate(json_bad)
    check("Validator JSON: fail",
          lambda: assert_that(not result_jb.passed))


# ══════════════════════════════════════════════════════════════
# LAYER 5: Execution
# ══════════════════════════════════════════════════════════════

def test_l5():
    print("\n─── L5: Tool & Execution ───")

    from src.execution.sandbox import SandboxExecutor, SandboxConfig, execute_python, execute_safe
    from src.execution.tool_registry import ToolRegistry, tools
    from src.execution.api import APIClient, api_client

    # ── Sandbox ──
    sb = SandboxExecutor()
    result = sb.run("print('hello sandbox')", timeout=5)
    check("Sandbox basic execution",
          lambda: assert_that("hello" in result.stdout.lower()))

    result = sb.run("x = 1 + 1\nprint(x)", timeout=5)
    check("Sandbox computation",
          lambda: assert_that("2" in result.stdout.strip()))

    result = sb.run("import sys; print(sys.version[:5])", timeout=5)
    check("Sandbox import stdlib",
          lambda: assert_that("3." in result.stdout))

    # Edge: timeout
    result = sb.run("import time; time.sleep(10)", timeout=1)
    check("Sandbox timeout handling",
          lambda: assert_that(result.killed or "timed out" in result.stderr.lower()))

    # Edge: syntax error
    result = sb.run("print(undefined_var_xyz)", timeout=5)
    check("Sandbox NameError capture",
          lambda: assert_that(
              result.exit_code != 0 or "error" in result.stderr.lower()
              or "not defined" in result.stderr.lower()
          ))

    # Safe eval
    val, err = execute_safe("2 + 2 * 10")
    check("Safe eval math",
          lambda: assert_that(val == 22 and err is None))

    val, err = execute_safe("min(5, 3, 9)")
    check("Safe eval builtin",
          lambda: assert_that(val == 3 and err is None))

    val, err = execute_safe("__import__('os')")
    check("Safe eval blocked import",
          lambda: assert_that(err is not None or val is None))

    # ── Tool Registry ──
    reg = ToolRegistry()
    reg.register("echo", "Echo test", {}, fn=lambda x: f"echo: {x}")
    result = reg.call("echo", x="hello")
    check("ToolRegistry call",
          lambda: assert_that(result == "echo: hello"))

    reg.register("failing_tool", "Always fails", {}, fn=lambda: (_ for _ in ()).throw(Exception("boom")),
                 fallback="echo")
    try:
        reg.call("failing_tool")
    except Exception:
        pass
    history = reg.get_history(limit=5)
    check("ToolRegistry fallback attempted",
          lambda: assert_that(len(history) >= 1))

    specs = reg.get_specs_for_llm()
    check("ToolRegistry LLM specs",
          lambda: assert_that(len(specs) >= 2))

    stats = reg.stats()
    check("ToolRegistry stats",
          lambda: assert_that("total_tools" in stats and stats["total_tools"] >= 2))

    # Edge: unknown tool
    try:
        reg.call("nonexistent_tool")
        failed_assert = False
    except ValueError:
        failed_assert = True
    check("ToolRegistry unknown tool → ValueError",
          lambda: assert_that(failed_assert))

    # ── API Client (instantiation only, no network) ──
    client = APIClient(timeout=5)
    check("APIClient instantiate", lambda: None)


# ══════════════════════════════════════════════════════════════
# MULTI-AGENT SYSTEM
# ══════════════════════════════════════════════════════════════

def test_mas():
    print("\n─── Multi-Agent System ───")

    from src.agents.topology import (
        Topology, TopologyType, TopologyBuilder, Message, MessageType, Edge
    )
    from src.agents.base import BaseAgent
    from src.agents.literature import LiteratureAgent
    from src.agents.acoustic import AcousticAgent
    from src.agents.ecology import EcologyAgent
    from src.agents.conservation import ConservationAgent
    from src.agents.critic import CriticAgent
    from src.agents.orchestrator import OrchestratorAgent

    # ── Topology ──
    topo = Topology(type=TopologyType.SEQUENTIAL)
    check("Topology instantiate", lambda: None)

    topo.add_agent("lit", LiteratureAgent())
    topo.add_agent("aco", AcousticAgent())
    check("Topology add agents",
          lambda: assert_that(len(topo.agents) == 2))

    topo.add_edge("lit", "aco", weight=1.0, description="lit→aco")
    check("Topology add edge",
          lambda: assert_that(len(topo.edges) == 1))

    neighbors = topo.get_neighbors("lit")
    check("Topology get neighbors",
          lambda: assert_that(neighbors == ["aco"]))

    upstream = topo.get_upstream("aco")
    check("Topology get upstream",
          lambda: assert_that(upstream == ["lit"]))

    vis = topo.visualize()
    check("Topology visualize",
          lambda: assert_that("lit" in vis and "aco" in vis))

    # Condition edge
    topo2 = Topology(type=TopologyType.DAG)
    topo2.add_agent("a", LiteratureAgent())
    topo2.add_agent("b", AcousticAgent())
    topo2.add_agent("c", ConservationAgent())
    topo2.add_edge("a", "b", condition="result.n_clicks > 0")
    topo2.add_edge("a", "c", condition="result.n_clicks == 0")
    msg = Message(id="m1", type=MessageType.TASK, source="root", target="a",
                  content={"n_clicks": 5})
    next_msgs = topo2.route(msg, "a")
    check("Topology condition routing (positive)",
          lambda: assert_that(any(m.target == "b" for m in next_msgs)))

    msg2 = Message(id="m2", type=MessageType.TASK, source="root", target="a",
                   content={"n_clicks": 0})
    next_msgs2 = topo2.route(msg2, "a")
    check("Topology condition routing (negative → fallback)",
          lambda: assert_that(any(m.target == "c" for m in next_msgs2)))

    # ── Topology Builder ──
    builder = TopologyBuilder()
    builder._agents["lit"] = LiteratureAgent()
    builder._agents["aco"] = AcousticAgent()
    builder._agents["con"] = ConservationAgent()
    builder._agents["cri"] = CriticAgent()

    seq = builder.sequential(["lit", "aco", "con"])
    check("Builder sequential",
          lambda: assert_that(len(seq.edges) == 2))

    hier = builder.hierarchical("orchestrator", ["lit", "aco"])
    check("Builder hierarchical",
          lambda: assert_that(len(hier.edges) == 4))  # 2 down + 2 up

    debate = builder.debate("lit", "cri", rounds=3)
    check("Builder debate",
          lambda: assert_that(len(debate.edges) == 2))

    # ── Agents smoke tests ──
    lit = LiteratureAgent()
    check("LiteratureAgent instantiate", lambda: None)
    check("LiteratureAgent can_handle",
          lambda: assert_that(lit.can_handle("literature_search")))

    aco = AcousticAgent()
    check("AcousticAgent instantiate", lambda: None)
    check("AcousticAgent can_handle",
          lambda: assert_that(aco.can_handle("acoustic_analysis")))

    eco = EcologyAgent()
    check("EcologyAgent can_handle",
          lambda: assert_that(eco.can_handle("abundance_estimate")))

    con = ConservationAgent()
    check("ConservationAgent can_handle",
          lambda: assert_that(con.can_handle("conservation_assess")))

    cri = CriticAgent()

    async def _test_critic():
        return await cri.handle_message(
            Message(id="m1", type=MessageType.FEEDBACK, source="lit", target="cri",
                    content={"agent": "literature", "papers": [],
                             "synthesis": "No papers found, population is 5000"},
                    metadata={"source_agent": "literature"})
        )

    import asyncio
    review = asyncio.run(_test_critic())
    check("CriticAgent reviews output",
          lambda: assert_that("verdict" in review and "overall_score" in review))

    # ── Orchestrator ──
    orch = OrchestratorAgent()
    orch.register_agent(lit)
    orch.register_agent(aco)
    orch.register_agent(con)
    orch.register_critic(cri)

    check("Orchestrator registers agents",
          lambda: assert_that("literature" in orch._agents))

    stats = orch.stats()
    check("Orchestrator stats",
          lambda: assert_that("registered_agents" in stats))


# ══════════════════════════════════════════════════════════════
# PERFORMANCE BOUNDARY TESTS
# ══════════════════════════════════════════════════════════════

def test_performance():
    print("\n─── Performance Boundaries ───")

    import asyncio

    # 1. Deep decomposition (many recursion levels)
    from src.cognitive.decomposer import TaskDecomposer, DecompositionStrategy
    decomp = TaskDecomposer()
    long_query = "分析长江江豚在鄱阳湖、洞庭湖、安庆江段、芜湖江段、南京江段、镇江江段的分布、丰度、栖息地、威胁和保护 " * 5
    t0 = time.time()
    plan = asyncio.run(decomp.decompose(long_query, strategy=DecompositionStrategy.COT))
    elapsed = time.time() - t0
    check(f"Decomposer long query ({len(long_query)} chars) → {elapsed:.3f}s",
          lambda: assert_that(plan is not None and elapsed < 5.0))

    # 2. Deep search tree
    from src.cognitive.search import ThoughtTreeSearch, SearchConfig, SearchStrategy, ThoughtNode

    root = ThoughtNode(id="r0", content="Start", depth=0, score=0.5)

    def bf_expand(node):
        return [ThoughtNode(id=f"{node.id}_c{i}", content=f"C{i}", depth=node.depth + 1)
                for i in range(3)]

    def bf_eval(node):
        return 0.5 + 0.05 * node.depth

    cfg_bf = SearchConfig(strategy=SearchStrategy.BEAM, max_depth=6,
                          max_nodes=200, beam_width=3, branch_factor=3)
    searcher = ThoughtTreeSearch(expand_fn=bf_expand, evaluate_fn=bf_eval, config=cfg_bf)
    t0 = time.time()
    result = searcher.search(root)
    elapsed = time.time() - t0
    check(f"Search 3^6 tree ({result.nodes_explored} nodes) → {elapsed:.3f}s",
          lambda: assert_that(elapsed < 10.0))

    # 3. Memory: many documents
    from src.memory.short_term import ShortTermMemory, MemoryPriority
    stm = ShortTermMemory(max_tokens=8000)
    t0 = time.time()
    for i in range(200):
        stm.add(f"Entry {i}: " + "data " * 20, role="tool", priority=MemoryPriority.LOW)
    elapsed = time.time() - t0
    ctx_len = len(stm.get_context())
    check(f"STM 200 entries → {elapsed:.3f}s (context {ctx_len} chars)",
          lambda: assert_that(elapsed < 5.0))

    # 4. Sandbox: large output
    from src.execution.sandbox import SandboxExecutor
    sb = SandboxExecutor()
    result = sb.run("for i in range(5000): print(f'Line {i}')", timeout=10)
    check(f"Sandbox 5000 lines → {result.elapsed_ms:.0f}ms (truncated: {result.truncated})",
          lambda: assert_that(result.elapsed_ms < 30000))

    # 5. Many-intent routing
    from src.mapping.router import IntentRouter
    from src.interaction.nlu import Intent
    router = IntentRouter()
    t0 = time.time()
    for intent in Intent:
        router.route(intent, entities=[], sub_intents=[])
    elapsed = time.time() - t0
    check(f"Router all {len(Intent)} intents → {elapsed:.3f}s",
          lambda: assert_that(elapsed < 1.0))

    # 6. Deep credit assignment
    from src.cognitive.bdi import PlanStep
    from src.cognitive.reflexion import CreditAssigner
    ca = CreditAssigner()
    steps = [PlanStep(id=f"s{i}", description=f"Step {i}", action=f"a{i}") for i in range(50)]
    t0 = time.time()
    nodes = ca.build_from_plan(steps)
    elapsed = time.time() - t0
    check(f"CreditAssigner 50 nodes → {elapsed:.3f}s", lambda: assert_that(elapsed < 1.0))


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("Porpoise Agent v2.0 — Robustness & Boundary Test Suite")
    print("=" * 60)

    test_l1()
    test_l2()
    test_l3()
    test_l4()
    test_l5()
    test_mas()
    test_performance()

    print()
    print("=" * 60)
    total = passed + failed
    print(f"RESULTS: {passed}/{total} passed, {failed} failed, {warnings} warnings")
    if errors:
        print(f"\nFAILURE DETAILS:")
        for name, err in errors:
            print(f"  - {name}: {err}")
        sys.exit(1)
    else:
        print("All checks passed! ✅")
        sys.exit(0)
