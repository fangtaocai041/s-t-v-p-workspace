# workspace 项目间调用协议 (v3.0)

> 生成时间: 2026-06-22 01:43
> 核心原则: 按需启动，依次执行，不启动无关项目

---

## 调用顺序 (严格遵守)

### 搜索类命令
```
"Cognitive Search" 或 物种名搜索:
  1. cognitive-search-engine (c)     ← 首先启动
  2. └→ MCP 引擎并行: scholar/article/scholarly/tavily/exa/ncbi
  3. 结果返回

"知识库查询" 或 中文名查询:
  1. fish-ecology-assistant (f)      ← 首先启动
  2. └→ 自动触发 conflict-arbiter (如果保护源≥2个)
  3. 结果返回
```

### 综合分析命令
```
"评估物种" 或 "全栈搜索":
  1. fish → 知识库查询
  2. cognitive → 文献搜索
  3. fish → 可信度评分
  4. 返回综合结果

"冲突检测":
  1. conflict-arbiter → 启动
  2. └→ 多源仲裁 (中国优先/全局加权)
  3. 返回仲裁结果

"健康检查":
  1. 依次检查 6 个 adapter
  2. 返回每个项目的健康报告
```

### 不启动的项目 (按需)
```
仅做搜索时:      不启动 fish/arbiter/coilia/culter/porpoise
仅知识库查询时:   不启动 cognitive/arbiter
仅分析时:         按需启动
```

## 实际代码验证

### 已验证的调用链
| 调用 | 状态 | 代码路径 |
|------|------|---------|
| search_species('Coilia') | ✅ | workspace→search_coordinator.search() |
| lookup_species('刀鲚') | ✅ | workspace→fish.adapter.search('lookup') |
| assess_conflict() | ✅ | workspace→conflict.adapter.search() |
| full_stack_search() | ✅ | fish→cognitive→fish (WF_A) |
| health_check() | ✅ | 6 adapters sequentially |

### 蓝图 vs 实际代码
| 模块 | 状态 | 
|------|------|
| rule_engine.SearchRuleEngine._execute_phase | 🟡 Legacy stub — 实际功能在 search_coordinator |
| porpoise.cognitive.reflexion | 🔴 标注未实现 |
| thompson/pipeline best-effort | 🟢 非关键路径, pass 合理 |
| MCP 6引擎 | ✅ 本会话已实际调用并验证 |

## 防幻觉措施 (嵌入代码)

### 已存在的验证层
1. **validator.py** — 交叉引用验证 (concurrent 3-source)
2. **credibility_scorer.py** — 0-100 可信度评分
3. **ZN_EN_RULES.md** — CN/EN 双通道过滤规则
4. **6 MCP 引擎实际检索** — 不依赖 LLM 记忆, 每次都实时查数据库

### 建议补强
1. 每次检索结果在输出时标注来源引擎
2. 纯 AI 生成内容 (无引擎回溯) 不标注为"已验证"
3. 论文清单用 MCP 引擎验证后再入库
