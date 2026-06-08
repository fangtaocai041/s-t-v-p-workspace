# eon-workspace

> **Eon-Taiji v7.2 — 五项目十层同心动态活体架构**

```
eon-core/                   ← ☯️ 统一内核 (十层)
fish-ecology-assistant/     ← V0 知识供给 (S)
cognitive-search-engine/    ← V1 验证引擎 (V)
porpoise-agent/             ← V2 江豚专研 (P₁)
coilia-agent/               ← V3 刀鲚专研 (P₂)
scripts/project_loader.py   ← 统一 DirectLoader
```

## 快速开始

```bash
# 集成测试
python scripts/test_workspace.py

# eon-core 健康检查
python eon-core/src/main.py --config eon-core/config/taiji.yaml health

# eon-core 路由测试
python eon-core/src/main.py --config eon-core/config/taiji.yaml route "长江江豚种群恢复"
```

## 项目

| 项目 | 版本 | 顶点 | GitHub |
|------|------|:----:|--------|
| [eon-core](eon-core/) | v7.2.0 | ☯️ 内核 | [fangtaocai041/eon-core](https://github.com/fangtaocai041/eon-core) |
| [cognitive-search-engine](cognitive-search-engine/) | v5.3.0 | V1 | [fangtaocai041/cognitive-search-engine](https://github.com/fangtaocai041/cognitive-search-engine) |
| [fish-ecology-assistant](fish-ecology-assistant/) | v6.3.0 | V0 | [fangtaocai041/fish-ecology-assistant](https://github.com/fangtaocai041/fish-ecology-assistant) |
| [porpoise-agent](porpoise-agent/) | v4.3.0 | V2 | [fangtaocai041/porpoise-agent](https://github.com/fangtaocai041/porpoise-agent) |
| [coilia-agent](coilia-agent/) | v1.3.0 | V3 | [fangtaocai041/coilia-agent](https://github.com/fangtaocai041/coilia-agent) |

## 文档

| 文档 | 说明 |
|------|------|
| [Eon-Taiji 进化全量图谱](docs/Eon-Taiji%20进化全量图谱.md) | 完整进化历史 |
| [项目关系文档](docs/PROJECT_RELATIONSHIPS.md) | 五项目包含/调用关系 |
| [TAIJI 架构文档](docs/TAIJI_TETRAHEDRON_ARCHITECTURE.md) | 十层架构详解 |
| [VERSION.yaml](VERSION.yaml) | 单源版本真相 |
| [coordination.yaml](coordination.yaml) | 协调配置 |
