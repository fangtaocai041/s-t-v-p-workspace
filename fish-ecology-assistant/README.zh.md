<p align="center">
  🇬🇧 <a href="README.md">English</a>
</p>

<div align="center">
  <h1>🌊 Fish Ecology Assistant</h1>
  <p><strong>鱼类生态学知识供给引擎</strong> — 多流域物种知识库 + 两阶段文献搜索 + 三角验证评分</p>
  <p>Python 3.10+ · pyyaml · Triangle Core S/V0 层</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/version-6.5.0-ec4899?style=flat-square" alt="v6.5.0"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square" alt="Python 3.10+"></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/changelog-v6.5.0-22c55e?style=flat-square" alt="Changelog"></a>
</p>

---

## 目录

- [项目简介](#项目简介)
- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [API 参考](#api-参考)
- [命令行工具](#命令行工具)
- [项目架构](#项目架构)
- [配置文件说明](#配置文件说明)
- [多项目协作](#多项目协作)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

**Fish Ecology Assistant** 是一个面向鱼类生态学研究的 Python 工具包，作为 [eon-core](https://github.com/fangtaocai041/eon-core) 生态系统的 **S/V0 知识供给层**（三角核心成员）运行。

### 核心能力

| 能力 | 说明 |
|------|------|
| 🐟 **多流域鱼类知识库** | 涵盖长江（443 种）、图们江、绥芬河、黑龙江等流域 |
| 🔍 **两阶段文献搜索** | 先查本地知识库 → 按需启动全量多引擎搜索 |
| ⭐ **三角验证评分** | 对论文按期刊/作者/时效性进行 0–100 可信度评分 |
| 🔄 **知识图谱同步** | KB ↔ 图谱双向同步，跨项目共享 |
| 🤖 **多 Agent 协作** | 与 cognitive-search-engine、porpoise-agent 等 5 个子系统协作 |

### 生态系统角色

```
三角核心（密闭三元组）
├── S/V0  fish-ecology-assistant  ← 本项目：知识供给
├── V/V1  cognitive-search-engine ← 搜索验证引擎
└──         eon-core              ← 协调内核

衍生项目
├── P₁  porpoise-agent  — 江豚种群监测
├── P₂  coilia-agent    — 刀鲚洄游生态
├── P₃  culter-agent    — 鲌类基因组学
└── C   conflict-arbiter — 保护等级冲突仲裁
```

---

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/fangtaocai041/fish-ecology-assistant.git
cd fish-ecology-assistant

# 安装 Python 依赖
pip install pyyaml
```

### 验证安装

```python
from src.orchestrator import FishEcologyOrchestrator

orch = FishEcologyOrchestrator()
print(orch.health())
# 输出: {'project': 'fish-ecology-assistant', 'status': 'HEALTHY', ...}
```

```bash
# 验证知识库中是否包含已知物种
python -c "
from src.orchestrator import get_orchestrator
r = get_orchestrator().kb_first_lookup(query='鳤')
print(r.summary_text)
"
```

### 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | ≥ 3.10 | 运行环境 |
| PyYAML | ≥ 6.0 | 解析 YAML 知识库 |
| cognitive-search-engine | workspace | 可选：全量搜索（目录链接） |

---

## 核心功能

### 1. 两阶段物种文献搜索（KB-First）

两阶段搜索是核心工作流：**先查本地知识库 → 按需启动全量搜索**。

#### 阶段 1 — 查知识库

```python
from src.orchestrator import get_orchestrator

orch = get_orchestrator()
result = orch.kb_first_lookup(query="珠星三块鱼")

print(result.found)                    # True / False
print(result.scientific_name)          # "Tribolodon brandti"
print(result.chinese_name)             # "珠星三块鱼"
print(result.family)                   # "鲤科"
print(result.synonyms)                 # ["Tribolodon hakonensis"]
print(result.aliases)                  # ["三块鱼", "滩头鱼"]
print(result.search_recommendation)    # "stay_in_kb" | "continue_to_c"
```

`KbFirstResult` 字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `found` | bool | 是否在知识库中找到 |
| `scientific_name` | str | 学名 |
| `chinese_name` | str | 中文名 |
| `aliases` | list[str] | 别名列表 |
| `synonyms` | list[str] | 同义名列表 |
| `family` | str | 科 |
| `order` | str | 目 |
| `conservation` | str | 保护等级 |
| `ecology` | str | 生态描述 |
| `distribution` | dict | 分布信息（国家/流域） |
| `summary_text` | str | 人类可读摘要 |
| `search_recommendation` | str | 建议：`"stay_in_kb"` 或 `"continue_to_c"` |

#### 阶段 2 — 全量搜索

通过 `ProjectHub` 调用 cognitive-search-engine 进行 7 引擎并行搜索：

```python
from src.project_hub import get_hub

hub = get_hub()
full_result = hub.search_species("珠星三块鱼", mode="kb_first")

if full_result["stage"] == "kb_check":
    print("知识库已有数据，等待用户决策")
elif full_result["stage"] == "full_search":
    print("全量搜索完成")
    print(full_result.get("full_result"))
```

#### 命令行两阶段搜索

```bash
# 交互模式：查 KB → 询问是否全量搜索
python scripts/search_species.py "珠星三块鱼"

# 自动模式：直接全量检索 + 回写知识库
python scripts/search_species.py "珠星三块鱼" --auto

# 仅查知识库
python scripts/search_species.py "珠星三块鱼" --kb-only

# 预览模式（不回写）
python scripts/search_species.py "珠星三块鱼" --dry-run
```

### 2. 项目中枢（ProjectHub）

统一加载和管理所有子项目的入口：

```python
from src.project_hub import get_hub

hub = get_hub()

# 三角核心完整性检查
print(hub.is_triangle_complete())   # True / False

# 三角核心成员状态
status = hub.triangle_status()
for key, info in status.items():
    print(f"{key}: {info['symbol']} ({info['pole']}) — {'✅' if info['available'] else '❌'}")

# 跨项目委托
hub.delegate_to("porpoise", "分析江豚声学数据")
hub.delegate_to("coilia", "检索刀鲚耳石微化学文献")

# 完整健康报告
health = hub.health_all()
print(health["three"])           # 三角状态
print(health["myriad"])          # 衍生项目状态
print(health["triangle_complete"])  # 完整性
```

### 3. 文献可信度评分

对论文按来源期刊进行 0–100 评分，支持四档分级：

```python
from scripts.credibility_scorer import score_papers, score_paper

papers = [
    {"title": "长江鱼类群落研究", "journal": "水生生物学报", "year": 2023},
    {"title": "Fish diversity in Yangtze", "journal": "Scientific Reports", "year": 2024},
]

# 批量评分
scored = score_papers(papers, species_name="鳤")

# 查看评分结果
for p in scored:
    flag = p["_credibility_flag"]      # 🟢 🟡 🟠 🔴
    label = p["_credibility_label"]    # 高 / 中 / 低 / 不可用
    score = p["_credibility_score"]    # 0–100
    print(f"{flag} {score:3d} | {p['title'][:40]} | {p.get('journal','')}")
```

评分标准：

| 评级 | 分数范围 | 标识 | 条件 |
|:----:|:--------:|:----:|------|
| 高 | 25–30 | 🟢 | SCI Q1/Q2 或 CSCD 核心期刊 |
| 中 | 15–24 | 🟡 | 一般 SCI 或统计源期刊 |
| 低 | 5–14 | 🟠 | 普通期刊 |
| 不可用 | 0–4 | 🔴 | 疑似掠夺性期刊或无来源 |

### 4. 知识库 ↔ 图谱同步

将 `fish_species_kb.yaml` 中的物种信息同步到 `cognitive-search-engine/config/species_graph.yaml`：

```bash
# 预览模式（不实际写入）
python scripts/kb_to_graph_sync.py --dry-run

# 实际执行同步
python scripts/kb_to_graph_sync.py
```

### 5. lit-search v3.1 命令行

```bash
# 摘要模式（默认）
python scripts/run_lit_search.py "珠星三块鱼"

# 穷举模式
python scripts/run_lit_search.py "Pseudaspius hakonensis" --mode exhaustive

# 表格模式
python scripts/run_lit_search.py "珠星三块鱼" --format table

# JSON 输出
python scripts/run_lit_search.py "珠星三块鱼" --format json --output result.json

# 仅图谱缓存
python scripts/run_lit_search.py "珠星三块鱼" --graph-only
```

### 6. 自进化反馈

每次搜索后记录性能指标，自动调整搜索参数：

```python
from scripts.self_evolve import log_search, get_evolution_history

log_search("tribolodon_brandti", {
    "mode": "satisficing",
    "known_papers": 15,
    "new_papers": 3,
    "total_papers": 18,
})

history = get_evolution_history()
print(f"已记录 {len(history)} 次搜索")
```

---

## API 参考

### `src/orchestrator.py` — 核心 API

| 函数/类 | 说明 |
|---------|------|
| `get_orchestrator()` | 获取 `FishEcologyOrchestrator` 单例 |
| `FishEcologyOrchestrator()` | 主 API 类 |
| `FishEcologyOrchestrator.kb_first_lookup(query)` | 知识库查询（Stage 1） |
| `FishEcologyOrchestrator.search_species(name, mode, group, limit)` | 统一物种搜索入口 |
| `FishEcologyOrchestrator.delegate_to(subsystem, task)` | 跨项目委托 |
| `FishEcologyOrchestrator.health()` | 健康状态 |
| `FishEcologyOrchestrator.info()` | 版本能力信息 |
| `KbFirstResult` | KB 查询结果 dataclass |

### `src/project_hub.py` — 多项目协调

| 函数/属性 | 说明 |
|-----------|------|
| `get_hub()` | 获取 `ProjectHub` 单例 |
| `reset_hub()` | 重置单例（测试用） |
| `hub.cognitive` | 访问 cognitive-search-engine |
| `hub.eon` | 访问 eon-core |
| `hub.porpoise` | 访问 porpoise-agent（按需加载） |
| `hub.coilia` | 访问 coilia-agent（按需加载） |
| `hub.conflict` | 访问 conflict-arbiter（按需加载） |
| `hub.is_triangle_complete()` | 三角完整性检查 |
| `hub.triangle_status()` | 三角详细状态 |
| `hub.health_all()` | 完整健康报告 |
| `hub.search_species(name, mode)` | 统一搜索入口 |
| `hub.delegate_to(subsystem, task)` | 委托任务 |
| `hub.relationship_map()` | 架构 ASCII 图 |

### `src/adapter.py` — 跨项目协议

| 类/方法 | 说明 |
|---------|------|
| `FishEcologyAdapter()` | 实现 `IProjectAdapter` 接口 |
| `adapter.search(name, mode)` | 搜索入口 |
| `adapter.health()` | 健康状态 |
| `adapter.score_credibility(papers)` | 论文评分 |
| `adapter.lookup_species(name)` | 物种查找 |

### `src/shared.py` — 共享工具

| 函数/常量 | 说明 |
|-----------|------|
| `JOURNAL_WHITELIST` | 期刊白名单（dict: 期刊名→分数） |
| `build_search_queries(sci, cn)` | 构建搜索查询列表 |
| `generate_ocr_variants(name, mode)` | 生成 OCR 拼写变体 |

---

## 命令行工具

| 脚本 | 用途 | 示例 |
|------|------|------|
| `scripts/run_lit_search.py` | 文献搜索（推荐） | `python scripts/run_lit_search.py "鳤"` |
| `scripts/search_species.py` | 两阶段检索编排 | `python scripts/search_species.py "珠星三块鱼" --auto` |
| `scripts/kb_to_graph_sync.py` | KB → 图谱同步 | `python scripts/kb_to_graph_sync.py` |
| `scripts/self_evolve.py` | 自进化反馈 | `python -c "from scripts.self_evolve import log_search; ..."` |
| `scripts/taxonomy_sync.py` | 分类学同步 | `python scripts/taxonomy_sync.py` |
| `scripts/verify_architecture.py` | 架构验证 | `python scripts/verify_architecture.py` |

```bash
# 查看帮助
python scripts/run_lit_search.py --help
python scripts/search_species.py --help
```

---

## 项目架构

```
fish-ecology-assistant/
├── README.md                       ← 英文文档
├── README.zh.md                    ← 中文文档
├── CHANGELOG.md                    ← 版本变更记录（v1.0 → v6.5.0）
├── pyproject.toml                  ← 项目元数据 + 依赖声明
│
├── src/                            ← Python 源码包
│   ├── __init__.py                 ← 版本号 + 公开 API 导出
│   ├── orchestrator.py             ← FishEcologyOrchestrator（主入口 API）
│   ├── project_hub.py              ← ProjectHub（多项目协调中枢）
│   ├── adapter.py                  ← FishEcologyAdapter（跨项目协议）
│   ├── shared.py                   ← 共享工具（期刊白名单、查询构建器、OCR 变体）
│   └── dao_engine.py               ← CLI 引擎（道→一→二→三→万物管线）
│
├── tests/                          ← 测试套件
│   ├── __init__.py
│   ├── test_orchestrator.py        ← 核心 API 测试
│   ├── test_project_hub.py         ← 多项目协调测试
│   └── test_shared.py              ← 共享工具测试
│
├── config/                         ← 配置文件
│   ├── fish_species_kb.yaml        ← 多流域鱼类物种知识库（443+ 种）
│   ├── agent.yaml                  ← Agent 配置（版本、角色）
│   ├── component_registry.yaml     ← 组件注册表
│   └── evolution.yaml              ← 进化参数
│
├── scripts/                        ← 可执行脚本
│   ├── run_lit_search.py           ← lit-search v3.1 命令行入口
│   ├── search_species.py           ← 两阶段搜索编排器
│   ├── credibility_scorer.py       ← 三角验证评分（重导出至 c 项目）
│   ├── kb_to_graph_sync.py         ← 知识库 ↔ 图谱同步
│   ├── self_evolve.py              ← 搜索后自进化反馈
│   ├── taxonomy_sync.py            ← 分类学同步
│   └── verify_architecture.py      ← 架构合规性验证
│
├── research_output/                ← 研究报告输出目录
│   └── .gitkeep
│
├── docs/                           ← 文档
├── .reasonix/                      ← Reasonix Agent 配置
├── logs/                           ← 运行日志
└── CHANGELOG.md                    ← 版本变更历史
```

### 模块职责

| 模块 | 职责 | 关键类/函数 |
|------|------|-------------|
| `src/orchestrator.py` | 主入口 API — 物种查询、KB 优先搜索、跨项目委托 | `FishEcologyOrchestrator`, `KbFirstResult`, `get_orchestrator()` |
| `src/project_hub.py` | 多项目协调 — 动态加载子项目适配器、状态监控 | `ProjectHub`, `get_hub()`, `TRIANGLE`, `DERIVED` |
| `src/adapter.py` | 跨项目通信协议 — 实现 `IProjectAdapter` 接口 | `FishEcologyAdapter` |
| `src/shared.py` | 共享工具函数 — 期刊白名单、查询构建、OCR 变体 | `JOURNAL_WHITELIST`, `build_search_queries()` |
| `src/dao_engine.py` | CLI 引擎 — 管线执行器 | `DaemonQuery`, `YinYangDuality`, `TriangleCore` |
| `scripts/run_lit_search.py` | 文献搜索 CLI | `cli()`, `score_papers()` |
| `scripts/search_species.py` | 两阶段搜索编排 | `load_kb()`, `call_c_search()`, `update_kb()` |

---

## 配置文件说明

### `config/fish_species_kb.yaml`

多流域鱼类物种知识库，按大陆 → 国家 → 流域分层存储。每个物种包含：

```yaml
species:
  - id: tribolodon_brandti
    scientific: Tribolodon brandti          # 学名
    name: 珠星三块鱼                         # 中文名
    family: 鲤科                              # 科
    order: 鲤形目                              # 目
    aliases: [三块鱼, 滩头鱼]                 # 别名
    synonyms: [Tribolodon hakonensis]         # 同义名
    ecology: 溯河洄游鱼类，产卵期3-5月         # 生态描述
    conservation: NE                          # 保护等级
    economic_value: 重要经济鱼类               # 经济价值
    max_length_cm: 50                         # 最大体长
    distribution:
      countries: [中国, 日本, 俄罗斯]
      basins: [图们江, 绥芬河, 黑龙江]
    literature:
      - doi: 10.1234/example
        title: "珠星三块鱼种群遗传结构"
        year: 2022
        journal: 水生生物学报
        category: genetics
    taxonomy_log:
      - detected_at: 2026-06-01
        field: family
        old_value: Cyprinidae
        new_value: Xenocyprididae
        evidence: [DOI, journal, author]
```

### `config/agent.yaml`

```yaml
agent:
  version: "6.5.0"
  role: "S/V0 — 知识供给层"
```

---

## 多项目协作

本项目是 Triangle Core 的一角，与其他项目通过标准化协议协作：

### 依赖关系

```
fish-ecology-assistant (S/V0 · 知识供给)
    │
    ├── 调用 → cognitive-search-engine (V/V1 · 搜索验证)
    │     search_species() → c 项目 7 引擎并行搜索
    │
    ├── 调用 → conflict-arbiter (C · 冲突仲裁)
    │     保护等级冲突检测
    │
    ├── 调用 → porpoise-agent (P₁ · 江豚)
    └── 调用 → coilia-agent (P₂ · 刀鲚)
```

### 跨项目搜索流程

```python
# Python API 调用
from src.project_hub import get_hub

hub = get_hub()
assert hub.is_triangle_complete(), "三角核心不完整"

# 调用 cognitive 搜索
result = hub.cognitive.search("珠星三块鱼")

# 委托衍生项目
hub.delegate_to("porpoise", "评估江豚栖息地")
hub.delegate_to("conflict", {"species": "鳤", "region": "china"})
```

```bash
# 命令行调用 c 项目搜索
python scripts/search_species.py "珠星三块鱼" --auto
```

### 关联项目表

| 项目 | 类型 | 技术栈 | 说明 |
|------|:----:|--------|------|
| **cognitive-search-engine** | 三角 V/V1 | Python, BDI+ReAct | 搜索验证：权威评分、Hub-and-Spoke 搜索、共享图谱 |
| **eon-core** | 三角 Coordinator | Python | 协调内核：EventBus、DAG 路由、健康监控 |
| **porpoise-agent** | 衍生 P₁ | Python | 江豚专研：声学分析、栖息地建模、种群评估 |
| **coilia-agent** | 衍生 P₂ | Python | 刀鲚专研：耳石微化学、洄游生态、资源评估 |
| **culter-agent** | 衍生 P₃ | Python | 鲌类专研：基因组学、年龄生长、同位素、营养生态位 |
| **conflict-arbiter** | 衍生 C | Python | 冲突仲裁：多源保护级别冲突检测、加权裁决 |
| **workspace** | 根目录 | — | 统一工作空间，`coordination.yaml` 协调配置 |

---

## 贡献指南

### 开发流程

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/xxx`
3. 提交变更：`git commit -m "描述"`
4. 推送分支：`git push origin feature/xxx`
5. 创建 Pull Request

### 代码规范

- Python 代码遵循 [PEP 8](https://peps.python.org/pep-0008/)
- 所有公开 API 需有 **docstring** 和 **类型注解**
- 新建功能必须在 `config/` 中有对应配置
- 新增功能需有对应的 `.py` 可执行脚本（功能脚本化原则）
- 新增依赖需更新 `pyproject.toml`

### 运行测试

```bash
cd fish-ecology-assistant
python -m pytest tests/ -v
```

### 功能脚本化原则

每个 Markdown 描述的功能必须有对应的可执行 `.py` 脚本：

| 功能 | Markdown 章节 | 对应脚本 |
|------|--------------|----------|
| 三角验证评分 | 核心功能 §3 | `scripts/credibility_scorer.py` |
| 自进化反馈 | 核心功能 §6 | `scripts/self_evolve.py` |
| 知识图谱同步 | 核心功能 §4 | `scripts/kb_to_graph_sync.py` |
| 两阶段搜索 | 核心功能 §1 | `scripts/search_species.py` |

---

## 许可证

MIT License © 2026 fangtaocai041

---

## 版本历史

详见 [CHANGELOG.md](CHANGELOG.md)。

<p align="right">(<a href="#readme-top">回到顶部</a>)</p>
