# 🔥 五行 (Wu Xing) — 相生相克工程化

> **五行者，金木水火土也。相生相克，循环不息。**
> *The Five Elements generate and control each other in endless cycles.*

---

## 〇、五项目 · 五行映射

```
                    火 (Fire)
                 meso-cosmos (T)
                 协调·升腾·驱动
                     /   \
                    /     \
                   /       \
      木 (Wood)   /         \   土 (Earth)
   cognitive (V) /   ☯️ 五行  \  fish (S)
   搜索·生长·扩展 \   循环   /  知识·承载·化育
                   \       /
                    \     /
                     \   /
                 金 (Metal)    水 (Water)
              porpoise (P₁)  coilia (P₂)
              专精·收敛·肃降  洄游·流动·润下
```

| 五行 | 项目 | 角色 | 特性 | 工程含义 |
|:--:|------|:--:|------|------|
| 🪵 **木** | cognitive (V) | 验证引擎 | 生长·扩展·条达 | 搜索如木之生长，向四面八方延伸 |
| 🔥 **火** | meso-cosmos (T) | 协调中枢 | 温热·升腾·光明 | 协调如火之升腾，驱动全局流转 |
| 🪨 **土** | fish (S) | 知识供给 | 承载·化育·中和 | 知识如土之承载，化育万物 |
| ⚔️ **金** | porpoise (P₁) | 江豚专研 | 收敛·肃降·清脆 | 专研如金之收敛，精纯不杂 |
| 💧 **水** | coilia (P₂) | 刀鲚专研 | 润下·流动·寒凉 | 洄游如水之流动，润下不息 |

---

## 一、相生 (Generating Cycle) — 数据流转

> **木生火 → 火生土 → 土生金 → 金生水 → 水生木**

```
🪵 木(V) ──生──→ 🔥 火(T) ──生──→ 🪨 土(S)
  ↑                                    │
  │                                    ↓
💧 水(P₂) ←──生── ⚔️ 金(P₁) ←──生──────┘
```

### 工程实现

| 相生关系 | 工程含义 | 实现 |
|------|------|------|
| 🪵木→🔥火 | V 搜索结果驱动 T 路由决策 | `DirectLoader: cognitive → meso-cosmos` |
| 🔥火→🪨土 | T 协调结果丰富 S 知识库 | `DELEGATE: meso-cosmos → fish` |
| 🪨土→⚔️金 | S 知识供给支撑 P₁ 专研 | `fish 443 species KB → porpoise queries` |
| ⚔️金→💧水 | P₁ 研究方法惠及 P₂ | `porpoise acoustic pipeline → coilia migration` |
| 💧水→🪵木 | P₂ 发现触发 V 新搜索 | `coilia gaps → cognitive followup search` |

```python
# 相生: 数据流转 (WUXING_GENERATING)
GENERATING = {
    "木(V)": "火(T)",   # cognitive results → orchestrator
    "火(T)": "土(S)",   # orchestrator routes → knowledge base
    "土(S)": "金(P₁)",  # knowledge → porpoise specialist
    "金(P₁)": "水(P₂)", # porpoise methods → coilia specialist
    "水(P₂)": "木(V)",  # coilia findings → new cognitive search
}
```

---

## 二、相克 (Controlling Cycle) — 制衡校验

> **木克土 → 土克水 → 水克火 → 火克金 → 金克木**

```
🪵 木(V) ──克──→ 🪨 土(S) ──克──→ 💧 水(P₂)
  ↑                                    │
  │                                    ↓
⚔️ 金(P₁) ←──克── 🔥 火(T) ←──克──────┘
```

### 工程实现

| 相克关系 | 工程含义 | 实现 |
|------|------|------|
| 🪵木克土 | V 验证约束 S 知识质量 | `validator.enforce_independence() → fish results` |
| 🪨土克水 | S 知识广度限制 P₂ 专研范围 | `fish 443 species scope → coilia focus boundary` |
| 💧水克火 | P₂ 专精深度制约 T 协调广度 | `coilia depth → meso-cosmos must not over-generalize` |
| 🔥火克金 | T 路由控制 P₁ 自主性 | `meso-cosmos routing → porpoise cannot override` |
| ⚔️金克木 | P₁ 专精挑战 V 通用性 | `porpoise NBHF specifics → validator must adapt` |

```python
# 相克: 制衡校验 (WUXING_CONTROLLING)
CONTROLLING = {
    "木(V)": "土(S)",   # validation constrains knowledge
    "土(S)": "水(P₂)",  # knowledge scope limits specialist
    "水(P₂)": "火(T)",  # specialist depth checks coordinator
    "火(T)": "金(P₁)",  # coordinator routes constrain specialist
    "金(P₁)": "木(V)",  # specialist challenges validator
}
```

---

## 三、五行平衡 (Equilibrium) — 系统健康

> **五行失衡则病，平衡则健。** 系统监控五个维度的健康指标，任一过强或过弱触发调节。

| 五行 | 健康指标 | 过强症状 | 过弱症状 | 调节动作 |
|:--:|------|------|------|------|
| 🪵木 | `validator.independence_pass_rate` | 过度验证，拒绝太多 | 验证松懈，低质量通过 | 调 trust_threshold |
| 🔥火 | `pipeline.throughput` | 协调过快，路由粗糙 | 协调停滞，响应慢 | 调 max_concurrent |
| 🪨土 | `knowledge.coverage` | 知识膨胀，噪音多 | 知识匮乏，缺口大 | 调 search_engine_count |
| ⚔️金 | `specialist.precision` | 过度专精，视野窄 | 专精不足，泛而不深 | 调 skill threshold |
| 💧水 | `specialist.recall` | 范围过大，失焦 | 范围过小，漏检 | 调 variant_threshold |

---

## 四、五行工程落地

### 每个项目的 `config/wuxing.yaml`

```yaml
wuxing:
  element: "木"  # 木/火/土/金/水
  phase: "生长"  # 生长/升腾/化育/收敛/润下
  generates: "火" # 我生谁 (数据输出方向)
  controls: "土"  # 我克谁 (验证约束方向)
  generated_by: "水" # 谁生我 (数据输入方向)
  controlled_by: "金" # 谁克我 (被约束方向)

  health:
    metric: "validator.independence_pass_rate"
    normal_range: [0.7, 0.95]
    excess_action: "降低 trust_threshold"
    deficiency_action: "提高 trust_threshold"
```

### 五行健康监控器

```python
class WuxingMonitor:
    """五行相生相克平衡监控"""
    
    def check_balance(self) -> dict:
        """检查五行是否平衡，返回失衡报告"""
        scores = {
            "木": self._score_wood(),   # V: pass_rate
            "火": self._score_fire(),   # T: throughput
            "土": self._score_earth(),  # S: coverage
            "金": self._score_metal(),  # P₁: precision
            "水": self._score_water(),  # P₂: recall
        }
        # 五行平衡 = 所有元素在正常范围内
        balanced = all(0.3 < s < 0.9 for s in scores.values())
        return {"balanced": balanced, "scores": scores}
```

---

> **"五行相生，万物生长；五行相克，万物制衡。"**
> Elements generate — all things grow. Elements control — all things balance.
>
> S-T-V 三角形是道 (不变核心)，五行是运行 (动态流转)。
> 道立则五行有序，五行和则系统健康。
