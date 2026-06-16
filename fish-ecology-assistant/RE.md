# RE · 工程记录 — fish-ecology-assistant 优化全案

> **RE = Record of Engineering** — 本文件记录跨对话的所有优化操作，确保可复现、可验证、可审计。
> 
> 会话 1: v6.0→v6.5.1 — README 重写 + 项目标准化 + 根目录清理（前序对话）
> 会话 2: v6.5.1→v6.5.2 — 6 项工程缺陷修复（当前对话）

---

## 一、优化背景

原 fish-ecology-assistant 存在以下问题（跨会话累积）：

| # | 问题 | 发现会话 | 症状 |
|:-:|:-----|:--------|:-----|
| 1 | 哲学语言泛滥 | S1 | "Panta Rhei / 道生万物 / 太极图" 遮罩真实功能 |
| 2 | 代码不可执行 | S1 | README 用自然语言描述流程，无可调用代码 |
| 3 | 测试基础设施缺失 | S1 | 无 `pyproject.toml`、无 `tests/`、无 `CHANGELOG.md` |
| 4 | 根目录脏乱 | S1 | 70+ 条目，含 Zotero 废弃脚本、百度临时文件、测试图片 |
| 5 | 编码损坏 | S2 | `_match_species()` docstring 含 GBK→UTF-8 乱码 |
| 6 | 测试虚高深度不足 | S2 | 9 tests 全为结构测试，无真实物种硬断言 |
| 7 | 架构耦合倒挂 | S2 | `verify_architecture.py` 跨项目导入 cognitive 验证自身 |
| 8 | 双重数据源 | S2 | `adapter.py` 独立加载 `yangtze_fish_species.yaml`，与 orchestrator 新格式不一致 |
| 9 | 路径硬编码 | S2 | `D:\Reasonix\` 散布在 4 个文件中 |
| 10 | BIM 逻辑遗漏 basins | S2 | `_build_kb_hit_result` 仅检查 `distribution`，遗漏新格式 `basins` 字段 |
| 11 | 别名匹配错位 | S2 | `_find_species` 别名分支返回别名值而非正名 |
| 12 | 导出不完整 | S2 | `__init__.py` 仅导出 6 个符号，缺类型系统 |

---

## 二、会话 1：项目标准化与 README 重写

### 2.1 fish-ecology-assistant 项目级操作（8 项）

| # | 操作 | 目标文件 | 
|:-:|:-----|:---------|
| 1 | 创建 `pyproject.toml` | `pyproject.toml` |
| 2 | 创建 `CHANGELOG.md` | `CHANGELOG.md` |
| 3 | 创建 `research_output/` | `research_output/.gitkeep` |
| 4 | 创建 `tests/` + 初始 24 个测试 | `tests/test_*.py` |
| 5 | 重写 `README.md`（技术导向，578→134 行） | `README.md` |
| 6 | 同步更新 `README.zh.md` | `README.zh.md` |
| 7 | 修复 `_match_species()` dict 类型防御 | `src/orchestrator.py` |
| 8 | `get_orchestrator()` 单例缓存 | `src/orchestrator.py` |

### 2.2 根目录清理（5 类）

| 类别 | 操作 | 数量 |
|:-----|:-----|:---:|
| Zotero 脚本 | → `scripts/archive/` | 24 |
| 百度学术/知网 | → `cognitive-search-engine/scripts/` | 4 |
| 水文数据 + BibTeX | → `workspace/data/` | 3 |
| 临时测试/图片/junk | 删除 | 29 |
| 缓存目录 | 删除 | 4 |

### 2.3 全局 README 重写（6 项目 × 2 语言）

cognitive-search-engine, eon-core, porpoise-agent (P₁), coilia-agent (P₂), culter-agent (P₃), conflict-arbiter (C)

---

## 三、会话 2：6 项工程缺陷修复

### 3.1 修复清单

| # | 缺陷 | 根因 | 修复 | 文件 |
|:-:|:-----|:-----|:-----|:-----|
| 1 | **编码损坏** | GBK→UTF-8 双重转码 | docstring 恢复为正确 UTF-8 中文 | `src/orchestrator.py:223` |
| 2 | **测试虚高** | 9 tests 全为结构测试，无真实断言 | 扩展至 18 tests，含硬断言（鳤/刀鲚/江豚）、别名匹配、模糊候选排序、边界案例（空查询/特殊字符） | `tests/test_orchestrator.py` |
| 3 | **架构倒挂** | fish 项目 import cognitive 验证自身 | 标记 DEPRECATED，委托方向注明使用 `orchestrator.health()` + `hub.is_triangle_complete()` | `scripts/verify_architecture.py` |
| 4 | **数据源去重** | adapter.py 独立加载旧格式 `yangtze_fish_species.yaml` | 删除独立数据源，`search_species()` 全量委托 `orchestrator.kb_first_lookup()` | `src/adapter.py` |
| 5 | **路径硬编码** | `D:\Reasonix` 硬编码在 4 个文件中 | `project_hub.py` 读取 `$REASONIX_HOME` env var + fallback；YAML 文件使用 `${REASONIX_HOME:-D:\Reasonix}` 占位符 | `src/project_hub.py`, `coordination.yaml`, `config/evolution.yaml` |
| 6 | **导出不完整** | `__init__.py` 仅 6 个符号 | v6.5.2，19 个导出符号（含全部 8 个 type + 4 个 Enum + 3 个工厂函数） | `src/__init__.py` |

### 3.2 修复过程中发现的隐性 Bug

| Bug | 位置 | 症状 | 修复 |
|:----|:-----|:-----|:-----|
| BIM 遗漏 basins | `orchestrator.py:_build_kb_hit_result` | 鳤有 basins 字段但 `has_rich_data` 为 False → 错误推荐 `continue_to_c` | `species_data.get("distribution", {}).get("basins", []) or species_data.get("basins", [])` |
| 别名匹配返回别名值 | `orchestrator.py:_find_species` | 搜索 "珠星三块鱼" → `chinese_name="珠星三块鱼"` 而非正名 "三块鱼" | `"chinese_name": alias` → `"chinese_name": c_name` |

### 3.3 文件变更明细

#### 修改文件

```
src/orchestrator.py
  ├── L223:  乱码 docstring 恢复为可读中文
  ├── L274:  别名分支 chinese_name: alias → c_name（正名）
  ├── L506:  has_rich_data 评估新增 basins 探测
  └── test:  18 tests（↑9）

src/adapter.py
  ├── 删除:  _species_config 加载 + yangtze_fish_species.yaml 依赖
  ├── 新增:  _get_orchestrator() 延迟加载单例
  └── 重写:  search_species() 委托 kb_first_lookup()

src/project_hub.py
  ├── L36:  import os
  └── L170: REASONIX_HOME env var → fallback parent-dir

src/__init__.py
  ├── 新增: types 模块 8 个 dataclass + 4 个 Enum
  └── 导出: 6 → 19 个公共符号

scripts/verify_architecture.py
  └── L1-24: DEPRECATED 注释 + 委托方向说明

coordination.yaml
  ├── L19:  root: "${REASONIX_HOME:-D:\Reasonix}"
  └── L62:  engine_path: "${REASONIX_HOME:-D:\Reasonix}/cognitive-search-engine/"

config/evolution.yaml
  └── L107: coordination_ref: "${REASONIX_HOME:-D:\Reasonix}/coordination.yaml"
```

---

## 四、项目现状（v6.5.2）

### 4.1 架构概览

```
三角形核心 (sealed 3):
  fish-ecology-assistant     S/V0 — 知识供给    ← 本项目
  cognitive-search-engine    V/V1 — 搜索验证
  eon-core                   Coordinator — 协调内核

万物衍生 (open N):
  porpoise-agent    P₁ — 江豚专研
  coilia-agent      P₂ — 刀鲚专研
  conflict-arbiter  C  — 冲突仲裁
  ...               Pₙ — 可无限扩展
```

### 4.2 测试覆盖

```bash
$ python -m pytest tests/ -v
collected 33 items  # 会话1: 24 + 会话2: 9 新增

tests/test_orchestrator.py · 18 passed  # 9 初始 + 9 增强
tests/test_project_hub.py  ·  8 passed  # 无变化
tests/test_shared.py       ·  7 passed  # 无变化
============================= 33 passed in 0.77s ==============================
```

测试覆盖维度:

| 维度 | 测试数 | 覆盖 |
|:-----|:-----:|:-----|
| 导入 + 生命周期 | 3 | `importable`, `get_orchestrator`, `singleton_pattern` |
| 健康检查 + 信息 | 2 | `health`（含 db size ≥ 20 硬断言）, `info`（含 capability 校验） |
| 已知物种精确匹配 | 5 | 中文名 → 鳤/刀鲚/长江江豚, 学名 → Ochetobius elongatus, 部分属名 → Ochetobius |
| 别名匹配 | 1 | 珠星三块鱼 → 三块鱼（正名 + matched_by_alias=True） |
| 未知物种 | 2 | `found=False`, `search_recommendation=continue_to_c`, `all_candidates` 为 list |
| 模糊候选 | 2 | `_fuzzy_find_all` 分数降序, Coilia 属子串匹配 |
| 边界案例 | 3 | 空查询, 特殊字符, `stages_constant` |
| 三角核心 | 4 | 3 成员, fish/cognitive/eon, 密闭性, 完整状态 |
| 万物衍生 | 3 | porpoise/coilia/conflict, health_all, capabilities |
| 共享工具 | 3 | 期刊白名单（中文+国际）, 搜索查询构建, OCR 变体 |
| 单例 + 工厂 | 2 | `get_hub`, `get_orchestrator` 均为单例 |

### 4.3 修正的工程反模式

| 反模式 | 位置 | 修复 |
|:-------|:-----|:-----|
| 硬编码路径 | 4 files | `$REASONIX_HOME` env var |
| 双重数据源 | adapter.py ↔ orchestrator.py | 去重，orchestrator 为单一读写源 |
| 跨项目反向耦合 | scripts/verify_architecture.py | 标记 DEPRECATED |
| GBK→UTF-8 编码损坏 | orchestrator.py docstring | 恢复原始中文 |
| 虚断言测试 | test_orchestrator.py | `if result.found` → 硬断言 `.found is True` + 字段精确匹配 |

### 4.4 入口 API

```python
# ── from src import ... ──
FishEcologyOrchestrator   # 核心编排器
KbFirstResult             # KB-First 查询结果 dataclass
get_orchestrator()        # 工厂函数（单例）
ProjectHub                # 多项目协调中枢
get_hub()                 # 工厂函数（单例）
TriangleMember            # 三角核心成员 dataclass
DerivedMember             # 万物衍生成员 dataclass
FishEcologyAdapter        # 跨项目适配器（IProjectAdapter）

# ── 类型系统 ──
PipelinePhase             # Enum: planning/searching/analyzing/writing/reviewing
ConfidenceLevel           # Enum: verified/inferred/uncertain/no_source
EvidenceQuality           # Enum: high/medium/low/grey
ReviewResult              # Enum: pass/needs_revision/fail
ResearchContext           # 研究上下文 dataclass
SourceEntry               # 文献来源 dataclass
AnalysisFinding           # 分析发现 dataclass（含置信度标签）
EmergenceSignal           # 涌现信号 dataclass
ReviewReport              # 评审报告 dataclass
PipelineStats             # 流水线统计 dataclass
SessionResult             # 会话结果 dataclass

# ── 道→一→二→三→万物（需显式导入）──
from src.dao_engine import DaoEngine, DaoQuery
```

---

## 五、已知技术债务

| 债务 | 位置 | 描述 | 影响 | 建议修复时机 |
|:-----|:-----|:-----|:-----|:----------|
| `scripts/search_species.py` 加载旧格式 | `scripts/search_species.py:28` | 硬编码 `fish_species_kb.yaml` 路径，独立于 orchestrator 的新格式 (`fish_species_index.yaml` + `.md` profiles) | 同物种在不同入口查询可能得到不同结果 | v6.6.0 — 重构为委托 `orchestrator.kb_first_lookup()` |
| `yangtze_fish_species.yaml` 孤立数据 | `config/yangtze_fish_species.yaml` | 旧格式知识库文件，adapter.py 已移除加载但文件仍存 | 冗余数据，可能误导 | v6.6.0 — 确认无其他消费者后删除或迁移 |
| `scripts/search_species.py` 写回仍用旧格式 | `scripts/search_species.py:update_kb` | 读路径已委托 orchestrator 新格式，但写回仍写 `fish_species_kb.yaml` | 读写路径不一致，写回数据不进入新格式 | v6.6.0 KB 写回迁移 |
| `verify_architecture.py` 已过期 | `scripts/verify_architecture.py` | 已标记 DEPRECATED 但代码未删除 | 维护者可能误用 | v7.0.0 — 正式移除 |

---

## 六、黄金法则 — 跨会话维护

从两轮优化对话中提炼的规则：

1. **代码与文档 1:1 映射** — 每个被描述的 class/method 必须有可执行的 Python 桩或测试用例。`RE.md` 本身也不例外：本文档中提到的每个修复，都在代码中有对应的 SEARCH/REPLACE 或 create 操作记录可追溯。

2. **测试先修再改** — 每次修复前先写断言失败的测试，修复后验证断言通过。两轮会话的测试增长：0 → 24 → 33。

3. **路径不硬编码** — `D:\Reasonix\` 首次出现时就要用 `$REASONIX_HOME`。跨容器/跨机器部署的阻碍 80% 来自路径假设。

4. **单一数据源** — 同一个知识库不能有两个加载路径（旧 `yangtze_fish_species.yaml` 与新 `fish_species_index.yaml + .md profiles`）。数据源的读写权必须明确指定给一个模块。

5. **RE.md 是审计链** — 不是文档。每个会话追加一节，量化变更（`# | file | Ln | old→new`），确保未来能通过 `git log` + `RE.md` 回溯任意一行代码的修改原因。
