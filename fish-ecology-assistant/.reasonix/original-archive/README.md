# 原始文件存档 — fish-ecology-assistant (灾难前快照)

**来源**: 工作空间根仓库 `s-t-v-p-workspace` 的 commit `7194383`  
**日期**: 2026-06-16 15:16:49（.git 被删除之前的最后一次快照）  
**提取时间**: 2026-06-17

## 背景

2026-06-16，fish-ecology-assistant 的 `.git` 目录被误删，独立仓库的提交历史永久丢失。
后从 Reasonix 会话日志恢复了文件内容（参见当前工作区的 recovery commits），
但 git 提交历史无法恢复。

本目录是从工作空间根仓库的 commit `7194383` 中提取的原始文件快照，
是灾难前的最后一版完整内容。

## 文件统计

| 目录 | 文件数 | 说明 |
|------|:------:|------|
| `src/` | 6 | Python 源码 |
| `scripts/` | 2 | 可执行脚本 |
| `tests/` | 4 | 测试文件 |
| `config/` | 8 | 配置文件 |
| `docs/` | 4 | 文档（含中文名文件） |
| `.reasonix/skills/` | 28 | AI Skill 剧本 |
| `.reasonix/handbooks/` | 16 | 工程手册 |
| `.reasonix/mcp-servers/` | 17 | MCP 服务配置 |
| `.reasonix/readme-versions/` | 7 | README 版本存档 |
| `research_output/` | 3 | 研究报告 |
| 根目录文件 | 11 | README/CHANGELOG/LICENSE 等 |
| **总计** | **113** | |

## 注意事项

- 当前工作区的文件是恢复后的版本（v6.5 + 新功能），**不要替换**
- 本存档仅作为历史参考和历史对比
- 未包含的文件：鱼种知识库 `fish_species_kb.yaml`（已在当前工作区 `config/` 中）
