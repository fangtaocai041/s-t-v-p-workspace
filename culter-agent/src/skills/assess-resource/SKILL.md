# Assess Resource — 鲌类资源评估

> **触发**: 用户查询鲌类资源量、CPUE、MSY、捕捞管理
> **方法**: 剩余产量模型 + YPR 分析 + 参考点评估

## PREFLIGHT

1. 确认目标水体和物种
2. 收集渔获量 (catch) 和捕捞努力量 (effort) 时间序列
3. 确认可用辅助数据: 体长频率、年龄组成

## CPUE 标准化

```
标准化方法:
  - GLM (对数正态/负二项)
  - GAM (处理非线性效应)
  - 零膨胀模型 (ZINB/Delta-GLM)

解释变量:
  - 年 (Year): 种群丰度趋势
  - 月 (Month): 季节效应
  - 区域 (Area): 空间效应
  - 渔船类型 (Vessel): 捕捞能力差异
```

## 剩余产量模型

```
Schaefer 模型:
  dB/dt = rB(1 - B/K) - C
  MSY = rK/4
  Bmsy = K/2

Fox 模型:
  dB/dt = rB(1 - ln(B)/ln(K)) - C
  MSY = rK/e
  Bmsy = K/e

拟合方法:
  - 过程误差模型 (Pella-Tomlinson)
  - 状态空间模型 (JAGS/BUGS/Stan)
  - CMSY/BSM (数据有限方法)
```

## YPR 分析

```
Beverton-Holt YPR:
  YPR = F × W∞ × Σ[Ωn × e^(-nK(tc-t0)) / (F + M + nK)]

参数需要:
  - L∞, K, t0 (VBGF)
  - M (自然死亡系数): Pauly/Then 经验公式
  - tc (开捕年龄)
  - a, b (体长-体重关系)
```

## 参考点

```
目标参考点: F0.1, Fmax, F40%SPR
极限参考点: Fcrash, Blim
预警参考点: Fpa, Bpa

Kobe 图: B/Bmsy vs F/Fmsy
```

## OUTPUT FORMAT

```
| 指标 | 估计值 | 参考点 | 状态 |
|------|--------|--------|------|
| CPUE | xx     | —      | ↓/→/↑ |
| B/Bmsy | x.xx | > 0.5 | OK/OVER/COLLAPSED |
| F/Fmsy | x.xx | < 1.0 | OK/OVER |
| MSY  | xx t   | —      | —    |
```
