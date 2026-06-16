# 🏗️ Fish Ecology Assistant 架构设计

> 每一层设计都由鱼类生态学研究的具体需求和 DeepSeek 的效率哲学驱动。
> 借鉴 porpoise-agent 的五阶段流水线和三层架构。

---

## 1. 设计哲学

### 核心原则

| # | 原则 | 说明 |
|---|------|------|
| I | Panta Rhei | 动态世界观 — 知识有时间戳，版本有生命周期，涌现是常态 |
| II | 效率即智能 | 熵预算、稀疏激活、差分验证 — 计算力按需分配 |
| III | 人机协作 | AI 是副驾驶，人类掌握方向、判断、发表 |
| IV | 可审计 | 每步推理留有可追踪痕迹（JSONL 审计日志） |

### 借鉴融合

| 借鉴来源 | 借鉴内容 | 适配方式 |
|-----------|----------|----------|
| porpoise-agent | 三层架构、五阶段流水线、结构化配置 | 适配为 Reasonix Skill 原生实现 |
| DeepSeek | Cache-First, R1 Harvesting | 直接复用 |
| Ecology-Harness (ECNU) | Skill Hub, MCP 编排 | 鱼类生态学专用 Skills |
| porpoise-agent | JSONL 审计日志、类型化 dataclass | 独立工具模块 |

---

## 2. 总体架构

```
用户界面层 (Reasonix Code Chat)
        ↓
编排层 (research-orchestrator + Karpathy Guard)
  ┌──────────────────────────────────────────┐
  │  Stage 1: Planner    → 问题拆解 + 关键词 │
  │  Stage 2: Executor   → 5 引擎并行搜索    │
  │  Stage 3: Analyst    → 分类 + 涌现检测   │
  │  Stage 4: Writer     → 校准语言写作      │
  │  Stage 5: Reviewer   → 4 维度评分        │
  └──────────────────────────────────────────┘
        ↓
Skill Hub / MCP 工具层
  (13 子智能体, 17 MCP 服务, 13 IMA 知识库)
        ↓
基础设施层
  (DeepSeek API, Reasonix Cache, R 4.6.0, 审计日志)
```

---

## 3. 五阶段研究流水线

| 阶段 | 技能 | 激活条件 | 模型 | 人工关卡 |
|:----:|------|:---------|:-----|:--------:|
| 1 | `research-planner` | 始终 | V3 (廉價) | — |
| 2 | `research-executor` | Planner 输出查询 | V3 | — |
| 3 | `research-analyst` | ≥1 搜索结果 | R1 | — |
| 4 | `research-writer` | ≥1 分析发现 | V3 | — |
| 5 | `research-reviewer` | ≥500 字草稿 | R1 | — |

### 迭代机制

```
Reviewer 判定:
  ✅ Pass → 输出最终报告
  🔄 Needs Revision → 返回 Writer（最多 3 轮）
  ❌ Fail → 呈现问题给用户
```

---

## 4. 稀疏激活架构

借鉴 DeepSeek MoE 路由：

| 模块 | 激活条件 | 说明 |
|:-----|:---------|:-----|
| Planner | 始终 | 轻量，先行 |
| Executor | ≥1 搜索查询 | 跳过纯理论问题 |
| Analyst | ≥1 搜索结果 | 跳过无结果场景 |
| Writer | ≥1 分析发现 | 跳过无发现场景 |
| Reviewer | ≥500 字输出 | 跳过快速查询 |
| Stats verify | 涉及代码/方法 | 其他情况静默 |
| IMA search | 领域匹配知识库 | 其他情况静默 |
| Emergence | ≥3 独立来源 | Analysts 阶段自动触发 |

---

## 5. 数据流

```
研究问题
  → Planner: 拆解 → 双语关键词 → 搜索策略
  → Executor: 5 引擎并行搜索 → 源数据库
  → Analyst: 分类 + 质量加权 + 时间轴 + 涌现检测
  → Writer: 结构化写作 + 校准语言 + 置信度标签
  → Reviewer: 4 维度评分 → 通过/修订/不通过
  → 最终报告 → research_output/
```

---

## 6. 置信度系统

| 标签 | 含义 | 触发条件 |
|:-----|:-----|:---------|
| ✅ 已验证 | 多源一致可复现 | ≥2 独立 ★★★ 源 |
| ⚠️ 推断 | 逻辑延伸 | 1 个 ★★☆ 源 + 间接证据 |
| ❓ 不确定 | 单源未复现 | 1 个 ★☆☆ 源 |
| 🚫 无来源 | 不可溯源 | 禁止写入 |

---

## 7. 涌现检测

```
Input: Analyst 阶段的分类发现
Process: 聚合独立来源 (不互相引用)
Threshold: ≥3 个独立来源指向同一非预期模式
Output: 涌现信号 → 标记置信度 → 写入报告
```

**置信度等级**:
- 3 个独立源 → 低置信度
- 4 个独立源 → 中置信度
- 5+ 个独立源 → 高置信度

---

## 8. 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 实现方式 | Reasonix Skills (Markdown) | 无需代码依赖，热更新 |
| 模型 | DeepSeek V3 + R1 自适应路由 | 廉价 token + cache + R1 推理 |
| 搜索策略 | 英文优先 + 中文补充 | 科学文献英文更全面 |
| 语言 | 中英双语 | 用户中文母语 + 国际学术标准 |
| 审计 | JSONL 独立模块 | 可复现 + 可追溯 |
| 配置 | YAML 结构化 | 借鉴 porpoise-agent |

---

## 9. 安全与治理

- 人工审批关卡: 野外调查 / 保护建议 / 发表草稿
- Karpathy Guard: 反幻觉 / 反复杂化 / 精准手术 / 目标驱动
- 审计日志: JSONL 格式，每事件可追踪
- 引用验证: 每声明 ≥2 独立源（核心发现）
- API Key 保护: .gitignore 隔离敏感配置
