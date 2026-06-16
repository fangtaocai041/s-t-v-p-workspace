# Fish Ecology Assistant 工作流 (v6.5.3)

> 三角核心 S/V0 层的搜索与协调工作流。

---

## 工作流 1: KB-First 两阶段搜索

**入口**: `scripts/search_species.py "<species>"` 或 `orchestrator.kb_first_lookup()`

```
用户输入 "鳤"
  │
  ▼
[Stage 1] 查知识库 (零 token 成本)
  │
  ├── load_kb()
  │     ├── 优先: orchestrator (新格式 index.yaml + .md profiles)
  │     └── 回退: fish_species_kb.yaml (旧格式 flat YAML)
  │
  ├── find_species_in_kb()
  │     ├── 精确匹配: query == 学名/中文名
  │     ├── 别名匹配: query in aliases[]
  │     ├── 同义名匹配: query in synonyms[]
  │     └── 模糊匹配: query 子串 in 名称 → 分数降序候选列表
  │
  └── kb_summary()
        ├── 优先: orchestrator 的 summary_text (含别名/分类/生态/分布)
        └── 回退: 手工组装 (旧格式字段)
  │
  ├── ✅ 命中 → 展示摘要
  │              ├── 用户决策：[y] 继续搜索 → Stage 2
  │              │             [n] 留在 KB → 结束
  │              │             [q] 退出
  │              └── 自动模式 (--auto): 直接进入 Stage 2
  │
  └── ❌ 未命中 → 展示候选列表 → 推荐 Stage 2
                      │
                      ▼
[Stage 2] 全量搜索 (cognitive-search-engine)
  │
  ├── call_c_search()
  │     └── subprocess → cognitive-search-engine/scripts/search_api.py
  │           ├── 并行引擎: tavily / exa / scholar / article / scholarly
  │           ├── 分类学不一致检测
  │           └── 结果去重 + 可信度评分
  │
  └── update_kb()
        ├── 追加 literature (按 DOI 去重)
        ├── 追加 taxonomy_log (分类变更记录)
        ├── 追加 change_log (操作审计)
        └── save_kb() → fish_species_kb.yaml
```

### CLI 参数

```bash
python scripts/search_species.py "鳤"                    # 交互模式
python scripts/search_species.py "鳤" --auto             # 自动全量 + 回写
python scripts/search_species.py "鳤" --kb-only          # 仅查 KB
python scripts/search_species.py "鳤" --auto --dry-run   # 预览（不回写）
python scripts/search_species.py "鳤" --kb-only --json   # JSON 输出
python scripts/search_species.py "鳤" --max 30           # 每引擎最大结果
```

---

## 工作流 2: 跨项目协调

**入口**: `ProjectHub` (`src/project_hub.py`)

```
三角核心 (sealed 3):
  hub.fish        → self (S/V0 知识供给)
  hub.cognitive   → V/V1 搜索验证引擎 [importlib DirectLoader]
  hub.eon         → Coordinator 协调内核 [importlib]

万物衍生 (open N):
  hub.porpoise    → P₁ 江豚专研
  hub.coilia      → P₂ 刀鲚专研（当前焦点）
  hub.conflict    → C 冲突仲裁
```

```python
from src import get_hub

hub = get_hub()

# 三角完整性检查（密闭集合铁律）
assert hub.is_triangle_complete()  # fish + cognitive + eon 全部可用

# 统一搜索
result = hub.search_species("鳤", mode="kb_first")

# 委托衍生项目
hub.delegate_to("coilia", "Coilia nasus otolith Sr/Ca data analysis")
hub.delegate_to("porpoise", "NBHF acoustic detection range")
```

---

## 工作流 3: 物种知识库查询 (Python API)

**入口**: `orchestrator.kb_first_lookup()` (`src/orchestrator.py`)

```python
from src import get_orchestrator

orch = get_orchestrator()

# ── 已知物种 ──
r = orch.kb_first_lookup(query="鳤")
r.found              # True
r.chinese_name       # "鳤"
r.scientific_name     # "Ochetobius elongatus"
r.family             # "鲤科"
r.summary_text       # 人类可读摘要
r.search_recommendation  # "stay_in_kb"（已有足够数据）

# ── 别名匹配 ──
r = orch.kb_first_lookup(query="珠星三块鱼")
r.found              # True
r.chinese_name       # "三块鱼"（正名）
r.matched_by_alias   # True

# ── 未知物种 ──
r = orch.kb_first_lookup(query="NonExistentFish")
r.found              # False
r.all_candidates     # []（模糊候选列表）
r.search_recommendation  # "continue_to_c"

# ── 综合搜索 ──
r = orch.search_species("鳤", mode="kb_first")
# stage: "kb_check"（KB 命中）
# needs_user_decision: True
```

---

## 工作流 4: 道→一→二→三→万物 执行链

**入口**: `DaoEngine` (`src/dao_engine.py`)

```
CLI:
  python src/dao_engine.py "鳤"
  python src/dao_engine.py "鳤" --search  (自动全量)
  python src/dao_engine.py "鳤" --json    (JSON 输出)
```

```python
from src.dao_engine import DaoEngine, DaoQuery

engine = DaoEngine()

# 道: 外部输入
dao = DaoQuery(raw="鳤", species_hint="鳤")

# 执行: 道→一→二→三→万物
result = engine.execute(dao)
# result = {
#   "dao": DaoQuery,       # 道
#   "one": OneEntry,       # 一 (太极)
#   "two": YinYangDuality, # 二 (阴 S + 阳 V)
#   "three": TriangleCore, # 三 (三角验证)
#   "myriad": MyriadManifest,  # 万物 (输出)
# }

print(engine.render(result))
```

输出示例:
```
══════════════════════════════════════════════════════
  道生一 · 一生二 · 二生三 · 三生万物
  Dao → One → Two → Three → the Myriad
══════════════════════════════════════════════════════

┌─ L0: 道 (Dao) ─────────────────────────────
│ 输入: "鳤"
│ 物种: 鳤
└──────────────────────────────────────────

┌─ L1: 一 (One) · 太极 ────────────────────
│ hub 加载: ✅
│ orch 就绪: ✅
└──────────────────────────────────────────

┌─ L2: 二 (Two) · 太极生两仪 ──────────────
│ 阴(S/知识): ✅ 鳤 (Ochetobius elongatus)
│ 阳(V/验证): 未发 (留步于阴)
│ 矛盾: 阴主导 — 知识库已足够, 阳未发
└──────────────────────────────────────────

┌─ L3: 三 (Three) · 三角密闭 ──────────────
│ ☯️ S/V0          阴·静
│ ☯️ V/V1          阳·动
│ ☯️ Coordinator   太极点
│ 三角完整: ✅
└──────────────────────────────────────────

┌─ L4: 万物 (Myriad) · 一切输出 ────────────
│ 总耗时: 12ms
│ 万物非一万种, 而是一切可能。
└──────────────────────────────────────────
```

---

## 工作流 5: 工程维护

### 测试

```bash
# 全量测试
python -m pytest tests/ -v

# 单模块
python -m pytest tests/test_orchestrator.py -v

# 适配器验证
python -c "
from src import FishEcologyAdapter
a = FishEcologyAdapter()
print(a.search_species('鳤').get('known_species'))
"
```

### 架构验证

```python
from src import get_hub, get_orchestrator

# 三角完整性
hub = get_hub()
assert hub.is_triangle_complete()

# 物种数据一致性
orch = get_orchestrator()
r = orch.kb_first_lookup(query="鳤")
assert r.found
assert r.family == "鲤科"
```

### 路径配置

```bash
# Windows (默认)
set REASONIX_HOME=D:\Reasonix

# Linux / 容器
export REASONIX_HOME=/app/reasonix

# 不设置 → 自动检测上级目录
```
