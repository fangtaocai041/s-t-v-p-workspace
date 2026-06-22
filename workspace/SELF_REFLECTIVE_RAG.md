# Self-Reflective RAG (自反射检索增强生成)

> 设计时间: 2026-06-22 02:10
> 借鉴: Self-Reflective RAG + Agentic RAG patterns

## 流程

```
Query 输入
   │
   ▼
┌──────────────────┐
│ 1. Retrieve      │  ← c项目 6 MCP 引擎实时检索
│    (多源并行)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 2. Verify        │  ← credibility_scorer (Step 8)
│    (可信度评分)   │      交叉引用验证
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ 3. Reflect       │  ← Self-Reflection:
│    (自反射)       │     结果是否可靠?
│                  │     是否遗漏关键文献?
│                  │     是否有更好的搜索词?
└──────┬───────────┘
       │
       ├── low confidence (<40) ──→ Re-query with expanded terms
       ├── medium (40-70)       ──→ Cross-reference with KG-RAG
       ├── high (>70)           ──→ Output directly
       │
       ▼
┌──────────────────┐
│ 4. Augment       │  ← Knowledge Graph 联想
│    (图谱增强)     │     同科/同域物种文献
│                  │     分类学变体搜索
└──────┬───────────┘
       │
       ▼
    Final Output (with confidence + graph context)
```

## 自反射规则

| 置信度 | 动作 | 说明 |
|--------|------|------|
| <40 | 重新搜索 (扩展词) | 原搜索词可能不精准 |
| 40-70 | KG-RAG 增强 | 加入同科/同域物种文献 |
| >70 | 直接输出 | 可信度足够 |

## Multi-Agent 协调协议 (CrewAI 模式)

借鉴 CrewAI 的 role-based agent 协作:

```
Orchestrator (workspace)
   ├── Searcher (cognitive)         Role: 文献检索
   ├── KnowledgeBase (fish)         Role: 知识库查询
   ├── Arbiter (conflict)           Role: 冲突裁决
   ├── Specialist (coilia/p/culter) Role: 物种专精
   └── Verifier (credibility_scorer) Role: 质量把关

Message Protocol:
  Orchestrator → Searcher:  search_request{species, group, limit}
  Orchestrator → KnowledgeBase: kb_query{name, mode}
  Searcher → Verifier:  raw_results
  Verifier → Orchestrator:  verified_results + confidence_scores
  Orchestrator → Arbiter (auto):  multi_source_conflict
```
