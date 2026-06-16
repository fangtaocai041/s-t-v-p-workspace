# 🐬 Porpoise Agent v2.1 — 江豚研究智能体

[![test](https://github.com/FFRC-LiuKai-Lab/porpoise-agent/actions/workflows/test.yml/badge.svg)](https://github.com/FFRC-LiuKai-Lab/porpoise-agent/actions/workflows/test.yml)

> **五层标准智能体分层架构 + 三重外部集成**
>
> 适配豚类（江豚为主）研究的 AI Agent 框架
> 基于 DeepSeek + cognitive-search-engine (v5.0 Hub-and-Spoke)
> 服务：无锡渔业学院/淡水渔业研究中心 刘凯研究员课题组

---

## 项目愿景

长江江豚 (*Neophocaena asiaeorientalis asiaeorientalis*) 是极度濒危的淡水鲸类，
仅存约1,000-1,200头。保护工作需要高效的数据分析、文献调研和决策支持。

**Porpoise Agent v2.1** 是一个融合形式化 Agent 理论与真实科研工具链的 AI 研究助手。

---

## 架构总览

```
用户输入
  │
  ▼
┌─────────────────────────────────────────────────────┐
│  L1  交互与感知层  │  NLU 意图识别 + 多格式渲染      │
├─────────────────────────────────────────────────────┤
│  L2  认知与决策层  │  BDI + ReAct + CoT/ToT/GoT     │
│                    │  + Reflexion + 思维树搜索       │
├─────────────────────────────────────────────────────┤
│  L3  记忆系统层    │  STM(上下文窗口) + LTM(ChromaDB)│
├─────────────────────────────────────────────────────┤
│  L4  映射与转换层  │  意图路由 + NL→代码/JSON/SQL    │
├─────────────────────────────────────────────────────┤
│  L5  工具与执行层  │  沙盒执行器 + 工具注册 + API    │
└─────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────┐
│  外部集成层                                        │
│  ├─ cognitive-search-engine (v5.0 Hub-and-Spoke)    │
│  ├─ Zotero 本地库 (SQLite 直读, 406 条)             │
│  └─ Obsidian Vault (课题组文档 + 文献笔记)          │
└─────────────────────────────────────────────────────┘
```

---

## 快速开始

### 1. 环境要求
- Python 3.11+
- DeepSeek API Key ([获取](https://platform.deepseek.com))
- Zotero 7 (可选, 用于本地文献库)
- Obsidian (可选, 用于知识管理)

### 2. 安装

```bash
git clone https://github.com/FFRC-LiuKai-Lab/porpoise-agent.git
cd porpoise-agent
pip install -e .
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY
```

### 3. 运行

```bash
porpoise chat                          # 交互式对话 (ReAct 循环)
porpoise run "搜索江豚声学文献"         # 单次任务 (Orchestrator + MAS)
porpoise topology                       # 查看 MAS 拓扑
porpoise doctor                         # 五层架构健康检查
```

---

## 核心特性

### 🧠 理论驱动

| 理论 | 项目实现 | 说明 |
|------|----------|------|
| **BDI Model** | `src/cognitive/bdi.py` | Belief-Desire-Intention 心智模型 |
| **MDP / POMDP** | `src/cognitive/react_loop.py` | 离散时间决策过程形式化: S_t→A_t→O_{t+1}→S_{t+1} |
| **ReAct** | `src/cognitive/react_loop.py` | Think→Act→Observe→Reflect 闭环反馈 |
| **Tree / Graph of Thoughts** | `src/cognitive/decomposer.py`, `search.py` | BFS/Beam/MCTS + DAG 合并 |
| **Reflexion** | `src/cognitive/reflexion.py` | Critic 反思 + 信用分配 + 反馈闭环 |
| **Multi-Agent Topology** | `src/agents/topology.py` | 图论驱动的 MAS 通信 (Sequential/Hierarchical/Debate/DAG) |
| **RAG** | `src/memory/long_term.py` | ChromaDB 向量检索增强生成 |

### 🔬 江豚研究专用

- **NBHF Click 检测**: 110-150 kHz 窄带高频脉冲 (SPL 阈值 + ICI 匹配)
- **PAM 数据处理管道**: SoundTrap、A-tag、C-POD、F-POD、RPCD-II
- **行为推断**: Buzz 检测 → 觅食活动指数 → 昼夜节律分析
- **丰度估计**: Cue Counting / Distance Sampling / SECR
- **18+ 声学特征**: 时间/频谱/能量三维特征提取

### 🔗 三重外部集成

| 集成 | 路径 | 能力 |
|------|------|------|
| **cognitive-search-engine** | `D:/Reasonix/cognitive-search-engine/` | v5.0 Hub-and-Spoke 图谱搜索: OCR 变体生成 + 7 引擎并行 + 引用图遍历 + review mining + 自适应停止 |
| **Zotero** | `D:/ZoteroData/zotero.sqlite` | SQLite 直读 406 条文献, 零 API 调用搜索, Zotero 更新后自动同步 |
| **Obsidian** | `D:/Obsidian Vault/` | 课题组文档注入 BDI 上下文, 新论文自动写入文献笔记, vault 全文搜索 |

### 🛡️ 安全与可审计

- **沙箱执行**: 子进程隔离 + 超时 + AST 安全检查 (危险操作拦截)
- **人工审批**: 野外方案 / 保护建议 / 数据删除 / 外部写入
- **审计日志**: JSONL 格式全决策追踪
- **引用验证**: Critic Agent 自动验证文献存在性

---

## 项目结构

```
porpoise-agent/
├── data/knowledge_base/
│   └── porpoise_research_teams.md   # 江豚研究机构与近缘种知识库
├── docs/
│   └── ARCHITECTURE.md              # 五层架构设计
├── src/
│   ├── interaction/                 # L1: 交互与感知层
│   │   ├── nlu.py                   #   意图识别 (14 种) + 实体提取
│   │   └── renderer.py              #   Markdown/JSON/Table 渲染
│   ├── cognitive/                   # L2: 认知与决策层
│   │   ├── bdi.py                   #   BDI 状态机
│   │   ├── react_loop.py            #   ReAct 主循环
│   │   ├── decomposer.py            #   CoT/ToT/GoT 任务分解
│   │   ├── reflexion.py             #   Critic 反思 + 信用分配
│   │   └── search.py                #   BFS/Beam/MCTS 思维搜索
│   ├── memory/                      # L3: 记忆系统层
│   │   ├── short_term.py            #   上下文窗口 + 遗忘曲线
│   │   ├── long_term.py             #   ChromaDB + RAG
│   │   └── manager.py               #   统一记忆协调器
│   ├── mapping/                     # L4: 映射与转换层
│   │   ├── router.py                #   意图→工具路由
│   │   ├── serializer.py            #   NL→Python/SQL/JSON
│   │   └── validator.py             #   AST/Schema/Safety 校验
│   ├── execution/                   # L5: 工具与执行层
│   │   ├── sandbox.py               #   沙盒执行器
│   │   ├── tool_registry.py         #   工具注册中心
│   │   └── api.py                   #   PubMed/CrossRef/SemanticScholar API
│   ├── agents/                      # 多智能体拓扑 (MAS)
│   │   ├── topology.py              #   图论拓扑引擎
│   │   ├── base.py                  #   Agent 基类 (BDI + 工具集)
│   │   ├── literature.py            #   文献分析 Agent
│   │   ├── acoustic.py              #   声学分析 Agent
│   │   ├── ecology.py               #   生态分析 Agent
│   │   ├── conservation.py          #   保护评估 Agent
│   │   ├── critic.py                #   批判 Agent (对抗角色)
│   │   └── orchestrator.py          #   编排 Agent
│   ├── integration/                 # 外部集成层
│   │   ├── cognitive_search_adapter.py  # cognitive-search-engine 适配器
│   │   ├── zotero_adapter.py            # Zotero SQLite 适配器
│   │   └── obsidian_adapter.py          # Obsidian Vault 适配器
│   └── cli.py                       # CLI 入口
├── config/
│   └── agent.yaml                   # 五层配置 + 集成配置
└── tests/
    ├── robustness_test.py           # 61 项功能+稳健性测试
    └── workflow_test.py             # 79 项端到端工作流测试
```

---

## 文献检索三层策略

```
用户查询 "Neophocaena asiaeorientalis 江豚声学"
  │
  ├─ L0: Zotero 本地库 (SQLite 直读, 406 条, 零 API)
  │     └─ 命中 → 即时返回, 免网络
  │
  ├─ L1: cognitive-search-engine (search_rules.yaml 完整管线)
  │     ├─ generate_variants("Neophocaena", "asiaeorientalis") → 20 OCR 变体
  │     ├─ build_search_queries() → 精确名 + 变体 + 中文 + 生态关键词
  │     ├─ ParallelSearch.search_all() → PubMed × Crossref × OpenAlex
  │     └─ CognitiveAgent.search() → 引用图遍历 + review mining + 自适应停止
  │     └─ 新论文 → 自动写入 Obsidian 文献笔记/
  │
  └─ L2: Semantic Scholar + PubMed (fallback, 无外部依赖时)
```

---

## 优势

### ✅ 理论完备性
- 五层架构对应用户定义的标准 Agent 分层模型，每层有明确的 MDP 形式化语义
- BDI + ReAct + Reflexion 形成完整的「感知→决策→执行→反思」控制论闭环
- ToT/GoT 思维搜索在推理空间中提供结构化探索（而非线性生成）

### ✅ 工程实用性
- **零 API 搜索**: Zotero 本地库优先，已有文献秒级返回
- **自动知识沉淀**: 新论文自动写入 Obsidian，符合学术工作流习惯
- **引擎热更新**: cognitive-search-engine 通过 importlib 文件直载，更新即生效
- **三级降级**: Zotero → cognitive-search-engine → builtin，每层独立可用

### ✅ 江豚领域深度
- 内置 8 个学科方向分类、25+ 研究单位、12+ 近缘种参照
- Obsidian 课题组分析文档（87K+ 字）自动注入每次检索的 BDI 上下文
- Critic Agent 审查保护建议，触发人工审批关卡

### ✅ 性能与安全
- NLU 解析: ~29K qps | BDI 循环: ~630K cycles/s | 沙盒执行: 1000 行 < 30ms
- AST 安全检查 + SQL 注入防护 + 子进程隔离 + 超时控制
- 数据不出本地（Zotero/Obsidian 均为本地文件）

---

## 不足与改进方向

### ❌ 对 LLM 依赖性高
- BDI 策略函数 π(Belief, Desire) 和 Reflexion Critic 的深度推理需要 LLM 支持
- 无 LLM 时降级为关键词匹配，语义理解能力大幅下降
- **改进方向**: 探索小型专用模型（如微调的分类器）替代部分 LLM 调用

### ❌ 知网/万方/维普盲区
- cognitive-search-engine 的 PubMed/Crossref/OpenAlex 不索引中文数据库
- 大量中国学者的江豚研究发表在中文核心期刊（水生生物学报、湖泊科学等）
- 当前无法自动检索这些来源
- **改进方向**: 通过知网研学导出或 Zotero 中文插件补充

### ❌ 声学分析未完全实现
- NBHF Click 检测代码已写入 `AcousticAgent`，但需要真实音频文件验证
- PAM 设备数据格式（SoundTrap .wav, A-tag, C-POD）解析需逐设备适配
- **改进方向**: 使用课题组已有的 PAM 数据做端到端测试

### ❌ 多 Agent 拓扑简化
- 当前 SOP 工作流为顺序链（literature→acoustic→ecology→conservation）
- 动态条件路由（"if result.confidence > 0.7 then..."）已定义但未经生产验证
- Debate 模式（Generator ↔ Critic 对抗）仅在测试中运行
- **改进方向**: 在真实多步研究任务中验证和调优拓扑路由

### ❌ 向量检索未启用
- ChromaDB 未安装时降级为内存关键词匹配
- 长期记忆的语义召回能力受限于是否有 ChromaDB
- **改进方向**: 将 ChromaDB 改为可选依赖自动安装

### ❌ 单用户单会话
- BDI Belief 和 STM 在会话结束后清除（除非手动 persist）
- 不支持跨会话的研究上下文恢复
- **改进方向**: 用 SQLite/JSON 持久化会话状态，下回启动自动恢复

---

## 理论基础

| 理论 | 出处 | 项目实现 |
|------|------|----------|
| BDI Model | Bratman 1987; Rao & Georgeff 1995 | `src/cognitive/bdi.py` |
| MDP / POMDP | Bellman 1957; Kaelbling et al. 1998 | `src/cognitive/react_loop.py` |
| ReAct | Yao et al. 2022 | `src/cognitive/react_loop.py` |
| Tree of Thoughts | Yao et al. 2023 | `src/cognitive/decomposer.py` |
| Graph of Thoughts | Besta et al. 2024 | `src/cognitive/decomposer.py` |
| Reflexion | Shinn et al. 2023 | `src/cognitive/reflexion.py` |
| RAG | Lewis et al. 2020 | `src/memory/long_term.py` |
| Multi-Agent Debate | Du et al. 2023; Liang et al. 2023 | `src/agents/topology.py` |
| Hub-and-Spoke Search | cognitive-search-engine v5.0 | `src/integration/cognitive_search_adapter.py` |

---

## 验证数据

| 维度 | 测试数 | 结果 |
|------|:--:|:--:|
| 模块导入 | 24 | ✅ 全部通过 |
| 功能 + 稳健性 | 61 | ✅ 全部通过 |
| 端到端工作流 | 79 (7 场景) | ✅ 全部通过 |
| 性能边界 | 10 | ✅ 全部达标 |
| NLU 吞吐 | — | ~29,000 qps |
| BDI 循环 | — | ~630,000 cycles/s |
| 沙盒执行 | — | 1,000 行 < 30ms |

---

## 对标项目

| 项目 | 借鉴点 |
|------|--------|
| [Reasonix](https://github.com/esengine/reasonix) | DeepSeek 原生 Agent Loop, prefix-cache |
| [cognitive-search-engine](https://github.com/fangtaocai041/cognitive-search-engine) | v5.0 Hub-and-Spoke 图谱搜索 (本项目核心依赖) |
| [Ecology-Harness](https://github.com/ECNU-ICALK/Ecology-Harness) | 生态学 Agent 编排 |
| [AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory) | 研究流水线设计 |
| [SciToolAgent](https://github.com/hicai-zju/scitoolagent) | 科学工具知识图谱 |
| [CetusID](https://github.com/Gui-Frainer/CetusID) | 鲸类声学分类 |

---

## 课题组信息

- **单位**: 南京农业大学无锡渔业学院 / 中国水产科学研究院淡水渔业研究中心 (FFRC)
- **课题组**: 刘凯研究员课题组
- **研究方向**: 长江江豚保护生物学、被动声学监测、栖息地评估、渔业资源管理
- **联系**: liukai@ffrc.cn

---

## 许可证

[English version](README_en.md) | 中文版

---

MIT License © 2025 无锡渔业学院/淡水渔业研究中心 刘凯研究员课题组
