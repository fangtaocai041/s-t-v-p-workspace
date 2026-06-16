<p align="center">
  🇨🇳 <a href="#chinese">中文</a> · 🇬🇧 <a href="README.md">English</a>
</p>

<div align="center">
  <h1>🐟 Culter Agent — 鲌类专研 (P₃)</h1>
  <p><strong>三角闭环衍生项目 · 鲌类 (Culter) 专研</strong></p>
  <p>8 Skills · 9-Phase Pipeline · 6 目标物种 · 知识库</p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/version-2.0.0-ec4899?style=flat-square" alt="v2.0.0"></a>
  <a href="#"><img src="https://img.shields.io/badge/skills-8-f59e0b?style=flat-square" alt="Skills:8"></a>
  <a href="#"><img src="https://img.shields.io/badge/pipeline-9_phase-22c55e?style=flat-square" alt="Pipeline:9"></a>
</p>

---

## 目录

- [项目简介](#项目简介)
- [快速开始](#快速开始)
- [分析管线](#分析管线)
- [Skills](#skills)
- [CLI](#cli)
- [API 参考](#api-参考)
- [项目架构](#项目架构)
- [知识库](#知识库)
- [关联项目](#关联项目)
- [许可证](#许可证)

---

## 项目简介

**Culter Agent** 是三角闭环的 **P₃ 衍生项目**，专研鲌属 (*Culter*) 鱼类，以翘嘴鲌 (*Culter alburnus*) 为主要研究对象。提供 9 阶段分析管线 + 8 个领域 Skills，覆盖基因组学、群体遗传学、年龄生长、营养生态、同域共存、栖息地建模、资源评估等方向。

### 目标物种

| 学名 | 中文名 | 说明 |
|------|--------|------|
| *Culter alburnus* | 翘嘴鲌 (大白鱼) | 主研 — 完整知识库 |
| *Culter mongolicus* | 蒙古鲌 | 相关物种 |
| *Culter oxycephalus* | 尖头鲌 | 相关物种 |
| *Chanodichthys erythropterus* | 红鳍原鲌 | 相关物种 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/fangtaocai041/culter-agent.git
cd culter-agent
pip install -e .
```

### CLI 使用

```bash
culter run --query "翘嘴鲌 年龄 生长参数"
culter run --query "Culter alburnus stable isotopes"
```

### 验证安装

```python
from culter_agent.src.adapter import get_adapter

adapter = get_adapter()
print(adapter.health())
print(adapter.info()["capabilities"])
```

---

## 分析管线

9 阶段管线（支持 standalone / integrated 双模式）：

| 阶段 | 名称 | 内容 |
|:----:|:-----|:-----|
| 1 | 物种识别 | 从查询文本检测目标物种 |
| 2 | 文献搜索 | 多引擎并行文献检索 |
| 3 | 基因组学 | 基因组组装、RAD-seq、转录组 |
| 4 | 群体遗传 | SSR/mtDNA/SNP 分析 |
| 5 | 年龄生长 | VBGF 参数、年轮鉴定 |
| 6 | 营养生态 | 稳定同位素、MixSIAR、生态位 |
| 7 | 同域共存 | 生态位分化、Pianka 重叠 |
| 8 | 栖息地 | HSI 建模 |
| 9 | 资源评估 | CPUE、YPR、MSY |

```python
from culter_agent.src.agent.orchestrator import CulterOrchestrator

orch = CulterOrchestrator()
result = orch.run("翘嘴鲌 稳定同位素 营养生态位")
print(f"物种: {result['species']}")
print(f"执行阶段: {result['phases']}")
```

---

## Skills

| Skill | 说明 |
|-------|------|
| `search-literature` | 多引擎并行文献搜索 |
| `analyze-genomics` | 基因组组装与分析 |
| `analyze-genetics` | SSR/mtDNA/SNP 群体遗传 |
| `analyze-growth` | 年龄鉴定、VBGF 参数 |
| `analyze-trophic` | 稳定同位素、MixSIAR、SIBER |
| `model-coexistence` | 生态位分化、Pianka 重叠 |
| `model-habitat` | HSI 栖息地适宜性建模 |
| `assess-resource` | CPUE 标准化、资源评估 |

---

## 项目架构

```
culter-agent/
├── src/
│   ├── adapter.py                ← 跨项目接口
│   ├── main.py                   ← CLI 入口
│   ├── knowledge_base.py         ← 物种知识库
│   └── agent/orchestrator.py     ← 9 阶段管线
├── src/skills/                   ← 8 个 SKILL.md
├── config/                       ← agent.yaml + component_registry.yaml
├── data/knowledge_base/          ← 翘嘴鲌知识库
├── scripts/shared_types.py       ← 共享类型
├── pyproject.toml                ← 项目元数据
└── Dockerfile                    ← 容器化
```

---

## 知识库

`data/knowledge_base/species/culter-alburnus.md` — 翘嘴鲌完整物种档案，12 个章节：

| 章节 | 内容 |
|:-----|:-----|
| 保护现状 | IUCN NE, 长江禁捕影响 |
| 生物学 | 最大 105cm/15kg, 寿命 15-20年 |
| 繁殖 | 成熟年龄 2-3, 产卵期 5-7月 |
| 栖息地 | 湖泊/水库/河流, 0-30m 水深 |
| 基因组 | ~1.0-1.2Gb, 2n=48, 测序进展 |
| 稳定同位素 | δ¹³C/δ¹⁵N, EA-IRMS, MixSIAR |
| 营养生态位 | 4 阶段食性转变, Levin 0.3-0.6 |
| 同域共存 | 3 个共存种对, 空间/食性/时间分化 |

---

## 关联项目

| 项目 | 角色 |
|:-----|:-----|
| fish-ecology-assistant | 知识供给 V0 |
| cognitive-search-engine | 搜索验证 V1 |
| eon-core | 协调内核 |
| porpoise-agent | P₁ 江豚 (姊妹项目) |
| coilia-agent | P₂ 刀鲚 (姊妹项目) |

## 许可证

MIT
