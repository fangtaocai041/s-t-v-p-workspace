# Fish Ecology Assistant 🐟

**鱼类生态学知识供给引擎** — 多流域物种知识库 + 两阶段文献搜索 + 三角验证评分。

[中文版](README.zh.md) | [变更日志](CHANGELOG.md) | [参与贡献](CONTRIBUTING.md)

---

## 快速开始

`ash
# 安装
pip install -e .

# 查询物种
python -c "from src import get_orchestrator; o = get_orchestrator(); print(o.kb_first_lookup(query='鳤').summary_text)"
`

## 核心功能

### 🧬 KB-First 两阶段搜索

`python
from src.orchestrator import get_orchestrator

orch = get_orchestrator()

# 阶段 1 — 知识库优先查询
result = orch.kb_first_lookup(query="Ochetobius elongatus")
print(result.found)              # True/False
print(result.scientific_name)    # 学名
print(result.summary_text)       # 可读摘要
print(result.search_recommendation)  # "stay_in_kb" 或 "continue_to_c"

# 阶段 2 — 按需委托全量搜索（仅当 KB 信息不足时）
if result.search_recommendation == "continue_to_c":
    from src.project_hub import get_hub
    hub = get_hub()
    full_search = hub.delegate_to("cognitive", {"query": "Ochetobius elongatus"})
`

### 🏠 项目管理中枢

`python
from src.project_hub import get_hub

hub = get_hub()
print(hub.health_all())       # 全项目健康状态
print(hub.is_triangle_complete())  # 三角核心是否完整
print(hub.relationship_map())     # ASCII 架构图
`

### 🔍 物种知识库查询

`python
from src.adapter import FishEcologyAdapter

adapter = FishEcologyAdapter()
profile = adapter.lookup_species("Cyprinus carpio")
print(profile.scientific_name, profile.family, profile.credibility_score)
`

### ⚙️ Dao 引擎（CLI 工具）

`ash
python src/dao_engine.py "珠星三块鱼"
python src/dao_engine.py "Tribolodon hakonensis"
`

## 项目架构

`
fish-ecology-assistant/
├── src/
│   ├── __init__.py         # 公共 API 导出
│   ├── orchestrator.py     # 主入口 API 层 (KB-First 两阶段搜索)
│   ├── project_hub.py      # 多项目协调中枢
│   ├── adapter.py          # FishEcologyAdapter 适配器
│   ├── shared.py           # 共享工具 (期刊白名单/OCR变体/搜索查询)
│   └── dao_engine.py       # Dao 可执行引擎
├── config/
│   └── fish_species_kb.yaml.bak  # 物种知识库 (443+ 物种)
├── scripts/                # 实用脚本
├── tests/                  # 测试套件
├── research_output/        # 研究报告输出
├── pyproject.toml           # 项目配置
└── CHANGELOG.md             # 版本历史
`

## 配置文件

| 文件 | 作用 |
|------|------|
| config/fish_species_kb.yaml.bak | 多流域鱼类物种知识库（长江 443 种 + 图们江/绥芬河） |
| pyproject.toml | Python 项目元数据与依赖 |

## 数据来源

- **长江流域**: 长江水生生物资源与环境本底状况调查 (2017-2021), 443 历史种 / 323 采集种
- **图们江/绥芬河**: 东北亚溯河洄游鱼类分布数据
- **其他流域**: 持续扩充中（珠江、黑龙江等）

## 三角核心架构

本系统是 **Triangle Core** 的 S/V0 知识供给层：

`
┌─────────────────────────────────────┐
│  S (知识供给) ←──→ V (搜索验证)     │
│  fish-ecology-    cognitive-search-  │
│  assistant        engine             │
│        ↕            ↕                │
│  T (三角核心) — eon-core             │
└─────────────────────────────────────┘
`

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT
