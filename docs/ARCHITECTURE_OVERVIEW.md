# 🏗️ 五项目架构 — 每个模块负责什么

> **同步**: 2026-06-09 · **验证**: 54/54 全部通过

---

## 总览图

```
┌──────────────────────────────────────────────────────────┐
│                    eon-core (协调内核)                    │
│  OriginKernel · EventBus · YinYang · Samsara · WuXing    │
│  四象顶点框架 · 八卦子模块 · 进化引擎 · 触须管理         │
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

### 项目定位
五项目的"操作系统"。不处理业务逻辑，只提供基础设施和协调能力。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/kernel/origin.py` | **OriginKernel** | 系统启动/关闭。持有 EventBus。管理生命周期。DAG拓扑路由。 |
| `src/kernel/event_bus.py` | **EventBus** | 所有子系统通信的唯一通道。异步队列。禁止子系统直接互调。 |
| `src/kernel/lifecycle.py` | **LifecycleSM** | 五阶段状态机: SEEDING→SPROUTING→BLOOMING→FRUITING→PRUNING |
| `src/poles/yang_pole.py` | **YangPole** | 阳·扩张: 向外搜索、知识获取、假设生成。只搜不验。 |
| `src/poles/yin_pole.py` | **YinPole** | 阴·收敛: 向内验证、噪声过滤、矛盾检测。只验不搜。 |
| `src/vertices/base_vertex.py` | **BaseVertex** | 四象顶点的抽象基类。定义 on_event/health_check/evolve 接口。 |
| `src/vertices/v0_fish/` | **V0 太阳** | fish-ecology 的顶点适配器。supply_vertex.py |
| `src/vertices/v1_cognitive/` | **V1 太阴** | cognitive 的顶点适配器。verify_vertex.py |
| `src/vertices/v2_porpoise/` | **V2 少阴** | porpoise 的顶点适配器。domain_vertex_p1.py |
| `src/vertices/v3_coilia/` | **V3 少阳** | coilia 的顶点适配器。domain_vertex_p2.py |
| `src/trigrams/` | **8个八卦模块** | ☰乾(元搜索) ☱兑(中文网关) ☲离(图谱遍历) ☳震(辩论) ☴巽(声学) ☵坎(种群) ☶艮(耳石) ☷坤(资源) |
| `src/mesh/tetrahedron.py` | **TetrahedronMesh** | 四面体几何+拓扑。谱间隙计算。边权重混沌扰动。顶点动态重组。 |
| `src/wuxing/flow_engine.py` | **WuXingFlow** | 五行流转引擎。相生相克信号。逃生机制(override)。后台协程非阻塞。 |
| `src/wuxing/mu_wood.py` | **木·生长** | 监控 cognitive 图谱生长率。防止过度膨胀。 |
| `src/wuxing/huo_fire.py` | **火·驱动** | 监控内核协调驱动力。防止系统停滞。 |
| `src/wuxing/tu_earth.py` | **土·供给** | 监控 fish 知识供给质量。防止信息冗余。 |
| `src/wuxing/jin_metal.py` | **金·收敛** | 监控 porpoise 精确度。防止过早收敛。 |
| `src/wuxing/shui_water.py` | **水·适应** | 监控 coilia 适应性。灵活应对变化。 |
| `src/samsara/karma_engine.py` | **KarmaEngine** | 业力计算。追踪善业/恶业。每60s评估。 |
| `src/samsara/court.py` | **KarmaCourt** | 业力法庭。评估所有Agent。触发转生。 |
| `src/samsara/ring.py` | **SamsaraRing** | 六道轮回环。管理6个状态的转换。 |
| `src/samsara/reincarnation.py` | **Reincarnation** | 转生协议。7步原子化。快照回滚。 |
| `src/sphere/gateway.py` | **SphereGateway** | 统一API网关。REST/gRPC/WebSocket/MCP。认证+限流+协议转换。 |
| `src/tendrils/manager.py` | **TendrilManager** | 触须生命周期管理。伸缩/重生/凋亡。 |
| `src/tendrils/base_tendril.py` | **BaseTendril** | 触须抽象基类。12根触须的公共接口。 |
| `src/evolution/self_evolve.py` | **SelfEvolve** | 规则自进化。IF recall<0.9 THEN increase(search_depth)。 |
| `src/evolution/chaos_engine.py` | **ChaosEngine** | Rössler吸引子。每100次查询对边权重施加混沌扰动。 |
| `src/evolution/search_optimizer.py` | **SearchOptimizer** | ParEGO多目标优化。CognitiveBudget+EntropyGuide。 |
| `config/taiji.yaml` | **taiji配置** | 全系统单一真相源。491行YAML。 |

---

## 二、fish-ecology-assistant — 知识供给层

### 项目定位
长江鱼类生态学知识库。提供物种查询+可信度评分+研究流水线。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/adapter.py` | **FishEcologyAdapter** | IProjectAdapter实现。lookup_species()→SpeciesProfile。对外的唯一接口。 |
| `src/orchestrator.py` | **FishEcologyOrchestrator** | 两阶段操作: orchestrator(完整流水线) → direct_db(快速查询)。 |
| `config/yangtze_fish_species.yaml` | **物种数据库** | 长江443种鱼类。dominant_species+protected_species+江豚+环境数据。 |
| `config/agent.yaml` | **Agent配置** | 5层Agent架构。BDI参数。哲学映射。跨项目委托。 |
| `.reasonix/skills/` | **28个AI Skills** | 研究流水线(6个)+物种搜索(4个)+研究(3个)+工具(3个)+统计(3个)+守护(2个)+系统(2个)+搜索(1个)+辩论(1个) |
| `.reasonix/mcp-servers/` | **21个MCP服务器** | scholar/article/scholarly/ncbi/tavily/exa/cnki/wanfang/cas/ocr/rplay/zotero... |
| `.reasonix/handbooks/engineering-grammar.md` | **工程语法手册** | 18条WHEN→THEN规则。哲学→代码映射。 |

### 核心函数

```
lookup_species(name: str) → SpeciesProfile
  输入: "鳤" 或 "Ochetobius elongatus"
  输出: {
    scientific_name, chinese_name, family, conservation,
    search_queries: ["鳤", "鳤 genetic", "鳤 morphology"...],
    ocr_variants: ["Ochetobibus elongatus"...],
    sources: ["pubmed","crossref","openalex","cnki"...]
  }
```

---

## 三、cognitive-search-engine — 搜索验证引擎

### 项目定位
多源学术文献搜索引擎。BDI+ReAct认知架构。图谱遍历。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/adapter.py` | **CognitiveSearchAdapter** | IProjectAdapter实现。search_species()→SearchResult。对外的唯一接口。 |
| `src/agent_core.py` | **CognitiveAgent** | BDI+ReAct循环: Think→Act→Observe→Reflect。 |
| `src/world_model.py` | **WorldModel** | BDI模型: init_belief/form_intention/observe/reflect/update。 |
| `src/rule_engine.py` | **SearchRuleEngine** | 10+搜索阶段处理器。_fn_search_scholar/_fn_traverse_citation/_fn_mine_review... |
| `src/parallel_search.py` | **ParallelSearch** | 多查询并行执行器。PubMed×Crossref×OpenAlex 三路并发。 |
| `src/variant_generator.py` | **VariantGenerator** | OCR变体自动生成。字母替换/删除/元音混淆/尾脱落。 |
| `src/graph_updater.py` | **GraphUpdater** | 知识图谱持久化。ZN/EN双语自动填充。作者/期刊自动注册。 |
| `src/memory_layer.py` | **MemorySystem** | 短期+长期记忆。分类知识图谱懒加载。 |
| `src/meso_agent.py` | **MesoAgent** | 中间协调层。统一管理WorldModel/SearchRuleEngine/MemorySystem。 |
| `src/validator.py` | **Validator** | 跨项目独立性验证。enforce_independence。三角验证(≥3源)。 |
| `src/catalog_loader.py` | **CatalogLoader** | 61数据库·8领域·4层级。graph_route+progressive_search。 |
| `src/inference_engine.py` | **InferenceEngine** | TAO+WuXing推理引擎。 |
| `src/evolution_executor.py` | **EvolutionExecutor** | 自进化反馈执行器。evaluate_and_adapt。 |
| `src/paper_health_check.py` | **PaperHealthCheck** | 论文有效性健康检查。 |
| `src/mcp_client.py` | **MCPClient** | MCP stdio客户端。15秒超时保护。7个MCP服务器。 |
| `config/species_graph.yaml` | **物种图谱** | 7个物种的结构化知识。论文节点+作者节点+引用边。 |
| `config/search_rules.yaml` | **搜索规则** | 10阶段结构化搜索规则引擎。 |
| `skills/` | **5个Skills** | graph-search-engine/cognitive-species-search/chinese-academic-search/meso-orchestrator/self-evolve |

### 核心函数

```
search_species(genus: str, species: str, full_pipeline=False) → SearchResult
  输入: "Ochetobius", "elongatus"
  过程: BDI预测→模式选择→执行分发→图谱更新→ZN/EN规则
  输出: {
    papers: [{title, authors, year, journal, doi, credibility_score}...],
    graph_updates: [新增论文/作者/关系],
    variants: [OCR变体],
    stop_reason: "satisfied" | "budget_exhausted" | "diminishing_returns"
  }
```

---

## 四、porpoise-agent — 江豚领域专研

### 项目定位
长江江豚专属AI研究Agent。NBHF声学分析+矛盾驱动路由+种群评估。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/adapter.py` | **PorpoiseAdapter** | IProjectAdapter实现。analyze_contradiction()→Route。对外的唯一接口。 |
| `src/agent/orchestrator.py` | **Orchestrator** (1644行) | 5阶段管线+矛盾分析+涌现检测+验证标签+自愈监控+战略层。 |
| `src/agent/loop.py` | **CacheFirstLoop** | DeepSeek prefix-cache优化循环(70-95%缓存命中)。 |
| `src/agent/memory.py` | **MemoryStore** | ChromaDB语义搜索(⚠️ stub, 待接线)。 |
| `src/agent/tools.py` | **ToolRegistry** | 7个工具函数(⚠️ 6个为stub, 待实现)。 |
| `src/agent/dimensional_evolution.py` | **DimensionalEvolution** | D₀→D₄维度进化追踪。 |
| `src/agent/stv_core.py` | **STVCore** | S-T-V三角协议核心。 |
| `src/agent/resilience_engine.py` | **ResilienceEngine** | EvolutionRollback+自愈监控。滑动窗口退化检测。 |
| `src/agent/emergence_monitor.py` | **EmergenceMonitor** | ≥3独立源→涌现信号检测。 |
| `src/agent/deepseek_optimizer.py` | **DeepSeekOptimizer** | MoE门控+KV缓存优化。 |
| `src/skills/` | **18个Skill模块** | detect-clicks/classify-vocalizations/estimate-abundance/model-habitat/assess-threats/plan-survey... |
| `src/cli.py` | **CLI入口** | chat/run/doctor 三个子命令。 |
| `data/knowledge_base/` | **26个知识文件** | 文献DB(12)+物种KB(5)+饵料鱼(2)+图片(2)+访问指南(1)+脚本(2)。 |

### 核心函数

```
analyze_contradiction(question: str) → ContradictionRoute
  输入: "长江江豚在禁渔后的种群恢复趋势"
  过程:
    1. 识别主要矛盾 (数据稀缺 vs 水利工程 vs 噪声干扰)
    2. 分配60%预算给主要矛盾 (budget_multiplier=2.5)
    3. 5阶段管线: Literature→Acoustic→Field→Conservation→Report
    4. 涌现检测: ≥3独立源→EmergenceSignal
    5. 验证标签: verified/pending/hypothesis/unverifiable
    6. 自愈监控: entropy/error_rate/contradiction_rate
  输出: {
    primary_contradiction, secondary_contradictions,
    budget_multiplier, phase, verification, emergence_signals
  }
```

---

## 五、coilia-agent — 刀鲚领域专研 (Pₙ模板原型)

### 项目定位
刀鲚专属AI研究Agent。耳石微化学+洄游生态+资源评估。同时是Pₙ模板原型。

### 模块清单

| 目录 | 模块 | 负责什么 |
|------|------|---------|
| `src/adapter.py` | **CoiliaAdapter** | IProjectAdapter实现。assess_species()→Assessment。对外的唯一接口。 |
| `src/agent/orchestrator.py` | **CoiliaOrchestrator** (340行) | 5阶段管线+关键词路由+SPECIES_PROFILE内置领域知识。 |
| `src/skills/search-literature/` | **文献检索** | 通过cognitive DirectLoader中英双语搜索。 |
| `src/skills/analyze-migration/` | **洄游分析** | 耳石Sr/Ca剖面+洄游路线重建。 |
| `src/skills/assess-stock/` | **资源评估** | CPUE分析+种群动态建模。 |
| `config/agent.yaml` | **Agent配置** | P₂/V3角色声明。external skills+inline_phases。shared配置。 |
| `src/main.py` | **CLI入口** | coilia run --query "刀鲚洄游路线 长江"。 |

### 核心函数

```
assess_species(species: str, context: str) → SpeciesAssessment
  输入: "Coilia nasus", "洄游生态"
  过程:
    1. SPECIES_PROFILE 加载: {耳石微化学规则, 历史峰值, 课题组}
    2. cognitive DirectLoader 获取文献
    3. 领域知识应用: Sr/Ca>3.0→marine, Sr/Ca<1.0→freshwater
  输出: {
    species, phase, findings, recommendations
  }
```

---

## 项目间数据流

```
P1: fish.lookup_species("鳤")    → cognitive.search_species("Ochetobius","elongatus")
P2: cognitive.search_result      → fish.score_credibility(papers)
P3: cognitive.search_result      → porpoise.analyze_contradiction() | coilia.assess_species()
P4: ALL.health()                 → eon-core Samsara.evaluate_karma()
```

---

> **每个项目有且仅有一个对外的核心函数。**
> fish=lookup_species · cognitive=search_species · porpoise=analyze_contradiction · coilia=assess_species · eon-core=route_event
