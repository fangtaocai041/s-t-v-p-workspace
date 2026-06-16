# Analyze Growth — 鲌类年龄与生长分析

> **触发**: 用户查询鲌类年龄、生长、VBGF 参数
> **方法**: 鳞片/耳石轮纹鉴定 + von Bertalanffy 生长方程

## PREFLIGHT

1. 确认目标物种: Culter alburnus / C. mongolicus / C. oxycephalus / Ch. erythropterus
2. 确认年龄材料: 鳞片 (常用) / 矢耳石 (高精度) / 脊椎骨 (辅助)
3. 收集文献中的 VBGF 参数

## AGE DETERMINATION

```
方法1: 鳞片轮纹
  - 取样位置: 背鳍下方、侧线以上
  - 判读: 年轮 (疏密切割型/疏密型)
  - 优点: 非致死, 可大批量
  - 缺点: 高龄鱼副轮干扰

方法2: 矢耳石 (sagitta)
  - 研磨至核心可见
  - 判读: 透射光下暗带/亮带交替
  - 优点: 准确度高, 高龄鱼可靠
  - 缺点: 致死取样

方法3: 脊椎骨
  - 判读: 锥体凹面的环纹
  - 优点: 高龄鱼辅助验证
```

## GROWTH MODELING

```
von Bertalanffy 生长方程 (VBGF):
  Lt = L∞ (1 - e^(-K(t - t0)))

参数:
  L∞ = 渐进体长 (mm)
  K   = 生长系数 (yr⁻¹)
  t0  = 理论生长起点年龄 (yr)

拟合方法:
  - 非线性最小二乘法 (nls, R)
  - Ford-Walford 图解法 (快速估计)
  - 贝叶斯层次模型 (多群体比较)

生长性能指数:
  φ' = log10(K) + 2 × log10(L∞)

拐点年龄:
  t拐 = ln((n+1)/1) / K + t0  (体重生长拐点)
```

## OUTPUT FORMAT

```
| 参数 | 估计值 ± SE | 来源 |
|------|------------|------|
| L∞   | xxx mm     | 文献 |
| K    | x.xx yr⁻¹  | 文献 |
| t0   | -x.xx yr   | 文献 |
| φ'   | x.xx       | 计算 |
| t拐  | x.x yr     | 计算 |
```
