<p align="center">
  <a href="README.md">English</a>
</p>

# eon-workspace

> **三生万物 v8.1 — 六项目统一工作空间**
> 道(eon-core) → S(fish知识) + T(cognitive验证) → 万物(P₁porpoise江豚 + P₂coilia刀鲚 + P₃culter鲌类)

## 快速开始

```bash
# 物种搜索
python eon-core/src/main.py search "珠星三块鱼"

# 三角验证评分
python fish-ecology-assistant/scripts/run_lit_search.py "珠星三块鱼"

# 知识库→图谱同步
python fish-ecology-assistant/scripts/kb_to_graph_sync.py
```

## 目录结构

```
根目录/
├── eon-core/                  → 道: 协调内核
├── fish-ecology-assistant/    → S: 知识供给
├── cognitive-search-engine/   → T: 搜索验证+仲裁
├── porpoise-agent/            → P₁: 江豚
├── coilia-agent/              → P₂: 刀鲚
├── culter-agent/              → P₃: 鲌类
└── workspace/                 → 配置/数据/文档/脚本
    ├── config/                → coordination.yaml, VERSION.yaml
    ├── data/                  → 数据文件
    ├── scripts/               → 工作空间级脚本
    ├── logs/                  → 运行日志
    └── docs/                  → 架构文档
```

## 项目一览

| 项目 | 版本 | 角色 |
|------|:----:|------|
| eon-core | v8.1.0 | 道(协调内核) |
| fish-ecology-assistant | v6.4.0 | S(知识供给) |
| cognitive-search-engine | v5.6.0 | T(搜索验证+仲裁) |
| porpoise-agent | v4.3.0 | P₁(江豚) |
| coilia-agent | v1.2.0 | P₂(刀鲚) |
| culter-agent | v2.0.0 | P₃(鲌类) |

精简: conflict-arbiter → cognitive 内嵌。eon-core 删除55个僵尸文件。
