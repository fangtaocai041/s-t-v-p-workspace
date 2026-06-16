<p align="center">
  🇬🇧 <a href="#english">English</a> · 🇨🇳 <a href="README.zh.md">中文</a>
</p>

<div align="center">
  <h1>🐟 Coilia Agent — 刀鲚专研 (P₂)</h1>
  <p><strong>三角闭环衍生项目 · 刀鲚 (Coilia nasus) 专研</strong></p>
  <p>8 分析脚本 · 5 SKILLs · 5 测试套件 · DirectLoader · 知识库</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/version-1.3.0-ec4899?style=flat-square" alt="v1.3.0"></a>
  <a href="#"><img src="https://img.shields.io/badge/scripts-8-f59e0b?style=flat-square" alt="Scripts:8"></a>
  <a href="#"><img src="https://img.shields.io/badge/skills-5-8b5cf6?style=flat-square" alt="Skills:5"></a>
  <a href="#"><img src="https://img.shields.io/badge/tests-5_suites-22c55e?style=flat-square" alt="Tests:5"></a>
</p>

---

## 目录

- [项目简介](#项目简介)
- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [分析脚本](#分析脚本)
- [CLI 命令](#cli-命令)
- [API 参考](#api-参考)
- [项目架构](#项目架构)
- [知识库](#知识库)
- [关联项目](#关联项目)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

**Coilia Agent** 是三角闭环的 **P₂ 衍生项目**，专研刀鲚 *Coilia nasus*（长江刀鱼）——"长江三鲜"之首。提供 8 个纯 Python 实现的分析脚本，覆盖群体遗传学、耳石微化学、洄游生态、食性分析、资源评估等研究方向。

### 核心能力

| 能力 | 说明 |
|------|------|
| 🧬 **群体遗传学** | 微卫星 (Ho/He/Fst) + 线粒体 (Hd/π) + SNP 群体分化，纯 Python |
| 🏷️ **耳石微化学** | Sr/Ca 比洄游履历重建，淡水/半咸水/海水三态分类 |
| 🌊 **洄游生态** | 溯河路线重建、水利工程影响评估、产卵场适宜性评分 |
| 🍽️ **食性分析** | 胃含物 (F%/N%/IRI) + 稳定同位素 (δ¹³C/δ¹⁵N) + 营养级 + 生态位宽度 |
| 📊 **资源评估** | CPUE 标准化 + Schaefer 剩余产量模型 + MSY 计算 |
| 🔍 **6 步文献搜索** | 精确名→宽网→OCR 变体→合并去重→5 方向分类→格式化输出 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/fangtaocai041/coilia-agent.git
cd coilia-agent
pip install -e .
```

### CLI 基本用法

```bash
# 执行刀鲚研究查询
coilia run --query "刀鲚洄游群体遗传结构"

# 查看帮助
coilia --help
```

### 验证安装

```python
from coilia_agent.src.adapter import CoiliaAdapter, get_adapter

adapter = get_adapter()
print(adapter.health())
# 输出: {'status': 'HEALTHY', 'species': 'Coilia nasus', ...}

info = adapter.info()
print(f"研究方向: {info['research_themes']}")
```

---

## 核心功能

### 1. 群体遗传学分析

```python
from scripts.genetics_analysis import analyze_microsatellite, analyze_mtDNA

# 微卫星分析
ms_result = analyze_microsatellite(
    loci=["Coil-1", "Coil-2", "Coil-3"],
    genotypes={"POP_A": [...], "POP_B": [...]},
)
print(f"Ho={ms_result.ho:.3f}, He={ms_result.he:.3f}")
print(f"Fst={ms_result.fst:.3f}")

# 线粒体单倍型分析
mt_result = analyze_mtDNA(sequences=[...])
print(f"单倍型多样性 Hd={mt_result.hd:.3f}, 核苷酸多样性 π={mt_result.pi:.4f}")
```

### 2. 耳石微化学与洄游履历

```python
from scripts.migration_analysis import analyze_otolith_sr_ca

# 耳石 Sr/Ca 比分析（淡水<1.5, 半咸水1.5-3.0, 海水>3.0）
result = analyze_otolith_sr_ca(
    sr_ca_ratios=[0.8, 1.2, 2.1, 3.5, 4.2, 3.8, 1.5, 0.9],
    distance_from_core_mm=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
)
print(f"淡水相: {result.freshwater_pct:.1f}%")
print(f"半咸水相: {result.brackish_pct:.1f}%")
print(f"海水相: {result.marine_pct:.1f}%")
```

### 3. 食性与营养生态位

```python
from scripts.feeding_analysis import analyze_stomach_content, calculate_trophic_level

# 胃含物分析（出现率 F%、数量百分比 N%、IRI 指数）
stomach_result = analyze_stomach_content(
    prey_items=[
        {"species": "日本沼虾", "count": 15, "occurrence": 8},
        {"species": "小鱼", "count": 5, "occurrence": 4},
    ],
    total_stomachs=10,
)
print(stomach_result.top_prey[:3])

# 营养级计算
trophic = calculate_trophic_level(d15n_value=15.2, baseline=8.5, tef=3.4)
print(f"营养级: {trophic.level:.1f}")
```

### 4. 资源评估

```python
from scripts.stock_assessment import standardize_cpue, schaefer_model

# CPUE 标准化
cpue = standardize_cpue(years=[2015, 2016, 2017, 2018, 2019, 2020],
                        catch=[120, 95, 80, 65, 50, 35],
                        effort=[100, 95, 90, 85, 80, 75])

# Schaefer 剩余产量模型
result = schaefer_model(cpue_ts=cpue, r_init=0.5, k_init=5000)
print(f"内禀增长率 r={result.r:.3f}, 环境容量 K={result.k:.0f}")
print(f"MSY={result.msy:.1f}")
```

### 5. 6 步文献搜索

```bash
# 完整 6 步搜索协议
python scripts/literature_search.py --query "Coilia nasus otolith"

# 指定研究主题
python scripts/literature_search.py --query "刀鲚洄游" --theme migration

# JSON 输出
python scripts/literature_search.py --query "Coilia nasus" --json --output results.json

# 查看搜索示例
python scripts/literature_search.py --example
```

---

## 分析脚本

| 脚本 | 行数 | 用途 | 独立运行 |
|:-----|:----:|:-----|:--------:|
| `scripts/literature_search.py` | 354 | 6 步搜索协议 | `--query "..."` |
| `scripts/migration_analysis.py` | 322 | 洄游生态 + 耳石微化学 | `--example` |
| `scripts/genetics_analysis.py` | 479 | 群体遗传学 | `--example` |
| `scripts/feeding_analysis.py` | 455 | 食性 + 稳定同位素 | `--example` |
| `scripts/stock_assessment.py` | 430 | CPUE + Schaefer MSY | `--cpue data.csv` |
| `scripts/early_life_analysis.py` | 416 | 早期资源 + 产卵场 | `--example` |
| `scripts/species_kb.py` | 137 | 知识库查询 | `--theme genetics` |
| `scripts/fish_kb_add_species.py` | 124 | 知识入库 → f 项目 | `--dry-run` |

```bash
# 每个脚本有 --example 演示模式
python scripts/genetics_analysis.py --example
python scripts/feeding_analysis.py --example
python scripts/migration_analysis.py --example
```

---

## CLI 命令

```bash
coilia run --query "研究问题"    # 执行刀鲚研究查询
coilia --help                    # 查看帮助
```

`run` 子命令输出搜索参数（物种约束 + 研究方向 + 协议引用），实际搜索由 cognitive-search-engine 执行。

---

## API 参考

### `src/adapter.py` — 跨项目接口

| 方法 | 说明 |
|------|------|
| `search(query)` | 接收查询 → 输出物种约束 + 研究方向参数 |
| `analyze(phase, search_result)` | 搜索结果 → P₂ 领域专研分析 |
| `health()` | 健康状态 |
| `info()` | 能力清单 |

### `src/agent/orchestrator.py`

| 方法 | 说明 |
|------|------|
| `run(query)` | 解析查询 → 确定研究方向 → 返回搜索参数 |

---

## 项目架构

```
coilia-agent/
├── README.md / README.zh.md     ← 中英文说明
├── pyproject.toml                ← 项目元数据 + coilia CLI 入口
├── Dockerfile                    ← python:3.11-slim 容器化
│
├── src/                          ← Python 源码包
│   ├── __init__.py               ← 版本号 v1.2.0
│   ├── main.py                   ← CLI 入口 (argparse)
│   ├── adapter.py                ← CoiliaAdapter (IProjectAdapter)
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   └── orchestrator.py       ← CoiliaOrchestrator
│   │
│   └── prompts/
│       └── system_prompts.py     ← 系统提示词
│
├── scripts/                      ← 可执行分析脚本 (8个，纯 Python/无外部统计库)
│   ├── literature_search.py      ← 6步搜索协议
│   ├── migration_analysis.py     ← 洄游生态 + 耳石微化学
│   ├── genetics_analysis.py      ← 群体遗传学
│   ├── feeding_analysis.py       ← 食性与营养生态
│   ├── stock_assessment.py       ← 资源评估 (CPUE+MSY)
│   ├── early_life_analysis.py    ← 早期资源 + 产卵场评分
│   ├── species_kb.py             ← 知识库查询
│   └── fish_kb_add_species.py    ← 知识入库
│
├── data/                         ← 数据
│   └── knowledge_base/species/
│       └── coilia-nasus.md       ← 刀鲚物种知识库
│
├── config/                       ← 配置文件
│   ├── agent.yaml                ← Agent 配置 v1.3.0
│   └── component_registry.yaml   ← 组件注册表
│
├── skills/                       ← Skill 定义 (5个)
│   ├── analyze-feeding/SKILL.md
│   ├── analyze-genetics/SKILL.md
│   ├── analyze-migration/SKILL.md
│   ├── assess-stock/SKILL.md
│   └── search-literature/SKILL.md
│
├── tests/                        ← 测试套件 (5个)
│   ├── test_analysis_scripts.py  ← 分析脚本单元测试
│   ├── test_coilia.py            ← 接口合规集成测试
│   ├── test_scripts.py           ← 知识库测试
│   ├── test_triangle_integration.py  ← 三角闭环集成测试
│   └── triangle_flow.py          ← 闭环流程演示
│
├── CHANGELOG.md                  ← 版本历史
├── CONTRIBUTING.md               ← 贡献指南
└── LICENSE                       ← MIT
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `src/adapter.py` | 跨项目通信协议 — 实现 IProjectAdapter 接口 |
| `src/agent/orchestrator.py` | 领域分析引擎 — 查询解析 + 研究方向路由 |
| `scripts/` | 8 个独立可执行分析脚本，零外部统计库依赖 |
| `data/knowledge_base/` | 刀鲚物种知识库（保护现状、生物学、研究方法、文献） |
| `skills/` | 5 个 Skill 定义供 Reasonix Agent 调用 |
| `tests/` | 5 个测试套件 + 1 个闭环流程演示 |

---

## 知识库

### `data/knowledge_base/species/coilia-nasus.md`

包含刀鲚的完整物种档案：

| 字段 | 内容 |
|------|------|
| 保护等级 | IUCN 濒危(EN), 中国红皮书名录濒危, 2021 全面禁捕 |
| 生物学 | 最大体长 41cm, 寿命 4-5 年, 溯河洄游, 产卵期 4-6 月 |
| 洄游 | 溯河期 2-4 月, 历史范围 长江口→洞庭湖, 关键障碍 三峡/葛洲坝 |
| 文化价值 | "长江三鲜之首", 曾达 ¥8000-10000/斤 |
| 近缘种 | 短颌鲚 (C. brachygnathus, 淡水定居), 凤鲚 (C. mystus, 沿海) |
| 资源趋势 | 1973 年 3750t 峰值 → 当前仅 1-3% |
| 研究方向 | 5 个方向: 耳石微化学 / 遗传 / 资源 / 早期资源 / 食性 |

---

## 关联项目

| 项目 | 角色 | 关系 |
|------|------|------|
| **fish-ecology-assistant** | 知识供给 V0 | 知识库回写目标 (`fish_kb_add_species.py`) |
| **cognitive-search-engine** | 搜索验证 V1 | 文献搜索结果来源 |
| **eon-core** | 协调内核 | 三角核心协调器 |
| **porpoise-agent** | P₁ 江豚 | 同级衍生项目 (姊妹 Agent) |
| **culter-agent** | P₃ 鲌类 | 同级衍生项目 |

---

## 贡献指南

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/xxx`
3. 提交变更：`git commit -m "描述"`
4. 推送分支：`git push origin feature/xxx`
5. 创建 Pull Request

### 运行测试

```bash
cd coilia-agent
python -m pytest tests/ -v
```

### 代码规范

- 纯 Python 实现（零 NumPy/SciPy/R 依赖）
- 每个分析脚本需支持 `--example` 演示模式
- 新增功能需对应 SKILL.md 更新

---

## 许可证

MIT License © 2026

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
