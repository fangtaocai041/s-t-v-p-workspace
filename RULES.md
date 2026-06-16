# RULES · 工作区规则手册

> 本文档是所有工程规则的**单一真相源**。每条规则都有对应的可执行检查脚本。

---

## 📋 规则索引

| # | 规则 | 检查脚本 | 类型 |
|:-:|:-----|:---------|:----:|
| 1 | 功能脚本化原则 | `scripts/check_feature_scripts.py` | 硬约束 |
| 2 | 操作前必须备份 | `scripts/backup.py` | 硬约束 |
| 3 | Git 提交纪律 | `scripts/check_git_discipline.py` | 硬约束 |
| 4 | Git 工作流（子项目+主空间同步） | `scripts/check_git_discipline.py` | 硬约束 |
| 5 | 日期准确性 | `scripts/check_dates.py` | 硬约束 |
| 6 | 交互设计原则 | `RULES.md`（本文） | 行为约束 |
| 7 | 文献搜索交互流程 | `fish-ecology-assistant/src/orchestrator.py` | 协议约束 |
| 8 | 文献检索工作流 | `fish-ecology-assistant/src/orchestrator.py` | 协议约束 |
| 9 | Identity: eon-workspace 统一入口 | `RULES.md`（本文） | 身份约束 |
| 10 | Reasonix 交互设计原则 | `RULES.md`（本文） | 行为约束 |

---

## 规则正文

### 规则 1 — 功能脚本化原则

**约束**: 硬约束 · 违反即禁止合并

所有 `.md` 文档中描述的功能、规则、流程，必须有对应的 `.py` 可执行脚本实现。

- ❌ 不允许在 `.md` 中描述一个功能却没有任何 `.py` 文件实现它
- 每个 `§章节` 描述的算法/流程，必须有对应的调用入口
- 每个脚本应能独立运行或导入

**检查命令**: `python scripts/check_feature_scripts.py`

**Why**: 纯文档描述的功能是"幽灵功能"——看起来存在但实际上没有实现。脚本化确保每个声明的能力都真实可用。

---

### 规则 2 — 操作前必须备份

**约束**: 硬约束 · 违反即禁止操作

在执行以下操作之前，必须先用 `scripts/backup.py` 创建备份：
1. 删除 `.git` 目录
2. 执行 `git reset --hard` / `git push --force`
3. 删除或移动项目目录
4. 修改 MCP 配置文件

**备份命令**: `python scripts/backup.py --all`

**Why**: 2026-06-16 软件崩溃导致 141 文件丢失 + config 加密。未备份情况下删除 `.git` 导致独立仓库历史永久丢失。

---

### 规则 3 — Git 提交纪律

**约束**: 硬约束 · 违反导致脏工作树风险

每次代码修改完成后，必须立即将变更保存至 Git（commit + push 到 GitHub），或至少 `git stash` 暂存。严禁让未提交的变更长期停留在工作树中。

**检查命令**: `python scripts/check_git_discipline.py`

**Why**: 2026-06-16 软件崩溃导致 `.git/objects/` 大量对象损坏、工作树 141 个文件被删除。依靠 GitHub remote 才恢复了全部数据。

---

### 规则 4 — Git 工作流（子项目 + 主空间同步）

**约束**: 硬约束 · 违反导致子项目与主空间不一致

```
1. 子项目提交:
   git -C <subproject> add -A
   git -C <subproject> commit -m "描述"
   git -C <subproject> push origin master

2. 主空间提交（必须同步）:
   git add -A
   git commit -m "描述"
   git push origin master
```

- 禁止 `git push --force` 到 main/master 分支
- 禁止在没有备份的情况下删除 `.git` 目录
- 子项目 `.git` 配置: `user.email=fangtaocai041@gmail.com, user.name=fangtaocai041`

**检查命令**: `python scripts/check_git_discipline.py`

---

### 规则 5 — 日期准确性

**约束**: 硬约束 · 违反导致时间戳错误

README 中的"最后更新"日期和变更记录日期必须使用**实际当天日期**，不得照搬版本历史中标注的未来/计划日期。

```python
# 每次更新 README 前:
from datetime import datetime, timezone
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
# "最后更新" = today, NOT from CHANGELOG version plan
```

**检查命令**: `python scripts/check_dates.py`

**Why**: v6.5.0 的 `2026-06-20` 是版本规划中的目标日期，并非实际发生日期。

---

### 规则 6 — 交互设计原则

**约束**: 行为约束 · AI agent 级别

在 Reasonix 环境中，任何自动化流程都应优先考虑用户交互，而不是悄悄代劳。**能交互处不自动**。

三个必须交互的节点：
1. **模式选择** — 自动决策后必须用 `ask_choice` 问用户是否调整
2. **写回确认** — 任何数据持久化操作前必须询问
3. **信息展开** — 仅输出摘要，用户选类再展开详情

6 项上限突破法：`ask_choice` 最多 6 个选项，超过时用两级分层。

---

### 规则 7 — 文献搜索交互流程

**约束**: 协议约束 · 搜索 Skill 级别

```
用户搜索请求
  → Step 1: 查 f 项目知识库（汇报已有信息 + 文献数 + 知识缺口）
  → Step 2: ask_choice 两级菜单（穷举/快速/c项目/档案/近缘种）
  → Step 3: 执行搜索 → 展示摘要统计（不预载详情）
  → Step 4: ask_choice 展开（按置信度/方向/中文/全部/跳过）
  → Step 5: 写回确认（写入知识库前必须问）
  → Step 6: 实际执行写入
```

---

### 规则 8 — 文献检索工作流

**约束**: 协议约束 · 搜索 Skill 级别

```
三步工作流:
  1. 查 f 项目知识库（fish-ecology-assistant/）
  2. 询问用户是否需要全量检索（ask_choice）
  3. 全量检索 + 回写 f 项目
```

**Why**: 避免重复检索已知文献，在用户知情决策后再执行昂贵全量检索，结果沉淀回知识库避免重复工作。

---

### 规则 9 — Identity: eon-workspace 统一入口

**约束**: 身份约束 · Reasonix Code 级别

Reasonix Code 是 eon-workspace 的统一入口，不是某个子项目的专属 Agent。

```
架构:
  Reasonix Code (统一入口)
  ├── eon-core/           → 协调内核, EventBus, DAG路由
  ├── cognitive-search-engine/  → 20引擎搜索, 图谱, 冲突仲裁
  ├── fish-ecology-assistant/   → 物种知识库, 文献管理
  ├── porpoise-agent/     → P₁: 江豚种群监测, 威胁评估
  ├── coilia-agent/       → P₂: 刀鲚耳石微化学, 洄游生态
  └── culter-agent/       → P₃: 鲌类基因组, 营养生态位
```

---

### 规则 10 — Reasonix 交互设计原则

**约束**: 行为约束 · AI agent 级别

与规则 6 配套，增加：
- 三步触发法：任何自动化流程在模式选择/数据写回/信息展开三个节点 MUST 暂停询问用户
- 摘要与选项一致性：执行摘要中的每个计数类别必须在展开选项中都有对应的入口
- 默认不预载：搜索结果是只读的结构化数据 → 仅展示摘要 → 用户选类后才展开

---

## 🛠️ 快速检查

```bash
# 一键执行全部规则检查
python scripts/enforce_rules.py

# 仅快速检查（跳过大文件扫描）
python scripts/enforce_rules.py --quick

# CI 友好 JSON 输出
python scripts/enforce_rules.py --json

# 备份
python scripts/backup.py --all
```
