# Reasonix MoE 路由器 (DeepSeek 模式)

> 设计时间: 2026-06-22 02:03
> 借鉴: DeepSeek V3.2 MoE (Router → Selected Experts) + ChatGPT Function Calling (Typed API) + Gemini Long Context (统一知识视图)

---

## MoE 架构图

```
Task/Query 输入
    │
    ▼
┌──────────────┐
│   Router     │  ← workspace.__init__.py (MoE Router)
│  (任务路由器)  │
└──────┬───────┘
       │
       │ 分析任务类型, 选择专家(项目)
       │
       ├─→ 搜索类 → cognitive-search-engine (Expert 1)
       │              ├─ MCP Engines: scholar/article/scholarly/tavily/exa/ncbi
       │              └─ 返回: SearchResult
       │
       ├─→ 查询类 → fish-ecology-assistant (Expert 2)
       │              ├─ 物种知识库 SQLite
       │              ├─ 自动触发 conflict-arbiter (if 保护源≥2)
       │              └─ 返回: Dict
       │
       ├─→ 评估类 → [porpoise → coilia → culter] (Experts 3-5)
       │              ├─ 按物种类型分流
       │              └─ 返回: Dict
       │
       ├─→ 冲突类 → conflict-arbiter (Expert 6)
       │              ├─ 多源仲裁 (中国优先/全局加权)
       │              └─ 返回: conflict_verdict
       │
       └─→ 全检类 → health_check() (所有 6 个 Expert)
                      └─ 返回: Dict[project, health]

不激活的 Expert: 0 compute, 0 memory
只有被 Router 选中的 Expert 才加载
```

## 路由器规则

### 规则 1: 搜索类 → Expert 1 (cognitive)

触发词: 搜索/检索/search/lookup/paper/literature/find/查找
激活: cognitive-search-engine
不激活: fish/arbiter/porpoise/coilia/culter

### 规则 2: 知识库查询类 → Expert 2 (fish)

触发词: what is/什么是/物种简介/保护等级/分布
激活: fish-ecology-assistant (+ auto-trigger arbiter if 保护源≥2)
不激活: cognitive/porpoise/coilia/culter

### 规则 3: 全流域分析类 → Expert 1 + Expert 2 (串联)

触发词: 综合分析/full_stack/complete/全栈
激活: fish → cognitive → fish (WF_A pipeline)
不激活: 其他

### 规则 4: 健康检查 → All Experts (并发)

触发词: health/status/check/状态/检查
激活: All 6 (concurrent)
返回: 各项目健康状态

## 性能

- 单 Expert 调用: < 100ms 路由开销
- 串联 (WF_A): 3-5 秒
- 健康检查: 1-2 秒 (并发)
- 未被选择的 Expert: 0 CPU, 0 内存

## 对比

| 维度 | 传统模式 | MoE 模式 |
|------|---------|---------|
| 项目启动 | 全部加载 | 按需激活 |
| 内存占用 | 8 项目常驻 | 1-2 项目 |
| 路由开销 | 手工选择 | 自动路由 |
| 错误隔离 | 相互影响 | 独立失败 |
