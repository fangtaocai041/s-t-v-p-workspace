# 🧭 三生万物 · 完整调用框架 (v2.0)

> 一句话记住：**你想干什么 → 调哪个 → 自动串哪些 → 得到什么**

---

## 🗺️ 项目速查表

| 简称 | 项目 | 一句话功能 | 中文名 |
|:--|:--|:--|:--|
| **S / f** | fish-ecology-assistant | 物种知识库：存文献、查档案、信用评分 | 知识供给层 |
| **T / c** | cognitive-search-engine | 21引擎搜索：全网搜论文、验证、评分 | 搜索验证层 |
| **道** | eon-core | 协调内核：EventBus、拓扑路由、健康心跳 | 协调层 |
| **火** | conflict-arbiter | 冲突仲裁：IUCN vs 中国红皮书的矛盾裁决 | 仲裁层 |
| **P₁** | porpoise-agent | 江豚专属：声学监测、种群评估 | 江豚智能体 |
| **P₂** | coilia-agent | 刀鲚专属：耳石微化学、洄游生态 | 刀鲚智能体 |
| **P₃** | culter-agent | 鲌类专属：基因组、营养生态位 | 鲌类智能体 |
| **核心** | san-sheng-wanwu-core | 硅基生命体：Cortex脑/Memory记忆/Senses感知 | 三生万物核心 |
| **基设** | infrastructure | 涌现检测、感知桥接、鱼类识别 | 基础设施 |
| **涌现** | unified_emergence.py | 5种涌现检测、跨物种合成、D₀-D₃维度追踪 | 涌现引擎 |

---

## 🔗 项目间关系图

```
                    你 (操作者)
                      │
              ┌───────┴───────┐
              │   workspace   │  ← 统一入口，你只跟它交互
              │  (MoE Router) │
              └───────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌────────┐   ┌──────────┐   ┌─────────┐
   │  f/S   │   │   c/T    │   │  eon-core│
   │知识供给│◄──│ 搜索验证 │   │  协调内核│
   └───┬────┘   └────┬─────┘   └────┬────┘
       │             │              │
       │  写回论文   │              │ 路由调度
       ├─────────────┘              │
       │                            │
       ▼                            ▼
   ┌────────┐              ┌─────────────┐
   │ conflict│              │infrastructure│
   │ 冲突仲裁│              │  涌现检测    │
   └────────┘              └─────────────┘

   ┌────────┐ ┌────────┐ ┌────────┐
   │porpoise│ │coilia  │ │culter  │
   │ P₁江豚 │ │ P₂刀鲚 │ │ P₃鲌类 │
   └────────┘ └────────┘ └────────┘
       ↑            ↑          ↑
       └────────────┴──────────┘
              按物种类型分流
```

---

## 🧬 涌现引擎 (Emergence Engine)

> **每次搜索后自动运行，无需手动调用。** 但可显式使用。

### 三层架构

```
每次 search_species() 完成
    │
    ▼
_record_emergence()  ← 自动调用 (search_coordinator.py:374)
    │
    ├─ record 论文数 → D₁
    ├─ record 分类分布 → D₁
    ├─ record 引擎成功率 → D₀
    │
    └─ check_emergence() → 检测到信号则 logger.info
```

### 五类涌现信号

| 类型 | 实战例子 |
|:--|:--|
| **ANOMALY** | 某搜索引擎连续返回 0 结果 |
| **BENEFICIAL** | 搜索精度+召回+效率同时提升 |
| **HARMFUL** | 错误率+延迟+失败率同时飙升 |
| **PHASE_TRANSITION** | D₁→D₂：从找论文跃迁到发现新知识领域 |
| **NEUTRAL** | 研究热点从遗传学转向生态学 |

### 手动调用

```python
# 实时监控
from infrastructure.unified_emergence import EmergenceMonitor, DimensionalLevel
mon = EmergenceMonitor(emergence_threshold_sigma=2.5, min_sources=2)
mon.record("papers:鳤", 23, DimensionalLevel.D1)
signals = mon.check_emergence()

# 批次分析 (如 22 年生物量时间序列)
from infrastructure.unified_emergence import EmergenceEngine
engine = EmergenceEngine()
result = engine.scan(data={"years": [2018,...,2025], "biomass": [100,...,260]})
# → 检测到 2020 年突变点 (长江禁渔)

# 自组织领域发现
from infrastructure.unified_emergence import emerge_domains
suggestions = emerge_domains(catalog)

# 跨物种合成
from workspace.scripts.cross_synthesis import CrossSynthesisEngine
cs = CrossSynthesisEngine()
emergence = cs.detect_emergence("江豚")
# → "江豚食物短缺 ← 刀鲚种群下降 (2023-2025)"
```

---

## 🎯 六大工作流 (按你的研究场景)

### 场景 1️⃣：快速查一种鱼的背景

```
你: "鳤鱼是什么？保护等级？分布在哪？"

调用: lookup_species("鳤")
     │
     ▼
   f项目 知识库
     │ 先查 SQLite species.db
     │ 再查 250+ 物种 .md 档案
     │
     ├─ 找到了 → 返回: 分类/分布/保护等级/已知文献数
     │
     └─ 保护源 ≥2 → 🔥 自动触发 conflict
                      │ IUCN 说 EN vs 中国红皮书说 VU
                      │ → "冲突等级1, 以中国红皮书为准"
                      └─ 结果存入 conflict_verdict
```

**代码**:
```python
from workspace import lookup_species
result = lookup_species("鳤")
print(result["species_data"]["保护等级"])
print(result.get("conflict_verdict"))
```

---

### 场景 2️⃣：搜索某物种的全部文献

```
你: "帮我找鳤鱼的所有论文"

调用: search_species("鳤")
     │
     ▼
   c项目 cognitive-search-engine
     │
     ├─ Step 1: 图谱预查 (0 token, 免费)
     │    └─ species_graph.yaml 中已有 172 篇论文
     │
     ├─ Step 2: 精确搜索 (PubMed + CNKI + Crossref)
     │
     ├─ Step 3: 作者交叉引用 (刘凯/熊飞/段辛斌...)
     │
     ├─ Step 4: 引用回溯 (找到的论文引用了什么)
     │
     ├─ Step 5: 变体搜索 (Ochetobius elongatus 的 OCR 变体)
     │
     └─ Step 6: 信用评分
          └─ 每篇论文 0-100 分 (来源权威性 + 引用数 + 时效性)
```

**代码**:
```python
from workspace import search_species
result = search_species("鳤", group="standard", limit=20)
for p in result.papers:
    print(f"[{p['credibility']}分] {p['title']}")
```

**搜索模式**:
| 模式 | 引擎数 | 速度 | 用哪个 |
|:--|:-:|:-:|:--|
| `quick` | 3 | ~10s | 快速确认 |
| `standard` | 6 | ~30s | **日常推荐** |
| `full` | 19 | ~90s | 写综述/基金申请 |
| `chinese` | 7 | ~30s | 中文文献为主 |

---

### 场景 3️⃣：搜索完 → 论文写回知识库

```
你: "刚才搜到的鳤鱼论文，写进知识库"

调用: (c项目搜索结果出来后，系统会问你)
     │
     ├─ c项目搜索完毕
     │
     ├─ 系统: "发现 8 篇新论文，是否写回 f项目？"
     │
     ├─ 你: "是"
     │
     └─ f项目 kb_to_graph_sync
          │ 中英文去重 (同一 DOI 不创建两个节点)
          │ 中文期刊自动填 authors_zh
          └─ species_graph.yaml 更新
```

**流程**:
```
c 搜索 → search_coordinator._write_back_to_fish()
       → f 项目 knowledge_base/species/ 更新
       → species_graph.yaml 新增论文节点
```

---

### 场景 4️⃣：全栈研究 = 一条龙

```
你: "我要全面研究鳤鱼"

调用: full_stack_search("鳤")
     │
     ▼
   WF_A 三阶段串联
     │
     ├─ Phase 1: f项目 知识库查询
     │    └─ "鳤: 保护等级 VU, 分布 长江中下游..."
     │
     ├─ Phase 2: c项目 文献搜索
     │    └─ 找到 23 篇论文, 8 篇高可信度
     │
     └─ Phase 3: f项目 信用评分
          └─ 每篇论文打分 + 分类
```

**代码**:
```python
from workspace import full_stack_search
result = full_stack_search("鳤")
# result = {profile, literature, credibility, workflow: "WF_A"}
```

---

### 场景 5️⃣：写综述 → 自动合成

```
你: "帮我写鳤鱼的文献综述"

调用: synthesize_review("鳤")
     │
     ├─ Phase 1: c项目搜索文献
     ├─ Phase 2: eon-core ReviewSynthesizer
     │    └─ 递归推理 (max_think_steps=8)
     │    └─ 质量把关 → 结构化 Markdown
     │
     └─ 输出: 鳤_文献综述.md
```

**代码**:
```python
from workspace import synthesize_review
review = synthesize_review("鳤", search_limit=50)
with open("鳤_文献综述.md", "w") as f:
    f.write(review.markdown)
```

---

### 场景 6️⃣：涌现检测 → 发现新知识

```
你: "看看最近有没有跨物种的新发现"

系统自动 (每次搜索后):
     │
     ▼
   infrastructure/unified_emergence.py
     │
     ├─ 5 个涌现检测器:
     │   ├─ 理论涌现: 两个不同领域的理论突然关联
     │   ├─ 矛盾涌现: 多篇论文的结论互相矛盾
     │   ├─ 时间涌现: 某个物种的研究突然激增
     │   ├─ 空间涌现: 分布范围突然变化
     │   └─ 语义涌现: 新术语/新概念出现
     │
     ├─ 跨物种合成 (cross_synthesis.py):
     │   └─ 如: 江豚猎物数据 + 刀鲚迁徙数据
     │       → 发现 "长江中游刀鲚减少 → 江豚食物短缺"
     │
     └─ 标记为 "推断" 而非 "事实"
```

---

## 🔀 决策树 (你该调哪个)

```
你有一个研究需求
│
├─ "我只想了解一种鱼的基本信息"
│   → lookup_species("鱼名")
│   → 自动附带冲突检测
│
├─ "我要搜索这种鱼的所有论文"
│   → search_species("鱼名", group="standard")
│   → 选模式: quick/standard/full/chinese
│
├─ "我要全面研究一种鱼 (从头到尾)"
│   → full_stack_search("鱼名")
│   → f→c→f 三阶段自动跑
│
├─ "帮我写综述"
│   → synthesize_review("鱼名", search_limit=50)
│   → 自动搜索 + 推理 + Markdown 输出
│
├─ "我有两个来源的保护等级不一样，谁对？"
│   → assess_conflict("鱼名", sources=[...])
│   → 中国优先 / 全局加权
│
├─ "我要分析江豚"
│   → assess_conservation("江豚")
│   → 自动路由到 porpoise-agent
│
├─ "我要分析刀鲚的洄游"
│   → assess_species("刀鲚", context="migration")
│   → 自动路由到 coilia-agent
│
├─ "系统状态怎么样？"
│   → health_check()
│   → 6 个项目逐一报告
│
└─ "设置 token 预算"
    → set_token_budget(300000)
    → 持久化，下次搜索自动用
```

---

## 📊 快速参考卡片

```python
from workspace import (
    search_species,       # c项目 文献搜索
    lookup_species,       # f项目 知识库查询
    full_stack_search,    # f→c→f 全栈
    synthesize_review,    # 搜索+推理→综述 Markdown
    assess_conservation,  # P₁ 江豚评估
    assess_species,       # P₂ 刀鲚评估
    assess_conflict,      # 火 冲突仲裁
    health_check,         # 全部健康检查
    set_token_budget,     # 设置 token 预算
    show_token_budget,    # 查看 token 预算
)

# 最短别名
from workspace import search, lookup, health, full, conflict
```

---

## ⚙️ 并行搜索引擎架构 (v2.0)

> 2026-06-25 重构 — 对标 SearXNG + Semantic Scholar + SIGIR 论文

### 数据流

```
search_species("鳤")
    │
    ▼
ParallelSearch.search()
    │
    ├─ [cache] species_graph 预查 ← 0 token, <1ms
    │
    ├─ Thompson 采样 → 选 top-k 引擎 (自适应探索/利用)
    │
    ├─ 每个引擎 submit 前:
    │   ├─ breaker.can_pass() → 被熔断则跳过
    │   └─ retry_call(fn, max_retries=2)
    │       ├─ timeout → RETRY → 退避 2s → 重试
    │       ├─ 429 → RATE_LIMIT → 退避 4s → 重试
    │       └─ 403 → FATAL → 立即放弃
    │
    ├─ 结果收集 → classify_error() 4 层标签
    │   ├─ 成功 → breaker.record_success()
    │   └─ 失败 → breaker.record_failure()
    │
    ├─ fuse_results(method="rrf"|"combmnz")
    │   ├─ RRF: 论文在多个引擎高排名 → 分数高
    │   └─ CombMNZ: 论文在多个引擎出现 → 共识加权
    │
    └─ _filter_by_genus → 返回
```

### 搜索引擎矩阵 (16 个)

| 引擎 | 类型 | 超时 | 重试 | 熔断 |
|:--|:--|:--|:--|:--|
| cache(species_graph) | 缓存 | <1ms | 无 | 无 |
| pubmed | 国际 | 45s | 2次 | ✅ |
| europe_pmc | 国际 | 45s | 2次 | ✅ |
| crossref | 国际 | 45s | 2次 | ✅ |
| openalex | 国际 | 45s | 2次 | ✅ |
| semantic_scholar | 国际 | 45s | 2次 | ✅ |
| arxiv | 预印本 | 45s | 2次 | ✅ |
| biorxiv_medrxiv | 预印本 | 45s | 2次 | ✅ |
| researchgate | 全文 | 45s | 2次 | ✅ |
| crossref_direct | 国际 | 45s | 2次 | ✅ |
| wikipedia | 百科 | 45s | 2次 | ✅ |
| duckduckgo | 网络 | 45s | 2次 | ✅ |
| gbif | 物种 | 45s | 2次 | ✅ |
| core | 开放获取 | 45s | 2次 | ✅ |
| cnki_web | 中文 | 45s | 2次 | ✅ |
| baidu_scholar | 中文 | 45s | 2次 | ✅ |
| wanfang_web | 中文 | 45s | 2次 | ✅ |

### 融合算法选择

```python
# 默认 RRF (看排名)
result = search_species("鳤")  # 内部用 fuse_results(method="rrf")

# 切换 CombMNZ (看共识度)
# 在 _engine.py 中修改: fuse_results(per_engine_results, method="combmnz")
```

### 错误分类标签

搜索完成后 `failed` 列表不再是简单的引擎名，而是带层级标签:

```
succeeded: ["pubmed", "crossref", "cache(8)"]
failed:    ["cnki_web(retry)", "researchgate(suspended)", "arxiv(fatal)"]
```

---

## 💰 Token 动态预算系统

### 三种配置方式 (优先级从高到低)

```python
# 1. 环境变量 (临时, 关终端失效)
$env:REASONIX_TOKEN_BUDGET = "500000"

# 2. 持久化 (重启保留)
from workspace import set_token_budget, get_token_budget, show_token_budget
set_token_budget(300000)              # 总预算 30 万
set_token_budget(500000, 50000)       # 总 50 万 + 月限额 5 万

# 3. 查看当前
show_token_budget()
# → {"total_budget": 300000, "source": "file", "default": 150000, "monthly_limit": 50000}
```

### DeepSeek 优化触发阈值

| 参数 | 旧值 (OpenAI) | 新值 (DeepSeek) |
|:--|:--|:--|
| T3 涌现噪声 | 20% | 35% |
| T5 Token 超限 | 2,500 | 10,000 |
| 满足阈值 | 8 篇 | 15 篇 |
| 总预算 | 50,000 | 150,000 (动态) |
| 引擎超时 | 15s | 45s |
| MCP 超时 | 20-45s | 40-90s |

---

## 📋 系统优化日志

| 日期 | 类别 | 变更 |
|:--|:--|:--|
| 2026-06-25 | 审计 | 37 文件 77 处修复: 裸except清零, Token迁移, eval加固, 种子, 锁, 除零 |
| 2026-06-25 | 优化 | DeepSeek 激进档: 触发阈值放宽 3-5× |
| 2026-06-25 | 新增 | Token 动态预算: set/get/show + 环境变量覆盖 |
| 2026-06-25 | 重构 | 并行搜索: 重试+退避, 4层错误分类, RRF融合, CombMNZ, 熔断器, 缓存混合 |
| 2026-06-25 | 文档 | 调用框架 + 审计模板 + 自动化扫描器 |
