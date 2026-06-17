# 三生万物 五项目工作空�?(v8.2)

> **物种全景分析管线 �?Phase 0:画像 �?1:统计 �?2:趋势 �?3:空白 �?4:涌现 �?5:假说**

## 架构概览

| 项目 | 角色 | 五行 | gRPC 端口 |
|------|------|:----:|:---------:|
| **eon-core** | UNIFIED_KERNEL (10层同�? | 全部 | �?|
| **fish-ecology-assistant** | S (State) �?V0 SupplyVertex | �?🟫 | 50051 |
| **cognitive-search-engine** | V (Validation) �?V1 VerifyVertex | �?🟨 | 50052 |
| **porpoise-agent** | P�?(衍生, DomainVertex) | �?💧 | 50053 |
| **coilia-agent** | P�?(衍生, DomainVertex) | �?🌲 | 50054 |
| **culter-agent** | P�?(衍生, DomainVertex) | �?🔥 | 50055 |

## 搜索协议

`workspace/skills/` �?`.reasonix/skills/` 内容一致，从两目录均可调用同一套搜索协议：

| Skill | 用�?| 模式 |
|-------|------|:----:|
| `graph-search-engine` | 图谱物种搜索 v4.1 | subagent |
| `cognitive-species-search` | 认知物种搜索 v3.2 | subagent |
| `chinese-academic-search` | 中文期刊搜索 | inline |
| `self-evolve` | 自进化反馈引�?| subagent |
| `parallel-farm` | 并行�?agent 派发 | inline |
| `meso-orchestrator` | 跨项目协�?| subagent |
| `auto-skill` | 自动技能沉淀 | inline |
| `ocr-solution-audit` | OCR 方案审计 | subagent |

### 调用方式

```
# �?workspace 目录调用
/run_skill name:graph-search-engine arguments:"搜索 Ochetobius elongatus 文献"

# �?.reasonix 目录调用（等效）
/run_skill name:graph-search-engine arguments:"搜索 Ochetobius elongatus 文献"

# 物种全景分析 (推荐)
python scripts/run_full_analysis.py "珠星三块�? "Tribolodon brandti"

# 运行测试�?
python scripts/test_pipeline.py

# 单模�?
python scripts/trend_analyzer.py "珠星三块�?
python scripts/gap_analyzer.py "珠星三块�?
python scripts/cross_synthesis.py "珠星三块�? "Tribolodon brandti"
python scripts/reasoning_engine.py "珠星三块�? "Tribolodon brandti"

# CLI交互入口
python scripts/search_species.py "珠星三块�?

# 旧搜索管线（兼容�?
python scripts/pipeline_search_species.py "检索珠星三块鱼相关文献"
python scripts/coordinator.py           # 自检
python scripts/credibility_scorer.py --example
python scripts/self_evolve.py --example
```

## 快速开�?

```bash
# 1. 验证工作空间完整�?
python workspace/launch_all.py

# 2. 物种文献搜索（全管线�?
python workspace/scripts/pipeline_search_species.py "检索珠星三块鱼相关文献"

# 3. 仅查知识�?
python workspace/scripts/pipeline_search_species.py "珠星三块�? --phase lookup

# 4. 全栈健康检�?
python -c "from workspace.scripts.coordinator import coordinator; print(coordinator.info('cognitive'))"
```

## 统一入口 API

| 函数 | 路由 | 用�?|
|------|------|------|
| `search_species(name)` | �?cognitive-search-engine | 物种文献搜索 |
| `lookup_species(name)` | �?fish-ecology-assistant | 物种知识库查�?|
| `assess_conservation(name)` | �?porpoise-agent | 保护评估 |
| `assess_species(name)` | �?coilia-agent | 物种评估 (洄游/资源) |
| `health_check()` | �?全部项目 | 全栈健康检�?|

## 目录结构

```
workspace/
├── __init__.py              �?包标�?
├── launch_all.py            �?一键启�?+ 健康检�?
├── activate.ps1             �?PowerShell 环境激�?
├── README.md                �?本文�?
├── skills/                  �?搜索协议 skill 定义（与 .reasonix/skills/ 同步�?
�?  ├── graph-search-engine.md
�?  ├── cognitive-species-search.md
�?  ├── chinese-academic-search.md
�?  ├── self-evolve.md
�?  ├── parallel-farm.md
�?  ├── meso-orchestrator.md
�?  ├── auto-skill.md
�?  └── ocr-solution-audit.md
├── scripts/                 �?Python 可执行实�?
�?  ├── run_full_analysis.py         �?一键全量分�?Phase 0-5 🆕
�?  ├── kb_loader.py                 �?统一数据加载�?       🆕
�?  ├── trend_analyzer.py            �?研究趋势分析          🆕
�?  ├── gap_analyzer.py              �?研究空白识别          🆕
�?  ├── cross_synthesis.py           �?跨物种涌�?5检测器)   🆕
�?  ├── reasoning_engine.py          �?生态假说推�?6假说)   🆕
�?  ├── test_pipeline.py             �?管线测试�?38�?      🆕
�?  ├── search_species.py            �?CLI交互入口
�?  ├── pipeline_search_species.py   �?搜索管线(兼容)
�?  ├── coordinator.py               �?五项目协调器
�?  ├── credibility_scorer.py        �?三角验证评分
�?  ├── self_evolve.py               �?自进化反�?
�?  └── kb_to_graph_sync.py          �?KB↔图谱同�?
├── config/
�?  └── root_config/
�?      ├── species_graph.yaml       �?48物种 176论文
�?      └── meso_agent.yaml          �?Meso协调配置
├── data/                    �?数据文件
├── docs/                    �?架构文档
├── ocr/                     �?OCR 测试工具
├── logs/                    �?运行日志
├── search_records/          �?搜索记录
└── bin/                     �?可执行文�?
```

## 五项目即五独立仓�?

每个项目有独立的 `.git`，可单独开�?部署。`pipeline_search_species.py` 是它们的统一搜索入口�?

## 相关文档

- `config/VERSION.yaml` �?版本单源真相
- `config/coordination.yaml` �?跨项目协调协�?
- `docs/root_docs/ARCHITECTURE_OVERVIEW.md` �?整体架构说明
- `docs/root_docs/SANSHENG_WANWU.md` �?三生万物哲学
