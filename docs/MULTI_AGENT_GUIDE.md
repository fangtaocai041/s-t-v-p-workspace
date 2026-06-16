# Reasonix 多智能体分工协作指南

> 你的 eon-workspace 已经是一个完整的 5 角色多智能体系统 — 不需要 Cherry Studio 的 workaround。

---

## 一、你的项目就是多智能体团队

Cherry Studio 文档推荐 5 角色分工模型。你的 Reasonix 工作区**已经用 7 个项目 + 19 个 MCP 服务器 + 27 个 Skill 完整实现了这个架构**：

| 角色 | Cherry Studio 做法 | **Reasonix 已有实现** |
|------|-------------------|----------------------|
| 🧑‍💼 Planner | 写一个 .md  Skill 文件 | `eon-core` DAG 路由 + `research-planner` Skill |
| 🔍 Researcher | Tavily + 学术搜索 MCP | `cognitive-search-engine` — 19 个 MCP 引擎（scholar/article/ncbi/tavily/scholarly/exa/web_search） |
| 📊 Analyst | 写一个分析 Skill | `research-analyst` Skill + `credibility_scorer.py` + `self_evolve.py` |
| ✍️ Writer | 写一个写作 Skill | `research-writer` Skill + `report_formatter.py` |
| ✅ Reviewer | 写一个审核 Skill | `research-reviewer` Skill + `verify_architecture.py` + 全部 `scripts/check_*.py` |

---

## 二、Reasonix 的三层协作架构（比 Cherry Studio 更强）

### 第 1 层：Skill 流水线（Pipeline）

```
research-planner → research-executor → research-analyst → research-writer → research-reviewer
       ↑                                                                          │
       └────────────────────── 需修改时自动循环 ──────────────────────────────────┘
```

配置在 `fish-ecology-assistant/config/agent.yaml` 的 `pipeline.stages` 里，无需写代码。

### 第 2 层：eon-core DAG 路由（Hierarchical）

```
                    ┌── porpoise-agent (P₁ 江豚)
eon-core ───────────┼── coilia-agent   (P₂ 刀鲚)
  (协调内核)        ├── culter-agent   (P₃ 鲌类)
                    ├── fish-ecology   (S 知识)
                    ├── cognitive      (V 搜索)
                    └── conflict       (C 仲裁)
```

配置在 `eon-core/config/taiji.yaml` 的 `tetrahedron.edges` 里。

### 第 3 层：MCP 并行搜索（19 引擎）

```python
# cognitive-search-engine/src/unified_search.py
ENGINE_GROUPS = {
    "quick":    ["scholar_graph", "ncbi_esearch", "web_search"],
    "standard": ["scholar_graph", "ncbi_esearch", "crossref_article", "web_search", "tavily_search"],
    "full":     ["scholar_graph", "ncbi_esearch", "...", "exa_search", "web_search"],
    "chinese":  ["scholar_graph", "ncbi_esearch", "web_search"],
}
```

---

## 三、Cherry Studio 对比 → 你不需要它的原因

| Cherry Studio 做法 | 问题 | Reasonix 怎么做 |
|-------------------|------|----------------|
| 写 `.claude/skills/skill_*.md` 手动创建角色 | 每个 Skill 要手写，没有代码实现 | Skill 是 `.reasonix/skills/` 下的 `.md` 文件 + 对应 `.py` 脚本，**功能脚本化原则**保证不是纯文档 |
| 配置 MCP 服务器（Tavily、Filesystem、ECharts） | 要手动一个一个在 UI 里配 | 你有 **19 个 MCP 服务器**已配置在 `C:\Users\小陶\.reasonix\config.json`，开箱即用 |
| 单 Agent + 多 Skill 流水线 | 同进程串行，无法并行 | `search_streaming()` 7 引擎并行 + `run_skill` 子 agent 隔离执行 |
| "工作目录切换法" 模拟多 Agent | 手动切目录，数据靠文件传递 | `project_hub.delegate_to()` 直接跨项目调用，零文件传递 |

---

## 四、你的实际工作流（以"刀鲚洄游综述"为例）

```
你: "搜一下刀鲚洄游生态的最新文献，写综述"

Step 1: KB-First 查本地
  └── fish-ecology-assistant/orchestrator.kb_first_lookup("刀鲚")
      输出: "已有15篇文献, 知识缺口: 2024年后禁捕恢复数据"

Step 2: 全量搜索（cognitive-search-engine 7引擎并行）
  └── scholar → "Coilia nasus migration" → 12篇
  └── ncbi    → "Coilia nasus otolith"  → 8篇
  └── article → "刀鲚 洄游 耳石"          → 6篇
  └── tavily  → 最新的禁捕恢复新闻       → 3篇
  └── 去重合并 → 23篇唯一文献

Step 3: 分析评分（research-analyst）
  └── credibility_scorer.py → 每篇 0-100 可信度
  └── self_evolve.py       → 根据反馈调整参数
  └── 输出: 高可信度14篇 / 中6篇 / 低3篇

Step 4: 撰写综述（research-writer）
  └── 结构化输出: 摘要→引言→耳石微化学→洄游路线→禁捕恢复→展望

Step 5: 审核迭代（research-reviewer）
  └── 检查引用完整性 → 发现缺少杨健2024 → 反馈回Step2补充
  └── 最终通过 → 写回 f项目知识库
```

---

## 五、Cherry Studio 文档映射到 Reasonix 命令

| Cherry Studio 操作 | Reasonix 等价命令 |
|-------------------|------------------|
| 创建 Agent + Skill | `run_skill("lit-search", "刀鲚洄游")` |
| 配置 MCP Tavily | 已配置 ✅ `tavily=npx -y tavily-mcp@latest` |
| 配置学术搜索 | 已配置 ✅ `scholar` / `article` / `ncbi` / `scholarly` 四组 |
| 流水线执行 | `python fish-ecology-assistant/scripts/run_lit_search.py "刀鲚"` |
| 技术路线图 | `echarts_generate_graph_chart` MCP + `research-writer` Skill |

---

## 六、Reasonix 独有的能力（Cherry Studio 做不到的）

| 能力 | 说明 |
|------|------|
| **KB-First 两阶段搜索** | 先查本地 26 物种知识库（零 token），不够再启动 7 引擎并行搜索 |
| **三角验证评分** | 期刊等级 × 作者 h-index × 时效性 → 0-100 可信度 |
| **跨项目委托** | `hub.delegate_to("cognitive", query)` — 一个函数调用跨项目 |
| **子 agent 隔离执行** | `run_skill(name, arguments)` — 子 agent 拥有独立上下文，结果蒸馏后返回 |
| **知识图谱进化** | `kb_to_graph_sync.py` — 文献写回图谱，跨项目共享 |
| **自进化反馈** | `self_evolve.py` — 根据搜索质量自动调整参数 |
| **19 MCP 服务器** | 比 Cherry Studio 手动配的多 4 倍，且开箱即用 |
| **规则强制执行** | `python scripts/enforce_rules.py` — 10 条规则自动检查 |

---

## 七、快速开始

```bash
# 1. 查物种知识库
python -c "from src import get_orchestrator; o=get_orchestrator(); print(o.kb_first_lookup('刀鲚').summary_text)"

# 2. 全量文献搜索
python fish-ecology-assistant/scripts/run_lit_search.py "刀鲚"

# 3. 可信度评分
python fish-ecology-assistant/scripts/credibility_scorer.py

# 4. 知识库同步
python fish-ecology-assistant/scripts/kb_to_graph_sync.py

# 5. 规则检查
python scripts/enforce_rules.py
```

---

## 八、核心原则

1. **不造轮子** — 你已经有 7 个项目 + 27 个 Skill + 19 个 MCP。Cherry Studio 文档描述的是你**三周前就已经实现完成**的东西
2. **功能脚本化** — 每个 `.md` 描述的能力有对应 `.py`，拒绝"纯文档功能"
3. **能交互处不自动** — 搜索结果不预载详情，两级菜单让用户选择展开
4. **KB-First** — 先查本地知识库，不花 token；不够再走全量搜索
