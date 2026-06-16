# Analyze Migration — 刀鲚洄游生态分析

> **参考脚本**: `scripts/migration_analysis.py`
> **触发**: 用户询问刀鲚洄游路线/履历/模式
> **数据源**: 耳石微化学 (Sr/Ca比)、标志放流、eDNA

## METHODS

### 耳石微化学 (Otolith Microchemistry)
- 技术: LA-ICP-MS (激光剥蚀-电感耦合等离子体质谱)
- 指标: Sr/Ca 比值 (高Sr=海水, 低Sr=淡水)
- 分析: 从耳石核心到边缘的线扫描，重建个体洄游履历

### 标志放流 (Mark-Recapture)
- 经典方法: T-bar tag, PIT tag
- 新方法: 声学遥测 (acoustic telemetry)

### eDNA (环境DNA)
- 检测水域中刀鲚DNA痕迹
- 估算分布范围和相对丰度

## OUTPUT TEMPLATE

```
刀鲚洄游分析报告

1. 个体洄游履历 (基于耳石Sr/Ca)
   - 淡水生活期: X天
   - 半咸水过渡期: Y天
   - 海水生长期: Z天

2. 群体洄游模式
   - 溯河时间: 2-4月
   - 降海时间: 秋冬季
   - 洄游距离: X km

3. 环境驱动因子
   - 水温阈值: X°C
   - 流量阈值: Y m³/s

4. 水利工程影响
   - 阻断位置: 三峡/葛洲坝/...
   - 可通过性评估: 低/中/高
```
