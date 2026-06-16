# Analyze Genomics — 鲌类基因组学分析

> **触发**: 用户查询鲌类基因组、全基因组测序、比较基因组、简化基因组
> **方法**: 基因组组装评估 + 简化基因组分析 + 比较基因组 + 系统发育基因组

## PREFLIGHT

1. 确认目标物种: Culter alburnus / C. mongolicus / Ch. erythropterus
2. 确认数据类型: 全基因组 / RAD-seq / GBS / 转录组 / 线粒体基因组
3. 检查 NCBI SRA/GenBank 中可用数据

## 基因组测序策略

```
全基因组 de novo:
  - PacBio HiFi (20-30x): 长读长，基因组连续性
  - Illumina (50-100x): 短读长，纠错 + GC bias 校正
  - Hi-C: 染色体水平挂载
  - 推荐: hifiasm + Hi-C 流程

简化基因组 (RAD-seq/GBS):
  - 限制酶选择: SbfI (RAD) / PstI-MspI (ddRAD) / ApeKI (GBS)
  - 测序深度: 10-20x / 样本
  - 分析: Stacks2 / ipyrad / GATK

转录组:
  - RNA-seq: 多个组织 (肌肉/肝脏/性腺/脑)
  - 组装: Trinity / rnaSPAdes
  - 注释: Trinotate / eggNOG-mapper
```

## 线粒体基因组

```
结构: ~16.6 kb, 13 PCGs + 22 tRNA + 2 rRNA + D-loop
可用物种:
  - Culter alburnus (翘嘴鲌)
  - Culter mongolicus (蒙古鲌)
  - Chanodichthys erythropterus (红鳍原鲌)

分析:
  - 注释: MITOS2 / MitoAnnotator
  - 系统发育: 13 PCGs 串联 → RAxML-NG / IQ-TREE
  - 选择压力: PAML (dN/dS)
```

## 比较基因组

```
目标问题:
  1. 鲌亚科 (Cultrinae) 系统发育位置
  2. Culter ↔ Chanodichthys 属间分化时间
  3. 肉食性适应的基因家族扩张/收缩

方法:
  - OrthoFinder: 同源基因家族鉴定
  - CAFE: 基因家族扩张/收缩
  - PAML branch-site model: 正选择检测
  - PSMC/MSMC: 种群历史动态 (Ne 变化)
```

## 适应性进化

```
候选基因方向:
  - 生长轴: GH/IGF/GHRH — 快速生长适应
  - 视觉: RH1/LWS — 中上层视觉捕食
  - 免疫: MHC/TLR — 不同水体病原适应
  - 渗透压: NKA/AQP — 淡水适应

扫描方法:
  - Fst outlier (BayeScan/pcadapt)
  - XP-EHH / iHS (选择性清除)
  - 环境关联分析 (LFMM/RDA)
```

## OUTPUT

```
| 项目 | 状态 | 数据/方法 |
|------|------|-----------|
| 全基因组组装 | ❌ 未公开 | PacBio HiFi + Hi-C 推荐 |
| 线粒体基因组 | ✅ 已有 | 3 物种 |
| RAD-seq/GBS | ✅ 已有 | 群体遗传结构 |
| 转录组 | ⚠️ 部分可用 | 生长/免疫基因 |
| 比较基因组 | ❌ 待开展 | OrthoFinder + CAFE |
```
