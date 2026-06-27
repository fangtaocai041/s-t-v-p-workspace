# 🏛️ D:\Reasonix 统一架构规范 (v8.6)

> **原则**：三角封闭、衍生开放。每个项目有唯一定位，互不替代，互不重复。
> **单一真相源**：`coordination.yaml`（项目关系）、`taiji.yaml`（DAG 拓扑）、`IProjectAdapter`（代码契约）。

---

## 第一部分：7 项目功能矩阵

| # | 项目 | 角色 | 层级 | 依赖 | 核心函数 | 对外暴露 |
|:--|:-----|:-----|:----:|:-----|:---------|:---------|
| 🌿 | **eon-core** | 协调中枢·管道调度 | Coord | 无 | `Pipeline.run()` → DAG 编排 | `get_eon()` |
| 📚 | **fish-ecology-assistant** | 知识供给 S (V0) | Core | eon-core | `lookup_species(name)` → 物种档案 | `search(query)` · `score()` |
| 🔍 | **cognitive-search-engine** | 搜索验证 V (V1) | Core | fish | `search_species(name)` → 文献列表 | `search(query)` · `verify()` |
| 🐬 | **porpoise-agent** | 江豚专研 P₁ (V2) | Derived | fish + cognitive | `assess_conservation(name)` → 保护评估 | `search(query, domain)` |
| 🐟 | **coilia-agent** | 刀鲚专研 P₂ (V3) | Derived | fish + cognitive | `assess_species(name)` → 耳石·洄游·资源 | `search(query, context)` |
| 🎣 | **culter-agent** | 鲌类专研 P₃ (V4) | Derived | fish + cognitive | `assess_culter_species(name)` → 生长·基因组·营养位 | `search(query, domain)` |
| ⚖️ | **conflict-arbiter** | 冲突仲裁 C (V5) | Derived | fish + cognitive | `assess_conflict(name, sources, claims)` → 裁决 | `search(query, sources, claims)` |
| 🌐 | **workspace** | 统一入口 | Root | 全部 | `search_species()` · `lookup_species()` · `health_check()` | 全部函数 |
| 🧬 | **san-sheng-wanwu-core** | 硅基生命体（元项目） | Meta | 全部 | 17皮层·18感知·4运动·181测试 | CLI: `silicon-agent` |
| 🔧 | **infrastructure** | 涌现引擎·NLP·视觉 | Shared | 无 | `EmergenceMonitor` · `EmergenceEngine` · `emerge_domains()` | `import infrastructure` |

---

## 第二部分：调用拓扑（谁可以调用谁）

```
                          ┌──────────────┐
                          │  workspace   │  ← 用户入口 (唯一)
                          │ __init__.py  │
                          └──────┬───────┘
                                 │ 懒加载 _get_adapter()
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                   ▼
        ┌──────────┐      ┌──────────────┐    ┌──────────────┐
        │ fish     │◄────►│ cognitive    │    │  conflict    │
        │ (V0 阳)  │ 双向  │ (V1 阴)      │    │  (V5 仲裁)   │
        └────┬─────┘      └──────┬───────┘    └──────┬───────┘
             │                    │                    ▲
             │ 依赖               │ 依赖               │ 依赖
             ▼                    ▼                    │
    ┌─────────────────────────────────────────────┐   │
    │  衍生项目 (derived)                           │   │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐     │   │
    │  │ porpoise │ │ coilia   │ │ culter   │─────┘   │
    │  │  V2/P₁   │ │  V3/P₂  │ │  V4/P₃  │          │
    │  └──────────┘ └──────────┘ └──────────┘          │
    │         所有 Pn 依赖 fish + cognitive            │
    └─────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────┐
    │  共享层 (shared)                              │
    │  ┌──────────────┐ ┌───────────────────────┐ │
    │  │infrastructure│ │ eon-core/src/shared/  │ │
    │  │·涌现引擎     │ │ ·rcca_core/evolution/ │ │
    │  │·NLP/视觉     │ │  thompson/emergence   │ │
    │  └──────────────┘ └───────────────────────┘ │
    │         任何项目均可 import                    │
    └─────────────────────────────────────────────┘
```

### 硬规则（写在代码里的契约）

| 规则 | 依据 |
|:-----|:-----|
| ✅ 三角可以互调（V0↔V1 双向） | `taiji.yaml` edges: V0→V1 |
| ✅ 衍生项目**只能**依赖三角，**不能**互相调用 | `coordination.yaml` depends_on: [fish, cognitive] |
| ✅ 任何项目可以 import infrastructure | `__init__.py`: `from infrastructure import ...` |
| ✅ 任何项目可以 import eon-core/src/shared | `rcca_core.py` SHIM 模式 |
| ❌ 三角**不能**依赖衍生项目 | `sealed_set(3)` |
| ❌ P₁ 不能直接调 P₂ | 通过 V5 (conflict-arbiter) 聚合 |

---

## 第三部分：标准调用路径

### 3.1 用户 → workspace（唯一入口）

```python
from workspace import (
    search_species,      # → cognitive-search-engine
    lookup_species,       # → fish-ecology-assistant (+ conflict 自动仲裁)
    assess_conservation,  # → porpoise-agent
    assess_species,       # → coilia-agent (culter 同接口)
    assess_conflict,      # → conflict-arbiter
    health_check,         # → 全部 6 项目
)
```

### 3.2 核心管道：EonCore → Pipeline → 各顶点

```python
# eon-core/src/kernel/pipeline.py
pipeline = Pipeline()
pipeline.load_topology()  # 从 taiji.yaml 读 DAG

# 默认全管道: V0 → V1 → [V2|V3|V4] → V5
result = pipeline.run("珠星三块鱼", mode="auto")

# 快捷模式:
result = pipeline.run("鳤", mode="search_only")  # 仅 V0→V1
result = pipeline.run("刀鲚", mode="domain_p2")  # V0→V1→V3
```

### 3.3 标准协议：所有项目的 adapter 实现 `IProjectAdapter`

```python
# scripts/adapter_protocol.py — 所有项目必须实现
class IProjectAdapter(ABC):
    project_name: str

    def search(self, query: str, **kwargs) -> Dict[str, Any]: ...
    def health(self) -> Dict[str, Any]: ...
    def info(self) -> Dict[str, Any]: ...
```

**已验证实现**：
- `FishEcologyAdapter` ← fish-ecology-assistant
- `CognitiveSearchAdapter` ← cognitive-search-engine
- `PorpoiseAdapter` ← porpoise-agent
- `CoiliaAdapter` ← coilia-agent
- `CulterAdapter` ← culter-agent
- `ConflictArbiterAdapter` ← conflict-arbiter
- `EonCoreAdapter` ← eon-core

### 3.4 懒加载机制（线程安全，零启动开销）

```python
# workspace/__init__.py
_adapters: Dict[str, Any] = {}  # 首次调用时才 import 对应项目

def _get_adapter(project_key: str):
    # 1. 检查缓存
    # 2. importlib 直接从文件路径加载 eon-core/scripts/project_loader.py
    # 3. 调用对应的 get_xxx() → 返回 ProjectWrapper
    # 4. 缓存结果
```

**注意**：`DirectLoader` 做了 `sys.path` 隔离和 `sys.modules` 恢复，防止不同项目的 `src.*` 命名空间冲突。

---

## 第四部分：联合查询（跨项目协作）

### 4.1 知识库查询 + 自动冲突仲裁

```python
# lookup_species 自动触发 conflict-arbiter
profile = lookup_species("鳤")
# → fish.search("鳤", mode="lookup")
#   → 提取 species_data 中的保护等级
#     → conflict.search("鳤", sources=[...], region="china")
#       → 返回 conflict_verdict
```

### 4.2 全栈物种搜索（WF_A）

```python
from workspace import full_stack_search
result = full_stack_search("珠星三块鱼")
# Step 1: lookup_species() → fish
# Step 2: search_species() → cognitive
# Step 3: fish.score() → 可信度评分
# → {species_profile, literature, credibility_scores}
```

### 4.3 六阶段 Pipeline（v8.2.0）

```
Phase 0: 画像    → kb_loader.py       → 知识库加载
Phase 1: 统计    → kb_loader.py       → 基础统计
Phase 2: 趋势    → trend_analyzer.py  → 研究趋势分析
Phase 3: 空白    → gap_analyzer.py    → 研究空白识别
Phase 4: 涌现    → cross_synthesis.py → 5检测器跨物种涌现
Phase 5: 假设    → reasoning_engine.py → 6假设生成
```

---

## 第五部分：共享层（零重复代码）

### 5.1 RCCA 核心（已部署到全部 7 项目）

```
Source:  eon-core/src/shared/rcca_core.py  ← 唯一规范源
Deploy:  各项目 src/rcca_core.py            ← SHIM → importlib 转发
```

| 模块 | 类 | 用途 |
|:-----|:---|:-----|
| 阻尼自我模型 | `SelfModelEngine` | 预测误差 → 稳定性检测 |
| 情绪引擎 | `EmotionEngine` | 事件驱动策略选择 |
| 转座层 | `TranspositionLayer` | 跨域推理模式迁移 |
| 反思循环 | `ReflectionLoop` | 递归思考→转座→自我适应 |
| 递归思考 | `RecursiveThinker` | think→act→observe 循环 |

### 5.2 涌现引擎（infrastructure）

```
Source:  infrastructure/unified_emergence.py  ← 唯一规范源
Import:  from infrastructure import EmergenceMonitor, EmergenceEngine, emerge_domains
Status:  porpoise-agent CLI 已集成 (proto), eon-core EmergenceBridge 闭环
```

### 5.3 共享数学原语（eon-core/shared）

```
pid_limiter.py       → PID 控制器
thompson.py          → Thompson Sampling 决策
circuit_breaker.py   → 熔断器
variant_generator.py → OCR 变体生成
evolution.py         → 自适应参数调整
checkpoint.py        → 检查点/恢复
```

---

## 第六部分：禁止与建议

| ❌ 禁止 | ✅ 建议 |
|:--------|:-------|
| 在多个项目复制核心代码 | SHIM 指向 eon-core/shared 或 infrastructure |
| 三角依赖衍生项目 | 保持 `sealed_set(3)` 封闭 |
| P₁ 直接调 P₂ | 通过 V5 (conflict-arbiter) 聚合 |
| 硬编码项目路径 | 使用 `workspace/_get_adapter()` 懒加载 |
| 绕过 workspace 直接调子项目 | 统一入口：`from workspace import ...` |
| 在 taiji.yaml 添加循环边 | DAG 必须无环（Kahn 算法验证） |

---

## 第七部分：自检清单

```bash
# 1. 所有项目 adapter 可用
python -c "from workspace import health_check; print(health_check())"

# 2. RCCA 跨项目一致
python -c "from workspace import rcca_health; print(rcca_health())"

# 3. 涌现引擎可用
python -c "from infrastructure import EmergenceEngine; print(EmergenceEngine().scan(data={}))"

# 4. DAG 无环
python -c "from eon_core.src.kernel.pipeline import Pipeline; Pipeline().load_topology()"

# 5. 全栈搜索
python -c "from workspace import full_stack_search; print(full_stack_search('鳤'))"
```
