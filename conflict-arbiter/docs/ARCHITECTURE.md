# Architecture

Conflict Arbiter 是三角闭环的 C (仲裁) 层。

## 核心流程
1. 接收物种名
2. 查询多个保护级别数据源（IUCN / 中国红色名录 / 省级名录）
3. 加权裁决冲突
4. 输出最终结论 + 可信度
