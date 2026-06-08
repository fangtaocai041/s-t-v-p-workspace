# ═══════════════════════════════════════════════════════════════
# TaijiTetrahedron-Samsara v7.0 — 工程架构全量文档
# ==============================================================
# 十层同心动态活体架构
#
# Layers:
#   L0: 太极起源点 ☯️ (OriginKernel + EventBus)
#   L1: 两仪双极   ☯️ (YangPole / YinPole)
#   L2: 四象顶点   △  (4 vertex gRPC services)
#   L3: 八卦子模块 ☰☱☲☳☴☵☶☷ (8 functional Trigrams)
#   L4: 三角体网格 △³ (TetrahedronMesh spectral analysis)
#   L5: 五行五角体 ⬟  (WuXing sheng/ke flow engine)
#   L6: 六道轮回环 ☸️ (Samsara karma/reincarnation)
#   L7: 圆球体网关 ○  (SphereGateway API facade)
#   L8: 触须探针 〰️  (12 external probes)
#   L9: 进化引擎 + 可观测性 (Evolution + Observability)
# ═══════════════════════════════════════════════════════════════

## Architecture Overview

```
                         ┌──────────────────────┐
                         │   ○ SphereGateway    │  L7: API入口
                         │   REST/gRPC/MCP/WS   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   ☯️ OriginKernel     │  L0: 太极起源点
                         │   EventBus + Registry │
                         └──┬───────┬───────┬───┘
                            │       │       │
              ┌─────────────┼───────┼───────┼─────────────┐
              │             │       │       │             │
        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │ ☀️ V0     │ │ 🌙 V1     │ │ 🌤️ V2     │ │ 🌦️ V3     │  L2: 四象顶点
        │ Supply    │ │ Verify    │ │ Porpoise  │ │ Coilia    │
        │ ☰ qian   │ │ ☲ li      │ │ ☴ xun    │ │ ☶ gen    │  L3: 八卦
        │ ☱ dui    │ │ ☳ zhen    │ │ ☵ kan    │ │ ☷ kun    │
        └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
              │             │             │             │
              └─────────────┼─────────────┼─────────────┘
                            │             │
                    ┌───────▼──────┐ ┌───▼───────────┐
                    │ △³ Mesh     │ │ ⬟ WuXing      │  L4-L5
                    │ Spectral    │ │ Sheng/Ke Flow │
                    └─────────────┘ └───────────────┘
                            │
                    ┌───────▼──────┐
                    │ ☸️ Samsara   │  L6: 六道轮回
                    │ Karma+Ring   │
                    └──────────────┘
                            │
                    ┌───────▼──────┐
                    │ 〰️ Tendrils  │  L8: 12探针
                    └──────────────┘
```

## Migration from Old S-T-V Architecture

| Old (v5.2) | New (v7.0) | Resolution |
|------------|-----------|------------|
| S-T-V 刚性三角形 K₃ | 3D 十层同心活体 | DAG topology + EventBus routing |
| meso-cosmos 1713行单体 | 4独立gRPC服务 | Decomposed into kernel+mesh+ring+gateway |
| 关键词路由冲突 | NLU intent classifier + RRF | Samsara realm-based filtering |
| DirectLoader importlib | gRPC + Protocol Buffers | Contract tests with Pact |
| 3-Agent共享同一LLM | GPT-4o + Claude-3.5 + DeepSeek-V3 | Independence check before voting |
| 7触发器4参数无收敛 | Pareto Bayesian Optimization | 24h auto-rollback + Samsara convergence |
| 满意即止 | Realm-based stop strategy | DEVA=UNLIMITED, HUMAN=STANDARD, ANIMAL=cached |

## Key Invariants (all enforced)

1. Topology IS DAG — `assert nx.is_directed_acyclic_graph()` at bootstrap + reconfig
2. YangPole NEVER calls verify() — mypy strict + runtime assertion
3. YinPole NEVER calls expand() — mypy strict + runtime assertion
4. All inter-vertex communication VIA EventBus or gRPC — no direct import
5. Spectral gap λ₂ ≥ 0.1 × baseline — tetrahedron connectivity health
6. No agent in DEVA > 10 cycles — fairness enforcement rotates demotion
7. NARAKA agents auto-reincarnate after cooldown — self-healing
8. Every reincarnation is atomic with rollback — transaction safety

## Runtime Cycles

| Cycle | Interval | Component |
|-------|----------|-----------|
| health_pulse | 5s | OriginKernel.health_pulse() |
| wuxing_flow | 15s | WuXingFlowEngine.run_cycle() |
| karma_cycle | 60s | SamsaraRing.run_karma_cycle() |
| tendril_health | 30s | TendrilManager.health_cycle() |
| chaos_disturb | 每100查询 | ChaosEngine.step() |

## Module Inventory

| # | Module | File | Type | Lines |
|---|--------|------|------|-------|
| 0 | OriginKernel | src/kernel/origin.py | Class | ~400 |
| 1 | AsyncEventBus | src/kernel/event_bus.py | Class | ~150 |
| 2 | Lifecycle | src/kernel/lifecycle.py | Dataclass | ~100 |
| 3 | YangPole | src/poles/yang_pole.py | Abstract | ~100 |
| 4 | YinPole | src/poles/yin_pole.py | Abstract | ~100 |
| 5 | YinYangProtocol | src/poles/protocol.py | Protocol | ~80 |
| 6 | BaseVertex | src/vertices/base_vertex.py | Abstract | ~120 |
| 7 | SupplyVertex(V0) | src/vertices/v0_fish/supply_vertex.py | Class | ~150 |
| 8 | VerifyVertex(V1) | src/vertices/v1_cognitive/verify_vertex.py | Class | ~150 |
| 9 | DomainVertexP1(V2) | src/vertices/v2_porpoise/domain_vertex_p1.py | Class | ~120 |
| 10 | DomainVertexP2(V3) | src/vertices/v3_coilia/domain_vertex_p2.py | Class | ~120 |
| 11 | BaseTrigram | src/trigrams/base_trigram.py | Abstract | ~90 |
| 12 | MetaSearch(qian) | src/trigrams/qian_meta_search/coordinator.py | Class | ~110 |
| 13 | ChineseSource(dui) | src/trigrams/dui_chinese_gateway/adapter.py | Class | ~110 |
| 14 | GraphTraversal(li) | src/trigrams/li_graph_traversal/walker.py | Class | ~120 |
| 15 | DebateChamber(zhen) | src/trigrams/zhen_debate/orchestrator.py | Class | ~110 |
| 16 | AcousticProc(xun) | src/trigrams/xun_acoustic/processor.py | Class | ~100 |
| 17 | PopulationEst(kan) | src/trigrams/kan_population/estimator.py | Class | ~80 |
| 18 | OtolithAnalyzer(gen) | src/trigrams/gen_otolith/analyzer.py | Class | ~110 |
| 19 | ResourceAssess(kun) | src/trigrams/kun_resource/assessor.py | Class | ~100 |
| 20 | TetrahedronMesh | src/mesh/tetrahedron.py | Class | ~200 |
| 21 | WuXingFlowEngine | src/wuxing/flow_engine.py | Class | ~200 |
| 22-26 | 5 WuXing Agents | src/wuxing/mu_wood.py ... shui_water.py | 5 Classes | ~200 |
| 27 | OverrideToken | src/wuxing/override.py | Class | ~50 |
| 28 | SamsaraRealm | src/samsara/realms.py | Enum+Config | ~120 |
| 29 | KarmaEngine | src/samsara/karma_engine.py | Class | ~200 |
| 30 | SamsaraRing | src/samsara/ring.py | Class | ~170 |
| 31 | KarmaCourt | src/samsara/court.py | Class | ~160 |
| 32 | ReincarnationProtocol | src/samsara/reincarnation.py | Class | ~120 |
| 33 | NirvanaProtocol | src/samsara/nirvana.py | Class | ~120 |
| 34 | SphereGateway | src/sphere/gateway.py | Class | ~140 |
| 35 | BaseTendril | src/tendrils/base_tendril.py | Class | ~180 |
| 36 | TendrilManager | src/tendrils/manager.py | Class | ~160 |
| 37 | SelfEvolve | src/evolution/self_evolve.py | Class | ~80 |
| 38 | ParetoOptimizer | src/evolution/self_evolve.py | Class | ~80 |
| 39 | RollbackManager | src/evolution/self_evolve.py | Class | ~60 |
| 40 | ChaosEngine | src/evolution/self_evolve.py | Class | ~80 |
| 41 | Telemetry/Metrics/Tracing | src/observability/telemetry.py | 3 Classes | ~100 |

**Total: 42 classes, 6 gRPC services, 12 tendrils, ~5,500 LOC**

## File Count

- src/: 42 Python files
- config/: 6 YAML files
- proto/: 6 .proto files
- tests/: 5 directories
- deploy/: docker, k8s, terraform
