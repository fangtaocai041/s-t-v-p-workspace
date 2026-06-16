# Fish Ecology Assistant 🐟

**鱼类生态学知识供给引擎** — 多流域物种知识库 + 两阶段文献搜索 + 三角验证评分。

[English](README.md) · [更新日志](CHANGELOG.md) · [参与贡献](CONTRIBUTING.md)

---

## 快速开始

```bash
# 安装
pip install -e .

# 查询物种（先查知识库，再搜网络）
python -c "from src import get_orchestrator; o = get_orchestrator(); print(o.kb_first_lookup(query='鳤').summary_text)"

# 文献搜索
python scripts/run_lit_search.py "珠星三块鱼"
```

## 核心功能

### 🧬 KB-First 两阶段搜索

搜物种文献时，**先查本地知识库**（不花 token），不够再走全量搜索。

```python
from src.orchestrator import get_orchestrator

orch = get_orchestrator()
result = orch.kb_first_lookup(query="Ochetobius elongatus")
print(result.found)               # 知识库有没有？
print(result.summary_text)        # 已有信息的摘要
print(result.search_recommendation)  # "stay_in_kb" 或 "continue_to_c"
```

### 🔍 物种知识库

26 个长江物种的已知信息，涵盖分类、分布、食性、繁殖、保护级别。

```python
from src.adapter import FishEcologyAdapter

adapter = FishEcologyAdapter()
profile = adapter.lookup_species("Ochetobius elongatus")
print(profile.scientific_name, profile.family)
```

### 📚 方陶文库 — 个人研究空间

项目附带了用户 [蔡方陶](方陶文库/蔡方陶/) 的研究笔记和理论探索：

| 文件 | 内容 |
|:-----|:------|
| [研究札记](方陶文库/蔡方陶/01-研究札记.md) | 理论思考、3个假说、"非对称恢复假说" |
| [研究笔记](方陶文库/蔡方陶/02-研究笔记.md) | 想法池、问题池、理论雏形 |
| [分析报告](方陶文库/分析报告/) | 物种分析报告（珠星三块鱼、刀鲚等） |
| [理论体系](方陶文库/theories/) | 11个生态学理论笔记 |
| [中国生态哲学](方陶文库/chinese-ecology/) | 道家思想 × 生态科学 |
| [团队对比](方陶文库/国内国际团队对比分析.md) | 国内外鱼类生态研究团队全景 |

### ⚙️ 命令行工具

```bash
# 文献搜索
python scripts/run_lit_search.py "鳤"

# 知识库 ↔ 图谱同步
python scripts/kb_to_graph_sync.py

# 分类学变更回写
python scripts/taxonomy_sync.py

# 可信度评分
python scripts/credibility_scorer.py
```

## 项目架构

```
fish-ecology-assistant/
├── src/
│   ├── orchestrator.py     ← 协调器：KB-First 搜索入口
│   ├── project_hub.py      ← 项目中枢：跨项目委托
│   ├── adapter.py          ← 跨项目接口
│   ├── dao_engine.py       ← Dao 引擎 CLI
│   └── shared.py           ← 共享类型
├── scripts/                ← CLI 工具
├── config/                 # 知识库配置
├── data/                   # 知识库数据
├── docs/                   # 架构文档
└── tests/                  # 测试
```

## 三角角色

本系统是 Triangle Core 的 **S/V0 (知识供给)** 层：

```
S  fish-ecology-assistant  →   知识库 + KB-First 搜索
    ↓ state_vector
T  porpoise-agent          →   任务调度
    ↓ action_request
V  cognitive-search-engine →   搜索验证
    ↓ feedback_vector
S  …                       →   闭环
```

## 许可证

MIT © 2026 fangtaocai041
