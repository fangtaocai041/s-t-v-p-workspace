# 🌊 三生万物 · SANSHENG WANWU

> **Eon-Taiji v8.2 — 七项目十层同心动态活体架构**
>
> 道生一 · 一生二 · 二生三 · 三生万物

```
eon-core/                   ← ☯️ 统一内核 (十层)
fish-ecology-assistant/     ← V0 知识供给 (S)
cognitive-search-engine/    ← V1 验证引擎 (V)
porpoise-agent/             ← P₁ 江豚专研
coilia-agent/               ← P₂ 刀鲚专研
culter-agent/               ← P₃ 鲌类专研
conflict-arbiter/           ← C  冲突仲裁
infrastructure/             ← 基础设施 (涌现检测/NLP/图像分类)
fishkb/                     ← 独立鱼类知识库 (在 fish-ecology-assistant 内)
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

# 标准管道
python -c "from eon-core.src.kernel.cross_project import CrossProjectPipeline; p=CrossProjectPipeline(); p.bootstrap(); print(p.run('鳤', mode='standard').summary)"
```

## 项目

| 项目 | 版本 | 顶点 | GitHub |
|------|------|:----:|--------|
| [eon-core](eon-core/) | v8.2.0 | ☯️ 内核 | [fangtaocai041/eon-core](https://github.com/fangtaocai041/eon-core) |
| [fish-ecology-assistant](fish-ecology-assistant/) | v6.6.0 | S/V0 | [fangtaocai041/fish-ecology-assistant](https://github.com/fangtaocai041/fish-ecology-assistant) |
| [cognitive-search-engine](cognitive-search-engine/) | v5.10.0 | V/V1 | [fangtaocai041/cognitive-search-engine](https://github.com/fangtaocai041/cognitive-search-engine) |
| [porpoise-agent](porpoise-agent/) | v2.2.0 | P₁ | [fangtaocai041/porpoise-agent](https://github.com/fangtaocai041/porpoise-agent) |
| [coilia-agent](coilia-agent/) | v1.4.0 | P₂ | [fangtaocai041/coilia-agent](https://github.com/fangtaocai041/coilia-agent) |
| [culter-agent](culter-agent/) | v2.1.0 | P₃ | [fangtaocai041/culter-agent](https://github.com/fangtaocai041/culter-agent) |
| [conflict-arbiter](conflict-arbiter/) | v1.1.0 | C | [fangtaocai041/conflict-arbiter](https://github.com/fangtaocai041/conflict-arbiter) |
| [infrastructure](infrastructure/) | v0.8.0 | 共享基础 | 本仓库内 |

## 管道

```
STANDARD:  fish.search → cognitive.verify → conflict.arbitrate → fish.score
FAST:      fish.search → fish.score
DOMAIN_P1: fish.search → porpoise.search → fish.score
DOMAIN_P2: fish.search → coilia.search → fish.score
DOMAIN_P3: fish.search → culter.search → fish.score
FULL:      fish.search → cognitive.verify → conflict.arbitrate → eon.analyze → fish.score
ARBITRATE: conflict.arbitrate
```

## 测试

| 项目 | 测试数 |
|------|:-----:|
| porpoise-agent | 185 |
| coilia-agent | 144 |
| cognitive-search-engine | 97 |
| eon-core | 65 |
| fish-ecology-assistant | 59 |
| infrastructure | 57 |
| conflict-arbiter | 48 |
| culter-agent | 36 |
| **总计** | **691** |

## 文档

| 文档 | 说明 |
|------|------|
| [Eon-Taiji 进化全量图谱](docs/Eon-Taiji%20进化全量图谱.md) | 完整进化历史 |
| [项目关系文档](docs/PROJECT_RELATIONSHIPS.md) | 七项目包含/调用关系 |
| [TAIJI 架构文档](docs/TAIJI_TETRAHEDRON_ARCHITECTURE.md) | 十层架构详解 |
| [VERSION.yaml](VERSION.yaml) | 单源版本真相 |
| [coordination.yaml](coordination.yaml) | 协调配置 |
| [方陶文库](方陶文库/) | 架构规范 + 生态学理论库 |
| [刘凯老师课题组](刘凯老师课题组/) | 课题组文献知识库 |

## 许可证

MIT © 2026 fangtaocai041
