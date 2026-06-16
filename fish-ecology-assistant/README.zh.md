# Fish Ecology Assistant 🐟

**鱼类生态学知识供给引擎** — 多流域物种知识库 + KB-First 两阶段文献搜索 + 三角验证评分。

[English](README.md) | [变更日志](CHANGELOG.md) | [参与贡献](CONTRIBUTING.md) | [使用指南](GUIDE.md)

---

## 项目简介

Fish Ecology Assistant 是一个 Python 鱼类生态学知识供给系统，核心能力：

- **多流域物种知识库**：长江（443 种）+ 图们江/绥芬河，含学名、中文名、别名、同义名、科属、保护级别、生态习性、分布流域
- **KB-First 两阶段搜索**：先查本地知识库 → 用户决策 → 按需委托 cognitive-search-engine 全量检索
- **三角验证评分**：期刊白名单 + DOI/PMID 标识符 + 预印本惩罚 → 0-100 可信度分数
- **跨项目协调中枢**：通过 ProjectHub 统一管理 fish/cognitive/eon-core 三角核心及 porpoise/coilia/conflict 衍生项目

---

## 安装

```bash
# 克隆仓库
git clone git@github.com:fangtaocai041/fish-ecology-assistant.git
cd fish-ecology-assistant

# 安装依赖
pip install -e .
```

**依赖**：Python ≥ 3.10，PyYAML ≥ 6.0。

---

## 快速开始

```python
from src import get_orchestrator

orch = get_orchestrator()

# KB-First 查询：先查本地知识库，不发起网络请求
result = orch.kb_first_lookup(query="鳤")
print(result.summary_text)
```

```bash
# 命令行查询
python src/dao_engine.py "珠星三块鱼"
python src/dao_engine.py "Tribolodon hakonensis"
python src/dao_engine.py --search "鳤"   # 自动全量搜索
```

---

## 核心功能

### 1. KB-First 两阶段搜索

核心设计模式：**知识库优先，按需搜索**。避免对已知物种重复全量检索。

```python
from src.orchestrator import get_orchestrator

orch = get_orchestrator()

# 阶段 1：知识库查询（零网络开销）
result = orch.kb_first_lookup(query="Ochetobius elongatus")
print(result.found)               # True / False
print(result.scientific_name)     # 规范学名
print(result.family)              # 科属
print(result.aliases)             # 别名列表
print(result.synonyms)            # 同义名列表
print(result.ecology)             # 生态习性
print(result.distribution)        # 分布流域/国家
print(result.summary_text)        # 可读摘要
print(result.search_recommendation)  # "stay_in_kb" | "continue_to_c"

# 阶段 2：委托全量搜索（仅当知识库信息不足）
if result.search_recommendation == "continue_to_c":
    hub = orch.hub
    full_result = hub.cognitive.search("Ochetobius elongatus")
```

**KbFirstResult 字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `found` | `bool` | 是否在知识库中找到 |
| `scientific_name` | `str` | 规范学名 |
| `chinese_name` | `str` | 中文名 |
| `aliases` | `List[str]` | 别名 |
| `synonyms` | `List[str]` | 分类学同义名 |
| `family` | `str` | 科属 |
| `order` | `str` | 目 |
| `conservation` | `str` | IUCN/保护级别 |
| `ecology` | `str` | 生态习性 |
| `distribution` | `dict` | 分布信息（continents/countries/basins） |
| `summary_text` | `str` | 可读摘要 |
| `search_recommendation` | `str` | `"stay_in_kb"` / `"continue_to_c"` |

### 2. 项目管理中枢

```python
from src.project_hub import get_hub

hub = get_hub()

# 健康检查
print(hub.health_all())

# 三角核心完整性
print(hub.is_triangle_complete())   # fish + cognitive + eon-core 全部可用？

# 跨项目委托
result = hub.delegate_to("coilia", "耳石微化学分析", species="Coilia nasus")

# 访问子系统
hub.cognitive.search("Acipenser sinensis")   # cognitive-search-engine
hub.eon                                       # eon-core 协调内核
hub.porpoise                                  # P₁ 江豚专研
hub.coilia                                    # P₂ 刀鲚专研
hub.conflict                                  # C 冲突仲裁
```

### 3. 可信度评分

```python
from src.adapter import FishEcologyAdapter

adapter = FishEcologyAdapter()

papers = [
    {"title": "...", "journal": "水生生物学报", "doi": "10.xxx/yyy", "pmid": "12345678"},
    {"title": "...", "journal": "bioRxiv", "doi": "10.xxx/zzz"},
]

scored = adapter.score_credibility(papers)
for p in scored:
    print(f"{p['credibility_score']:3d} {p['flag']} | {p.get('title', '?')[:50]}")
```

**评分规则：**
- 基线 50 分
- 期刊在 SCI 白名单中 +30 分
- 期刊在北大核心/CSCD 白名单中 +25 分
- 有 DOI +10 分
- 有 PMID +10 分
- 预印本（bioRxiv/Research Square/SSRN） -30 分
- ≥80 → 🟢 高可信度 / ≥60 → 🟡 中可信度 / <60 → 🟠 需交叉验证

### 4. 分类变更回写

cognitive-search-engine 检测到分类学不一致时，自动写回 fish-ecology-assistant 知识库。

```python
adapter.update_taxonomy(
    species_name="Pseudaspius hakonensis",
    discrepancy={
        "field": "family",
        "c_project_value": "Leuciscidae",
        "f_project_value": "Cyprinidae",
        "note": "Tribolodon → Pseudaspius 属级变更 (Sakai et al., 2020)",
        "evidence": ["10.1007/s10228-020-00768-y"],
        "action_required": True,
    },
)
```

### 5. 文献搜索脚本

```bash
# 图谱缓存查询 + 三角评分
python scripts/run_lit_search.py "珠星三块鱼"

# 全量搜索模式
python scripts/run_lit_search.py "Pseudaspius hakonensis" --mode exhaustive

# 表格输出
python scripts/run_lit_search.py "鳤" --format table --n 20

# JSON 导出
python scripts/run_lit_search.py "鲢" --format json --output result.json
```

---

## 项目结构

```
fish-ecology-assistant/
├── src/                        # 源代码
│   ├── __init__.py             # 公共 API 导出（get_orchestrator, get_hub）
│   ├── orchestrator.py         # 主入口：KB-First 搜索 + KbFirstResult
│   ├── project_hub.py          # 跨项目协调中枢
│   ├── adapter.py              # 适配器：物种查询 + 可信度评分 + 分类回写
│   ├── shared.py               # 共享工具：期刊白名单、OCR变体生成
│   └── dao_engine.py           # CLI 可执行引擎（道→一→二→三→万物）
│
├── config/                     # 配置文件
│   ├── agent.yaml              # Agent 行为配置
│   ├── fish_species_kb.yaml     # 多流域鱼类物种知识库（443+ 物种）
│   ├── component_registry.yaml # 组件注册表
│   ├── coordination.yaml       # 跨项目协调通路定义
│   ├── evolution.yaml          # 自进化参数
│   └── models.yaml             # 模型配置
│
├── scripts/                    # 可执行脚本
│   ├── search_species.py       # 物种搜索
│   └── run_lit_search.py       # 文献搜索（图谱 → 评分 → 交互展开）
│
├── tests/                      # 测试
│   ├── test_orchestrator.py    # 主入口测试（9 项）
│   ├── test_project_hub.py     # 中枢测试
│   └── test_shared.py          # 共享工具测试
│
├── docs/                       # 文档
│   ├── ARCHITECTURE.md         # 架构说明
│   ├── SKILL_PIPELINE.md       # Skill 执行管线
│   ├── WORKFLOWS.md            # 工作流说明
│   └── 刘凯课题组成果回写_20260613.md  # 课题组成果记录
│
├── research_output/            # 研究报告输出
│
├── pyproject.toml              # Python 项目配置
├── CHANGELOG.md                # 变更日志
├── CONTRIBUTING.md             # 贡献指南
├── GUIDE.md                    # 使用指南
└── LICENSE                     # MIT 许可证
```

---

## 配置文件说明

| 文件 | 用途 |
|------|------|
| `config/agent.yaml` | Agent 行为配置：版本号、Pipeline 阶段、子智能体清单 |
| `config/fish_species_kb.yaml` | 多流域鱼类知识库：长江 443 种 + 图们江/绥芬河物种数据 |
| `config/component_registry.yaml` | 组件注册表：各引擎/模块的入口和配置 |
| `config/coordination.yaml` | 跨项目协调：三角核心通路定义（P0-P7） |
| `config/evolution.yaml` | 自进化参数：搜索模式自动调整策略 |
| `config/models.yaml` | 模型配置：DeepSeek/其他 LLM 参数 |

---

## 数据来源

| 流域 | 来源 | 物种数 |
|------|------|--------|
| **长江** | 长江水生生物资源与环境本底状况调查 (2017-2021) | 443 历史种 / 323 采集种 |
| **图们江/绥芬河** | 东北亚溯河洄游鱼类分布数据 | 持续更新中 |
| **其他流域** | 珠江、黑龙江等 | 持续扩充中 |

---

## 三角核心架构

本系统是 workspace 的 **S/V0 知识供给层**，与其他项目协作构成三角闭环：

```
fish-ecology-assistant (S/V0 知识供给)
        ↕ 两阶段搜索 + 可信度评分反馈
cognitive-search-engine (V/V1 搜索验证)
        ↕ 协调路由
eon-core (三角核心·协调中枢)
        ↓ 赋能衍生
porpoise-agent (P₁ 江豚) · coilia-agent (P₂ 刀鲚) · conflict-arbiter (C 仲裁)
```

**关键通路：**
- **P1** `fish → cognitive`：知识库物种查询委托搜索
- **P2** `cognitive → fish`：搜索结果可信度评分 + 分类变更回写
- **P0** `eon → all`：协调路由 + 资源分配

---

## 测试

```bash
# 运行全部测试
pytest tests/ -v

# 特定测试模块
pytest tests/test_orchestrator.py -v
pytest tests/test_project_hub.py -v
pytest tests/test_shared.py -v
```

---

## API 参考

### 快速查阅

```python
from src import get_orchestrator, get_hub, FishEcologyAdapter

# 知识库查询
orch = get_orchestrator()
result = orch.kb_first_lookup(query="鳤")

# 跨项目协调
hub = get_hub()
hub.cognitive.search("Acipenser sinensis")
hub.is_triangle_complete()

# 可信度评分 + 分类回写
adapter = FishEcologyAdapter()
scored = adapter.score_credibility(papers)
adapter.update_taxonomy("Pseudaspius hakonensis", discrepancy)
```

### 完整方法参考

**FishEcologyOrchestrator** (`src/orchestrator.py`)

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `kb_first_lookup(query)` | `KbFirstResult` | KB-First 查询（零网络开销） |
| `search_species(name, mode)` | `dict` | 统一物种搜索入口 |
| `delegate_to(subsystem, task)` | `dict` | 跨项目委托 |
| `health()` | `dict` | 健康状态检查 |
| `info()` | `dict` | 版本和能力清单 |

**ProjectHub** (`src/project_hub.py`)

| 属性/方法 | 说明 |
|-----------|------|
| `hub.cognitive` | cognitive-search-engine 适配器 |
| `hub.eon` | eon-core 协调内核 |
| `hub.porpoise` | P₁ 江豚专研 |
| `hub.coilia` | P₂ 刀鲚专研 |
| `hub.conflict` | C 冲突仲裁 |
| `hub.is_triangle_complete()` | 三角核心是否完整 |
| `hub.health_all()` | 全部子系统健康状态 |
| `hub.delegate_to(subsystem, task)` | 跨项目任务委托 |

**FishEcologyAdapter** (`src/adapter.py`)

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `search(query)` | `dict` | 物种搜索（两层级回退） |
| `score_credibility(papers)` | `List[dict]` | 论文可信度评分 |
| `update_taxonomy(name, discrepancy)` | `dict` | 分类变更回写知识库 |
| `health()` | `dict` | 健康检查 |
| `info()` | `dict` | 版本和能力清单 |

---

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT License © 2026 fangtaocai041
