# 🏗️ 五项目架构 — 每个模块负责什么

> **同步**: 2026-06-09 · **三生万物精简版**

---

## 总览图

```
┌──────────────────────────────────────────────────────────┐
│                    eon-core (协调内核)                    │
│  OriginKernel · EventBus · YinYangPoles · SamsaraRing    │
│  顶点框架 · 八卦子模块 · 进化引擎                         │
└──────┬───────────────────────────────────────┬───────────┘
       │ 协调                                    │ 协调
       ▼                                         ▼
┌──────────────┐  P1/P2  ┌──────────────┐       │
│ fish-ecology │◄───────►│ cognitive    │       │
│ (知识供给)    │         │ (搜索验证)    │       │
│              │         │              │       │
│ 物种数据库    │         │ BDI搜索      │       │
│ 可信度评分    │         │ 图谱遍历     │       │
│ 28 AI Skills │         │ OCR变体      │       │
└──────┬───────┘         └──────┬───────┘       │
       │ P3(派生)               │ P3(派生)       │
       ▼                        ▼               │
┌──────────────┐         ┌──────────────┐       │
│ porpoise     │         │ coilia       │       │
│ (江豚专研)    │         │ (刀鲚专研)    │◄──────┘
│              │         │              │
│ 声学分析     │         │ 耳石微化学    │
│ 矛盾路由     │         │ 洄游生态     │
│ 种群建模     │         │ 资源评估     │
└──────────────┘         └──────────────┘
```

---

## 一、eon-core — 协调内核 + 基础设施

### 定位
五项目的"操作系统"。不处理业务逻辑，只提供基础设施和协调能力。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/kernel/origin.py` | **OriginKernel** | 系统启动/关闭。持有 EventBus。管理生命周期。DAG拓扑路由。 |
| `src/kernel/event_bus.py` | **EventBus** | 所有子系统通信的唯一通道。异步队列。 |
| `src/kernel/lifecycle.py` | **LifecycleSM** | 五阶段状态机: SEEDING→SPROUTING→BLOOMING→FRUITING→PRUNING |
| `src/poles/yang_pole.py` | **YangPole** | 扩张: 向外搜索、知识获取。只搜不验。 |
| `src/poles/yin_pole.py` | **YinPole** | 收敛: 向内验证、噪声过滤、矛盾检测。只验不搜。 |
| `src/vertices/base_vertex.py` | **BaseVertex** | 顶点抽象基类。定义 on_event/health_check/evolve 接口。 |
| `src/vertices/v0_fish/` | **fish 顶点适配器** | fish-ecology-assistant 的 eon-core 代理。supply_vertex.py |
| `src/vertices/v1_cognitive/` | **cognitive 顶点适配器** | cognitive-search-engine 的 eon-core 代理。verify_vertex.py |
| `src/vertices/v2_porpoise/` | **porpoise 顶点适配器** | porpoise-agent 的 eon-core 代理。domain_vertex_p1.py |
| `src/vertices/v3_coilia/` | **coilia 顶点适配器** | coilia-agent 的 eon-core 代理。domain_vertex_p2.py |
| `src/trigrams/` | **8个功能子模块** | 元搜索/中文网关/图谱遍历/辩论/声学/种群/耳石/资源 |
| `src/mesh/tetrahedron.py` | **TetrahedronMesh** | 四面体拓扑。谱间隙计算。边权重混沌扰动。 |
| `src/wuxing/` | **WuXing监控模块** | 5个方向的后台健康监控。非阻塞协程。 |
| `src/samsara/` | **Samsara业力评估** | 运行时质量评估。KarmaCourt每60s评估。Reincarnation回滚。 |
| `src/sphere/gateway.py` | **SphereGateway** | 统一API网关。REST/gRPC/WebSocket/MCP。 |
| `src/tendrils/` | **Tendril探针** | 对外部服务的连接管理。 |
| `src/evolution/self_evolve.py` | **SelfEvolve** | 规则自进化。IF recall<0.9 THEN increase(search_depth)。 |
| `src/evolution/chaos_engine.py` | **ChaosEngine** | Rössler吸引子。每100次查询对边权重施加混沌扰动。 |
| `src/evolution/search_optimizer.py` | **SearchOptimizer** | ParEGO多目标优化。CognitiveBudget+EntropyGuide。 |

---

## 二、fish-ecology-assistant — 知识供给层

### 定位
长江鱼类生态学知识库。提供物种查询 + 可信度评分 + 研究流水线。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/adapter.py` | **FishEcologyAdapter** | IProjectAdapter实现。`lookup_species()` / `score_credibility()`。对外的唯一接口。 |
| `src/orchestrator.py` | **FishEcologyOrchestrator** | 两阶段操作: orchestrator(完整流水线) → direct_db(快速查询)。 |
| `config/fish_species_kb.yaml` v2.1 | **多流域物种知识库** | 长江443种 + 图们江 + 绥芬河 + 黑龙江。 |
| `config/agent.yaml` | **Agent配置** | 5层Agent架构。BDI参数。跨项目委托。 |
| `.reasonix/skills/` | **28个AI Skills** | 研究流水线(6) + 物种搜索(4) + 研究(3) + 工具(3) + 统计(3) + 守护(2) + 系统(2) + 搜索(1) + 辩论(1) |
| `.reasonix/mcp-servers/` | **21个MCP服务器** | scholar/article/scholarly/ncbi/tavily/exa/cnki/wanfang/cas/ocr/... |

### 核心函数

```python
lookup_species(name: str) -> SpeciesProfile
  # 输入: "鳤" 或 "Ochetobius elongatus"
  # 输出: {scientific_name, chinese_name, family, conservation,
  #        search_queries, ocr_variants, sources}

score_credibility(papers: list[dict]) -> list[dict]
  # 输入: cognitive 搜索结果 [{title, journal, doi, pmid}...]
  # 输出: 每篇 + {credibility_score [0-100], flag}
```

---

## 三、cognitive-search-engine — 搜索验证引擎

### 定位
多源学术文献搜索引擎。BDI+ReAct认知架构。图谱遍历。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/adapter.py` | **CognitiveSearchAdapter** | IProjectAdapter实现。`search_species()`。对外的唯一接口。 |
| `src/agent_core.py` | **CognitiveAgent** | BDI+ReAct循环: Think→Act→Observe→Reflect。 |
| `src/world_model.py` | **WorldModel** | BDI模型: init_belief / form_intention / observe / reflect / update。 |
| `src/rule_engine.py` | **SearchRuleEngine** | 12阶段搜索管线。graph/exact/chinese/review/citation/variant... |
| `src/parallel_search.py` | **ParallelSearch** | 多查询并行执行器。PubMed×Crossref×OpenAlex 三路并发。 |
| `src/variant_generator.py` | **VariantGenerator** | OCR变体自动生成。字母替换/删除/元音混淆/尾脱落。 |
| `src/graph_updater.py` | **GraphUpdater** | 知识图谱持久化。ZN/EN双语自动填充。 |
| `src/memory_layer.py` | **MemorySystem** | 短期+长期记忆。分类知识图谱懒加载。 |
| `src/meso_agent.py` | **MesoAgent** | 中间协调层。统一管理 WorldModel / SearchRuleEngine / MemorySystem。 |
| `src/validator.py` | **Validator** | 跨项目独立性验证。三角验证(≥3源)。 |
| `src/mcp_client.py` | **MCPClient** | MCP stdio客户端。15秒超时保护。7个MCP服务器。 |
| `config/species_graph.yaml` | **物种图谱** | 7个物种的结构化知识。论文节点+引用边。 |
| `config/search_rules.yaml` | **搜索规则** | 12阶段结构化搜索规则引擎。 |

### 核心函数

```python
search_species(genus: str, species: str, full_pipeline=False) -> SearchResult
  # 输入: "Ochetobius", "elongatus"
  # 过程: BDI预测→模式选择→12阶段管线→图谱更新→ZN/EN规则
  # 输出: {papers: [{title, authors, year, journal, doi, credibility}...],
  #        graph_updates, variants, stop_reason}
```

---

## 四、porpoise-agent — 江豚领域专研 (P₁)

### 定位
长江江豚专属AI研究Agent。NBHF声学分析 + 矛盾驱动路由 + 种群评估。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/adapter.py` | **PorpoiseAdapter** | IProjectAdapter实现。`analyze_contradiction()`。对外的唯一接口。 |
| `src/agent/orchestrator.py` | **Orchestrator** (1644行) | 5阶段管线+矛盾分析+涌现检测+验证标签+自愈监控。 |
| `src/agent/loop.py` | **CacheFirstLoop** | DeepSeek prefix-cache优化循环(70-95%缓存命中)。 |
| `src/agent/memory.py` | **MemoryStore** | ChromaDB语义搜索。 |
| `src/agent/tools.py` | **ToolRegistry** | 7个工具函数。 |
| `src/skills/` | **18个Skill模块** | detect-clicks / classify-vocalizations / estimate-abundance / model-habitat / assess-threats / plan-survey... |
| `data/knowledge_base/` | **26个知识文件** | 文献DB(12) + 物种KB(5) + 饵料鱼(2) + 图片(2)。 |

### 核心函数

```python
analyze_contradiction(question: str) -> ContradictionRoute
  # 输入: "长江江豚在禁渔后的种群恢复趋势"
  # 过程: 矛盾识别→预算分配→5阶段管线→涌现检测→验证标签→自愈监控
  # 输出: {primary_contradiction, secondary_contradictions,
  #        budget_multiplier, phase, verification, emergence_signals}
```

---

## 五、coilia-agent — 刀鲚领域专研 (P₂)

### 定位
刀鲚专属AI研究Agent。耳石微化学 + 洄游生态 + 资源评估。也是 Pₙ 模板原型。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/adapter.py` | **CoiliaAdapter** | IProjectAdapter实现。`assess_species()`。对外的唯一接口。 |
| `src/agent/orchestrator.py` | **CoiliaOrchestrator** (340行) | 5阶段管线+关键词路由+内置领域知识。 |
| `src/skills/search-literature/` | **文献检索** | 通过 cognitive DirectLoader 中英双语搜索。 |
| `src/skills/analyze-migration/` | **洄游分析** | 耳石Sr/Ca剖面+洄游路线重建。 |
| `src/skills/assess-stock/` | **资源评估** | CPUE分析+种群动态建模。 |
| `src/main.py` | **CLI入口** | `coilia run --query "刀鲚洄游路线 长江"` |

### 核心函数

```python
assess_species(species: str, context: str) -> SpeciesAssessment
  # 输入: "Coilia nasus", "洄游生态"
  # 过程: SPECIES_PROFILE→cognitive搜索→领域知识应用
  # 输出: {species, phase, findings, recommendations}
```

---

## 六、conflict-arbiter — 冲突仲裁层

### 定位
多源保护推荐冲突检测 + 可信度加权仲裁 + 熔断。

### 核心函数

```python
assess_conflict(species: str, sources: list[dict]) -> ConflictReport
  # 输入: species="Coilia nasus",
  #       sources=[{source, protection_level, iucn}, ...]
  # 输出: {conflict_level, consensus, verdict}
```

---

## 项目间数据流

```
P1: fish.lookup_species("鳤") → cognitive.search_species("Ochetobius","elongatus")
P2: cognitive.search_result   → fish.score_credibility(papers)
P3: cognitive.search_result   → porpoise.analyze_contradiction() | coilia.assess_species()
P4: porpoise.health()         → eon-core Samsara.evaluate_karma()
P5: any_project.output()      → conflict.assess_conflict()
P6: conflict.verdict()        → user
P7: cognitive.taxonomy_change → fish.update_taxonomy()
```

---

> **每个项目有且仅有一个对外核心函数。**
> fish=`lookup_species` · cognitive=`search_species` · porpoise=`analyze_contradiction`
> coilia=`assess_species` · eon-core=`route_event` · conflict=`assess_conflict`
