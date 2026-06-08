# 五项目包含关系与调用框架 (v7.2)

> 更新：2026-06-08 | 版本: Eon-Taiji v7.2.0
> meso-cosmos-agent 已删除 → 功能迁移至 eon-core
> P₁(porpoise) 与 P₂(coilia) 为同级平行项目

## 一、整体架构

```
                    scripts/project_loader.py
                   (统一 DirectLoader 入口)
                    │
    ┌───────┬───────┼───────┬───────┐
    ▼       ▼       ▼       ▼       ▼
  fish   cognitive porpoise coilia  (via adapter.py)
  V0      V1        V2      V3
  (S)     (V)       (P₁)    (P₂)

        全部通过 eon-core OriginKernel 协调
              ┌──────────────────┐
              │   ☯️ eon-core    │
              │   DAG + EventBus │
              │   + Samsara 六道 │
              └──────────────────┘
```

## 二、调用关系矩阵

| 调用方 ↓ / 被调用方 → | fish(V0) | cognitive(V1) | porpoise(V2) | coilia(V3) | eon-core |
|:----------------------|:--------:|:-------------:|:------------:|:----------:|:--------:|
| **fish(V0)**          | —        | —             | —            | —          | —        |
| **cognitive(V1)**     | —        | —             | —            | —          | —        |
| **porpoise(V2)**      | —        | project_loader| —            | —          | —        |
| **coilia(V3)**        | —        | project_loader| —            | —          | —        |
| **eon-core**          | adapter  | adapter       | adapter      | adapter    | —        |

## 三、项目概览

| 项目 | 顶点 | Python行数 | 入口 | 核心类 |
|------|:----:|:---------:|------|--------|
| eon-core | ☯️ | ~7,000 | `src/main.py` | OriginKernel, SamsaraRing |
| cognitive-search-engine | V1 | ~7,800 | `src/meso_agent.py` | MesoAgent, CognitiveAgent |
| fish-ecology-assistant | V0 | ~300 | `src/orchestrator.py` | FishEcologyOrchestrator |
| porpoise-agent | V2 | ~10,000 | `src/agent/orchestrator.py` | Orchestrator |
| coilia-agent | V3 | ~500 | `src/agent/orchestrator.py` | CoiliaOrchestrator |

## 四、adapter.py 接口契约

每个项目暴露统一的 `IProjectAdapter` 接口：

| 项目 | 适配器类 | 工厂函数 | search() 行为 |
|------|---------|----------|--------------|
| fish | FishEcologyAdapter | `get_fish()` | 物种库查询 + DELEGATE 协议 |
| cognitive | CognitiveSearchAdapter | `get_cognitive()` | MesoAgent.search() |
| porpoise | PorpoiseAdapter | `get_porpoise()` | Orchestrator.run() |
| coilia | CoiliaAdapter | `get_coilia()` | CoiliaOrchestrator.run() |

统一调用: `from scripts.project_loader import get_fish, get_cognitive, get_porpoise, get_coilia`

## 五、Git Submodule 关系

```
fish-ecology-assistant/external/cognitive-search-engine/   ← 已删除 (v7.1)
porpoise-agent/external/cognitive-search-engine/            ← 建议删除
```

> project_loader 通过 workspace 根路径 `../cognitive-search-engine/` 直接加载，不再需要 submodule 副本。

## 六、调用链路

```
用户查询
  → eon-core SphereGateway (L7)
    → OriginKernel.route_event() (L0: 意图分类 + DAG路由)
      → EventBus.publish(topic="vertex.V2") (L0)
        → V2.on_event() (L2: 顶点)
          → project_loader.get_porpoise() (统一入口)
            → PorpoiseAdapter.search() (adapter)
              → Orchestrator.run() (内部管线)
                → [可选] get_cognitive() → MesoAgent.search()
          → KarmaEngine.record_deed() (L6: 业力记录)
      → SamsaraRing.run_karma_cycle() (L6: 每60秒评估)
  → SphereGateway.respond() (L7: 返回结果)
```

## 七、与旧架构对比

| 维度 | v5.2 (旧) | v7.2 (新) |
|------|----------|----------|
| 项目数 | 6 | 5 |
| 协调层 | meso-cosmos (单体) | eon-core (DAG+EventBus) |
| 跨项目调用 | 3种路径硬编码 | 统一 project_loader |
| Agent 状态 | 无 | 六道轮回自动流转 |
| fish Python入口 | 无 | adapter + orchestrator |
| coilia 地位 | P₂ 同级 → 被误合并 → 恢复 | P₂ 同级 (正确) |
