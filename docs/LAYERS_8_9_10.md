# L8·L9·L10: 触须探针 · 进化引擎 · 部署流水线

> **道→一→二→三→万物 — 万物层 (8·9·10)**
> L8 触须: 12根向外探索的数据探针
> L9 进化: 自愈·混沌·Pareto优化
> L10 部署: Docker·K8s·CI/CD
> **同步**: 2026-06-09

---

## L8: 触须探针 — 12根外部数据探针

### 8.1 工程合约

```
TendrilManager (单例, OriginKernel 持有)
  ├── tendrils: Dict[str, BaseTendril]     // 12根已注册触须
  ├── registry: TendrilRegistry             // 触须注册表 (YAML→运行时)
  └── lifecycle: TendrilLifecycle           // 伸缩状态机

BaseTendril (抽象基类):
  属性:
    tendril_id: str                         // 唯一标识
    target: ExternalSource                  // 目标数据源
    protocol: REST | GraphQL | MCP | Scraping
    state: EXTENDED | RETRACTING | RETRACTED | EXTENDING | PRUNED
    health: { alive: bool, latency_ms: int, error_rate: float }
    rate_limiter: TokenBucket               // 独立限流器
    cache: TendrilCache                     // 本地结果缓存 (TTL=300s)

  方法:
    async extend() → None                   // 伸展触须: 建立连接
    async probe(query) → ExternalResult     // 探测: 查询外部源
    async retract() → None                  // 收缩: 断开连接
    async regenerate() → None               // 重生: 凋亡后重新生长
```

### 8.2 12根触须映射

| # | 触须ID | 目标 | 协议 | 附着顶点 | 对应MCP工具 | 状态 |
|---|--------|------|------|:---:|---------|:--:|
| 1 | `google_scholar` | Google Scholar | Scraping | V0 | `scholar_search_literature_graph` | ✅ |
| 2 | `pubmed` | PubMed API | REST | V0 | `ncbi_ncbi_esearch/esummary/efetch` | ✅ |
| 3 | `crossref` | CrossRef API | REST | V0 | `scholar_search_literature_graph` | ✅ |
| 4 | `openalex` | OpenAlex API | REST | V0 | `scholar_search_literature_graph` | ✅ |
| 5 | `cnki` | 中国知网 | Scraping | V0 | `web_search site:cnki.net` | ⚠️ |
| 6 | `cscd` | CSCD引文数据库 | REST | V0 | `web_search` | ⚠️ |
| 7 | `wanfang` | 万方数据 | Scraping | V0 | `web_search site:wanfangdata.com.cn` | ⚠️ |
| 8 | `semantic_scholar` | Semantic Scholar | REST | V1 | `scholar_search_literature_graph` | ✅ |
| 9 | `tavily` | Tavily AI搜索 | REST | V0 | `tavily_tavily_search` | ✅ |
| 10 | `exa` | Exa语义搜索 | REST | V0 | `exa_web_search_exa` | ✅ |
| 11 | `zotero` | Zotero文献库 | SQLite | V2 | `zotero` MCP | ✅ |
| 12 | `rplay` | R统计环境 | stdio | V2/V3 | `rplay_execute_r_command` | ✅ |

### 8.3 触须生命周期状态机

```
EXTENDED ──(连续3次失败)──→ RETRACTING ──→ RETRACTED
    ↑                            │              │
    │                            │              │ (冷却30s)
    │                            ▼              ▼
    └────(探测成功)──── EXTENDING ◄── (尝试重连)

RETRACTED ──(1h内5次伸缩)──→ UNSTABLE ──(暂停1h)──→ EXTENDING (0.5倍速限)

UNSTABLE ──(永久不可用)──→ PRUNED (从注册表移除)

EXTENDED ──(外部API关闭通知)──→ PRUNED
```

### 8.4 工程语言化 — 运行规则

```
// 每30s对所有EXTENDED触须执行健康检查
WHEN health_cycle_triggered()
THEN
  FOR EACH tendril IN tendrils WHERE state == EXTENDED:
    health = tendril.health_check()
    IF health.alive == False:
      tendril.consecutive_failures += 1
      IF tendril.consecutive_failures >= 3:
        tendril.retract()
        tendril.state = RETRACTED

// 冷却后尝试重生
WHEN tendril.state == RETRACTED AND time_since_retract > 30s:
  tendril.state = EXTENDING
  success = tendril.extend()
  IF success:
    tendril.state = EXTENDED
    tendril.consecutive_failures = 0
  ELSE:
    tendril.unstable_count += 1
    IF tendril.unstable_count >= 5:
      tendril.state = UNSTABLE

// 新数据源接入时动态生长
WHEN new_external_source_registered(source):
  template = load_tendril_template(source.type)
  tendril = TendrilFactory.create(template, source)
  tendril_manager.register(tendril)
  tendril.extend()  // 初始状态 EXTENDING
```

### 8.5 实际代码映射

```
TendrilManager:    eon-core/src/tendrils/manager.py       (✅ 类存在)
BaseTendril:       eon-core/src/tendrils/base_tendril.py   (✅ 类存在)
TendrilCache:      eon-core/src/tendrils/cache.py          (✅ 类存在)
触须注册表:        eon-core/config/tendrils_registry.yaml  (✅ 存在)

待实现:
  - 各触须的 probe() 方法 → 对接实际 MCP 工具
  - 伸缩状态机的异步协程
  - 触须健康指标暴露到 Prometheus
```

---

## L9: 进化引擎 — 自愈·混沌·Pareto

### 9.1 工程合约

```
EvolutionEngine (单例, OriginKernel 持有)
  ├── pareto: ParetoOptimizer        // 多目标贝叶斯优化
  ├── chaos: ChaosEngine             // 确定性混沌扰动
  ├── rollback: RollbackManager      // 参数快照 + 自动回滚
  └── self_evolve: SelfEvolve        // 规则自进化

ParetoOptimizer:
  目标: [recall, token_efficiency, contradiction_resolution_rate]
  算法: ParEGO (Pareto Efficient Global Optimization)
  周期: 每24h或每1000次查询

ChaosEngine:
  模型: Rössler 吸引子 (3维确定性混沌)
  扰动: 每100次查询, 对边权重施加 chaos_factor×dW
  目的: 避免路由陷入局部最优

RollbackManager:
  快照: 每24h对全系统参数做一次快照
  回滚: 当 recall < 0.5 持续3个周期, 自动回滚到最近健康快照
  窗口: 保留最近7个快照

SelfEvolve:
  触发: 每24h评估一次进化规则
  规则: IF recall < 0.9 THEN increase(search_depth, 1)
        IF token_avg > 2000 THEN enable(early_stopping)
        IF contradiction_rate > 0.2 THEN increase(debate_rounds, 1)
```

### 9.2 混沌引擎 — Rössler 吸引子

```
工程语言:
  dx/dt = -y - z
  dy/dt = x + a*y      (a = 0.2)
  dz/dt = b + z*(x - c) (b = 0.2, c = 5.7)

  每100次查询:
    w = integrate_rossler(dt=0.01, steps=100)
    FOR EACH edge IN tetrahedron.edges:
      edge.weight += chaos_factor × w.z  // z分量作为扰动
      edge.weight = clamp(edge.weight, 0.01, 1.0)

  代码: eon-core/src/evolution/chaos_engine.py  (✅ 类存在)
```

### 9.3 Pareto优化 — 多目标权衡

```
目标空间:
  f₁ = recall_rate          → 最大化
  f₂ = token_efficiency     → 最大化 (papers_per_1k_tokens)
  f₃ = contradiction_resolution → 最大化

Pareto前沿:
  当 search_depth ↑ → recall ↑ (好) 但 token_efficiency ↓ (坏)
  当 early_stop ↑ → token_efficiency ↑ (好) 但 recall ↓ (坏)
  → 在Pareto前沿上选择非支配解

工程语言:
  WHEN pareto_cycle_triggered():
    current_point = (recall, token_eff, contra_res)
    IF is_dominated(current_point, pareto_frontier):
      // 当前参数被支配 → 需要优化
      new_params = pareto.search_near(current_point)
      apply(new_params)
    ELSE:
      pareto_frontier.add(current_point)

代码: eon-core/src/evolution/self_evolve.py  (✅ 类存在)
```

### 9.4 自愈机制

```
// D₃ 自愈监控体 (porpoise-agent)
SelfHealingMonitor:
  监控指标: [entropy, latency, error_rate, contradiction_rate]

  WHEN entropy > 0.8 FOR 3min:
    action = AUTO_RESET
    log("熵值过高, 自动重置搜索状态")

  WHEN contradiction_rate > 0.5 FOR 5min:
    action = ESCALATE_TO_HUMAN
    log("矛盾率异常, 请求人工介入")

  WHEN error_rate > 0.3 FOR 2min:
    action = RETREAT_TO_PLANNER
    log("错误率过高, 退回到规划阶段")

代码:
  porpoise-agent/src/agent/resilience_engine.py (✅ EvolutionRollback)
  porpoise-agent/src/agent/orchestrator.py       (✅ SelfHealingMonitor)
```

### 9.5 实际代码映射

```
EvolutionEngine:      eon-core/src/evolution/self_evolve.py    ✅
ChaosEngine:          eon-core/src/evolution/chaos_engine.py   ✅
ParetoOptimizer:      eon-core/src/evolution/search_optimizer.py ✅
RollbackManager:      porpoise-agent/src/agent/resilience_engine.py ✅
SelfHealingMonitor:   porpoise-agent/src/agent/orchestrator.py ✅

进化配置文件:
  eon-core/config/samsara.yaml          // 业力参数
  cognitive-search-engine/config/evolution.yaml
  fish-ecology-assistant/config/evolution.yaml
  porpoise-agent/config/evolution.yaml
```

---

## L10: 部署流水线 — Docker·K8s·CI/CD

### 10.1 容器化策略

```
每个项目独立 Docker 容器:

eon-core:
  Dockerfile: eon-core/deploy/docker/Dockerfile
  端口: REST:8080, gRPC:9090
  依赖: Python 3.12+

fish-ecology-assistant:
  运行时: Reasonix Code (非独立容器)
  部署: .reasonix/setup-migrate.ps1 一键脚本

cognitive-search-engine:
  运行时: importlib DirectLoader (被调用, 非独立服务)
  部署: git submodule → 自动获取最新

porpoise-agent:
  Dockerfile: porpoise-agent/Dockerfile
  端口: CLI (chat/run/doctor)
  依赖: DeepSeek API, ChromaDB

coilia-agent:
  部署: pip install -e . (轻量CLI)
  依赖: cognitive DirectLoader
```

### 10.2 K8s 拓扑 (规划)

```
┌─────────────────────────────────────────────┐
│                  K8s Cluster                 │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ eon-core │  │ porpoise │  │ coilia   │  │
│  │  (Deploy)│  │  (Deploy)│  │  (Deploy)│  │
│  │  replicas│  │  replicas│  │  replicas│  │
│  │   :1     │  │   :2     │  │   :1     │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │        │
│  ┌────▼──────────────▼──────────────▼────┐  │
│  │         SphereGateway (NodePort)      │  │
│  │         REST:30080  gRPC:30090        │  │
│  └───────────────────────────────────────┘  │
│                                              │
│  ┌──────────┐  ┌───────────────────────┐   │
│  │ ChromaDB │  │    Jaeger + Prometheus │   │
│  │  (Stateful│  │    (Monitoring Stack)  │   │
│  │   Set)   │  └───────────────────────┘   │
│  └──────────┘                               │
└─────────────────────────────────────────────┘

config: eon-core/deploy/k8s/ (规划中)
```

### 10.3 CI/CD 流水线

```
GitHub Actions (.github/workflows/):

1. validate.yml (每次push):
   - verify_standalone.py      // 5项目独立验证
   - verify_pathways.py        // 通路结构验证
   - verify_philosophy_rules.py // 18规则覆盖检查
   - run_all_tests.py --level low  // 冒烟测试

2. integration.yml (PR → main):
   - verify_pathways.py --live    // LIVE通路执行
   - demo_evolution.py            // 端到端演化演示

3. deploy.yml (tag push):
   - docker build + push
   - K8s helm upgrade

当前状态:
  ✅ cognitive-search-engine/.github/workflows/validate.yml
  ✅ fish-ecology-assistant/.github/workflows/validate.yml
  ✅ porpoise-agent/.github/workflows/validate.yml
  ⚠️ eon-core: 缺少 CI 配置
  ⚠️ coilia-agent: 缺少 CI 配置
```

### 10.4 工程语言化 — 部署规则

```
// 冒烟测试 (每次push)
WHEN git_push():
  verify_standalone()            // 5项目独立 → 必须全部通过
  verify_pathways()              // 4通路结构 → 必须全部通过
  verify_philosophy_rules()      // 18规则 → 必须全部通过
  IF any_failed THEN BLOCK merge

// 集成测试 (PR → main)
WHEN pr_to_main():
  verify_pathways("--live")      // 真实通路执行
  demo_evolution()               // 端到端演化
  run_all_tests("--level", "medium")
  IF any_failed THEN REQUEST_CHANGES

// 部署 (tag push)
WHEN tag_push("v*"):
  docker_build(all_projects)
  docker_push(all_projects)
  k8s_helm_upgrade()
  health_check_smoke()
  IF health_failed THEN ROLLBACK
```

---

> **L8 触须**: 12根探针向外索取知识。可伸缩。可凋亡。可重生。
> **L9 进化**: 混沌扰动避免僵化。Pareto优化权衡多目标。自愈监控自动修复。
> **L10 部署**: 容器化隔离。K8s编排。CI/CD自动化验证。

**验证**: `verify_standalone 5/5 · verify_pathways 16/16 · verify_philosophy_rules 18/18`
