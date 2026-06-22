# Multi-Agent 协调协议 (v1.0)

> 设计时间: 2026-06-22 02:10
> 借鉴: CrewAI (role-based), AutoGen (dynamic negotiation), LangGraph (stateful workflows)

## Agent 角色定义

| Agent | Role | Tools | Trigger |
|-------|------|-------|---------|
| orchestrator | 任务协调 | health_check, routing | 所有请求入口 |
| searcher | 文献检索 | 6 MCP engines, credibility_scorer | search/lookup 请求 |
| knowledgebase | 知识库查询 | species.db, fish_species_kb.yaml | 中文名/物种信息查询 |
| arbiter | 冲突裁决 | conflict_arbiter.search() | 保护源>=2 自动触发 |
| specialist_coilia | 刀鲚专精 | coilia_agent.search() | Coilia 相关 |
| specialist_porpoise | 江豚专精 | porpoise_agent.search() | Neophocaena 相关 |
| verifier | 质量把关 | credibility_scorer | 所有搜索后自动 |
| kg_retriever | 知识图谱 | 457-species graph | 查询时自动联想 |

## 工作流定义 (LangGraph 风格)

### WF_A: 全栈物种研究
```
START → knowledgebase.lookup → searcher.search → verifier.verify → END
                 │                        │
                 └──(if 保护源>=2)→ arbiter.arbitrate
```

### WF_B: 快速搜索
```
START → searcher.search → verifier.verify → END
```

### WF_C: 深度分析 (专精物种)
```
START → knowledgebase.lookup → specialist.search → searcher.search → kg_retriever.enhance → verifier.verify → END
```

## 状态传递 (Typed Agent State)

```python
@dataclass
class AgentState:
    query: str
    species: str
    mode: str
    confidence: int           # 0-100
    graph_context: list       # KG-RAG 联想结果
    raw_results: list         # MCP 结果
    verified_results: list    # 经验证的结果
    auto_triggered: dict      # 自动触发的 agent 和结果
```
