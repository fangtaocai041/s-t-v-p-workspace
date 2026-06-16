<p align="center">
  🇬🇧 <a href="README.md">English</a>
</p>

<div align="center">
  <h1>🐟 Culter Agent — 鲌类专研 (P₃)</h1>
  <p><strong>三角闭环衍生项目 · P₃ 鲌类专研</strong></p>
  <p>8 Skills · DirectLoader 认知搜索 · 知识库 · 9 阶段管线</p>
  <p>🤝 同级项目: <a href="../porpoise-agent/">porpoise-agent (P₁ 江豚)</a> · <a href="../coilia-agent/">coilia-agent (P₂ 刀鲚)</a></p>
  <p>🧠 协调器: <a href="../eon-core/">eon-core</a></p>
</div>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/skills-8-f59e0b?style=flat-square" alt="Skills:8"></a>
  <a href="../VERSION.yaml"><img src="https://img.shields.io/badge/workspace-v8.1.0-6366f1?style=flat-square" alt="Workspace:v8.1.0"></a>
  <a href="config/agent.yaml"><img src="https://img.shields.io/badge/agent-v2.0.0-ec4899?style=flat-square" alt="Agent:v2.0.0"></a>
</p>

## 架构角色: **衍生项目 P₃ (鲌类专研)**

> **三角核心**: fish(知识 V0) + cognitive(验证 V1) + eon-core(协调 T)
> **P₃** 从三角核心衍生，依赖三角提供物种知识和文献搜索。
> 鲌类专属: 基因组学、年龄生长、稳定同位素生态、同域共存、资源评估。

## 目标物种

| 物种 | 学名 | 分类 |
|------|------|------|
| 翘嘴鲌 (白鱼/翘壳) | *Culter alburnus* | 鲤科 > 鲌亚科 |
| 蒙古鲌 (蒙古红鲌) | *Culter mongolicus* | 鲤科 > 鲌亚科 |
| 尖头鲌 | *Culter oxycephalus* | 鲤科 > 鲌亚科 |
| 红鳍原鲌 | *Chanodichthys erythropterus* | 鲤科 > 鲌亚科 |

## 9 阶段管线

```
文献调研 → 年龄生长 → 基因组学 → 群体遗传 → 营养生态位 → 同域共存 → 资源评估 → 栖息地建模 → 报告生成
```

## 技能 (8)

| 技能 | 描述 |
|------|------|
| `search-literature` | 中英双语文献检索 (通过 cognitive DirectLoader) |
| `analyze-growth` | 年龄鉴定与 von Bertalanffy 生长建模 |
| `analyze-genomics` | 全基因组/RAD-seq 组装、比较基因组学 |
| `analyze-genetics` | 群体遗传学、谱系地理、基因流 |
| `analyze-trophic` | δ¹³C/δ¹⁵N 稳定同位素、MixSIAR 混合模型 |
| `model-coexistence` | 生态位分化量化、共存机制 |
| `assess-resource` | CPUE 标准化、MSY 估算、YPR 分析 |
| `model-habitat` | HSI 栖息地适宜性建模、产卵场评估 |

## 快速开始

```bash
# 通过 project_loader 加载
python -c "from scripts.project_loader import get_culter; a=get_culter(); print(a.info())"

# 通过 coordinator 健康检查
python -c "from scripts.coordinator import coordinator; print(coordinator.health('culter'))"

# 独立运行
python culter-agent/src/main.py --query "翘嘴鲌 年龄与生长"
```

## 目录结构

```
culter-agent/
├── config/agent.yaml              # Agent 配置 (v2.0.0)
├── data/knowledge_base/           # 物种知识库
├── src/
│   ├── adapter.py                 # IProjectAdapter → CulterAdapter
│   ├── agent/orchestrator.py      # 9 阶段管线编排器
│   ├── skills/                    # 8 个技能模块
│   ├── prompts/                   # 系统提示词
│   └── main.py                    # CLI 入口
└── README.md
```

## 关联项目

| 项目 | 角色 | 关系 |
|------|------|------|
| [eon-core](../eon-core/) | 协调内核 (T) | 通过 DAG 拓扑协调 P₃ |
| [fish-ecology-assistant](../fish-ecology-assistant/) | 知识供给 V0 | 提供物种档案与可信度评分 |
| [cognitive-search-engine](../cognitive-search-engine/) | 搜索验证 V1 | 文献搜索与图谱遍历 |
| [porpoise-agent](../porpoise-agent/) | P₁ 江豚 | 同级衍生项目 |
| [coilia-agent](../coilia-agent/) | P₂ 刀鲚 | 同级衍生项目 (模板来源) |
| [conflict-arbiter](../conflict-arbiter/) | C 冲突仲裁 | 多源保护推荐冲突检测 |
