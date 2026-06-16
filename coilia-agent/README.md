# Coilia Agent 🐟

**P₂ 万物衍生** — 刀鲚专研 · 耳石微化学 · 洄游生态 · 资源评估。

> 万物皆变 · Panta Rhei
>
> 长江三鲜之首。每一条鱼耳石里的 Sr/Ca 比值，
> 都在诉说它一生的洄游路线。

[English](README.md) · [中文版](README.zh.md) · [更新日志](CHANGELOG.md)

---

## 核心哲学

> 世界是动态的，知识是暂时的，涌现是常态。

P₂ 是从三角核心衍生的第二个项目。它依赖 S/V0 的物种知识、V/V1 的搜索验证、Coordinator 的协调调度。P₂ 只做一件事：**研究刀鲚**。

### 在万物中的角色

```
三生万物架构：
  三角核心 (sealed 3)             → 基础能力
    ├── S/V0  fish-ecology-assistant
    ├── V/V1  cognitive-search-engine
    └── Coord eon-core
  
  万物衍生 (open N):
    P₁  porpoise-agent  → 江豚专研
    P₂  coilia-agent    → 刀鲚专研  ← 你在这里
    C   conflict-arbiter → 冲突仲裁
```

---

## 这个项目是什么

刀鲚（*Coilia nasus*），"长江三鲜"之首。每年春夏之交，它们从海里游回长江产卵。但过度捕捞和水工建筑让它们的洄游路线越来越艰难。

这个项目通过耳石微化学（Sr/Ca 比值）重建每一条鱼的洄游历史——它在哪里出生、在哪里长大、在哪里产卵。每一片耳石，都是一本打开的生命日记。

> 赫拉克利特说：人不能两次踏进同一条河流。
>
> 我们说：但一条刀鲚可以——只要河流还在。

---

## 快速上手

```bash
# 文献搜索
python scripts/literature_search.py "Coilia nasus"

# 洄游分析（耳石微化学）
python scripts/migration_analysis.py --species "Coilia nasus"

# 食性分析
python scripts/feeding_analysis.py --species "Coilia brachygnathus"
```

---

## 核心能力

| 能力 | 说明 |
|:-----|:------|
| **耳石微化学** | Sr/Ca 比值 → 洄游路线重建 |
| **洄游生态** | 长江 → 近海 → 长江 生命周期 |
| **资源评估** | CPUE 分析 + 种群动态模型 |
| **食性分析** | 胃含物 + 稳定同位素 (δ¹³C, δ¹⁵N) |

---

> 鱼在水里，你在岸上，代码在中间。
> 愿每一片耳石的故事都被读懂。
>
> **最后更新: 2026-06-21 · Reasonix Code · DeepSeek 驱动**
