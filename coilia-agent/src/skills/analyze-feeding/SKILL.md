# Analyze Feeding — 刀鲚食性与营养生态分析

> **参考脚本**: `scripts/feeding_analysis.py`
> **触发**: 用户询问刀鲚食性/营养级/食物网
> **数据源**: 胃含物分析、稳定同位素 (δ¹³C/δ¹⁵N)、DNA 宏条形码

## METHODS

### 胃含物分析 (Stomach Content Analysis)
- 技术: 解剖镜检 + 分类鉴定
- 指标: 出现频率 (F%)、数量百分比 (N%)、重量百分比 (W%)
- 分析: 相对重要指数 (IRI)、食性宽度 (Levins index)
- 应用: 不同季节/体长/栖息地食性组成差异

### 稳定同位素 (Stable Isotope Analysis)
- 标记: δ¹³C (碳源指示)、δ¹⁵N (营养级指示)
- 分析: 贝叶斯混合模型 (MixSIAR/SIAR)
- 应用: 营养生态位、食性转变、食物网位置

### DNA 宏条形码 (DNA Metabarcoding)
- 技术: 通用引物扩增 + 高通量测序
- 标记: COI、18S、12S
- 应用: 高分辨率食性鉴定、稀有食物项检测

## OUTPUT TEMPLATE

```
刀鲚食性分析报告

1. 胃含物组成
   - 主要饵料: XX (IRI=XXXX)
   - 次要饵料: YY (IRI=YYY)
   - 空胃率: X%

2. 食性转变 (生活史阶段)
   - 仔鱼期: 浮游动物为主
   - 幼鱼期: 小型甲壳类 + 仔鱼
   - 成鱼期: 虾类 + 小型鱼类

3. 营养生态位
   - δ¹⁵N 范围: X.XX - Y.YY‰
   - δ¹³C 范围: X.XX - Y.YY‰
   - 营养级: X.X
   - 生态位宽度 (TA/SEAc): X.X

4. 季节性变化
   - 春季: XX
   - 夏季: YY
   - 秋季: ZZ
   - 冬季: WW
```
