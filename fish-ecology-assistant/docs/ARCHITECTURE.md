# Fish Ecology Assistant 架构设计 (v6.5.3)

> 三角核心 S/V0 层 — 鱼类生态学知识供给引擎

---

## 0. 设计哲学

架构由三条哲学线索交织驱动，每条都有对应的工程落地。

### 0.1 Panta Rhei — 动态世界观

> "人不能两次踏进同一条河流" — 赫拉克利特

知识生态是流动的，不是静态的档案库。

| 哲学命题 | 工程落地 | 代码位置 |
|----------|----------|----------|
| 知识有时间戳 | 物种 KB 每条 literature 有 `added_at` 字段 | `scripts/search_species.py:update_kb()` |
| 版本有生命周期 | CHANGELOG + `.reasonix/readme-versions/` 存档链 | `CHANGELOG.md` |
| 分类学是动态的 | `taxonomy_log` 记录每次变更的时间/来源/证据 | `config/fish_species_kb.yaml` |
| 搜索策略自适应 | `evolution.yaml` 根据历史指标自动调参 | `config/evolution.yaml` |
| 路径不硬编码 | `$REASONIX_HOME` 环境变量，部署环境可变 | `src/project_hub.py:170` |

### 0.2 系统论 — 三生万物

> "道生一，一生二，二生三，三生万物" — 道德经

系统的最小完整结构是三元组（三角），不是二元对立，也不是一元中心。

| 哲学命题 | 工程落地 |
|----------|----------|
| 道 = 外界 | 用户的研究问题，CLI 输入 |
| 一 = 太极 | `ProjectHub` — 统一入口，未分阴阳 |
| 二 = 两仪 | 阴=知识(S/V0) ↔ 阳=验证(V/V1) 对立统一 |
| 三 = 三角 | fish + cognitive + eon — 密闭三元组 |
| 万物 = 衍生 | porpoise/coilia/conflict — 无限扩展 |

**铁律**: 三角密闭(缺一不可) · 万物开放(无限衍生) · 三角不依赖万物

### 0.3 涌现 — 自下而上的模式发现

> "整体大于部分之和" — 亚里士多德

当 ≥3 个独立来源指向同一非预期模式，系统自动标记涌现信号。

| 哲学命题 | 工程落地 | 参数 |
|----------|----------|------|
| 独立来源聚合 | `EmergenceSignal` dataclass | `threshold: 3` |
| 置信度分级 | 3源=低 / 4源=中 / 5+源=高 | `emergence_threshold` |
| 自适应阈值 | 误报率高时自动提高阈值 | `config/evolution.yaml` |
| 跨项目共享 | emergence signals 写入 `logs/self_evolve.jsonl` | `logs/` |

---

## 1. 总体架构: 三生万物

```
                   三 生 万 物
               Triangle → the Myriad

    ┌───────────────────────────────────┐
    │        三角核心 (sealed 3)        │
    │          缺一不可                 │
    │                                   │
    │  S/V0  fish-ecology-assistant    │  ← 本项目：知识供给
    │  V/V1  cognitive-search-engine   │  ← 搜索验证
    │  Coord eon-core                  │  ← 协调内核
    └──────────────┬────────────────────┘
                   │ 赋能
          ┌────────┼────────┐
          ▼        ▼        ▼
       P₁        P₂         C
    porpoise   coilia   conflict-arbiter
    (江豚)     (刀鲚)    (冲突仲裁)
       │
       ▼
    P₃, P₄ ... 万物 · 开放集合 · 无限衍生
```

### 铁律

- **三角密闭**: 正好 3 个，缺一不可
- **万物开放**: 0 到 N，三角不依赖任何衍生项目
- **三角提供基础能力** (知识+验证+协调)，衍生项目在此基础上执行

---

## 2. 模块结构

```
src/
├── __init__.py         ← 19 个公共导出符号
├── orchestrator.py     ← 核心编排器 · KB-First 搜索
├── project_hub.py      ← 跨项目协调中枢 · 三生万物
├── adapter.py          ← 跨项目适配器 (IProjectAdapter)
├── dao_engine.py       ← 道→一→二→三→万物 执行引擎
├── shared.py           ← 共享工具 (期刊白名单/OCR 变体)
├── types.py            ← 类型系统 (8 dataclass + 4 Enum)
└── audit_logger.py     ← JSONL 审计日志
```

### 2.1 orchestrator — 核心编排器

| 方法 | 返回 | 说明 |
|------|------|------|
| `kb_first_lookup(query)` | `KbFirstResult` | 两阶段搜索第一阶段：纯知识库查询 |
| `search_species(name, mode)` | `dict` | 统一物种搜索入口，三角核心联动 |
| `delegate_to(subsystem, task)` | `dict` | 委托任务到衍生项目 |
| `health()` | `dict` | 健康检查 |
| `info()` | `dict` | 版本 + 能力清单 |

数据流: 优先加载新格式 (`fish_species_index.yaml` + `knowledge_base/species/*.md`)，失败回退旧格式 (`fish_species_kb.yaml`)。

### 2.2 project_hub — 跨项目协调

```python
hub = get_hub()
hub.is_triangle_complete()    # True/False
hub.triangle_status()         # {fish, cognitive, eon} 各状态
hub.search_species("鳤")      # 三角核心联动搜索
hub.delegate_to("coilia", "query")  # P₂ 刀鲚专研
```

三角成员使用 `importlib` DirectLoader 零进程加载，无需子进程或 HTTP。

### 2.3 adapter — 跨项目接口

实现 `IProjectAdapter` 协议，所有物种查询委托 `orchestrator.kb_first_lookup()`，不独立加载数据源。

### 2.4 dao_engine — 哲学链执行引擎

```
DaoQuery → OneEntry → YinYangDuality → TriangleCore → MyriadManifest
  道         一          二 (阴+阳)       三             万物
```

类型安全的 dataclass 链，每层 validate() 门控。`python dao_engine.py "鳤"` 可独立运行。

---

## 3. 两阶段搜索架构

```
用户输入 "鳤"
  │
  ▼
Stage 1: kb_first_lookup("鳤")
  │
  ├── ✅ 知识库命中
  │     ├── summary_text (人类可读摘要)
  │     ├── search_recommendation = "stay_in_kb" / "continue_to_c"
  │     └── 用户决定 → 留在 KB / 继续搜索
  │
  └── ❌ 未命中
        ├── fuzzy_find_all() → 候选列表
        └── search_recommendation = "continue_to_c"
              │
              ▼
Stage 2: cognitive-search-engine (三角之V)
          └── 多源并行搜索 → 可信度评分 → 写回 KB
```

### CLI 入口

```bash
python scripts/search_species.py "鳤"            # 交互式
python scripts/search_species.py "鳤" --auto     # 自动全量
python scripts/search_species.py "鳤" --kb-only  # 仅 KB
```

---

## 4. 物种知识库

### 4.1 数据格式

**新格式（主要）**:

```
config/
├── fish_species_index.yaml    ← 索引：id → name/scientific/family/basins
└── knowledge_base/species/    ← 30 个 .md 档案
    ├── ochetobius_elongatus.md   # YAML frontmatter + Markdown body
    ├── coilia_nasus.md
    └── ...
```

**旧格式（写回目标）**:
`config/fish_species_kb.yaml` — flat YAML，`scripts/search_species.py` 的写回路仍使用此格式。

### 4.2 匹配策略

| 输入类型 | 例子 | 匹配方式 |
|----------|------|----------|
| 中文名 | "鳤" | 精确匹配 |
| 学名 | "Ochetobius elongatus" | 精确/子串匹配 |
| 部分属名 | "Ochetobius" | 子串匹配 |
| 别名 | "珠星三块鱼" | aliases 字段匹配 |
| 同义名 | (同义名列表) | synonyms 字段匹配 |

### 4.3 物种条目结构 (.md)

```yaml
---
id: ochetobius_elongatus
scientific: Ochetobius elongatus
name: 鳤
family: 鲤科
conservation: CR          # IUCN 等级
category: endangered_in_graph
basins:
- 长江流域
literature:               # 关联文献
- doi: 10.1007/s12686-018-1075-3
  title: Development and characterization of 26 SNP markers...
  year: 2018
  journal: Conservation Genetics Resources
  category: genetics
aliases: []               # 别名列表
synonyms: []              # 同义名列表
---
```

---

## 5. 类型系统

```
src/types.py

PipelinePhase  Enum: PLANNING / SEARCHING / ANALYZING / WRITING / REVIEWING
ConfidenceLevel Enum: VERIFIED / INFERRED / UNCERTAIN / NO_SOURCE
EvidenceQuality Enum: HIGH / MEDIUM / LOW / GREY
ReviewResult    Enum: PASS / NEEDS_REVISION / FAIL

ResearchContext   dataclass — 研究上下文
SourceEntry       dataclass — 文献来源
AnalysisFinding   dataclass — 分析发现（含置信度）
EmergenceSignal   dataclass — 涌现信号
ReviewReport      dataclass — 评审报告
PipelineStats     dataclass — 流水线统计
SessionResult     dataclass — 会话结果
```

---

## 6. 数据流

### 6.1 搜索流程

```
用户 CLI 输入 "鳤"
  │
  ├── scripts/search_species.py
  │     ├── load_kb() → 优先 orchestrator（新格式），回退 YAML
  │     ├── find_species_in_kb() → 别名/同义名/模糊匹配
  │     ├── ask_user() → 交互决策
  │     ├── call_c_search() → subprocess → cognitive-search-engine
  │     └── update_kb() → 写回 fish_species_kb.yaml
  │
  └── src/orchestrator.py (Python API)
        └── kb_first_lookup() → KbFirstResult
              ├── _find_species() → 精确/别名/同义名
              └── _fuzzy_find_all() → 分数降序候选
```

### 6.2 跨项目委托

```
ProjectHub
  ├── hub.cognitive.search("鳤")    → V/V1 搜索验证
  ├── hub.porpoise.health()        → P₁ 江豚
  ├── hub.coilia.health()          → P₂ 刀鲚 (当前焦点)
  └── hub.conflict.arbitrate(...)  → C 冲突仲裁
```

---

## 7. 配置体系

```
config/
├── agent.yaml               ← 主代理配置 (版本/管线/子代理/技能)
├── fish_species_index.yaml  ← 物种索引 (30 种)
├── fish_species_kb.yaml     ← 旧格式知识库 (写回目标)
├── yangtze_fish_species.yaml← 孤立数据 (待迁移)
├── coordination.yaml        ← 三生万物协调配置
├── evolution.yaml           ← 自适应参数进化
├── component_registry.yaml  ← 组件注册表 (活系统)
├── species_variants.yaml    ← 物种名称变体
├── models.yaml              ← 模型配置
├── mcp_servers.yaml         ← MCP 服务
└── wuxing.yaml              ← 五行健康监控
```

---

## 8. 路径约定

所有 `D:\Reasonix\` 硬编码已替换为 `$REASONIX_HOME` 环境变量：

```python
# project_hub.py
self._workspace = Path(os.environ.get("REASONIX_HOME", self._root.parent))
```

```yaml
# coordination.yaml
root: "${REASONIX_HOME:-D:\\Reasonix}"
```

---

## 9. 测试架构

```
tests/
├── test_orchestrator.py   ← 18 个测试
│   ├── 导入/生命周期       (3)
│   ├── 已知物种精确匹配    (5)
│   ├── 别名匹配           (1)
│   ├── 未知物种           (2)
│   ├── 模糊候选           (2)
│   └── 边界案例           (3)
├── test_project_hub.py    ← 8 个测试
│   ├── 三角核心           (4)
│   ├── 万物衍生           (3)
│   └── 单例              (1)
└── test_shared.py         ← 7 个测试
    ├── 期刊白名单         (3)
    ├── 搜索查询构建       (2)
    └── OCR 变体           (2)
```

---

## 10. 技术债务

| 债务 | 影响 | 计划 |
|:-----|:-----|:-----|
| `scripts/search_species.py` 写回使用旧格式 | 读写路径不一致 | v6.6.0 KB 迁移 |
| `config/yangtze_fish_species.yaml` 孤立数据 | 冗余，可能误导 | v6.6.0 确认后删除 |
| `scripts/verify_architecture.py` 已 DEPRECATED | 维护者可能误用 | v7.0.0 移除 |

---

## 参考

- [RE.md](../RE.md) — 工程记录 (会话 1 + 会话 2)
- [CHANGELOG.md](../CHANGELOG.md) — 版本历史
- [coordination.yaml](../coordination.yaml) — 三生万物协调
- [porpoise-agent docs](../porpoise-agent/docs/ARCHITECTURE.md)
