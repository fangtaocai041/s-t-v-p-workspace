# fish-ecology-assistant Skill 管线逻辑分类索引

> 28 个 Reasonix Skill (markdown)，按 5 阶段管线分组

## 管线总览

```
用户问题
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│  research-orchestrator (主调度器)                               │
│  5阶段: Plan → Search → Analyze → Write → Review (最多3轮修订) │
└─────────────────────────────────────────────────────────────────┘
  │
  ├── Phase 1: PLAN (规划)
  │   └── research-planner     — 任务分解 + 研究设计
  │
  ├── Phase 2: SEARCH (搜索) — 8个搜索类skill
  │   ├── academic-species-search   — PubMed E-utilities 直接搜索
  │   ├── unified-species-search    — NCBI + 引用回溯 + 中文回溯
  │   ├── cognitive-species-search  — DirectLoader → cognitive引擎
  │   ├── fuzzy-species-search      — OCR变体模糊搜索
  │   ├── google-scholar-search     — Google Scholar 关键词搜索
  │   ├── ima-smart-search          — IMA 智能搜索
  │   └── research-executor         — 综合执行 (web_search/tavily/scholar)
  │
  ├── Phase 3: ANALYZE (分析) — 7个分析类skill
  │   ├── research-analyst      — 综合分析 + 假设生成
  │   ├── paper-analyzer        — 单篇论文深度分析
  │   ├── stats-assistant       — R 统计分析 + 可视化
  │   ├── stats-method-finder   — 统计方法查找
  │   ├── debate-validator      — 辩论验证 (对立观点)
  │   ├── graph-search-engine   — 知识图谱遍历
  │   └── frontier-tracker      — 前沿追踪
  │
  ├── Phase 4: WRITE (写作) — 3个写作类skill
  │   ├── research-writer          — 研究报告生成
  │   ├── phd-proposal-writer      — 博士论文计划书
  │   └── obsidian-assistant       — Obsidian 笔记导出
  │
  ├── Phase 5: REVIEW (审查) — 6个审查类skill
  │   ├── research-reviewer     — 研究审查 (最多3轮)
  │   ├── rule-auditor          — 规则合规审计
  │   ├── verify-stats-handbook — 统计方法手册验证
  │   ├── component-health-check— 组件健康巡检
  │   └── living-system-dashboard— 活系统仪表盘
  │
  └── 横切类 (Cross-cutting) — 4个
      ├── karpathy-guard        — Karpathy 行为准则
      ├── cross-delegate        — 跨项目委托
      ├── meso-orchestrator     — meso-cosmos 协调
      └── self-evolve           — 自进化触发器
```

## 分类统计

| 类别 | 数量 | Skills |
|------|:----:|--------|
| 搜索 | 8 | academic-species, unified-species, cognitive-species, fuzzy-species, google-scholar, ima-smart, research-executor, zotero |
| 分析 | 7 | research-analyst, paper-analyzer, stats-assistant, stats-method-finder, debate-validator, graph-search-engine, frontier-tracker |
| 写作 | 3 | research-writer, phd-proposal-writer, obsidian-assistant |
| 审查 | 5 | research-reviewer, rule-auditor, verify-stats-handbook, component-health-check, living-system-dashboard |
| 调度 | 1 | research-orchestrator |
| 规划 | 1 | research-planner |
| 横切 | 4 | karpathy-guard, cross-delegate, meso-orchestrator, self-evolve |

## 调用路径

```
Python 入口:
  fish-ecology-assistant/src/orchestrator.py → delegate_search()
    └── 生成 DELEGATE 协议消息
        └── Reasonix runtime 调度 research-orchestrator skill
            ├── Phase 1: research-planner
            ├── Phase 2: research-executor (→ academic-species-search / unified-species-search)
            ├── Phase 3: research-analyst (→ stats-assistant / debate-validator)
            ├── Phase 4: research-writer (→ phd-proposal-writer)
            └── Phase 5: research-reviewer (最多3轮修订)

跨项目调用:
  project_loader.get_fish().search("species")
    └── FishEcologyAdapter.search()
        └── FishEcologyOrchestrator.delegate_search()
            └── 返回 DELEGATE 协议消息
```

## Python ↔ Skill 桥接

| Python 层 | Skill 层 |
|-----------|---------|
| `src/orchestrator.py` | `research-orchestrator.md` (主调度) |
| `src/adapter.py` | 对外暴露 IProjectAdapter 接口 |
| `config/agent.yaml` | 全局配置 + 管线参数 |
| `config/yangtze_fish_species.yaml` | 长江鱼类物种知识库 |
| `scripts/project_loader.py` | 统一 DirectLoader 入口 |
