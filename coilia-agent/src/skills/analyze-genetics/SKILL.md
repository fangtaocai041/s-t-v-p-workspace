# Analyze Genetics — 刀鲚群体遗传学分析

> **参考脚本**: `scripts/genetics_analysis.py`
> **触发**: 用户询问刀鲚遗传结构/种群分化/基因流
> **数据源**: 微卫星 (SSR)、线粒体 DNA (COI/D-loop)、SNP、RAD-seq

## METHODS

### 微卫星标记 (SSR)
- 技术: 微卫星位点 PCR 扩增 + 毛细管电泳
- 分析: 等位基因频率、期望/观测杂合度 (He/Ho)、Fis
- 应用: 群体遗传分化 (Fst/Gst)、基因流 (Nm)、遗传多样性

### 线粒体 DNA
- 标记: COI (DNA barcoding)、D-loop 控制区
- 分析: 单倍型多样性 (Hd)、核苷酸多样性 (π)、单倍型网络图
- 应用: 系统地理结构、历史种群动态

### SNP 标记
- 技术: RAD-seq / 简化基因组测序
- 分析: PCA、STRUCTURE、Admixture
- 应用: 精细群体结构、选择信号检测

## OUTPUT TEMPLATE

```
刀鲚群体遗传学分析报告

1. 遗传多样性
   - 平均等位基因数 (Na): X
   - 期望杂合度 (He): X.XX
   - 单倍型多样性 (Hd): X.XX

2. 群体结构
   - Fst (长江 vs 钱塘江): X.XX (p<0.05)
   - 最可能的 K 值: X (STRUCTURE 分析)
   - 群体分化程度: 低/中/高

3. 历史动态
   - 中性检验 (Tajima's D): X.XX
   - 有效群体大小 (Ne): X,XXX
   - 瓶颈效应: 有/无

4. 保护遗传学建议
   - 管理单元 (MUs) 划分
   - 遗传多样性保护策略
   - 增殖放流遗传管理
```
