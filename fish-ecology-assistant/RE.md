# RE · 工程记录 — fish-ecology-assistant 优化全案

> **RE = Record of Engineering** — 本文件记录该对话中所有优化操作，确保可复现、可验证、可审计。

---

## 一、优化背景

原 fish-ecology-assistant README 存在以下问题：

1. **哲学语言泛滥** — "Panta Rhei / 道生万物 / 太极图 / 系统论 / DeepSeek 效率" 等非技术表述遮罩真实功能
2. **代码不可执行** — README 中用自然语言描述流程，如 "Knowledge-First 二阶段搜索"，但缺少可直接调用的代码
3. **信息与项目不一致** — 版本号缺失、脚本列表不全、模块未列出
4. **缺乏测试基础设施** — 无 `pyproject.toml`、无 `tests/`、无 `CHANGELOG.md`
5. **根目录脏乱** — 70+ 条目，含 Zotero 废弃脚本、百度临时文件、测试图片

---

## 二、全量优化操作清单

### 2.1 fish-ecology-assistant 项目级操作（8 项）

| # | 操作 | 目标文件 | 状态 |
|:-:|:-----|:---------|:----:|
| 1 | 创建 `pyproject.toml` | `pyproject.toml` | ✅ |
| 2 | 增强 `src/__init__.py` 公共 API | `src/__init__.py` | ✅ |
| 3 | 创建 `tests/` + 24 个测试用例 | `tests/test_*.py` | ✅ |
| 4 | 创建 `research_output/` | `research_output/.gitkeep` | ✅ |
| 5 | 创建 `CHANGELOG.md` | `CHANGELOG.md` | ✅ |
| 6 | 重写 `README.md`（技术导向） | `README.md` | ✅ |
| 7 | 同步更新 `README.zh.md` | `README.zh.md` | ✅ |
| 8 | 修复代码 bug + 单例缓存 | `src/orchestrator.py`, `scripts/credibility_scorer.py` | ✅ |

### 2.2 根目录清理操作（5 类）

| 类别 | 操作 | 数量 | 状态 |
|:-----|:-----|:---:|:----:|
| Zotero 脚本 | → `scripts/archive/` | 24 个 | ✅ |
| 百度学术/知网 | → `cognitive-search-engine/scripts/` | 4 个 | ✅ |
| 水文数据 + BibTeX | → `workspace/data/` | 3 个 | ✅ |
| 临时测试/图片/junk | 删除 | 29 个 | ✅ |
| 缓存目录 | 删除 | 4 个 | ✅ |

### 2.3 全局项目 README 重写（6 个项目）

| # | 项目 | 英文 | 中文 |
|:-:|:-----|:---:|:---:|
| 1 | cognitive-search-engine | ✅ | ✅ |
| 2 | eon-core | ✅ | ✅ |
| 3 | porpoise-agent (P₁) | ✅ | ✅ |
| 4 | coilia-agent (P₂) | ✅ | ✅ |
| 5 | culter-agent (P₃) | ✅ | ✅ |
| 6 | conflict-arbiter (C) | ✅ | ✅ |

---

## 三、文件变更明细

### 3.1 fish-ecology-assistant 新增文件

```
fish-ecology-assistant/
├── pyproject.toml                          # 项目元数据 + pytest 配置
├── CHANGELOG.md                            # v1.0 → v6.5.1 完整版本记录
├── research_output/.gitkeep                # 输出目录
├── tests/__init__.py                       # 测试初始化
├── tests/test_orchestrator.py              # 9 个测试：import/health/info/kb_first/stages/singleton
├── tests/test_project_hub.py               # 8 个测试：triangle/derived/health/triangle_status/singleton
└── tests/test_shared.py                    # 7 个测试：whitelist/build_queries/ocr_variants
```

### 3.2 fish-ecology-assistant 修改文件

```
src/__init__.py              → 导出 9 个公共 API: FishEcologyOrchestrator, KbFirstResult, ProjectHub 等
src/orchestrator.py          → 修复 _match_species(): 支持 dict 类型同义名（防御 AttributeError）
                              → 添加 _orchestrator_instance 全局单例缓存
                              → README.md 版本从 578 行重写为 134 行
                              → README.zh.md 同步
scripts/credibility_scorer.py→ 增加弃用说明 docstring，指向 cognitive-search-engine
```

### 3.3 根目录清理

```
移入 scripts/archive/ (24):
  zotero_*.py ×22, reorganize_cnki.ps1, minimize-zotero-to-tray-1.1.5.xpi

移入 cognitive-search-engine/scripts/ (4):
  baidu_batch.py, baidu_classify.py, baidu_import.py, cnki_cookie_string.txt

移入 workspace/data/ (3):
  皇庄水文站_2025-05_2026-06.csv, 皇庄水文站_2026-05_2026-06.csv, 课题组_刘凯_全部文献.bib

删除 (33):
  测试脚本 ×7, 测试图片 ×13, MySQL 尝试 ×4, 垃圾 ×5, 缓存 ×4
```

---

## 四、README 重构对照

### 4.1 删除的内容（哲学表述 → 零残留）

| 旧版存在 | 处理 |
|:---------|:----:|
| "Panta Rhei · Everything Flows" 世界观 | ❌ 删除 |
| "道生一 · 一生二 · 二生三 · 三生万物" 引擎描述 | ❌ 删除 |
| "太极图 / 阴 / 阳" 角色比喻 | ❌ 删除 |
| "系统论 / 可执行哲学 / 涌现检测" | ❌ 删除 |
| "DeepSeek 思维效率 / 约束即自由" | ❌ 删除 |
| README 内嵌版本历史 | → 移至 CHANGELOG.md |

### 4.2 新增的内容（技术导向）

| 新增项 | 量 |
|:-------|:--|
| 可执行 Python 代码段 | 8 个 |
| CLI 命令示例 | 7 条 |
| API 参考表 | 4 个模块 |
| KbFirstResult 字段表 | 完整 dataclass |
| 标准章节结构 | 10 章 |

### 4.3 修复的代码 Bug

1. **`_match_species()` TypeError** — 知识库同义名字段可能是 `dict`（含 `name`/`ref`/`status` 键），原代码对字符串调用 `.lower()` 直接报 `AttributeError`。修复为 `isinstance(c_name, str)` → `isinstance(c_name, dict)` 二态支持。

2. **`get_orchestrator()` 非单例** — 每次调用创建新实例，与小写 `get_` 前缀语义不符。添加全局 `_orchestrator_instance` 缓存。

---

## 五、测试覆盖

```bash
$ python -m pytest fish-ecology-assistant/tests/ -v
============================= test session starts =============================
collected 24 items

fish-ecology-assistant/tests/test_orchestrator.py::test_importable PASSED
fish-ecology-assistant/tests/test_orchestrator.py::test_get_orchestrator PASSED
fish-ecology-assistant/tests/test_orchestrator.py::test_health PASSED
fish-ecology-assistant/tests/test_orchestrator.py::test_info PASSED
fish-ecology-assistant/tests/test_orchestrator.py::test_kb_first_lookup_known_species PASSED
fish-ecology-assistant/tests/test_orchestrator.py::test_kb_first_lookup_by_scientific PASSED
fish-ecology-assistant/tests/test_orchestrator.py::test_kb_first_lookup_unknown PASSED
fish-ecology-assistant/tests/test_orchestrator.py::test_stages_constant PASSED
fish-ecology-assistant/tests/test_orchestrator.py::test_singleton_pattern PASSED
fish-ecology-assistant/tests/test_project_hub.py::test_triangle_members PASSED
fish-ecology-assistant/tests/test_project_hub.py::test_derived_members PASSED
fish-ecology-assistant/tests/test_project_hub.py::test_get_hub PASSED
fish-ecology-assistant/tests/test_project_hub.py::test_hub_health_all PASSED
fish-ecology-assistant/tests/test_project_hub.py::test_hub_capabilities PASSED
fish-ecology-assistant/tests/test_project_hub.py::test_hub_triangle_status PASSED
fish-ecology-assistant/tests/test_project_hub.py::test_hub_singleton PASSED
fish-ecology-assistant/tests/test_project_hub.py::test_relationship_map PASSED
fish-ecology-assistant/tests/test_shared.py::test_journal_whitelist_not_empty PASSED
fish-ecology-assistant/tests/test_shared.py::test_journal_whitelist_has_chinese_journals PASSED
fish-ecology-assistant/tests/test_shared.py::test_journal_whitelist_has_international PASSED
fish-ecology-assistant/tests/test_shared.py::test_build_search_queries_with_chinese PASSED
fish-ecology-assistant/tests/test_shared.py::test_build_search_queries_scientific_only PASSED
fish-ecology-assistant/tests/test_shared.py::test_generate_ocr_variants PASSED
fish-ecology-assistant/tests/test_shared.py::test_generate_ocr_variants_with_limit PASSED

============================= 24 passed in 0.12s ==============================
```

---

## 六、优化后的根目录

```
D:\Reasonix\
├── fish-ecology-assistant/   (22py)  V0 知识供给  ← 全量优化
├── cognitive-search-engine/  (38py)  V1 搜索验证
├── eon-core/                 (14py)  Coordinator
├── porpoise-agent/           (57py)  P₁ 江豚
├── coilia-agent/             (22py)  P₂ 刀鲚
├── culter-agent/             (10py)  P₃ 鲌类
├── conflict-arbiter/          (5py)  C 仲裁
├── infrastructure/           (41py)  涌现/GBIF/NCBI
├── scripts/                  (84py)  CI + archive/
├── config/                   (2个)
├── 方陶文库/                 个人知识库
├── 刘凯老师课题组/            课题组数据
└── 【散落文件: 0 ✅】
```

---

## 七、黄金法则 — 未来维护

从本对话提炼的三条操作规则：

1. **README 只写两样东西**: 代码示例 + 事实描述。把 "Panta Rhei / 道 / 涌现" 留给技术委员会讨论，不要在公开文档中展示。
2. **文档改了就要加测试**: 每次 README 添加新代码段 → 同时在 `tests/` 加一个对应测试。`24/24 pass` 是对最新读者的免看门铃。
3. **根目录只放项目**: 散落的 70 个零散文件比一个 500 行的 README 更具杀伤力。建 `scripts/archive/`，不要怕开墓地；文件放进去总比永远迷失在根目录强。
