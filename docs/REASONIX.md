# 项目基础信息（不可变层——整个会话永不变）

## 项目概述
- 项目名称：三生万物·鱼类生态智能体体系（SanShengWanWu Fish Ecology Agent Ecosystem）
- 项目类型：多 Agent 协作系统 + 知识工程平台
- 主要技术栈：Python 3.11+ · FastAPI · SQLite FTS5 · ChromaDB · NetworkX · PyTorch (可选)
- 包管理器：pip (pyproject.toml)
- 运行环境：D:\Reasonix (Windows) · Reasonix IDE (DeepSeek v4 flash/pro 驱动)

## 项目目标
构建一套模块化的 AI Agent 系统，为淡水鱼类生态学研究提供知识供给、文献搜索验证、领域专研分析和跨源冲突仲裁能力。系统服务于长江流域旗舰物种（江豚、刀鲚、鲌类等）的科研工作者和保护区管理者。

## 核心架构

```
三角核心 (sealed_set):   fish-ecology-assistant (知识供给 S/V0) + cognitive-search-engine (搜索验证 V/V1) + eon-core (协调中枢 Coord)
衍生项目 (open_set):     porpoise-agent (P₁ 江豚) · coilia-agent (P₂ 刀鲚) · culter-agent (P₃ 鲌类)
横切服务:                conflict-arbiter (冲突仲裁) · infrastructure (涌现引擎/NLP/视觉)
统一入口:                workspace (from workspace import search_species, lookup_species, health_check)
元项目:                  san-sheng-wanwu-core (17皮层·18感知·4运动)
```

## 关键依赖
- Python >= 3.11
- PyYAML (所有项目配置)
- NetworkX (eon-core 图论, theory_graph_engine)
- ChromaDB (porpoise-agent 向量记忆)
- SQLite FTS5 (fish-ecology-assistant 物种知识库)
- DeepSeek API (reasonix.toml provider: deepseek-flash/pro)
- MCP 工具: Zotero · CNKI · PaddleOCR · GBIF · FishBase · PubMed · GitHub · Tavily · Playwright

## 文件组织规范
- `src/` — 源代码，每个项目独立
- `tests/` — 测试代码
- `docs/` — 项目文档
- `config/` — YAML 配置文件
- `scripts/` — 共享脚本 (adapter_protocol.py + project_loader.py)
- 项目间 import 使用 DirectLoader (sys.path 隔离 + sys.modules 恢复)
- 任何项目可 import infrastructure (涌现引擎) 和 eon-core/src/shared/ (RCCA 核心)

## 编码规范
- 语言版本：Python 3.11+
- 代码风格：标注类型 (from __future__ import annotations) · dataclass 优先
- 命名约定：PascalCase 类名 · snake_case 函数/变量 · UPPER_CASE 常量
- 空白：4 空格缩进 · 120 字符行宽
- 所有公开函数必须带 docstring (Google Style)
- 导入顺序：builtin → third-party → project (分组间空行)

## 硬性约束
- [ ] 不要修改 `tests/` 下的任何测试用例（除非修复已知 bug）
- [ ] 不要修改 `coordination.yaml` / `taiji.yaml` （拓扑变更需明确审批）
- [ ] 不要在多个项目中复制 RCCA 核心代码（使用 SHIM 转发）
- [ ] 不要在衍生项目中直接调用其他衍生项目（必须通过三角或冲突仲裁）
- [ ] 新增 MCP 工具必须注册到 reasonix.toml
- [ ] 所有 API Key 通过环境变量注入（不要硬编码）

## 测试要求
- 单元测试框架：pytest
- 测试命令：`pytest tests/ -v`
- 覆盖率目标：≥ 80%
- porpoise-agent: 185/185 · coilia-agent: 144/144 · infrastructure: 57/57

## 项目特定术语表
| 术语 | 含义 |
|------|------|
| 三角核心 (Triangle Core) | fish + cognitive + eon-core — 最小稳定集 |
| 衍生项目 (Pn) | porpoise(P₁) / coilia(P₂) / culter(P₃) — 领域专精 |
| 涌现引擎 (Emergence Engine) | infrastructure/unified_emergence.py — 跨层模式检测 |
| RCCA | Recursive Convergence Cognitive Architecture — 递归收敛认知架构 |
| MCP | Model Context Protocol — 外部工具协议 |
| DirectLoader | eon-core/scripts/project_loader.py — 安全的项目间导入机制 |
| SHIM | Python 透明转发模块 (importlib 重定向) |
| S/V 三角 | Supply (知识供给) + Verification (搜索验证) |
| D₀~D₃ | 涌现维度 (Point→Line→Plane→Body) |
| Taiji | 太极 DAG 拓扑引擎 (taiji.yaml) |

## 常见决策记录
- ADR-001: 为什么用 DirectLoader 而非 pip install — 7 项目共享同一 Python 环境，独立开发/部署
- ADR-002: 为什么涌现引擎在 infrastructure 而非 eon-core — 与 NLP/视觉共同组成共享工具层
- ADR-003: 为什么三角封闭、衍生开放 — 保证核心稳定性，允许领域无限扩展
