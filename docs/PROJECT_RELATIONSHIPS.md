# 🗂️ 五项目包含关系 — 消除混乱

> **关键**: 项目(代码目录) ≠ 角色(架构层次)。同一套代码，不同视角的映射不同。
> **同步**: 2026-06-09

---

## 视角一: 代码目录 (文件系统 — 平级)

```
D:\Reasonix\                     ← workspace 根目录
  ├── eon-core/                  ← 项目之一 (内核基础设施代码)
  ├── fish-ecology-assistant/    ← 项目之一 (知识供给代码)
  ├── cognitive-search-engine/   ← 项目之一 (搜索验证代码)
  ├── porpoise-agent/            ← 项目之一 (江豚专研代码)
  └── coilia-agent/              ← 项目之一 (刀鲚专研代码)

5个项目在文件系统上是平级的。
每个项目有自己的 config/ src/ skills/ docs/。
```

---

## 视角二: 架构角色 (道→一→二→三→万物)

```
道 (操作者)              ← 不是项目。是 Reasonix/用户。
 │
一 (IProjectAdapter)     ← 不是项目。是接口契约 scripts/adapter_protocol.py。
 │                        5个项目都实现了它。
 │
二 (YinYang)             ← 不是独立项目。代码在 eon-core/src/poles/。
 │                        YangPole(扩张) + YinPole(验证)。
 │
三 (三角闭环)            ← 3个项目的协同:
 │   fish-ecology-assistant    (S/V0 — 知识供给)
 │   cognitive-search-engine   (V/V1 — 验证引擎)
 │   eon-core                  (Coordinator — 协调内核)
 │
 └─ 万物 (从三演化)      ← 包含:
     ├─ porpoise-agent         (P₁/V2 — 江豚专研, 独立项目)
     ├─ coilia-agent           (P₂/V3 — 刀鲚专研, 独立项目)
     ├─ Pₙ                     (spawn_agent 生成的任何新项目)
     ├─ 四象 (V0 V1 V2 V3)     (代码在 eon-core/src/vertices/)
     ├─ 八卦 (8 trigrams)      (代码在 eon-core/src/trigrams/)
     ├─ 五行 (5 elements)      (代码在 eon-core/src/wuxing/)
     └─ 六道 (6 realms)        (代码在 eon-core/src/samsara/)
```

---

## 视角三: eon-core 的双重身份 (这是混乱的根源)

```
eon-core 作为「项目」:          eon-core 作为「架构角色」:
─────────────────────          ─────────────────────────
D:\Reasonix\eon-core\           三角闭环的协调内核
├── src/kernel/origin.py        管理 EventBus, DAG路由, 生命周期
├── src/poles/                  实现阴阳双极 (二)
├── src/vertices/               实现四象顶点分发 (万物)
├── src/trigrams/               实现八卦子模块 (万物)
├── src/wuxing/                 实现五行流转 (万物)
├── src/samsara/                实现六道轮回 (万物)
├── src/mesh/                   实现四面体拓扑 (万物)
├── src/sphere/                 实现球体网关 (万物)
├── src/tendrils/               实现触须探针 (万物)
└── src/evolution/              实现进化引擎 (万物)

一个项目，承载了两层架构:
  1) 作为「三」的协调内核 (OriginKernel, EventBus)
  2) 作为「万物」的基础设施 (四象八卦五行六道)
```

---

## 视角四: 每个架构层在哪个项目哪个文件中

```
层      架构概念        所在项目          实际文件
──      ────────        ────────          ────────
道      操作者          不是项目           Reasonix/用户
一      统一接口         workspace         scripts/adapter_protocol.py
二      阳·扩张         eon-core           src/poles/yang_pole.py
二      阴·验证         eon-core           src/poles/yin_pole.py
三      S/知识供给      fish-ecology      src/adapter.py (lookup_species)
三      V/验证引擎      cognitive          src/adapter.py (search_species)
三      Coordinator     eon-core           src/kernel/origin.py

万物    四象 V0         eon-core           src/vertices/v0_fish/
万物    四象 V1         eon-core           src/vertices/v1_cognitive/
万物    四象 V2         eon-core           src/vertices/v2_porpoise/
万物    四象 V3         eon-core           src/vertices/v3_coilia/
万物    八卦 ☰☱        eon-core           src/trigrams/qian_*/ dui_*/
万物    八卦 ☲☳        eon-core           src/trigrams/li_*/ zhen_*/
万物    八卦 ☴☵        eon-core           src/trigrams/xun_*/ kan_*/
万物    八卦 ☶☷        eon-core           src/trigrams/gen_*/ kun_*/
万物    五行 🪵🔥🪨⚔️💧  eon-core           src/wuxing/
万物    六道 ☸️🧘⚔️🐂👻🔥 eon-core           src/samsara/
万物    P₁(江豚)        porpoise-agent    src/agent/orchestrator.py
万物    P₂(刀鲚)        coilia-agent      src/agent/orchestrator.py
万物    Pₙ(模板)        spawn_agent.py    scripts/spawn_agent.py
```

---

## 视角五: 通路 (数据流 — 谁调谁)

```
P1: fish-ecology ──lookup_species──→ cognitive-search-engine
    项目A 调用 项目B 的 search()。数据: 物种名 → 搜索查询。

P2: cognitive ──search_result──→ fish-ecology
    项目B 返回结果给项目A。数据: 论文列表 → 可信度评分。

P3: cognitive ──search_result──→ porpoise / coilia
    项目B 赋能项目C/D。数据: 文献 → 领域分析。

P4: 所有项目 ──health()──→ eon-core
    所有适配器报告健康 → eon-core Samsara 业力评估。
```

---

## 一句话消除混乱

```
Q: eon-core 和其他4个项目是什么关系？
A: 代码上平级。架构上 eon-core 既是「三」的协调内核,
   又是「万物」(四象八卦五行六道) 的代码载体。

Q: 四象八卦五行六道在哪个项目里？
A: 全部在 eon-core/src/ 下。它们是 eon-core 的内部模块。

Q: porpoise/coilia 是「万物」还是「三」？
A: 是「万物」。它们是从三角派生的独立项目。
   三角只需要 fish + cognitive + eon-core 即可运行。

Q: spawn_agent 生成的 Pₙ 放在哪？
A: workspace 根目录下的新项目目录 (如 acipenser-agent/)。
   与 porpoise-agent/ coilia-agent/ 平级。
```
