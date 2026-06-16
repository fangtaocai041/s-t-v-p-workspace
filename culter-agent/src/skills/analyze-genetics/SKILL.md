# Analyze Genetics — 鲌类群体遗传与谱系地理

> **触发**: 用户查询鲌类遗传多样性、种群结构、谱系地理、系统发育
> **方法**: 微卫星/线粒体/SNP + 种群结构 + 谱系地理重建 + 种群历史

## PREFLIGHT

1. 确认目标物种及其分布水系
2. 确定遗传标记类型: SSR / mtDNA / SNP (RAD-seq/GBS)
3. 收集已发表群体的基因型数据和地理坐标

## 遗传多样性评估

```
指标:
  - 单倍型多样性 (h): 0-1, 越高越多样
  - 核苷酸多样性 (π): 通常 0.001-0.01
  - 等位基因丰富度 (Ar): 校正样本量后的等位基因数
  - 期望杂合度 (He) / 观测杂合度 (Ho)
  - 近交系数 (Fis): 正值 = 近交, 负值 = 远交

工具:
  - Arlequin / GenAlEx / hierfstat (R)
  - VCFtools / PLINK (SNP)
```

## 种群遗传结构

```
方法:
  - Structure/Admixture: 贝叶斯聚类 (K=1-N)
  - PCA/DAPC: 主成分/判别分析
  - AMOVA: 分子方差分析 (Φ-statistics)
  - Fst 成对比较: Weir & Cockerham 法

关键问题:
  - 长江/珠江/黑龙江群体间 Fst 值?
  - 湖泊群体间基因流方向?
  - 人工养殖群体是否与野生群体显著分化?
```

## 谱系地理 (Phylogeography)

```
方法:
  - 线粒体单倍型网络: TCS/median-joining
  - 系统发育树: ML (IQ-TREE) / BI (MrBayes)
  - 分化时间: BEAST 分子钟 (化石校准点)
  - 祖先分布区重建: BioGeoBEARS / S-DIVA

关键假设:
  - 第四纪冰期避难所: 珠江/北部湾?
  - 冰后期扩散路线: 南→北?
  - 长江中下游湖泊隔离时间?
```

## 种群历史动态

```
方法:
  - 中性检验: Tajima's D, Fu's Fs
  - 错配分布: SSD, Raggedness index
  - 贝叶斯天际线 (BSP): 有效种群大小随时间变化
  - PSMC/MSMC: 全基因组历史 Ne

预期格局:
  - 冰期瓶颈 → 冰后期扩张
  - 湖泊群体: 近期隔离 (全新世)
  - 河流群体: 长期大种群
```

## Gene Flow

```
方法:
  - Migrate-n: 贝叶斯基因流估算
  - ABBA-BABA (D-statistic): 基因渗入检测
  - TreeMix: 种群分化 + 迁移边

关键问题:
  - 翘嘴鲌↔蒙古鲌: 是否存在基因渗入?
  - 增殖放流是否影响野生群体遗传完整性?
```

## OUTPUT

```
| 指标 | 长江群体 | 珠江群体 | 黑龙江群体 |
|------|---------|---------|-----------|
| 单倍型多样性 h | 0.xx | 0.xx | 0.xx |
| 核苷酸多样性 π | 0.0xx | 0.0xx | 0.0xx |
| He | 0.xx | 0.xx | 0.xx |
| 有效种群大小 Ne | xxx | xxx | xxx |

谱系地理推断:
- 冰期避难所: xxx
- 扩散路线: xxx
- 分化时间: xxx Mya
```
