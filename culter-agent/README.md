# Culter Agent 🐟

**P₃ 万物衍生** — 鲌类专研 · 基因组 · 年龄生长 · 同域共存。

> 万物皆变 · Panta Rhei
>
> 翘嘴鲌、蒙古鲌、尖头鲌、红鳍原鲌……
> 同一条江水里，它们怎么分享同一张餐桌？

[English](README.md) · [中文版](README.zh.md) · [更新日志](CHANGELOG.md)

---

## 核心哲学

> 世界是动态的，知识是暂时的，涌现是常态。

P₃ 是从三角核心衍生的第三个项目。它依赖 S/V0 的物种知识、V/V1 的搜索验证、Coordinator 的协调调度。P₃ 只做一件事：**研究鲌类**。

### 在万物中的角色

```
三生万物架构：
  三角核心 (sealed 3)             → 基础能力
    ├── S/V0  fish-ecology-assistant
    ├── V/V1  cognitive-search-engine
    └── Coord eon-core
  
  万物衍生 (open N):
    P₁  porpoise-agent  → 江豚专研
    P₂  coilia-agent    → 刀鲚专研
    P₃  culter-agent    → 鲌类专研  ← 你在这里
    C   conflict-arbiter → 冲突仲裁
```

---

## 这个项目是什么

鲌属（*Culter*）是长江中上游最常见的经济鱼类之一。翘嘴鲌、蒙古鲌、尖头鲌——它们形态相似、食性重叠、分布同域。它们是怎么共存的？是食物生态位分化、还是时空资源分割？

这个项目通过几何形态测量、稳定同位素（δ¹³C, δ¹⁵N）、肠道内含物分析和基因组学来回答这些问题。

> 赫拉克利特说：人不能两次踏进同一条河流。
>
> 我们说：但五条鲌鱼可以——只要每条鱼都有自己的生态位。

---

## 快速上手

```bash
# CLI 入口
python src/main.py --help

# 鲌类物种评估
python -c "from src.adapter import CulterAdapter; a = CulterAdapter(); print(a.health())"
```

---

## 核心能力

| 能力 | 说明 |
|:-----|:------|
| **几何形态测量** | landmark 分析 + Procrustes 叠印 |
| **稳定同位素** | δ¹³C, δ¹⁵N → 营养生态位 |
| **肠道内含物** | 食性组成 + 重叠指数 |
| **基因组** | RAD-seq / SNP 标记 |
| **同域共存** | 生态位分化 + 时空资源分割 |

---

> 鱼在水里，你在岸上，代码在中间。
> 愿每条鱼都有自己的生态位。
>
> **最后更新: 2026-06-21 · Reasonix Code · DeepSeek 驱动**
