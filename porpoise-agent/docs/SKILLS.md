# 🎯 技能体系 (Skills)

> 借鉴 ecological-agent-skills 的 Markdown 格式，每个技能是一个 SKILL.md 文件

## 技能列表

| # | 技能名称 | 所属阶段 | 说明 |
|---|----------|----------|------|
| 1 | search-literature | Phase 1 文献调研 | 多源文献搜索、筛选、摘要 |
| 2 | analyze-acoustic | Phase 2 数据分析 | PAM 数据处理管道 |
| 3 | detect-clicks | Phase 2 数据分析 | NBHF click 检测与分类 |
| 4 | classify-vocalizations | Phase 2 数据分析 | 声信号分类 (click/buzz/noise) |
| 5 | estimate-abundance | Phase 2 数据分析 | 种群丰度估计 |
| 6 | model-habitat | Phase 2 数据分析 | 栖息地建模 (SDM/MaxEnt) |
| 7 | assess-threats | Phase 4 保护评估 | 威胁因子评估 |
| 8 | plan-survey | Phase 3 野外调查 | 调查路线规划 |
| 9 | analyze-genetics | Phase 2 数据分析 | 遗传/基因组分析 |
| 10 | generate-report | Phase 5 成果产出 | 研究报告生成 |
| 11 | review-conservation | Phase 4 保护评估 | 保护策略评估 |

## 技能格式规范

每个技能目录包含一个 SKILL.md，格式如下：

```markdown
# Skill: <技能名称>

## 触发条件
- 用户提及关键词: ...
- 研究阶段: Phase X

## 输入
- 必需: ...
- 可选: ...

## 步骤
1. ...
2. ...

## 决策点
- 当 AUC < 0.7 时: ...
- 当样本量 < 30 时: ...

## 输出格式
```json
{ ... }
```

## 参考
- Kimura et al. (2010) ...
```

## 技能执行模式

- **inline**: 直接注入到系统提示词中，Agent 自行判断调用时机
- **subagent**: 启动独立子 Agent，在隔离上下文中执行
