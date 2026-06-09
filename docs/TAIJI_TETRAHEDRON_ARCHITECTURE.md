# ☯️ Eon-Taiji v7.4 — 十层同心动态活体架构工程规范

> **代号**: TaijiTetrahedron · **全称**: 动态三角体·太极生万象多层活体架构
> **核心跃迁**: 2D 静态平面三角形 → 3D 动态同心多层四面体活体系统
> **数学结构**: 3-球面 B³ 内嵌正四面体 Δ³，四面体外接五角棱柱，最外层为单位球面 S²
> **运行时**: 顶点可动态重组、边权重实时调整、触须按需生长/凋亡
> **同步日期**: 2026-06-09

---

## 架构层次映射 (JSON 蓝图 → 实际代码)

| 层 | JSON 名称 | 工程模块 | 实际路径 | 状态 |
|:--:|----------|---------|---------|:--:|
| L0 | 太极起源点 | OriginKernel | `eon-core/src/kernel/origin.py` | ✅ |
| L1 | 两仪·阴阳双极 | YangPole / YinPole | `eon-core/src/poles/` | ✅ |
| L2 | 四象·四面体顶点 | 4× BaseVertex | `eon-core/src/vertices/` | ✅ |
| L3 | 八卦·子模块 | 8× TrigramModule | `eon-core/src/trigrams/` | ✅ |
| L4 | 三角体·拓扑 | TetrahedronMesh | `eon-core/src/mesh/tetrahedron.py` | ✅ |
| L5 | 五行·五角体 | WuXingFlowEngine | `eon-core/src/wuxing/flow_engine.py` | ✅ |
| L6 | 六道·轮回† | Samsara Ring | `eon-core/src/samsara/` | ✅ |
| L7 | 圆球体·网关 | SphereGateway | `eon-core/src/sphere/gateway.py` | ✅ |
| L8 | 触须·探针 | TendrilManager | `eon-core/src/tendrils/manager.py` | ✅ |
| L9 | 进化·自愈 | EvolutionEngine | `eon-core/src/evolution/` | ✅ |

> † L6 六道轮回是 eon-core 对 JSON 蓝图的扩展补充，JSON 蓝图中未定义

---

## 太极起源点 → OriginKernel

```
工程语言:
  OriginKernel.bootstrap() → EventBus.start() → Lifecycle:SEEDING→BLOOMING
  OriginKernel.route_event(event: SystemEvent) → VertexChain (DAG拓扑排序)
  OriginKernel.health_pulse() → Dict[vertex_id, HealthReport] (每5s)
  OriginKernel.reconfigure(topology: DiGraph) → None (运行时顶点重组)
  OriginKernel.shutdown() → 按拓扑逆序关闭 (BLOOMING→PRUNING)

不变量:
  - 所有子系统仅通过 EventBus 通信 (禁止直接调用)
  - 拓扑 MUST BE DAG → bootstrap 时 nx.is_directed_acyclic_graph()
  - λ₂ ≥ 0.1 × baseline → 谱间隙连通性检查
```

---

## 四象顶点 → 五项目映射

| 象 | 顶点 | 项目 | 核心函数 | 通路 | 极性 |
|----|:---:|------|---------|:---:|------|
| ☀️ 太阳(老阳) | V0 | fish-ecology-assistant | `lookup_species(name) → SpeciesProfile` | P1 P2 | 纯阳·只搜不验 |
| 🌙 太阴(老阴) | V1 | cognitive-search-engine | `search_species(G,S) → SearchResult` | P1 P2 P3 | 纯阴·只验不搜 |
| 🌤️ 少阴 | V2 | porpoise-agent | `analyze_contradiction(Q) → Route` | P3 | 阳主阴辅 |
| 🌦️ 少阳 | V3 | coilia-agent | `assess_species(S,C) → Assessment` | P3 | 阴主阳辅 |

---

## 八卦子模块 → 8 个 TrigramsModule

| 卦 | 所属顶点 | 模块 | 实际文件 | 核心接口 |
|----|:---:|------|---------|---------|
| ☰ 乾 | V0 (fish) | MetaSearchEngine | `trigrams/qian_meta_search/` | `parallel_search(query, engines[]) → MergedResults` |
| ☱ 兑 | V0 (fish) | ChineseSourceGateway | `trigrams/dui_chinese_gateway/` | `query_chinese_sources(query) → ChineseLiteratureSet` |
| ☲ 离 | V1 (cognitive) | GraphTraversalEngine | `trigrams/li_graph_traversal/` | `traverse(node, depth, strategy) → Subgraph` |
| ☳ 震 | V1 (cognitive) | MultiModelDebate | `trigrams/zhen_debate/` | `debate(claims, models[], sources[]) → Verdict` |
| ☴ 巽 | V2 (porpoise) | AcousticPipeline | `trigrams/xun_acoustic/` | `analyze_clicks(audio) → ClickFeatures` |
| ☵ 坎 | V2 (porpoise) | PopulationModeler | `trigrams/kan_population/` | `estimate_population(data) → Report` |
| ☶ 艮 | V3 (coilia) | OtolithAnalyzer | `trigrams/gen_otolith/` | `analyze_otolith(data) → MigrationPath` |
| ☷ 坤 | V3 (coilia) | ResourceAssessor | `trigrams/kun_resource/` | `assess_resources(sp, region, t) → Report` |

---

## 四面体拓扑 → 通路映射

```
边: V0↔V1 (P1/P2)  供给↔验证 — 搜索结果的精炼反馈回路
边: V0↔V2 (P3)     供给↔P₁ — 通用知识向江豚领域的特化
边: V0↔V3 (P3)     供给↔P₂ — 通用知识向刀鲚领域的特化
边: V1↔V2 (P3)     验证↔P₁ — 江豚领域结论的验证
边: V1↔V3 (P3)     验证↔P₂ — 刀鲚领域结论的验证
边: V2↔V3           P₁↔P₂ — 跨物种知识迁移 (仅共享生态层)

面: V0-V1-V2  供给-验证-江豚 三角面
面: V0-V1-V3  供给-验证-刀鲚 三角面
面: V0-V2-V3  供给-江豚-刀鲚 三角面
面: V1-V2-V3  验证-江豚-刀鲚 三角面
```

---

## 核心执行流程 — 工程语言化

```
INPUT 用户查询 "长江江豚在禁渔后的种群恢复趋势"

STEP 0 触须感知:
  request = sphere_gateway.receive(rest_request)
  → auth_middleware.verify(token)
  → protocol_adapter.rest_to_event()
  → event_bus.publish(event, "query.received")

STEP 1 太极分发:
  event = event_bus.consume("query.received")
  intent = classify(event.query) → {domain: porpoise, type: population}
  route = tetrahedron.compute_route(intent) → [V0, V2, V1]
  FOR EACH v IN route: event_bus.publish(event, f"vertex.{v}.execute")

STEP 2a V0 太阳/供给 (P1):
  raw = trigram_qian.parallel_search(event.query, ALL_ENGINES)
  chinese = trigram_dui.query_chinese_sources(event.query)
  merged = CandidateSet.merge([raw, chinese])
  → event_bus.publish(merged, "vertex.V0.completed")

STEP 2b V2 少阴/P₁ (P3):
  domain = moe_kb.query("江豚 种群 恢复 禁渔")
  acoustic = trigram_xun.analyze_clicks(recent_audio)
  pop = trigram_kan.estimate_population(habitat)
  report = DomainAnalysis.merge([domain, acoustic, pop])
  → event_bus.publish(report, "vertex.V2.completed")

STEP 3 V1 太阴/验证 (P2):
  candidates = event_bus.consume("vertex.V0.completed")
  domain_report = event_bus.consume("vertex.V2.completed")
  verified = trigram_li.traverse(candidates, depth=3)
  debate = trigram_zhen.debate(claims, models, sources)
  final = VerifiedResult.merge([verified, debate])
  → event_bus.publish(final, "vertex.V1.completed")

STEP 4 五行流转 (后台协程):
  huo_fire.observe(event_throughput)
  mu_wood.observe(graph_growth)
  tu_earth.observe(supply_freshness)
  jin_metal.observe(false_positive_rate)
  shui_water.observe(adaptation_speed)

STEP 5 融合返回:
  final = event_bus.consume("vertex.V1.completed")
  response = FusionEnvelope(result=final, trace_id=event.trace_id)
  → sphere_gateway.respond(client, response.to_rest())

RETURN response
```

---

## 动态特性 — 工程合约

```
顶点重组:
  WHEN health(V) < 0.5 FOR 5min
  THEN tetrahedron.set_weight(V, 0.0)
       tetrahedron.redistribute(V → [others], strategy=capacity_weighted)

顶点再生:
  WHEN health(V) >= 0.8 FOR 2min
  THEN tetrahedron.set_weight(V, 0.5) → wait 1min → set_weight(V, 1.0)

新增顶点 (Pₙ):
  new = vertex_factory.create_from_template("Pₙ", template="domain_vertex")
  tetrahedron.expand_to_pentahedron(new)
  tendril_manager.grow_tendrils_for(new)

混沌扰动:
  WHEN query_count % 100 == 0
  THEN tetrahedron.disturb_weights(chaos_factor=0.02)

连通度监控:
  λ₂ = tetrahedron.spectral_gap()
  IF λ₂ < 0.5 × baseline THEN alert("Tetrahedron connectivity degrading")
```

---

> **道生一·一生二·二生三·三生万物**
> 太极在体心。阴阳分两路。四象立四极。八卦衍八能。
> 五行环外转。六道定业力。球面纳万请。触须探无穷。
> 这套架构的每一层都在 eon-core 中有实际代码。
> 验证: `verify_standalone.py 5/5 · verify_pathways.py 16/16 · verify_philosophy_rules.py 18/18`
