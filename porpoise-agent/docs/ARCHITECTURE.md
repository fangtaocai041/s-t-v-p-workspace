# 🏗️ Porpoise Agent 架构设计 v2.0

> 基于**五层标准智能体分层架构模型 (Standard Agent Architectural Model)**
>
> 每一层抽象都由江豚研究的具体需求、DeepSeek 特性、以及形式化理论驱动。

## 设计哲学

### 四条铁律

| # | 原则 | 说明 |
|---|------|------|
| I | **五层闭环** | 交互→认知→记忆→映射→执行 形成控制论反馈系统 |
| II | **BDI 形式化** | Belief/Desire/Intention 状态机驱动决策 |
| III | **DeepSeek 原生** | 深度利用 prefix-cache、R1 推理链 |
| IV | **人机协作** | Agent 是副驾驶，关键决策保留人工审批 |

### 理论基础

本架构融合以下理论框架:

| 理论 | 对应组件 | 说明 |
|------|----------|------|
| **BDI Model** | `src/cognitive/bdi.py` | Belief-Desire-Intention 心智模型 |
| **MDP / POMDP** | `src/cognitive/react_loop.py` | 离散时间决策过程形式化 |
| **ReAct** | `src/cognitive/react_loop.py` | Think→Act→Observe→Reflect 闭环 |
| **Tree/Graph of Thoughts** | `src/cognitive/decomposer.py`, `src/cognitive/search.py` | 树/图搜索推理路径 |
| **Reflexion** | `src/cognitive/reflexion.py` | Critic 自我反思 + 信用分配 |
| **Multi-Agent Topology** | `src/agents/topology.py` | 图论驱动的 MAS 通信架构 |
| **RAG** | `src/memory/long_term.py` | 向量检索增强生成 |

## 2. 总体架构: 五层闭环反馈系统

```
┌─────────────────────────────────────────────────┐
│              用户界面 (CLI / API)                 │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│  Layer 1: 交互与感知层 (src/interaction/)        │
│  ┌─────────────┐  ┌──────────────────────────┐  │
│  │ NLU 解析器  │  │  响应渲染器               │  │
│  │ (意图/实体) │  │  (Markdown/JSON/Table)   │  │
│  └─────────────┘  └──────────────────────────┘  │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│  Layer 2: 认知与决策层 (src/cognitive/)          │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ BDI 状态 │ │ ReAct    │ │ 任务分解器     │  │
│  │ 机       │ │ 主循环   │ │ (CoT/ToT/GoT)  │  │
│  └──────────┘ └──────────┘ └────────────────┘  │
│  ┌──────────┐ ┌──────────┐                     │
│  │Reflexion │ │ 思维搜索 │                     │
│  │ Critic   │ │(BFS/Beam)│                     │
│  └──────────┘ └──────────┘                     │
└──────────┬──────────────────┬───────────────────┘
           │                  │
┌──────────▼──────┐  ┌───────▼────────────────────┐
│ Layer 3: 记忆层 │  │ Layer 4: 映射与转换层       │
│ (src/memory/)   │  │ (src/mapping/)             │
│ ┌────────────┐  │  │ ┌──────────┐ ┌──────────┐ │
│ │ 短期记忆   │  │  │ │ 意图路由 │ │ 序列化器 │ │
│ │ (STM)      │  │  │ │          │ │NL→Code   │ │
│ └────────────┘  │  │ └──────────┘ └──────────┘ │
│ ┌────────────┐  │  │ ┌──────────┐              │
│ │ 长期记忆   │  │  │ │ 输出校验 │              │
│ │ (ChromaDB) │  │  │ │          │              │
│ └────────────┘  │  │ └──────────┘              │
└──────────┬──────┘  └───────┬────────────────────┘
           │                  │
┌──────────▼──────────────────▼───────────────────┐
│  Layer 5: 工具与执行层 (src/execution/)          │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ 沙盒执行 │ │ 工具注册 │ │ API 客户端     │  │
│  │ 器       │ │ 中心     │ │ (PubMed等)     │  │
│  └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 3. 数据流: ReAct 闭环

对应经典的控制论反馈系统 (Cybernetic Feedback System):

```
用户输入
  │
  ▼
[Layer 1: 感知]
  NLU 解析 → Intent + Entities
  │
  ▼
[Layer 3: 记忆]
  STM 上下文 + LTM RAG 召回
  │
  ▼
[Layer 2: 认知 — Think]
  BDI 更新 → CoT 分解 → 生成计划
  │
  ▼
[Layer 4: 映射]
  意图路由 → NL→代码序列化 → 校验
  │
  ▼
[Layer 5: 执行 — Act]
  工具调用 / 沙盒执行
  │
  ▼
[Layer 5: 观察 — Observe]
  捕获 stdout / stderr / API 响应
  │
  ▼
[Layer 2: 反思 — Reflect]
  Critic 评估 → 信用分配 →
  ├─ 成功 → 输出结果 → [Layer 1: 渲染]
  └─ 失败 → 生成反馈 → [Layer 2: Think] (重新循环)
```

## 4. BDI 形式化

| BDI 组件 | 项目实现 | MDP 对应 |
|----------|----------|----------|
| **Belief (B)** | `memory/` STM+LTM 快照 + `observation_history` | 状态 S_t |
| **Desire (D)** | System Prompt + `Desire` 配置 | 目标函数 G |
| **Intention (I)** | `src/cognitive/decomposer.py` CoT 分解计划 | 策略 π |
| **信念更新** | `bdi.perceive(observation)` | B_{t+1} = update(B_t, O_t) |
| **意图修正** | `src/cognitive/bdi.revise_intention(new_plan)` | I_{t+1} = replan(I_t, B_{t+1}, D) |

## 5. MDP 形式化

在 t 时刻，Agent 的运作逻辑:

1. **策略函数**: π(A_t | O_t, M_t) → Action (LLM 决策)
2. **状态转移**: S_{t+1} = f(S_t, A_t, O_{t+1})
3. **记忆演化**: M_{t+1} = Φ(M_t, O_t, A_t)
4. **环境动力学**: O_{t+1} ~ P(O | O_t, A_t)

## 6. 多智能体拓扑

```
SOP 工作流 (默认):
  literature → acoustic → ecology → conservation → critic

对抗模式 (可选):
  generator (literature) ↔ critic
  多轮博弈 → 收敛到更优解

层级模式:
  orchestrator
    ├── literature
    ├── acoustic
    ├── ecology
    └── conservation
```

## 7. 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 架构 | 五层闭环 | 形式化 BDI + MDP + ReAct |
| 语言 | Python 3.11+ | 生态/声学工具链 |
| 模型 | DeepSeek V3 + R1 | 廉价 token + prefix-cache + 中文 |
| 任务分解 | CoT (默认) / ToT / GoT | 自适应复杂度 |
| 记忆 | STM (窗口) + LTM (ChromaDB) | 双层存储 |
| 序列化 | NL → Python/SQL/JSON | 三通道工程语言化 |
| 校验 | AST + Schema + Safety | 执行前安全检查 |
| 执行 | 子进程沙盒 | 隔离 + 超时 + 输出捕获 |
| MAS | 图拓扑 (DAG) | 有向通信 + 条件边 |
| 批判 | Critic Agent | 对抗博弈 + 质量审查 |

## 8. 安全与治理

- **沙箱执行**: 子进程隔离 + 超时 + 输出限制
- **安全检查**: AST 遍历检测危险操作
- **人工审批**: field_survey / conservation_recommendation / data_deletion
- **审计日志**: JSONL 格式记录所有决策
- **数据脱敏**: GPS 坐标自动模糊化
- **引用验证**: Critic Agent 验证文献存在性
