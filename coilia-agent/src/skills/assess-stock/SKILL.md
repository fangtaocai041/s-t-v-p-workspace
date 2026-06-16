# Assess Stock — 刀鲚资源评估

> **参考脚本**: `scripts/stock_assessment.py`
> **触发**: 用户询问刀鲚资源量/恢复趋势/可持续捕捞
> **数据源**: 渔业调查、CPUE数据、文献

## METHODS

### CPUE 标准化 (Catch Per Unit Effort)
- 输入: 单位捕捞努力量渔获量时间序列
- 模型: GLM/GAM标准化，去除季节/区域/渔具效应

### 种群动态模型
- Beverton-Holt 单位补充量模型
- 体长频率法 (Length-frequency analysis)
- 虚拟种群分析 (VPA)

### MSY 估算 (Maximum Sustainable Yield)
- 输入: 生长参数(K/L∞/t0)、自然死亡率(M)、捕捞死亡率(F)
- 输出: MSY、Fmsy、Bmsy

## OUTPUT TEMPLATE

```
刀鲚资源评估报告

1. 资源现状
   - 估算资源量: X t (历史峰值3750t的Y%)
   - CPUE趋势: 上升/稳定/下降

2. 禁捕效果
   - 禁捕X年后恢复速率: Y%/年
   - 预计恢复到MSY水平需: Z年

3. 管理建议
   - IF 资源量 > Bmsy THEN 可考虑试点捕捞
   - IF 资源量 < 0.5×Bmsy THEN 维持全面禁捕
   - 监测频率: 每年/每季
```
