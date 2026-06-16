# Conflict Arbiter 🔥

**C 万物衍生** — 多源保护级别冲突检测 · 中国优先加权 · 时空可比性。

> 🌊 万物皆变 · Panta Rhei
>
> IUCN 说濒危，国标说无危，CITES 说附录 II。
> 一个物种，三张红牌——谁是对的？

[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)

[English](README.md) · [中文](README.zh.md) · [更新日志](CHANGELOG.md)

---

## 🎯 核心哲学

> 世界是动态的，知识是暂时的，涌现是常态。

C（Conflict Arbiter）是万物衍生中的仲裁者。当不同数据源对同一物种的保护级别给出不同结论时——IUCN 说 CR、中国红皮书说 EN、CITES 说附录 II——它来裁决。

### 🔗 在万物中的角色

```
三生万物架构：
  三角核心 (sealed 3)             → 基础能力
    ├── S/V0  fish-ecology-assistant
    ├── V/V1  cognitive-search-engine
    └── Coord eon-core
  
  万物衍生 (open N):
    P₁  porpoise-agent  → 江豚专研
    P₂  coilia-agent    → 刀鲚专研
    P₃  culter-agent    → 鲌类专研
    C   conflict-arbiter → 冲突仲裁  ← 你在这里
```

---

## 🧩 这个项目是什么

保护生物学中最尴尬的问题之一：同一个物种，不同的保护名录给出不同的结论。

- **IUCN 红色名录**：全球视角，更新周期长
- **中国红皮书**：国家视角，但部分物种数据陈旧
- **CITES 附录**：贸易管制视角，不直接对应濒危等级
- **国家重点保护野生动物名录**：法律效力，但 2021 年才大修

当它们打架时，C 使用中国优先加权、时空可比性检查和证据链追溯来给出仲裁意见。

> 赫拉克利特说：人不能两次踏进同一条河流。
>
> 我们说：但一个物种可能被三个保护名录给出三种结论。
> 我们的工作是——找出真相。

---

## ⚡ 快速上手

```bash
# 直接调用仲裁引擎
python -c "
from src.arbiter import ConflictArbiter
a = ConflictArbiter()
result = a.arbitrate('Ochetobius elongatus')
print(result)
"
```

---

## 🚀 核心能力

| 🚀 能力 | 📝 说明 |
|:-----|:------|
| **多源冲突检测** | IUCN / 中国红皮书 / CITES / 国保名录 |
| **中国优先加权** | 中国分布物种以中国分类为权威 |
| **时空可比性** | 区分"不同时间/空间的声明"与"真正矛盾" |
| **证据链追溯** | taxonomy_log 记录每次变更的来源和证据 |

## 🔗 生态体系

> 🔥 和则无穷力量，分则顶尖专家引擎。

本项目是「三生万物」生态的 冲突仲裁专家引擎 (C)。

```
三角核心 (sealed 3):
  📦 fish-ecology-assistant    → 知识供给 (V0)
  🔍 cognitive-search-engine   → 搜索验证 (V1)
  ⚙️ eon-core                  → 协调内核 (Coord)

万物衍生 (open N):
  🐬 porpoise-agent    → 江豚专研 (P₁)
  🐟 coilia-agent      → 刀鲚专研 (P₂)
  🐟 culter-agent      → 鲌类专研 (P₃)
  🔥 conflict-arbiter  → 冲突仲裁 (C)
```

| 🏗️ 项目 | 🔗 顶点 | 🎯 角色 |
|:---------|:--------:|:--------|
| [fish-ecology-assistant](../fish-ecology-assistant/) | V0 | 📦 知识供给 |
| [cognitive-search-engine](../cognitive-search-engine/) | V1 | 🔍 搜索验证 |
| [eon-core](../eon-core/) | Coord | ⚙️ 协调内核 |
| [porpoise-agent](../porpoise-agent/) | P₁ | 🐬 江豚专研 |
| [coilia-agent](../coilia-agent/) | P₂ | 🐟 刀鲚专研 |
| [culter-agent](../culter-agent/) | P₃ | 🐟 鲌类专研 |
| [conflict-arbiter](../conflict-arbiter/) | C | 🔥 冲突仲裁 |

---
---

> 🌊 万物皆变 · Panta Rhei
>
> 🏛️ 赫拉克利特说：人不能两次踏进同一条河流。
>
> 💻 我们说：但一个物种可能被三个保护名录给出三种结论。我们的工作是——找出真相。
>
> **📅 最后更新: 2026-06-17 · 🖥️ Reasonix Code · ⚡ DeepSeek 驱动**

[⬆ 回到顶部](#)
