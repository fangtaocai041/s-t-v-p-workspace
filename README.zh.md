# 三生万物 \u00b7 SanSheng WanWu

> **Eon-Taiji v8.2 \u2014 七项目十层同心动态活体架构

>
> 道生一 \u00b7 一生二 \u00b7 二生三 \u00b7 三生万物

```
eon-core/                   \u2192 统一内核 (十层)
fish-ecology-assistant/     \u2192 V0 知识供给 (S)
cognitive-search-engine/    \u2192 V1 验证引擎 (V)
porpoise-agent/             \u2192 P1 江豚专研
coilia-agent/               \u2192 P2 刀鲚专研
culter-agent/               \u2192 P3 鲌类专研
conflict-arbiter/           \u2192 C  冲突仲裁
infrastructure/             \u2192 基础设施 (涌现检测/NLP/图像分类)
fishkb/                     \u2192 独立鱼类知识库
workspace/                  \u2192 统一工作空间 (配置/数据/脚本)
san-sheng-wanwu-core/       \u2192 硅基生命体架构 (RCCA v2.1)
```

## 快速开始

详见 [workspace/README.md](workspace/README.md)

## 项目一览

| 项目 | 版本 | 顶点 | GitHub |
|------|:----:|:----:|--------|
| eon-core | v8.2.0 | 内核 | [fangtaocai041/eon-core](https://github.com/fangtaocai041/eon-core) |
| fish-ecology-assistant | v6.6.0 | S/V0 | [fangtaocai041/fish-ecology-assistant](https://github.com/fangtaocai041/fish-ecology-assistant) |
| cognitive-search-engine | v5.10.0 | V/V1 | [fangtaocai041/cognitive-search-engine](https://github.com/fangtaocai041/cognitive-search-engine) |
| porpoise-agent | v2.2.0 | P1 | [fangtaocai041/porpoise-agent](https://github.com/fangtaocai041/porpoise-agent) |
| coilia-agent | v1.4.0 | P2 | [fangtaocai041/coilia-agent](https://github.com/fangtaocai041/coilia-agent) |
| culter-agent | v2.1.0 | P3 | [fangtaocai041/culter-agent](https://github.com/fangtaocai041/culter-agent) |
| conflict-arbiter | v1.1.0 | C | [fangtaocai041/conflict-arbiter](https://github.com/fangtaocai041/conflict-arbiter) |
| san-sheng-wanwu-core | v2.1.0 | RCCA | [fangtaocai041/san-sheng-wanwu-core](https://github.com/fangtaocai041/san-sheng-wanwu-core) |
| infrastructure | v0.8.0 | 共享基础 | 本仓库内 |

## RCCA 集成 (v2.1.0)

RCCA 已部署到全部7个子项目。详见 [workspace/README.md](workspace/README.md)

## 感受器层 (workspace/senses/)

便携感知协议 + 学科知识图谱 (12领域), 零外部依赖。详见 [workspace/README.md](workspace/README.md)


## 交互式引导（目的模糊时用）

当你不知道想做什么时，用这些斜杠命令找方向：

| 命令 | 用途 |
|------|------|
| /explore-workspace | “不知道能做什么” — 聊聊兴趣，推荐路径 |
| /focus-research | “有个模糊的研究想法” — 逐步聚焦到可执行计划 |
| /discover-species | “不知道研究哪种鱼” — 随机/关联/主题发现 |
| /capabilities | “还有什么我能用的？” — 全景能力一览 |

建议：任何时候觉得目的模糊，先敲 /explore-workspace。聊着聊着就清楚了。

## 管线

```
STANDARD:  fish.search -> cognitive.verify -> conflict.arbitrate -> fish.score
FAST:      fish.search -> fish.score
FULL:      fish.search -> cognitive.verify -> conflict.arbitrate -> eon.analyze -> fish.score
PHASE_0-5: portrait -> stats -> trend -> gaps -> synthesis -> reasoning
```

## 测试 (910 项)

| 项目 | 测试数 |
|------|:-----:|
| san-sheng-wanwu-core | 181 |
| porpoise-agent | 185 |
| coilia-agent | 144 |
| cognitive-search-engine | 97 |
| eon-core | 65 |
| fish-ecology-assistant | 59 |
| infrastructure | 57 |
| conflict-arbiter | 48 |
| culter-agent | 36 |
| workspace pipeline | 38 |

## 文档

- VERSION.yaml —— 单源版本真相
- coordination.yaml —— 跨项目协调配置
- [workspace/README.md](workspace/README.md) —— workspace 级使用指南

## 许可证
MIT (c) 2026 fangtaocai041
