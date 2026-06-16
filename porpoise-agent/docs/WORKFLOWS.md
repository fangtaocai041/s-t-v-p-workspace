# 🔄 工作流设计 v2.0

> 基于五层架构 + BDI + ReAct + MAS 的工作流

## 1. 核心执行循环: ReAct

```
┌──────────────────────────────────────────────────────┐
│                  ReAct 闭环反馈                       │
│                                                      │
│  ┌─────────┐    ┌─────────┐    ┌──────────┐         │
│  │  THINK  │───→│   ACT   │───→│ OBSERVE  │         │
│  │ (BDI)   │    │ (执行)  │    │ (捕获)   │         │
│  └─────────┘    └─────────┘    └────┬─────┘         │
│       ↑                             │               │
│       │         ┌──────────┐        │               │
│       └─────────│ REFLECT  │←───────┘               │
│                 │ (Critic) │                         │
│                 └────┬─────┘                         │
│                      │                               │
│               ┌──────┴──────┐                        │
│               ↓              ↓                       │
│           成功→输出      失败→修正→THINK              │
└──────────────────────────────────────────────────────┘
```

### 伪代码

```python
def react_loop(query: str, max_steps: int = 50):
    bdi = BDI(goal=query)
    memory = recall(query)  # STM + LTM RAG

    for step in range(max_steps):
        # THINK: BDI 更新 + CoT 分解
        thought = think(bdi, memory)

        if is_done(thought):
            break

        # ACT: 映射 + 执行
        action = parse_action(thought)
        tool_call = serialize_to_json(action)  # Layer 4
        observation = execute(tool_call)       # Layer 5

        # OBSERVE: 更新 BDI Belief
        bdi.perceive(observation)

        # REFLECT: Critic 评估
        reflection = critic.evaluate(step, action, observation)
        if reflection.severity == CRITICAL:
            bdi.revise_intention(reflection.suggestion)
            continue

        # 持久化
        memory.memorize_step(observation, action, reflection)

    return compile_result()
```

## 2. BDI 状态演化

```
           ┌──────────────┐
           │   DESIRE     │  持久目标
           │ "完成文献综" │  (System Prompt)
           │  述"         │
           └──────┬───────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐
│ BELIEF │  │INTENTION │  │ EXECUTE  │
│ 当前认 │  │ CoT 计划 │  │ 执行步骤 │
│ 知     │  │          │  │          │
└───┬────┘  └────┬─────┘  └────┬─────┘
    │            │             │
    │  观察更新  │  计划修正   │  结果反馈
    └────────────┴─────────────┘
```

## 3. 任务分解策略

| 策略 | 复杂度 | 适用场景 | 算法 |
|------|--------|----------|------|
| **CoT** (默认) | O(n) | 线性任务 (文献搜索) | 顺序分解 |
| **ToT** | O(b^d) | 多路径推理 (假设检验) | BFS/Beam/MCTS |
| **GoT** | O(n²) | 多分支协同 (跨学科分析) | DAG + 合并 |

### 自适应选择

```
IF task_complexity == "simple" THEN CoT
ELIF task_uncertainty > 0.5 THEN ToT(BFS, beam_width=3)
ELIF task_cross_domain THEN GoT(enable_merge=True)
```

## 4. Reflexion 反思流程

```
Step 失败
  │
  ▼
Critic 评估
  ├── 错误分类: timeout / syntax / permission / not_found
  ├── 根因分析: 信用分配 → 定位失败节点
  └── 生成建议: verbal_feedback
      │
      ▼
  注入下一次 THINK 上下文
      │
      ▼
  LLM 基于反馈生成修正计划
      │
      ▼
  重试 (最多 3 次)
```

## 5. MAS 工作流拓扑

### SOP 模式 (默认)

```
orchestrator
  │
  ├─→ literature ─→ acoustic ─→ ecology ─→ conservation
  │                                                    │
  └────────────────────────────────────────────────────┘
                                                    │
                                                  critic (可选)
```

### 对抗模式 (辩论)

```
generator (literature) ←→ critic
    │        多轮         │
    └────── 博弈 ────────┘
              │
         收敛到更优解
```

### 动态路由 (实验性)

```
orchestrator → NLU → Intent → LLM 决策下一跳
  │
  ├─ 关键词 "搜索" → literature
  ├─ 关键词 "分析" → acoustic
  ├─ 关键词 "保护" → conservation
  └─ 不确定 → literature (fallback)
```

## 6. 人工审批节点

| 节点 | 触发 | 审批内容 |
|------|------|----------|
| 野外方案 | `field_survey_plan` | 调查路线、设备部署、安全 |
| 保护建议 | `conservation_recommendation` | 可行性、政策对齐 |
| 数据删除 | 任何删除操作 | 二次确认 |
| 外部写入 | API POST/PUT/DELETE | 确认目标 URL |
| 代码执行 | 危险 AST 节点 | 审查代码逻辑 |

## 7. 记忆演化

```
短期记忆 (STM):
  ┌─────────────────────────────────────┐
  │ [sys] [user] [asst] [tool] [user]...│
  │        滑动窗口 (8000 tokens)       │
  │  超过 80% → 压缩旧条目为摘要        │
  └──────────────┬──────────────────────┘
                 │ 高优先级冲入
                 ▼
长期记忆 (LTM):
  ┌─────────────────────────────────────┐
  │ ChromaDB:                            │
  │  literature / observations / notes   │
  │  reports / execution_log             │
  │                                      │
  │ 查询: 余弦相似度 → top_k → RAG      │
  └─────────────────────────────────────┘
```

记忆演化函数: `M_{t+1} = Φ(M_t, O_t, A_t)`
