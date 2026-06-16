---
name: domain-search
description: v3.0 活系统领域搜索——加权图谱路由+触手健康感知+反馈自进化，三层协作：感知→路由→生长
---

# Domain-Aware Search v3.0 — 活系统

## 数据源

- **Catalog:** `cognitive-search-engine/config/database_catalog.yaml` (8领域, 39库, 拓扑边, 上下文规则)
- **Tendrils:** `eon-core/config/tendrils_registry.yaml` (12探针, 健康状态)
- **Feedback:** `logs/catalog_feedback.jsonl` (搜索反馈, 权重自进化)

## 活系统三原则

```
1. 感知 (Perceive): 每次搜索自动记录 feedback → logs/catalog_feedback.jsonl
2. 路由 (Route):    graph_route(query, health_aware=True) → 加权+健康过滤
3. 生长 (Grow):     apply_feedback(catalog) → 成功DB增权+0.02, 失败降权-0.05
```

## 执行流程

```
用户查询 → read_file(catalog) → graph_route(query, health_aware=True) → 并行搜索
  │                    │                    │
  │  score_domains()   │  graph_route()     │  record_search_result()
  │  加权领域匹配       │  拓扑路由+触手过滤  │  记录反馈供下次进化
  │                    │                    │
  └─ context_rules ────┴─ tendril_map ──────┴─ apply_feedback()
     "毒理+鱼"→毒理主导    健康/降级/未知         自动调权(≥3样本)
```

## 输出格式

```
## 🔍 {topic}
📊 领域: [(domain, score), ...]
🗄️ 路由: top-8 (得分 + 触手状态)

| 得分 | 触手 | 数据库 | 类型 |
|:----:|:----:|--------|------|
| 0.32 | ✅ | EPA CompTox | 学术 |
| 0.32 | ✅ | ECOTOX | 学术 |
| 0.30 | ✅ | PubMed | 学术 |
| 0.01 | ⚠️ 降级 | CNKI | 学术 |
```

## 交叉引用

| 组件 | 位置 | 用途 |
|------|------|------|
| `graph_route()` | `catalog_loader.py` | 加权图谱路由 |
| `score_domains()` | `catalog_loader.py` | 上下文感知领域匹配 |
| `record_search_result()` | `catalog_loader.py` | 反馈记录 |
| `apply_feedback()` | `catalog_loader.py` | 权重自进化 |
| `load_tendril_health()` | `catalog_loader.py` | 触手健康读取 |
| `paywall-bypass` | Skill | 付费墙突破 |
| `chinese-academic-search` | Skill | 中文深度搜索 |
| `unified-species-search` | Skill | 物种专用三路并行 |

## 扩展

- 新领域/数据库 → 编辑 `database_catalog.yaml`
- 新触手 → 编辑 `tendrils_registry.yaml` + catalog topology.tendril_map
- 权重自动调 → `apply_feedback()` ≥3样本自动生效
