# 🗂️ 项目关系 — 谁是谁

> **核心**: 项目(目录) ≠ 角色(架构)。同一套代码，两种身份。
> **同步**: 2026-06-09 · 三生万物精简版

---

## 一、文件系统布局 (5个项目平级)

```
<workspace>/
  ├── eon-core/                  ─ 内核基础设施
  ├── fish-ecology-assistant/    ─ 鱼类知识供给
  ├── cognitive-search-engine/   ─ 搜索验证引擎
  ├── porpoise-agent/            ─ 江豚专研 (P₁)
  └── coilia-agent/              ─ 刀鲚专研 (P₂)
```

---

## 二、架构角色 (两层: 三角核心 + 万物衍生)

### 三角核心 (sealed_set, arity=3) — 缺一不可

| 项目 | 角色 | 接口 | 核心函数 |
|------|------|------|---------|
| **fish-ecology-assistant** | 知识供给 (S/V0) | SpeciesKnowledgeProvider | `lookup_species(name)` |
| **cognitive-search-engine** | 搜索验证 (V/V1) | LiteratureValidator | `search_species(genus, species)` |
| **eon-core** | 协调内核 | OriginKernel | `route_event(event)` |

**不变量**: 三项目必须同时存在。缺失任意一个 → 系统不可运行。

### 万物衍生 (open_set, arity≥0) — 可无限扩展

| 实例 | 项目 | 目标物种 | 核心函数 |
|------|------|---------|---------|
| P₁ | porpoise-agent | Neophocaena asiaeorientalis (长江江豚) | `analyze_contradiction(question)` |
| P₂ | coilia-agent | Coilia nasus (刀鲚) | `assess_species(species, context)` |
| Pₙ | `spawn_agent.py` 生成 | 任意物种 | 模板生成 |

**不变量**: 三角核心可以脱离万物独立运行。万物依赖三角的知识供给和搜索验证。

---

## 三、eon-core 的双重身份

```
eon-core AS 项目目录:       eon-core AS 架构角色:
─────────────────────      ──────────────────────
eon-core/                  (1) 三角核心.协调者
  src/kernel/origin.py       → EventBus, DAG路由, 生命周期
  src/poles/                 → YangPole(扩张) + YinPole(收敛)
  src/vertices/              → 4个顶点适配器 (代理各项目)
                            (2) 万物.基础设施宿主
  src/trigrams/              → 8个功能子模块
  src/wuxing/                → 健康监控
  src/samsara/               → 业力评估
  src/mesh/                  → 四面体拓扑
  src/sphere/                → API网关
  src/tendrils/              → 外部探针
  src/evolution/             → 自进化

一份代码, 两个身份:
  1) 三角核心的协调者 (OriginKernel, EventBus)
  2) 万物的基础设施宿主 (顶点/子模块/监控/评估)
```

---

## 四、7 条数据流通路

| ID | 路径 | 转换 | 触发 |
|----|------|------|------|
| P1 | fish → cognitive | `lookup_species()` → `search_species()` | 用户查物种 |
| P2 | cognitive → fish | `search()` → `score_credibility()` | 搜索完成 |
| P3 | cognitive → porpoise/coilia | `search()` → domain analysis | 需要领域上下文 |
| P4 | porpoise → eon-core | `health()` → `evaluate_karma()` | 健康脉冲(60s) |
| P5 | any → conflict | `output()` → `detect_conflicts()` | 多源不一致 |
| P6 | conflict → user | `verdict()` → `consensus_report()` | 仲裁完成 |
| P7 | cognitive → fish | taxonomy_discrepancy() → update_taxonomy() | 分类变更 |

---

## 五、一句话消除混乱

```
Q: eon-core 和另外 4 个项目是什么关系？
A: 文件系统层面: 平级。架构层面: eon-core 是三角核心的协调者 + 万物的基础设施宿主。

Q: porpoise 和 coilia 属于三角核心还是万物？
A: 万物。它们是三角核心派生的物种专研项目。三角核心 = [fish, cognitive, eon-core]。

Q: 三角核心必须存在吗？
A: 必须。缺任意一个顶点，系统不可运行。万物可以没有，三角不能缺。

Q: 顶点适配器 (vertices/) 和八卦子模块 (trigrams/) 在哪里？
A: 全部在 eon-core/src/ 下。它们是 eon-core 的内部基础设施。

Q: Pₙ 新项目在哪里生成？
A: 在 workspace 根目录 <species>-agent/，与 porpoise-agent/ 和 coilia-agent/ 同级。
   spawn_agent.py 一键生成。
```
