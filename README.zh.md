<p align="center">
  <a href="README.md">English</a>
</p>

# eon-workspace

> **三生万物 v8.2 �?六项目统一工作空间 + 物种全景分析管线**
> �?eon-core) �?S(fish知识) + T(cognitive验证) �?万物(P₁porpoise江豚 + P₂coilia刀�?+ P₃culter鲌类)

## 快速开�?

```bash
# 物种全景分析 (管线 Phase 0-5)
python workspace/scripts/run_full_analysis.py "珠星三块�? "Tribolodon brandti"

# 物种搜索
python eon-core/src/main.py search "珠星三块�?

# 运行测试�?(38�?
python workspace/scripts/test_pipeline.py

# 三角验证评分
python fish-ecology-assistant/scripts/run_lit_search.py "珠星三块�?

# 知识库→图谱同步
python fish-ecology-assistant/scripts/kb_to_graph_sync.py
```

## 目录结构

```
根目�?
├── eon-core/                  �?�? 协调内核
├── fish-ecology-assistant/    �?S: 知识供给
├── cognitive-search-engine/   �?T: 搜索验证+仲裁
├── porpoise-agent/            �?P�? 江豚
├── coilia-agent/              �?P�? 刀�?
├── culter-agent/              �?P�? 鲌类
└── workspace/                 �?配置/数据/文档/脚本
    ├── config/                �?coordination.yaml, VERSION.yaml
    ├── data/                  �?数据文件
    ├── scripts/               �?工作空间级脚�?
    ├── logs/                  �?运行日志
    └── docs/                  �?架构文档
```

## 项目一�?

| 项目 | 版本 | 角色 |
|------|:----:|------|
| eon-core | v8.1.0 | �?协调内核) |
| fish-ecology-assistant | v6.4.0 | S(知识供给) |
| cognitive-search-engine | v5.6.0 | T(搜索验证+仲裁) |
| porpoise-agent | v4.3.0 | P�?江豚) |
| coilia-agent | v1.2.0 | P�?刀�? |
| culter-agent | v2.0.0 | P�?鲌类) |

精简: conflict-arbiter �?cognitive 内嵌。eon-core 删除55个僵尸文件�?
