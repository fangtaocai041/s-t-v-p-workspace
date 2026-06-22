---
name: capabilities
description: 能力漫游与推荐 — 浏览工作空间所有能力，根据你的场景推荐最佳工具
runAs: inline
---

# /capabilities — 能力漫游

查看这个工作空间能做什么，获取场景化推荐。

## 核心能力一览

### 🔬 物种分析管线 (Phase 0-5)
| Phase | 名称 | 命令 | 输出 |
|:-----:|:-----|:-----|:-----|
| 0 | 物种画像 | `run_full_analysis.py` | 基本信息 + 生态概览 |
| 1 | 文献统计 | (自动) | 论文数/时间跨度/研究方向 |
| 2 | 趋势分析 | (自动) | 方法学跃迁 + Top 期刊 |
| 3 | 空白识别 | (自动) | 研究方向/地理/方法空白 |
| 4 | 涌现检测 | `cross_synthesis.py` | 跨物种涌现假说 |
| 5 | 假设推理 | `reasoning_engine.py` | 生态假设 + 验证方法 |

### 📚 文献搜索
| 能力 | 命令 |
|:-----|:-----|
| 物种文献搜索 | `search_species.py` |
| 全管线搜索 | `pipeline_search_species.py` |
| 三项目协作 | `run_fish_pipeline()` |

### 🧬 认知核心 (RCCA)
| 模块 | 用途 |
|:-----|:------|
| SelfModelEngine | 自我稳定性检测 |
| EmotionEngine | 资源分配策略 |
| TranspositionLayer | 跨域概念转座 |
| ReflectionLoop | 反思-转座-进化闭环 |

### 🧠 学科知识图谱 (12 领域)
数学 / 物理 / 化学 / 生物 / 计算机 / 心理学 / 哲学 / 中国哲学 / 马克思主义 / 经济学 / 文学 / 科幻

### 🛠️ 工程技能
| 技能 | 用途 |
|:-----|:------|
| `/grill-with-docs` | 面审 + 文档生成 |
| `/tdd` | 测试驱动开发 |
| `/diagnosing-bugs` | Bug 诊断 |
| `/triage` | Issue 分诊 |
| `/to-prd` | PRD 生成 |
| `/improve-codebase-architecture` | 架构优化 |

## 场景推荐

### 🎯 "我想研究一个物种"
→ 推荐: `/explore-workspace` → 物种画像管线

### 📝 "我有个模糊的研究想法"
→ 推荐: `/focus-research` → 逐步聚焦

### 🐟 "我不知道研究什么物种"
→ 推荐: `/discover-species` → 物种发现

### 🔧 "我想写代码改功能"
→ 推荐: `/grill-with-docs` → 面审 → `/tdd` → 实现

### 🐛 "有个bug搞不定"
→ 推荐: `/diagnosing-bugs` → 6 阶段诊断循环

### ❓ "还有什么我能做的？"
→ 这个页面就是答案 😄
