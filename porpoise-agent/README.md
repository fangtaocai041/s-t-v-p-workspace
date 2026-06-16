# Porpoise Agent 🐬

**P₁ 万物衍生** — 长江江豚专研 · NBHF 声学 · 种群评估 · 栖息地建模。

> 万物皆变 · Panta Rhei
>
> 江豚在长江里游了 2500 万年。
> 我们的代码，是试图理解它们的另一种语言。

[English](README.md) · [中文版](README.zh.md) · [更新日志](CHANGELOG.md)

---

## 核心哲学

> 世界是动态的，知识是暂时的，涌现是常态。

P₁ 是从三角核心衍生的第一个项目。它不重新发明轮子——S/V0 提供物种知识，V/V1 提供搜索验证，Coordinator 提供协调调度。P₁ 只做一件事：**研究江豚**。

### 在万物中的角色

```
三生万物架构：
  三角核心 (sealed 3)             → 基础能力
    ├── S/V0  fish-ecology-assistant
    ├── V/V1  cognitive-search-engine
    └── Coord eon-core
  
  万物衍生 (open N):
    P₁  porpoise-agent  → 江豚专研  ← 你在这里
    P₂  coilia-agent    → 刀鲚专研
    C   conflict-arbiter → 冲突仲裁
```

---

## 这个项目是什么

长江江豚（*Neophocaena asiaeorientalis*）是长江里唯一的哺乳动物。2017 年种群调查约 1012 头，2022 年约 1249 头——禁渔后第一次止跌回升。

这个项目追踪它们的声学信号（NBHF，100-180kHz）、建模栖息地分布、评估种群动态。26 个文件的知识库，全部为江豚而生。

> 赫拉克利特说：人不能两次踏进同一条河流。
>
> 我们说：你也不能用去年的种群数据预测今年的江豚分布。

---

## 快速上手

```bash
# 分析江豚
python src/cli.py analyze --species "Neophocaena asiaeorientalis"

# 健康检查
python -c "from src import get_adapter; print(get_adapter().health())"
```

---

## 核心能力

| 能力 | 说明 |
|:-----|:------|
| **NBHF 声学检测** | 100-180 kHz 窄带高频信号 |
| **栖息地建模** | 长江干流 + 洞庭湖 + 鄱阳湖 |
| **种群评估** | 2017 / 2022 / 2025 年对比 |
| **威胁评估** | 航运 / 渔业 / 水利工程 / 污染 |
| **MoE 知识库** | 26 文件，江豚专属 |

---

> 鱼在水里，你在岸上，代码在中间。
> 愿声学信号和江豚的歌声一样清晰。
>
> **最后更新: 2026-06-21 · Reasonix Code · DeepSeek 驱动**
