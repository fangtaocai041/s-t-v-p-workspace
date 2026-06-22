# Reasonix 标准化 API 接口 (ChatGPT Function Calling + DeepSeek MoE)

> 设计时间: 2026-06-22 02:04

## 6 个 Expert 的标准化接口

| Expert | Function | Input | Output | Auto-triggers |
|--------|---------|-------|--------|---------------|
| cognitive | search_literature | species_name, group, limit | SearchResult | credibility_scorer |
| fish | lookup_species | name, mode | dict + conflict_verdict | conflict if sources>=2 |
| porpoise | assess_conservation | species, context | dict | — |
| coilia | assess_species | species, context | dict | — |
| culter | assess_species | species, context | dict | — |
| conflict | resolve_conflict | species_name, sources, region | conflict_verdict | — |

## 借鉴模式总结

| AI 模型 | 模式 | Reasonix 应用 |
|---------|------|-------------|
| DeepSeek MoE | Router + Expert activation | workspace 按需激活项目 |
| DeepSeek MoE | Shared expert isolation | rcca_core/shared_types 建议集中 |
| ChatGPT | Function Calling typed API | 每项目标准接口 schema |
| ChatGPT | Structured Output | 统一返回 SearchResult/dict |
| Gemini | Long context (1M window) | 跨项目统一知识视图 |
| Codex | Iterative self-improvement | 自问自答自检模式 |

## 共享代码 (Shared Expert)

```
D:/Reasonix/scripts/
  rcca_core.py          ← 规范副本 (14 copies -> keep 1)
  shared_types.py       ← 规范副本
  coordination_test.py  ← 协调测试
```

当前: rcca_core.py x14 副本, shared_types.py x14 副本
建议: 新项目从 scripts/ 导入, 不再复制
