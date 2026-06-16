# eon-workspace 🐟

**鱼类生态学多项目研究平台** — 7 个项目各司其职，一起把文献搜索、知识管理、物种分析串起来。

[English](README.md) · [更新日志](CHANGELOG.md) · [怎么参与](CONTRIBUTING.md)

---

## 这里面有什么

```
eon-workspace/
├── eon-core/                    ← 协调内核，管路由和服务发现
├── fish-ecology-assistant/      ← 26 个物种的知识库，查文献先看这儿
├── cognitive-search-engine/     ← 20 个引擎并行搜文献，搜完打分
├── porpoise-agent/              ← 江豚专场：声学分析 + 种群建模
├── coilia-agent/                ← 刀鲚专场：耳石微化学 + 洄游推断
├── culter-agent/                ← 鲌类专场：基因组 + 营养生态位
├── conflict-arbiter/            ← 保护级别冲突检测（IUCN vs 国标）
├── infrastructure/              ← 跨物种模式发现
├── scripts/                     ← 工作空间级脚本
├── config/                      ← 全局配置
└── docs/                        ← 架构文档
```

## 怎么用

```bash
# 加载所有项目
python -c "from scripts.project_loader import load_all; print(load_all())"

# 查物种文献（先查知识库，再搜网络）
python fish-ecology-assistant/scripts/run_lit_search.py "珠星三块鱼"

# 健康检查
python -c "from scripts.coordinator import coordinator; print(coordinator.health())"

# 跑全部测试
python scripts/run_all_tests.py
```

## 项目怎么配合

```
S  fish-ecology-assistant  →   知识库 + KB-First 搜索
    ↓ state_vector
T  porpoise-agent          →   任务调度 + 模型分析
    ↓ action_request
V  cognitive-search-engine →   搜索验证 + 可信度评分
    ↓ feedback_vector
S  …                       →   闭环
```

### 各项目干啥的

| 项目 | 说人话版本 |
|------|-----------|
| eon-core | 管其他项目怎么找到对方、怎么通信 |
| fish-ecology-assistant | 26种长江鱼的知识库，搜之前先看看有没有现成的 |
| cognitive-search-engine | 20个引擎同时搜，去重打分，保证不漏 |
| porpoise-agent | 专门研究长江江豚的声学和种群 |
| coilia-agent | 专门研究刀鲚的耳石和洄游路线 |
| culter-agent | 专门研究翘嘴鲌这些鲌类的基因组 |
| conflict-arbiter | IUCN说濒危、国标说无危？它来裁决 |

## 数据

- **知识库**: 26 个长江物种（含 7 个保护物种 + 三块鱼跨国分布）
- **文献图谱**: 48 个物种 / 176 篇论文
- **历史调查**: 443 个历史物种 / 323 个采集种（2017-2021）

## GitHub

| 仓库 | 地址 |
|------|------|
| eon-workspace | `github.com/fangtaocai041/s-t-v-p-workspace` |
| eon-core | `github.com/fangtaocai041/eon-core` |
| cognitive-search-engine | `github.com/fangtaocai041/cognitive-search-engine` |
| fish-ecology-assistant | `github.com/fangtaocai041/fish-ecology-assistant` |
| porpoise-agent | `github.com/fangtaocai041/porpoise-agent` |
| coilia-agent | `github.com/fangtaocai041/coilia-agent` |
| culter-agent | `github.com/fangtaocai041/culter-agent` |

## 许可证

MIT © 2026 fangtaocai041
