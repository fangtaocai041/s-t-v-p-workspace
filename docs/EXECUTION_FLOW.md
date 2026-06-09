# ☯️ 道生一·一生二·二生三·三生万物

> **核心架构 v7.4 — 最终版**
> **核心: 道→一→二→三。万物从三演化。**
> **一**: IProjectAdapter 统一接口
> **二**: YinYang 阴阳两面 (expand + verify)
> **三**: fish + cognitive + eon-core 三角闭环
> **万物**: 四象·八卦·五行·六道·Pₙ — 全部从三派生
> **同步**: 2026-06-09

---

## 0. 总览: 一条指令的完整旅程

```
道 (操作者: Reasonix / User)
 │  给出指令: "搜索鳤的文献并评估保护状态"
 │
 ▼
一 (指令工程化)
 │  parse_query("鳤 保护评估") → StructuredIntent
 │
 ▼
二 (太极·阴阳两面)
 │  YangPole.expand("鳤")      → 搜索候选集
 │  YinPole.verify(candidates)  → 验证过滤
 │
 ▼
三角体 (eon-core OriginKernel 协调)
 │  route_event(intent) → VertexChain [V0→V1→V2]
 │  拓扑验证: DAG ✓  λ₂ ≥ 0.15 ✓
 │
 ▼
四象 (4个顶点分发)
 │  V0(fish):       lookup_species("鳤") → SpeciesProfile
 │  V1(cognitive):  search_species("Ochetobius","elongatus") → SearchResult
 │  V2(porpoise):   analyze_contradiction("保护状态") → Route
 │  V3(coilia):     (闲置 — 非刀鲚查询)
 │
 ▼
八卦 (每个顶点2个子模块执行)
 │  ☰乾: parallel_search(11 engines)
 │  ☱兑: query_chinese_sources(CNKI/万方/CSCD)
 │  ☲离: traverse_citation_graph(3层)
 │  ☳震: multi_model_debate(3 LLM × 3 sources)
 │  ☴巽: (闲置 — 非声学查询)
 │  ☵坎: (闲置 — 非种群查询)
 │
 ▼
五行 (流转监控 — 后台协程)
 │  🪵木: observe(graph_growth)      → 0.02 (正常)
 │  🔥火: observe(event_throughput)  → 45/s (正常)
 │  🪨土: observe(supply_freshness)  → 0.95 (新鲜)
 │  ⚔️金: observe(false_positive)    → 0.03 (正常)
 │  💧水: observe(adaptation_speed)  → 0.8 (正常)
 │
 ▼
六道 (业力评估)
 │  KarmaCourt.evaluate(V0): +5 karma → HUMAN (稳定)
 │  KarmaCourt.evaluate(V1): +8 karma → DEVA (优秀, token×1.5)
 │  KarmaCourt.evaluate(V2): +2 karma → HUMAN
 │  无 NARAKA — 全部健康
 │
 ▼
输出 (SphereGateway 融合返回)
 │  FusionEnvelope { result, confidence:0.92, trace_id, coverage }
 │  → REST/JSON 返回给用户
 │
 ▼
道 (操作者收到答案)
   输出: "鳤(Ochetobius elongatus): 15篇文献, CR保护等级,
          主要矛盾: 数据稀缺 vs 水利工程影响, 建议: 加强监测"
```

---

## 1. 道 → 一: 指令工程化

```
道 (Tao) = Reasonix Code / 用户
  职责: 提出问题，接收答案，做出最终判断
  不变量: 人不做机器的判断，机器不做人的决策

一 (One) = 结构化意图 (StructuredIntent)
  工程语言:
    parse_query(raw: str) → StructuredIntent {
      species: str,           // "鳤"
      action: Enum,           // SEARCH | ASSESS | COMPARE | MONITOR
      domain: Optional[str],  // "保护"
      depth: Enum,            // QUICK | STANDARD | EXHAUSTIVE
      sources: List[str],     // ["pubmed","cnki","crossref"]
    }

  运行规则:
    WHEN user_input contains species_name
    THEN extract species + action
    IF action is NULL THEN default = SEARCH
    IF depth is NULL THEN depth = estimate_depth(species)
    RETURN StructuredIntent

  实际代码: 未独立模块 — 当前由各项目 orchestrator 自行解析
  待实现: scripts/intent_parser.py
```

---

## 2. 一 → 二: 太极·阴阳两面

```
二 (Two) = YinYang 双极处理
  哲学: 太极生两仪 — 阳(扩张·供给) + 阴(收敛·验证)
  工程: 每个查询经过阴阳两面处理

  阳面 (YangPole):
    input:  StructuredIntent
    action: expand(intent.species) → CandidateSet
    规则:
      WHEN intent.action == SEARCH
      THEN parallel_search(species, engines=ALL, depth=3)
      RETURN CandidateSet { papers, variants, queries }

  阴面 (YinPole):
    input:  CandidateSet
    action: verify(candidates) → VerifiedSet
    规则:
      WHEN candidates.count > 0
      THEN FOR EACH paper: score_credibility(paper)
           filter(credibility >= 40)
           mark(verified | pending | hypothesis | unverifiable)
      RETURN VerifiedSet

  阴阳交互协议:
    YangPole.expand() ──→ EventBus ──→ YinPole.verify()
    YinPole 不搜索，YangPole 不验证 (编译期类型约束)

  实际代码:
    YangPole: eon-core/src/poles/yang_pole.py (expand/supply/generate_hypotheses)
    YinPole: eon-core/src/poles/yin_pole.py (contract/verify/detect_contradiction)
    当前状态: 类定义存在，但未与 pathway executor 集成
```

---

## 3. 二 → 三角体: eon-core 协调

```
三角体 (Tetrahedron) = OriginKernel 协调层
  输入: VerifiedSet (从 YinPole 输出)
  动作: route_event(event) → VertexChain

  工程语言:
    intent = classify(event)  // {species: "鳤", action: SEARCH, domain: "保护"}
    chain = tetrahedron.compute_route(intent)
    // chain = [V0(fish), V1(cognitive), V2(porpoise)]
    // V3(coilia) 不在链中 — 仅当 species ∈ {Coilia} 时激活

    FOR EACH vertex IN chain:
      event_bus.publish(event, f"vertex.{vertex.id}.execute")
      result = await event_bus.consume(f"vertex.{vertex.id}.completed")

    RETURN merge(results)

  路由规则:
    IF species in ["鳤","鯮","鳡","翘嘴鲌"]      → [V0, V1]            (三角内)
    IF species in ["Neophocaena","江豚"]           → [V0, V1, V2]        (三角+派生)
    IF species in ["Coilia","刀鲚"]                → [V0, V1, V3]        (三角+派生)
    IF species in ["Acipenser","中华鲟"]            → [V0, V1, V3(模板)]  (三角+万物)

  拓扑不变量:
    chain MUST BE DAG → nx.is_directed_acyclic_graph()
    λ₂ ≥ 0.1 × baseline → spectral_gap check
    NO vertex in NARAKA → skip isolated vertices

  实际代码:
    OriginKernel: eon-core/src/kernel/origin.py (route_event, bootstrap, reconfigure)
    TetrahedronMesh: eon-core/src/mesh/tetrahedron.py (compute_route, spectral_gap)
    EventBus: eon-core/src/kernel/event_bus.py
```

---

## 4. 三角体 → 四象: 4个顶点分发

```
四象 (Four Symbols) = 4个顶点服务
  每个顶点独立处理分配给自己的子任务

  V0 ☀️ 太阳 (fish-ecology-assistant):
    职责: 知识供给 — 查询物种数据库 + 生成搜索关键词
    输入: event {species: "鳤"}
    动作:
      profile = lookup_species("鳤")     → SpeciesProfile
      queries = generate_variants(profile) → OCR变体 + 中英文关键词
      sources = select_sources(profile)    → [pubmed, cnki, crossref, ...]
    输出: KnowledgeSupply { profile, queries, sources }

  V1 🌙 太阴 (cognitive-search-engine):
    职责: 验证引擎 — 多源搜索 + 图谱遍历 + 权威评分
    输入: KnowledgeSupply (from V0)
    动作:
      papers = search_species(genus, species)     → SearchResult
      graph = traverse_citation_graph(papers, 3)  → Subgraph
      scored = credibility_score(papers)           → [0-100 per paper]
    输出: VerifiedResult { papers, graph, credibility }

  V2 🌤️ 少阴 (porpoise-agent):
    职责: 江豚专研 — 矛盾分析 + 声学评估
    激活条件: species ∈ {Neophocaena, 江豚}
    动作:
      contradiction = analyze_contradiction(query)  → Route
      emergence = detect_emergence(scored_papers)   → EmergenceSignal[]
    输出: DomainAnalysis { contradiction, emergence }

  V3 🌦️ 少阳 (coilia-agent):
    职责: 刀鲚专研 — 耳石微化学 + 资源评估
    激活条件: species ∈ {Coilia, 刀鲚}
    动作:
      assessment = assess_species(species, context) → Assessment
    输出: SpeciesAssessment

  运行规则:
    WHEN vertex.health < 0.5 THEN skip vertex (tetrahedron 重组)
    WHEN vertex.realm == NARAKA THEN isolate (token×0)
    WHEN vertex.realm == DEVA THEN boost (token×1.5)
```

---

## 5. 四象 → 八卦: 8个子模块

```
八卦 (Eight Trigrams) = 每个顶点内的2个功能子模块
  每个卦执行一个具体的原子功能

  V0 的八卦:
    ☰ 乾 (Qian): MetaSearchEngine
      接口: parallel_search(query, engines[]) → MergedResults
      规则: 11引擎并行 → 去重 → 排序 → 满意度判定 → 停止或继续
      状态: ✅ 已实现 (cognitive-search-engine/src/parallel_search.py)

    ☱ 兑 (Dui): ChineseSourceGateway
      接口: query_chinese_sources(query) → ChineseLiteratureSet
      规则: CNKI/CSCD/万方 三源并行 → 中文期刊加权+25
      状态: ⚠️ 接口定义存在, 通过 web_search 间接实现

  V1 的八卦:
    ☲ 离 (Li): GraphTraversalEngine
      接口: traverse(node, depth, strategy) → Subgraph
      规则: Hub-and-Spoke → 3阶段 → OCR变体扫描 → 缺口检测
      状态: ✅ 已实现 (cognitive-search-engine/src/rule_engine.py)

    ☳ 震 (Zhen): MultiModelDebate
      接口: debate(claims, models[], sources[]) → Verdict
      规则: 3 LLM × 3 sources → Socratic debate → consensus score
      状态: ⚠️ 接口定义存在, 未完全实现

  V2 的八卦:
    ☴ 巽 (Xun): AcousticPipeline
      接口: analyze_clicks(audio) → ClickFeatures
      规则: Butterworth 100-180kHz → SPL threshold -134dB → RF classify
      状态: ⚠️ 接口定义存在, 核心函数为 stub (tools.py: detect_clicks)

    ☵ 坎 (Kan): PopulationModeler
      接口: estimate_population(data) → Report
      规则: cue_counting | distance_sampling | SECR
      状态: ⚠️ 接口定义存在, 核心函数为 stub (tools.py: estimate_abundance)

  V3 的八卦:
    ☶ 艮 (Gen): OtolithAnalyzer
      接口: analyze_otolith(data) → MigrationPath
      规则: Sr/Ca > 3.0 → marine; Sr/Ca < 1.0 → freshwater
      状态: ⚠️ 规则编码在 orchestrator.py, 接口未独立

    ☷ 坤 (Kun): ResourceAssessor
      接口: assess_resources(sp, region, t) → Report
      规则: CPUE标准化 → 剩余产量模型 → MSY估算
      状态: ⚠️ 规则编码在 orchestrator.py, 接口未独立

  运行规则 (FOR EACH trigram):
    WHEN trigram.enabled AND vertex.active THEN
      result = trigram.execute(input)
      IF result.confidence < 0.5 THEN flag_for_review(result)
      emit metric {trigram_id, latency, confidence}
```

---

## 6. 八卦 → 五行: 流转监控

```
五行 (WuXing) = 5个监控代理 — 后台协程, 非阻塞

  🪵 木 (Wood) → 附着 V1(cognitive):
    监控: graph_node_growth_rate, new_species_per_month, variant_coverage
    相生: 木生火 → growth_data → huo_fire
    相克: 木克土 → IF growth > threshold THEN advisory(tu_earth, "slow_down_supply")

  🔥 火 (Fire) → 附着 Origin(太极体心):
    监控: event_throughput, routing_latency_p99, phase_transition_rate
    相生: 火生土 → drive_data → tu_earth
    相克: 火克金 → IF latency > threshold THEN advisory(jin_metal, "inject_energy")

  🪨 土 (Earth) → 附着 V0(fish):
    监控: supply_freshness, knowledge_duplication_rate, source_diversity
    相生: 土生金 → quality_data → jin_metal
    相克: 土克水 → IF duplication > threshold THEN advisory(shui_water, "reduce_exploration")

  ⚔️ 金 (Metal) → 附着 V2(porpoise):
    监控: conclusion_stability, false_positive_rate, domain_boundary_adherence
    相生: 金生水 → convergence_data → shui_water
    相克: 金克木 → IF false_positive > threshold THEN advisory(mu_wood, "prune_graph")

  💧 水 (Water) → 附着 V3(coilia):
    监控: adaptation_speed, external_event_response_time, migration_pattern_detection
    相生: 水生木 → adaptation_data → mu_wood
    相克: 水克火 → IF adaptation < threshold THEN advisory(huo_fire, "cool_down")

  逃生机制:
    AdvisorySignal 被连续拒绝 3 次 AND 指标未改善
    → 第 4 次升级为 MandatorySignal
    → 目标节点 MUST 执行

  实际代码:
    flow_engine: eon-core/src/wuxing/flow_engine.py
    5 agents:   eon-core/src/wuxing/{mu,huo,tu,jin,shui}*.py
    override:   eon-core/src/wuxing/override.py
```

---

## 7. 五行 → 六道: 业力评估

```
六道 (Samsara) = KarmaEngine 业力评估 — 每 60s 一轮

  KarmaCourt.evaluate():
    FOR EACH vertex IN [V0, V1, V2, V3]:
      karma = compute_karma(vertex, health, metrics)
      realm = decide_realm(karma)
      apply_realm(vertex, realm)

  六道状态:
    ☸️ DEVA   (karma ≥ 85): token×1.5, 深搜索, 最长10周期
    🧘 HUMAN  (karma 40-85): token×1.0, 标准搜索, 可主动 self_evolve()
    ⚔️ ASURA  (karma 60-90, 矛盾率>0.15): token×1.2, 需去矛盾验证
    🐂 ANIMAL (karma 20-40): token×0.5, 禁用LLM, 仅缓存+规则
    👻 PRETA  (karma 10-20): token×0.25, 严酷限流
    🔥 NARAKA (karma < 10): token×0, 完全隔离, 冷却后自动重生

  业力计算:
    karma = base_karma
          + health_score × 20
          + successful_queries × 2
          + verified_results × 3
          - failed_queries × 5
          - timeout_events × 10
          - contradiction_unresolved × 8

  不变量:
    DEVA ≤ 10 周期 → 公平性自动轮换
    NARAKA → 冷却30s → 自动重生到 HUMAN (karma=50)
    每次转生原子化 → 7步协议 + 快照回滚

  实际代码:
    KarmaEngine:   eon-core/src/samsara/karma_engine.py
    KarmaCourt:    eon-core/src/samsara/court.py
    SamsaraRing:   eon-core/src/samsara/ring.py
    Reincarnation: eon-core/src/samsara/reincarnation.py
```

---

## 8. 六道 → 输出: 融合返回

```
输出 (Output) = SphereGateway 融合 + 返回

  SphereGateway.respond():
    INPUT  results from all executed vertices
    ACTION:
      envelope = FusionEnvelope {
        result:     merge(all_vertex_results),
        confidence: weighted_average(scores),
        trace_id:   event.trace_id,
        coverage:   SearchCoverageReport(papers),
        topology:   tetrahedron.snapshot(),
        wuxing:     wuxing_flow.snapshot(),
        karma:      samsara_ring.snapshot(),
      }
      response = protocol_adapter.to_rest(envelope)
    RETURN response → 道 (操作者)

  输出格式:
    {
      "result": { "species": "鳤", "papers": 15, "status": "CR" },
      "confidence": 0.92,
      "trace": "道→一→二→三角→V0→V1→V2→输出 (287ms)",
      "topology": { "active_vertices": 3, "edges": 6, "λ₂": 0.18 },
      "karma": { "V0": "HUMAN", "V1": "DEVA", "V2": "HUMAN", "V3": "HUMAN" }
    }

  实际代码:
    SphereGateway:  eon-core/src/sphere/gateway.py
    当前状态: 类定义存在, 需集成到 pathway executor 输出
```

---

## 9. 每条指令的完整生命周期

```
道 (用户/Reasonix)
 │  输入: "鳤 保护评估"
 │  输出: { result, confidence, trace, karma }
 │
 ├─ 一 (parse_query)           → StructuredIntent          ~1ms
 ├─ 二 (YangPole + YinPole)    → CandidateSet + Verified   ~50ms
 ├─ 三角体 (OriginKernel)       → VertexChain [V0,V1,V2]    ~1ms
 ├─ 四象 (V0+V1+V2)            → 3× VertexResult           ~200ms
 │   ├─ V0: lookup + variants  ~20ms
 │   ├─ V1: search + traverse  ~150ms
 │   └─ V2: contradiction      ~30ms
 ├─ 八卦 (乾+兑+离+震)          → 4× TrigramResult         ~100ms
 ├─ 五行 (后台, 不阻塞)         → metrics emitted           ~1ms
 ├─ 六道 (后台, 不阻塞)         → karma updated             ~1ms
 └─ 输出 (SphereGateway)        → FusionEnvelope            ~5ms
                                                           ─────
                                                            ~360ms
```

---

> **道的完整循环**:
> 操作者给出指令 → 工程语言化为意图 → 阴阳两面处理 → 三角体协调路由
> → 四象顶点分发执行 → 八卦子模块精细化 → 五行后台监控流转
> → 六道业力评估 → 融合输出返回操作者
> 每一层有明确的输入/输出契约。每一步可独立验证。

**验证**: `verify_standalone 5/5 · verify_pathways 16/16 · verify_philosophy_rules 18/18`
