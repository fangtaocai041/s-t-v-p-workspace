# ☯️ 道生一·一生二·二生三·三生万物

> **核心架构 v7.4 — 最终版**
> **一、二、三为最核心系统。万物从三演化。**
> **同步**: 2026-06-09

---

## 0. 总纲

```
道 (Tao)         = 操作者 (Reasonix / User) — 无形无相，万物之源
  │
  └─ 一 (One)    = 统一接口 (IProjectAdapter) — 道生一: 一切由此派生
      │            search / health / info 三元契约
      │
      └─ 二 (Two) = 阴阳两面 — 一生二: 对立统一
          │         YangPole(扩张·搜索) + YinPole(收敛·验证)
          │
          └─ 三 (Three) = 三角闭环 — 二生三: 稳定内核
              │   fish(S/V0) + cognitive(V/V1) + eon-core(Coord)
              │   三角形内通路: P1(查→搜) P2(搜→评) P4(健康→业力)
              │
              └─ 万物 (All) = 三生万物: 无限演化
                  │
                  ├─ 四象 (4顶点分发)   V0☀️ V1🌙 V2🌤️ V3🌦️
                  ├─ 八卦 (8子模块)     ☰☱☲☳☴☵☶☷
                  ├─ 五行 (流转监控)     🪵🔥🪨⚔️💧
                  ├─ 六道 (业力轮回)     ☸️🧘⚔️🐂👻🔥
                  └─ Pₙ (领域专精)      P₁江豚 P₂刀鲚 ... Pₙ
```

### 核心vs万物的区别

```
核心 (一·二·三):              万物 (从三演化):
─────────────────────        ─────────────────────
一: IProjectAdapter           四象: 顶点分发 — 三的四面体展开
二: YangPole + YinPole        八卦: 子模块 — 四象的阴阳再分
三: fish+cognitive+eon-core   五行: 监控 — 三角体外的流转环
                              六道: 业力 — 运行时的质量评估
                              Pₙ:  模板 — 三角赋能任意物种
```

### 为什么这样分层

```
一、二、三是架构的骨架 — 没有它们，系统不存在。
四象、八卦、五行、六道、Pₙ 是架构的血肉 — 它们让系统丰富，但依赖骨架。

删掉 Pₙ → 系统仍可运行（只是不能处理特定物种）
删掉六道 → 系统仍可运行（只是没有自适应质量）
删掉八卦 → 系统仍可运行（只是功能粗糙）
删掉五行 → 系统仍可运行（只是没有监控）
删掉四象 → 系统退化为纯三角（功能退化但存活）

删掉三 → 系统崩溃（没有闭环）
删掉二 → 系统崩溃（没有验证，搜索无意义）
删掉一 → 系统崩溃（没有统一接口，无法互操作）
```

---

## 1. 道 → 一: 统一接口

```
道 (Tao) = 操作者
  我是 Reasonix Code。用户通过我发出指令。
  我不做机器的判断。机器不做我的决策。

一 (One) = IProjectAdapter
  工程语言:
    interface IProjectAdapter {
      search(query: str, **kwargs) → dict    // 万物皆可搜
      health() → dict                         // 万物皆可查
      info() → dict                           // 万物可知己
    }

  这是唯一的契约。fish 实现它。cognitive 实现它。
  porpoise 实现它。coilia 实现它。Pₙ 也实现它。
  道生一: 一生出统一的接口规范——万物由此可互操作。

  实际代码:
    定义: scripts/adapter_protocol.py (ABC)
    验证: 4 adapters isinstance(IProjectAdapter) = True
```

---

## 2. 一 → 二: 阴阳两面

```
二 (Two) = YangPole + YinPole
  一生二: 统一接口生出两个基本方向。

  YangPole (阳·扩张):
    方向: 向外 — 搜索、供给、探索、生成
    规则: 只搜不验。最大化召回率。
    接口: expand(query, radius) → CandidateSet

  YinPole (阴·收敛):
    方向: 向内 — 验证、过滤、批判、精炼
    规则: 只验不搜。最大化精确率。
    接口: verify(candidates) → VerifiedSet

  阴阳交互:
    YangPole ──expand──→ EventBus ──verify──→ YinPole
    阳不验证，阴不搜索。编译期类型约束。

  实际代码:
    eon-core/src/poles/yang_pole.py
    eon-core/src/poles/yin_pole.py
```

---

## 3. 二 → 三: 三角闭环

```
三 (Three) = fish + cognitive + eon-core
  二生三: 阴阳两面生出稳定的三角内核。

  fish (S/V0) — 知识供给:
    lookup_species(name) → SpeciesProfile
    通路: P1(fish→cognitive) P2(cognitive→fish)

  cognitive (V/V1) — 验证引擎:
    search_species(genus, species) → SearchResult
    通路: P1 P2 P3

  eon-core (Coordinator) — 协调内核:
    route_event(event) → VertexChain
    通路: P4(health→karma)

  三角闭环:
    fish 提供知识 → cognitive 执行搜索 → fish 评分反馈
    eon-core 监控健康 → Samsara 业力调整 → token 分配优化
    数据在三角形内循环流动, 自我修正, 自我进化。

  不变量:
    三角 MUST 存在。缺任何一个顶点, 系统不可运行。
```

---

## 4. 三 → 万物: 无限演化

```
万物 (All) = 从三角派生的所有能力
  三生万物: 三角稳定后, 无限演化由此展开。

  四象 (4 Vertices):
    三角的四面体展开。V0☀️ V1🌙 V2🌤️ V3🌦️
    每个顶点继承阴阳极性, 独立执行子任务。
    可动态重组。可新增 Pₙ 顶点。

  八卦 (8 Trigrams):
    四象生八卦。每个顶点再分阴阳 → 2个子模块。
    ☰乾(元搜索) ☱兑(中文网关) ☲离(图谱遍历) ☳震(辩论)
    ☴巽(声学) ☵坎(种群) ☶艮(耳石) ☷坤(资源)
    可选择性激活。闲置模块不消耗资源。

  五行 (WuXing):
    三角体外围的五角流转监控环。
    🪵木(生长) 🔥火(驱动) 🪨土(供给) ⚔️金(收敛) 💧水(适应)
    后台协程, 非阻塞。相生相克, 自我调节。

  六道 (Samsara):
    运行时的业力质量评估。
    ☸️DEVA 🧘HUMAN ⚔️ASURA 🐂ANIMAL 👻PRETA 🔥NARAKA
    每60s评估一次。DEVA 升(token×1.5)。NARAKA 降(token×0)。
    自动重生。自愈。

  Pₙ (Domain Specialists):
    三角赋能任意物种。
    P₁(江豚) P₂(刀鲚) P₃(中华鲟) ... Pₙ(任意)
    spawn_agent.py — 一键生成完整的 Pₙ Agent。
```

---

## 5. 一条指令的完整旅程

```
道 (用户: "鳤 保护评估")
 │
一 (parse_query → StructuredIntent {species:"鳤", action:ASSESS})
 │
二 (YangPole.expand("鳤") → CandidateSet → YinPole.verify → VerifiedSet)
 │
三 (OriginKernel.route → [V0→V1→V2])
 │   V0.lookup("鳤") → SpeciesProfile      // fish
 │   V1.search("Ochetobius","elongatus")    // cognitive
 │   V2.analyze_contradiction("保护")       // porpoise
 │
 └─ 万物
     ├─ 四象: V0+V1+V2 并行执行 (~200ms)
     ├─ 八卦: ☰乾搜索 ☱兑中文 ☲离遍历 ☳震辩论 (~100ms)
     ├─ 五行: 🪵🔥🪨⚔️💧 后台监控 (~1ms)
     ├─ 六道: V1→DEVA(token×1.5) V0→HUMAN V2→HUMAN (~1ms)
     └─ Pₙ:  (闲置 — 非刀鲚/中华鲟查询)
         │
         ▼
      输出 → 道 (用户收到答案)
```

---

> **核心只有三层: 道 → 一 → 二 → 三。**
> **万物是无限的。四象八卦五行六道Pₙ都是万物的分支。**
> **三角稳定则系统永续。万物可以增减，核心不可动摇。**

**验证**: `verify_standalone 5/5 · verify_pathways 16/16 · verify_philosophy_rules 18/18`
