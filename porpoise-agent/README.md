<p align="center">
  🇬🇧 <a href="README_en.md">English</a>
</p>

<div align="center">
  <h1>🐬 Porpoise Agent</h1>
  <p><strong>江豚研究智能体框架</strong> — 多智能体协作 · BDI 决策 · 五层认知架构 · 外部系统集成</p>
  <p>Python 3.11+ · 7 Agent · 5 Cognitive Layers · 4 Integrations</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/version-2.1.0-8b5cf6?style=flat-square" alt="v2.1.0"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.11+-3776AB?style=flat-square" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/agents-7-f59e0b?style=flat-square" alt="7 Agents"></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-4_suites-22c55e?style=flat-square" alt="Tests"></a>
</p>

---

## 目录

- [项目简介](#项目简介)
- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [CLI 命令](#cli-命令)
- [API 参考](#api-参考)
- [项目架构](#项目架构)
- [外部集成](#外部集成)
- [配置文件](#配置文件)
- [关联项目](#关联项目)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

**Porpoise Agent** 是针对长江江豚 (*Neophocaena asiaeorientalis asiaeorientalis*) 研究的 AI Agent 框架，采用**多智能体系统 (MAS)** + **BDI 认知架构** 实现自动化的文献检索、声学分析、生态建模、保护评估等科研流程。

### 核心能力

| 能力 | 说明 |
|------|------|
| 🧠 **多智能体协作** | 7 个专用 Agent 分工协作：文献、声学、生态、保护、评审、编排 |
| 🔍 **BDI 认知决策** | Belief-Desire-Intention 状态机驱动推理与行动 |
| 📚 **三层记忆系统** | 短期记忆 (上下文) + 长期记忆 (ChromaDB 向量存储/RAG) |
| 🔌 **四重外部集成** | cognitive-search-engine 搜索、Neo4j 图谱、Zotero 文献库、Obsidian 笔记 |
| 🛡️ **沙箱执行** | 隔离 Python 运行时，安全执行用户代码 |
| 🧪 **测试覆盖** | BDI 状态机 + 记忆 + 序列化 + 7 场景工作流 + 鲁棒性压力测试 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/FFRC-LiuKai-Lab/porpoise-agent.git
cd porpoise-agent
pip install -e .
```

### 验证安装

```python
from porpoise_agent.src.agents import OrchestratorAgent

orchestrator = OrchestratorAgent()
print(f"Agents registered: {len(orchestrator.list_agents())}")
# 输出: Agents registered: 0
```

### CLI 基本用法

```bash
# 健康检查
porpoise doctor

# 查看当前 MAS 拓扑
porpoise topology

# 交互式对话模式
porpoise chat

# 执行单次研究任务
porpoise run "分析长江江豚声学数据"
```

---

## 核心功能

### 1. 多智能体系统 (MAS)

7 个专用 Agent 协作完成任务：

```python
from porpoise_agent.src.agents import (
    OrchestratorAgent,
    LiteratureAgent,
    AcousticAgent,
    EcologyAgent,
    ConservationAgent,
    CriticAgent,
)

orch = OrchestratorAgent()
orch.register_agent(LiteratureAgent())     # 文献检索 Agent
orch.register_agent(AcousticAgent())       # 声学分析 Agent
orch.register_agent(EcologyAgent())        # 生态建模 Agent
orch.register_agent(ConservationAgent())   # 保护评估 Agent
orch.register_agent(CriticAgent())         # 质量评审 Agent

result = orch.run("分析江豚种群现状与威胁因素")
print(result["status"])        # "completed" / "failed"
print(result["output"])        # 执行结果
```

### 2. BDI 认知决策

```python
from porpoise_agent.src.cognitive import BDICoordinator, Belief, Desire

bdi = BDICoordinator()

# 定义信念
bdi.add_belief(Belief("species", "Neophocaena asiaeorientalis"))
bdi.add_belief(Belief("population", 1200))

# 定义愿望
bdi.add_desire(Desire("assess_threat_level", priority=0.9, 
                       condition=lambda b: b.get("population", 0) < 1500))

# 执行推理
plan = bdi.deliberate()
for step in plan.steps:
    print(f"  {step.action} → {step.target}")
```

### 3. 三层记忆系统

```python
from porpoise_agent.src.memory import MemoryManager

memory = MemoryManager()

# 短期记忆（当前上下文）
memory.stm.store("last_query", "江豚栖息地")
print(memory.stm.recall("last_query"))  # "江豚栖息地"

# 长期记忆（ChromaDB 向量存储）
memory.ltm.store_document("paper_001", "长江江豚声学特征分析")
results = memory.ltm.search("acoustic characteristics", top_k=5)
print(f"Found {len(results)} relevant documents")
```

### 4. 沙箱安全执行

```python
from porpoise_agent.src.execution import execute_safe

# 在隔离环境中执行 Python 代码
result = execute_safe("""
import numpy as np
data = [1, 2, 3, 4, 5]
print(f"Mean: {np.mean(data)}")
return sum(data) / len(data)
""")
print(result.output)    # Mean: 3.0
print(result.result)    # 3.0
```

---

## CLI 命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `porpoise chat` | 交互式对话 (ReAct 循环) | `porpoise chat --model deepseek-reasoner` |
| `porpoise run TASK` | 执行单次研究任务 | `porpoise run "分析江豚声学数据"` |
| `porpoise topology` | 显示当前 MAS 拓扑 | `porpoise topology` |
| `porpoise doctor` | 健康检查 | `porpoise doctor` |

```bash
porpoise --help
porpoise chat --help
```

---

## API 参考

### `porpoise_agent.src.agents`

| 类 | 说明 |
|----|------|
| `OrchestratorAgent` | 主编排器 — NLU 解析 → 意图路由 → 多 Agent 调度 → 结果聚合 |
| `LiteratureAgent` | 文献检索 — 调用 cognitive-search-engine 搜索学术论文 |
| `AcousticAgent` | 声学分析 — NBHF 回声定位信号处理 |
| `EcologyAgent` | 生态建模 — 栖息地评估、种群动态 |
| `ConservationAgent` | 保护评估 — 威胁等级评定、保护建议 |
| `CriticAgent` | 质量评审 — 对 Agent 输出进行自我反思与修正 |
| `TopologyBuilder` | 拓扑构建 — MAS 通信拓扑管理 |
| `BaseAgent` | Agent 基类 — BDI + ToolRegistry + 消息处理器 |

### `porpoise_agent.src.cognitive`

| 类 | 说明 |
|----|------|
| `BDICoordinator` | BDI 状态机 — 信念/愿望/意图推理 |
| `ReActLoop` | 推理-行动循环 — 思考→行动→观察→迭代 |
| `TaskDecomposer` | 任务分解 — CoT / ToT / GoT 策略 |
| `Critic` | 自我评审 — 信用分配 + 反馈循环 |

### `porpoise_agent.src.memory`

| 类 | 说明 |
|----|------|
| `ShortTermMemory` | 短期记忆 — 上下文窗口 + 压缩 |
| `LongTermMemory` | 长期记忆 — ChromaDB 向量存储 + RAG |
| `MemoryManager` | 记忆管理器 — 协调 STM + LTM |

### `porpoise_agent.src.execution`

| 类/函数 | 说明 |
|---------|------|
| `SandboxExecutor` | 隔离 Python 运行时 |
| `ToolRegistry` | 工具注册/发现/调用 |
| `APIClient` | PubMed / CrossRef / Semantic Scholar / NCBI API 客户端 |
| `execute_safe(code)` | 快捷安全执行函数 |

### `porpoise_agent.src.integration`

| 类 | 说明 |
|----|------|
| `CognitiveSearchAdapter` | 连接 cognitive-search-engine (v5.0 Hub-and-Spoke) |
| `KnowledgeGraph` | Neo4j 图数据库接口 |
| `ZoteroAdapter` | Zotero SQLite 文献库桥接 |
| `ObsidianAdapter` | Obsidian 笔记库桥接 |

---

## 项目架构

```
porpoise-agent/
├── README.md / README_en.md        ← 中英文说明
├── pyproject.toml                   ← 项目元数据 + 依赖
│
├── src/                             ← Python 源码包
│   ├── __init__.py                  ← 版本号 + 架构声明
│   ├── cli.py                       ← CLI 入口 (4 命令)
│   │
│   ├── agents/                      ← 多智能体系统 (MAS)
│   │   ├── __init__.py              ← 导出 7 个 Agent 类
│   │   ├── base.py                  ← BaseAgent 基类
│   │   ├── orchestrator.py          ← OrchestratorAgent 主编排器
│   │   ├── literature.py            ← LiteratureAgent
│   │   ├── acoustic.py              ← AcousticAgent
│   │   ├── ecology.py               ← EcologyAgent
│   │   ├── conservation.py          ← ConservationAgent
│   │   ├── critic.py                ← CriticAgent
│   │   └── topology.py              ← Topology / TopologyBuilder
│   │
│   ├── cognitive/                   ← 认知层 (BDI + ReAct)
│   │   ├── bdi.py                   ← BDICoordinator
│   │   ├── react_loop.py            ← ReActLoop
│   │   ├── decomposer.py            ← TaskDecomposer (CoT/ToT/GoT)
│   │   ├── reflexion.py             ← Critic + 反馈循环
│   │   └── search.py                ← ThoughtTreeSearch
│   │
│   ├── memory/                      ← 记忆系统
│   │   ├── short_term.py            ← ShortTermMemory
│   │   ├── long_term.py             ← LongTermMemory (ChromaDB)
│   │   └── manager.py               ← MemoryManager
│   │
│   ├── mapping/                     ← 映射与转换层
│   │   ├── router.py                ← IntentRouter
│   │   ├── serializer.py            ← EngineeringSerializer
│   │   └── validator.py             ← OutputValidator
│   │
│   ├── execution/                   ← 工具与执行层
│   │   ├── sandbox.py               ← SandboxExecutor
│   │   ├── tool_registry.py         ← ToolRegistry
│   │   └── api.py                   ← APIClient
│   │
│   ├── interaction/                 ← 交互与感知层
│   │   ├── nlu.py                   ← NLUProcessor
│   │   └── renderer.py              ← ResponseRenderer
│   │
│   ├── integration/                 ← 外部系统集成
│   │   ├── cognitive_search_adapter.py  ← 搜索引擎桥接
│   │   ├── knowledge_graph.py       ← Neo4j 知识图谱
│   │   ├── obsidian_adapter.py      ← Obsidian 笔记
│   │   └── zotero_adapter.py        ← Zotero 文献库
│   │
│   ├── prompts/                     ← 系统提示词
│   └── utils/                       ← 工具函数
│       ├── config.py                ← 配置加载器
│       ├── logging.py               ← 审计日志
│       └── types.py                 ← 类型定义
│
├── config/                          ← 配置文件
│   ├── agent.yaml                   ← Agent 配置
│   ├── models.yaml                  ← 模型路由 + 定价
│   └── mcp_servers.yaml             ← MCP 服务
│
├── tests/                           ← 测试套件
│   ├── test_bdi.py                  ← BDI 状态机测试
│   ├── test_memory.py               ← 记忆系统测试
│   ├── test_serializer.py           ← 序列化 + 验证测试
│   ├── workflow_test.py             ← 7 场景端到端工作流
│   └── robustness_test.py           ← 鲁棒性压力测试
│
├── docs/                            ← 文档
├── data/                            ← 知识库数据
├── examples/                        ← 示例脚本
└── scripts/                         ← 工具脚本
```

### 模块职责

| 模块 | 职责 | 关键类 |
|------|------|--------|
| `agents/` | 多智能体系统 — 7 个专用 Agent 分工协作 | `OrchestratorAgent`, `LiteratureAgent`, `AcousticAgent` |
| `cognitive/` | 认知决策 — BDI 状态机 + ReAct 推理循环 | `BDICoordinator`, `ReActLoop`, `TaskDecomposer` |
| `memory/` | 记忆系统 — STM 上下文 + LTM 向量检索 | `MemoryManager`, `ShortTermMemory`, `LongTermMemory` |
| `execution/` | 工具执行 — 沙箱 + API 客户端 + 工具注册表 | `SandboxExecutor`, `ToolRegistry`, `APIClient` |
| `interaction/` | 交互感知 — 意图识别 + 响应渲染 | `NLUProcessor`, `ResponseRenderer` |
| `mapping/` | 逻辑映射 — 意图路由 + 序列化 + 输出验证 | `IntentRouter`, `EngineeringSerializer` |
| `integration/` | 外部系统桥接 — 搜索/图谱/Zotero/Obsidian | `CognitiveSearchAdapter`, `KnowledgeGraph` |

---

## 外部集成

| 系统 | 适配器 | 用途 |
|------|--------|------|
| **cognitive-search-engine** | `CognitiveSearchAdapter` | 物种文献 7 引擎并行搜索 |
| **Neo4j 知识图谱** | `KnowledgeGraph` | 物种关系图存储与查询 |
| **Zotero 文献库** | `ZoteroAdapter` | 课题组文献数据库读取 |
| **Obsidian 知识库** | `ObsidianAdapter` | 个人笔记库集成 |

---

## 配置文件

### `config/agent.yaml`

Agent 运行时配置（5 层参数、模型选择、工具权限）。

### `config/models.yaml`

模型路由配置：

```yaml
models:
  - name: deepseek-chat
    provider: deepseek
    context_window: 64000
    purpose: general_reasoning
  - name: deepseek-reasoner
    provider: deepseek
    context_window: 64000
    purpose: complex_reasoning
```

### `config/mcp_servers.yaml`

MCP 工具服务注册（scholar 搜索、文献全文获取、文件系统等）。

---

## 关联项目

| 项目 | 角色 | 关系 |
|------|------|------|
| **eon-core** | 协调内核 | 顶点 V2 — 江豚领域 Agent |
| **fish-ecology-assistant** | 知识供给 V0 | 物种知识库与基础数据 |
| **cognitive-search-engine** | 搜索验证 V1 | 7 引擎文献搜索与权威评分 |
| **coilia-agent** | P₂ 刀鲚专研 | 同级衍生项目 (姊妹 Agent) |
| **culter-agent** | P₃ 鲌类专研 | 同级衍生项目 |

---

## 贡献指南

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/xxx`
3. 提交变更：`git commit -m "描述"`
4. 推送分支：`git push origin feature/xxx`
5. 创建 Pull Request

### 运行测试

```bash
cd porpoise-agent
python -m pytest tests/ -v
```

---

## 许可证

MIT License © 2026 Liu Kai Research Group, FFRC

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
