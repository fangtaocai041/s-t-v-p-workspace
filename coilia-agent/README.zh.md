# Coilia Agent 🐟

**P₂ 万物衍生** — 刀鲚专研 · 耳石微化学 · 洄游生态 · 资源评估。

> 🌊 万物皆变 · Panta Rhei
>
> 长江三鲜之首。每一条鱼耳石里的 Sr/Ca 比值，
> 都在诉说它一生的洄游路线。

[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![version](https://img.shields.io/badge/version-1.3.0-ec4899)]()
[![scripts](https://img.shields.io/badge/scripts-8-f59e0b)]()
[![skills](https://img.shields.io/badge/skills-5-8b5cf6)]()
[![tests](https://img.shields.io/badge/tests-5_suites-22c55e)]()

[English](README.md) · [中文](README.zh.md) · [更新日志](CHANGELOG.md)

---

## 📋 项目简介

**Coilia Agent** 是三角闭环的 **P₂ 衍生项目**，专研刀鲚 *Coilia nasus*（长江刀鱼）——"长江三鲜"之首。提供 8 个纯 Python 实现的分析脚本，覆盖群体遗传学、耳石微化学、洄游生态、食性分析、资源评估等研究方向。

### 🚀 核心能力

| 🚀 能力 | 📝 说明 |
|:---------|:--------|
| 🧬 群体遗传学 | 微卫星 + 线粒体 + SNP，纯 Python 实现 |
| 🏷️ 耳石微化学 | Sr/Ca 比洄游履历重建，淡水/半咸水/海水三态分类 |
| 🌊 洄游生态 | 溯河路线重建、水利工程影响评估、产卵场适宜性评分 |
| 🍽️ 食性分析 | 胃含物 + 稳定同位素 + 营养级 + 生态位宽度 |
| 📊 资源评估 | CPUE 标准化 + Schaefer 剩余产量模型 + MSY 计算 |
| 🔍 6 步文献搜索 | 精确名→宽网→OCR 变体→合并去重→5 方向分类→格式化 |

---

## ⚡ 快速开始

### 📦 安装

```bash
git clone https://github.com/fangtaocai041/coilia-agent.git
cd coilia-agent
pip install -e .
```

### 🎮 CLI 基本用法

```bash
coilia run --query "刀鲚洄游群体遗传结构"
coilia --help
```

### ✅ 验证安装

```python
from coilia_agent.src.adapter import get_adapter

adapter = get_adapter()
print(adapter.health())
```

---

## 🚀 核心功能

### 🧬 群体遗传学分析

```python
from scripts.genetics_analysis import analyze_microsatellite

ms_result = analyze_microsatellite(loci=["Coil-1", "Coil-2", "Coil-3"],
    genotypes={"POP_A": [...], "POP_B": [...]})
print(f"Ho={ms_result.ho:.3f}, He={ms_result.he:.3f}, Fst={ms_result.fst:.3f}")
```

### 🏷️ 耳石微化学与洄游履历

```python
from scripts.migration_analysis import analyze_otolith_sr_ca

result = analyze_otolith_sr_ca(
    sr_ca_ratios=[0.8, 1.2, 2.1, 3.5, 4.2, 3.8, 1.5, 0.9],
    distance_from_core_mm=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
print(f"淡水相: {result.freshwater_pct:.1f}%")
```

### 🍽️ 食性与营养生态位

```python
from scripts.feeding_analysis import calculate_trophic_level

trophic = calculate_trophic_level(d15n_value=15.2, baseline=8.5, tef=3.4)
print(f"营养级: {trophic.level:.1f}")
```

### 📊 资源评估

```python
from scripts.stock_assessment import schaefer_model

result = schaefer_model(cpue_ts=cpue_data, r_init=0.5, k_init=5000)
print(f"MSY={result.msy:.1f}")
```

### 🔍 6 步文献搜索

```bash
python scripts/literature_search.py --query "Coilia nasus otolith"
python scripts/literature_search.py --query "刀鲚洄游" --theme migration --json --output results.json
```

---

## 📁 分析脚本

| 📄 脚本 | 🎯 用途 | 🚀 运行方式 |
|:---------|:---------|:------------|
| `literature_search.py` | 6 步搜索协议 | `--query "..."` |
| `migration_analysis.py` | 洄游生态 + 耳石微化学 | `--example` |
| `genetics_analysis.py` | 群体遗传学 | `--example` |
| `feeding_analysis.py` | 食性 + 稳定同位素 | `--example` |
| `stock_assessment.py` | CPUE + Schaefer MSY | `--cpue data.csv` |
| `early_life_analysis.py` | 早期资源 + 产卵场 | `--example` |
| `species_kb.py` | 知识库查询 | `--theme genetics` |
| `fish_kb_add_species.py` | 知识入库 → f 项目 | `--dry-run` |

---

## 📁 项目架构

```
coilia-agent/
├── src/                          ← Python 源码
│   ├── adapter.py                ← 跨项目接口 (IProjectAdapter)
│   ├── main.py                   ← CLI 入口 (coilia run --query "...")
│   ├── agent/orchestrator.py     ← 领域分析引擎
│   ├── prompts/system_prompts.py ← 系统提示词
│   └── skills/                   ← 6 个 SKILL 模块
│       ├── search-literature/    ← 文献搜索
│       ├── analyze-genetics/     ← 群体遗传学
│       ├── analyze-migration/    ← 洄游生态 + 耳石微化学
│       ├── analyze-feeding/      ← 食性分析 + 稳定同位素
│       ├── assess-stock/         ← 资源评估
│       └── analyze-early-life/   ← 早期资源 + 产卵场
├── scripts/                      ← 8 个独立可执行分析脚本
├── data/knowledge_base/          ← 刀鲚物种知识库
├── config/                       ← agent.yaml + component_registry.yaml
├── tests/                        ← 测试套件
├── Dockerfile                    ← 容器化
└── pyproject.toml                ← 项目元数据 (coilia CLI)
```

---

## 📚 知识库

`data/knowledge_base/species/coilia-nasus.md` 包含刀鲚完整物种档案：

| 📋 字段 | 📝 内容 |
|:---------|:--------|
| 保护等级 | IUCN 濒危(EN), 中国红皮书名录濒危 |
| 生物学 | 最大体长 41cm, 寿命 4-5 年, 溯河洄游 |
| 洄游 | 溯河期 2-4 月, 关键障碍 三峡/葛洲坝 |
| 近缘种 | 短颌鲚 (淡水定居), 凤鲚 (沿海) |
| 资源趋势 | 1973 年 3750t 峰值 → 当前仅 1-3% |

---

## 🧪 运行测试

```bash
python -m pytest tests/ -v
```

## 📜 许可证

MIT

---

> 🌊 万物皆变 · Panta Rhei
>
> 🏛️ 赫拉克利特说：人不能两次踏进同一条河流。
>
> 💻 我们说：但一条刀鲚可以——只要河流还在。
>
> **📅 最后更新: 2026-06-21 · 🖥️ Reasonix Code · ⚡ DeepSeek 驱动**

[⬆ 回到顶部](#)
