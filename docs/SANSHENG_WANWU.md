# 三生万物 v8 — 唯一架构规范

> 道生一 · 一生二 · 二生三 · 三生万物
> 2026-07-11 · v8.0 七项目统一 · 替代 WUXING_ARCHITECTURE / TAIJI_TETRAHEDRON / LAYERS_8_9_10 / TAO_ARCHITECTURE

---

## 零、道 — 操作者

```
道 = user (Reasonix/操作者)
─ 不需要注册
─ 不需要 adapter
─ 发出指令，接收结果
```

---

## 一、一 — 统一接口 (IProjectAdapter)

**工程语言:**
```python
class IProjectAdapter:
    def search(query: str, **kwargs) -> dict    # 执行领域查询/搜索
    def health() -> dict                          # 返回健康状态
    def info() -> dict                            # 返回能力列表
```

**谁实现:**
| 项目 | adapter 路径 | factory |
|------|-------------|---------|
| eon-core | `src/adapter.py` | `get_adapter()` |
| fish-ecology-assistant | `src/adapter.py` | `get_adapter()` |
| cognitive-search-engine | `src/adapter.py` | `get_adapter()` |
| porpoise-agent | `src/adapter.py` | `get_adapter()` |
| coilia-agent | `src/adapter.py` | `get_adapter()` |
| culter-agent | `src/adapter.py` | `get_adapter()` |
| conflict-arbiter | `src/adapter.py` | `get_adapter()` |

**统一加载入口:**
```python
from scripts.project_loader import get_eon, get_fish, get_cognitive, get_porpoise, get_coilia, get_culter, get_conflict

adapter = get_fish()
result = adapter.search("Ochetobius elongatus")
```

---

## 二、二 — 阴阳两极 (Yang + Yin)

```
YangPole (阳·扩张)           YinPole (阴·收敛)
    expand(query)                verify(candidates)
    ─ 向外搜索                    ─ 向内验证
    ─ 只搜不验                    ─ 只验不搜
    ─ 最大化召回率                 ─ 最大化精确率
```

**实现:**
- `eon-core/src/poles/yang_pole.py` — expand(query, radius) → CandidateSet
- `eon-core/src/poles/yin_pole.py` — verify(candidates) → VerifiedSet

**交互:** `YangPole.expand() → EventBus → YinPole.verify()`

---

## 三、三 — 三角闭环 (核心三项目)

```
┌─────────────────────────────────────────────────────┐
│                 三角 (TriangleCore)                  │
│                                                     │
│   fish-ecology-assistant (知识供给)                  │
│     lookup_species(name) → SpeciesProfile           │
│         ↕ P1/P2                                     │
│   cognitive-search-engine (搜索验证)                 │
│     search_species(genus, species) → SearchResult   │
│         ↕ P3                                        │
│   porpoise-agent / coilia-agent (物种专研)          │
│     analyze_contradiction() / assess_species()      │
│                                                     │
│   不变量: 三角必须完整。缺任一 = 系统不可用          │
└─────────────────────────────────────────────────────┘
```

### 三角内的 7 条数据流通路

| ID | 路径 | 转换 | 触发条件 |
|----|------|------|---------|
| P1 | fish → cognitive | `lookup_species()` → `search_species()` | 用户查某物种 |
| P2 | cognitive → fish | `search()` → `score_credibility()` | 搜索完成后 |
| P3 | cognitive → porpoise/coilia | `search()` → domain analysis | 搜索结果需填入领域上下文 |
| P4 | porpoise → eon-core | `health()` → `evaluate_karma()` | 健康脉冲 |
| P5 | any → conflict | `output()` → `detect_conflicts()` | 多源结果不一致 |
| P6 | conflict → user | `verdict()` → `consensus_report()` | 冲突仲裁完成 |
| P7 | cognitive → fish | detect_taxonomy_discrepancy() → update_taxonomy() | 分类变更检测 |

### 项目角色一览

| 项目 | 角色 | 核心函数 | 可独立运行 |
|------|------|---------|:----------:|
| **fish-ecology-assistant** | 知识供给 (S/V0) | `lookup_species(name) → SpeciesProfile` | ✅ 是 |
| **cognitive-search-engine** | 搜索验证 (V/V1) | `search_species(genus, species) → SearchResult` | ✅ 是 |
| **eon-core** | 协调内核 | `route_event(event) → VertexChain` | ✅ 是 |
| **porpoise-agent** | 江豚专研 (P₁) | `analyze_contradiction(question) → Route` | ✅ 是 |
| **coilia-agent** | 刀鲚专研 (P₂) | `assess_species(species, context) → Assessment` | ✅ 是 |
| **culter-agent** | 鲌类专研 (P₃) | `assess_culter_species(species, context) → Assessment` | ✅ 是 |
| **conflict-arbiter** | 冲突仲裁 (C) | `assess_conflict(species, sources) → ConflictReport` | ✅ 是 |

---

## 四、万物 — 无限物种专研 (Pₙ)

```
P₁ = porpoise-agent   → Neophocaena asiaeorientalis (长江江豚)
P₂ = coilia-agent     → Coilia nasus (刀鲚)
P₃ = culter-agent     → Culter alburnus (翘嘴鲌) + 近缘种
P₄ ... Pₙ = spawn_agent.py → 任意物种

模板: scripts/spawn_agent.py
  ─ 复制 porpoise-agent 骨架
  ─ 替换: config + knowledge_base + prompts
  ─ 自动注册 adapter
```

**Pₙ 依赖:**
```
WHEN spawn Pₙ:
  REQUIRE fish-ecology-assistant  (知识供给)
  REQUIRE cognitive-search-engine (文献搜索)
  OPTIONAL conflict-arbiter       (冲突仲裁)
```

---

## 五、请求路由 — 一次调用的完整路径

```
用户输入: "鳤 保护评估"
  │
  ├─ project_loader 解析 → structured_intent {species: "Ochetobius elongatus", action: ASSESS}
  │
  ├─ YangPole.expand("鳤 保护")        → 宽网搜索查询
  ├─ YinPole.verify(结果集)            → 过滤噪音
  │
  ├─ fish.lookup_species("鳤")         → SpeciesProfile (分类/分布/保护等级)
  ├─ cognitive.search_species(genus, species) → 12阶段文献搜索
  │
  ├─ (如果目标 = 江豚) porpoise.analyze_contradiction("保护") → 领域分析
  ├─ (如果目标 = 刀鲚) coilia.assess_species("Coilia nasus")  → 领域分析
  │
  ├─ (如果多源有矛盾) conflict.assess_conflict(sources) → 仲裁报告
  │
  └─ 返回统一结果给 user
```

---

## 六、共存文档清单（删除后只剩这些）

| 文件 | 状态 | 内容 |
|------|:----:|------|
| `docs/SANSHENG_WANWU.md` | ✅ **本文件** | 唯一架构规范 |
| `docs/ARCHITECTURE_OVERVIEW.md` | ✅ 保留（精简） | 工程语: 每个模块负责什么 |
| `docs/PROJECT_RELATIONSHIPS.md` | ✅ 保留（精简） | 项目间通路 + adapter 调用链 |
| `docs/EXECUTION_FLOW.md` | ✅ 保留 | 运行时流程 |
| `coordination.yaml` | ✅ 保留（精简） | 协调配置（项目注册 + 通路 + 搜索注册表） |

```
v8.0 已删除（实际清理完成）:
  ✗ docs/TAO_ARCHITECTURE.md                — 本版本从磁盘删除（之前仅标记）
  ✗ coordination.yaml (3副本)                — cognitive/fish/porpoise 项目级副本
  ✗ config/meso_agent.yaml (2副本)           — cognitive/porpoise 重复
  ✗ cognitive-search-engine/skills/ (5副本)  — 与 .reasonix/skills/ 完全相同
  ✗ fish .reasonix/skills/meso-orchestrator.md — 与根级完全相同
  ✗ workspace.py (根级)                      — 仅6行废弃重定向

v7.x 已删除（哲学叠层导致调用混乱）:
  ✗ docs/WUXING_ARCHITECTURE.md
  ✗ docs/TAIJI_TETRAHEDRON_ARCHITECTURE.md
  ✗ docs/Eon-Taiji 进化全量图谱.md / .html
  ✗ docs/LAYERS_8_9_10.md
  ✗ config/wuxing.yaml (所有项目)
```

---

## 七、验证

```bash
# 全栈适配器加载验证 (7/7)
python -c "from scripts.project_loader import get_all_adapters; print({k:type(v).__name__ for k,v in get_all_adapters().items()})"

# 通路完整性验证 (6/6)
python -c "from scripts.coordinator import coordinator; print(coordinator.verify_all())"

# coordinator 全项目健康检查 (7/7)
python -c "from scripts.coordinator import coordinator; [print(f'{p}: {coordinator.health(p)[\"status\"]}') for p in ['eon','fish','cognitive','porpoise','coilia','culter','conflict']]"

# eon-core 启动验证
python -m eon_core.src.main
```
