# 🔄 Fish Ecology Assistant 工作流设计

> 借鉴 porpoise-agent 的五阶段状态机，适配鱼类生态学研究的实际工作流。

---

## 状态机

```
                    ┌─────────┐
                    │  START  │
                    └────┬────┘
                         │
                    ┌────▼────┐
              ┌─────│ PLANNING│
              │     └────┬────┘
              │          │ 输出: 研究计划 + 双语关键词
              │     ┌────▼────┐
              │     │SEARCHING│ ← 可并行 (多个子主题)
              │     └────┬────┘
              │          │ 输出: 源数据库
              │     ┌────▼────┐
              │     │ANALYZING│ ← 涌现检测
              │     └────┬────┘
              │          │ 输出: 分析报告
              │     ┌────▼────┐
              │     │ WRITING │
              │     └────┬────┘
              │          │ 输出: 文档草稿
              │     ┌────▼────┐
              │     │REVIEWING│
              │     └────┬────┘
              │          │
              │   ┌──────┼──────┐
              │   │      │      │
              │  ✅    🔄     ❌
              │ PASS  REVISE  FAIL
              │   │      │      │
              │   │   ┌──┘      │
              │   │   │ (≤3轮)  │
              │   │   └──►WRITING
              │   │
              │   ▼
              │  END
              │
              └── 快速查询路线 (跳过搜索/分析/写作/评审)
                   直接回答 → END
```

---

## 工作流 1: 完整研究流水线

**触发词**: "Research [topic], run full pipeline"

```
用户: "Research effects of Yangtze fishing ban on fish communities, full pipeline"
    │
    ▼
[Planner] 拆解问题
    ├── 子主题 1: 禁渔前后鱼类群落结构变化
    ├── 子主题 2: 功能性群落的响应
    └── 子主题 3: 经济鱼类的恢复模式
    │
    ▼
[Executor] 并行搜索 (5 引擎)
    ├── English: "Yangtze fishing ban fish community structure 2022-2025"
    ├── English: "functional diversity Yangtze fish post-ban"
    └── 中文: "长江十年禁渔 鱼类群落 恢复"
    │
    ▼
[Analyst] 分类 + 涌现检测
    ├── 分类: 群落结构 / 功能多样性 / 经济物种
    ├── 时间轴: 2021(禁渔开始) → 2023 → 2025
    └── 涌现: ≥3 源独立报告"鳤鱼种群快速恢复" → 标记
    │
    ▼
[Writer] 结构化综述
    ├── ✅ 已验证: 禁渔后鱼类总丰度提升 (5 源一致)
    ├── ⚠️ 推断: 顶级捕食者恢复可能滞后
    └── ❓ 不确定: 支流与干流的响应差异
    │
    ▼
[Reviewer] 4 维度评分
    ├── 完整性: 4/5
    ├── 准确性: 5/5
    ├── 格式: 4/5
    └── 语言: 4/5
    │
    ▼
  ✅ Pass → 保存到 research_output/
```

---

## 工作流 2: 快速文献查询

**触发词**: "Search for [topic]"

```
用户: "Search for latest Culter alburnus genetic diversity studies"
    │
    ▼
[Planner] → 子主题 1 个
    │
    ▼
[Executor] 搜索
    ├── scholar: "Culter alburnus genetic diversity population"
    ├── tavily: "Culter alburnus RAD-seq phylogeography"
    └── scholarly: "Culter alburnus microsatellite genetic structure"
    │
    ▼
跳过 Analyst/Writer/Reviewer
    → 直接输出源数据库给用户
```

---

## 工作流 3: 博士研究提案

**触发词**: "/skill phd-proposal-writer Research direction: [topic]"

```
用户: "PhD proposal: drivers of sympatric coexistence of Culter species"
    │
    ▼
[phd-proposal-writer] 直接调用
    ├── 搜索: 领域背景文献
    ├── 结构化: 五章提案模板
    │   ├── 一、立项依据
    │   ├── 二、研究目标与内容
    │   ├── 三、研究方案与技术路线
    │   ├── 四、创新点与预期成果
    │   └── 五、研究计划与进度安排
    └── 参考文献 (≤40, 近 5 年)
```

---

## 工作流 4: 统计手册验证

**触发词**: "/skill verify-stats-handbook [章节号]"

```
[verify-stats-handbook] 自动执行
    ├── ① 读取手册 → 提取包列表
    ├── ② CRAN 版本检查 → 比对最新版本
    ├── ③ 官方文档比对 → 检查 API 变更
    ├── ④ 概率陈旧评分
    │   P(stale) = 0.4*f(频率) + 0.35*g(破坏性) + 0.25*h(依赖度)
    └── ⑤ 生成验证报告 + 建议复查日期
```

---

## 人类审批关卡

借鉴 porpoise-agent 的显式 human_in_loop 配置：

| 场景 | 审批要求 | 配置位置 |
|:-----|:---------|:---------|
| 野外调查方案 | 必须审批 | `config/agent.yaml` |
| 保护管理建议 | 必须审批 | `config/agent.yaml` |
| 数据删除操作 | 必须审批 | `config/agent.yaml` |
| 外部 API 写入 | 必须审批 | `config/agent.yaml` |
| 发表级草稿 | 建议审批 | `config/agent.yaml` |

---

## 错误处理与降级

```
MCP 工具不可用:
  scholar → tavily → web_search
  任一工具失败 → 跳过并标注 → 不阻塞流水线

搜索无结果:
  自动切换引擎重试 (最多 3 次)
  仍无结果 → 明确报告 "0 results" → 不编造

子智能体超时:
  使用已有结果继续
  通知用户部分完成

评审 3 轮仍未通过:
  输出当前版本 + "Failed final review"
  标记给用户人工判断
```

---

## 参考

- porpoise-agent: `docs/WORKFLOWS.md` — 五阶段状态机设计
- fish-ecology-assistant: `GUIDE.md` — 完整使用指南
- fish-ecology-assistant: `config/agent.yaml` — 流水线配置
