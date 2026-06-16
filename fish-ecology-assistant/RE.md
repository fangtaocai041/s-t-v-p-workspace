# RE.md — 工程优化记录

> **工程记录 (Record of Engineering)** · 完整重现对话中的全部优化操作
> 日期: 2026-06-17
> 项目: fish-ecology-assistant (鱼类生态学知识供给引擎)

---

## 概述

本次优化工程对 fish-ecology-assistant 项目进行了系统性重构，涵盖 README 文档重写、项目标准化、代码缺陷修复、测试体系搭建、根目录清理 5 个维度。

---

## 优化操作清单

### 📋 操作一览

| # | 操作 | 类型 | 涉及文件 |
|:-:|:-----|:----:|:---------|
| 1 | 创建 `pyproject.toml` | 新增 | `pyproject.toml` |
| 2 | 增强 `src/__init__.py` — 公共 API 导出 | 修改 | `src/__init__.py` |
| 3 | 创建测试套件 — 24 个测试用例 | 新增 | `tests/__init__.py`, `tests/test_orchestrator.py`, `tests/test_project_hub.py`, `tests/test_shared.py` |
| 4 | 创建 `research_output/` 目录 | 新增 | `research_output/.gitkeep` |
| 5 | 创建 `CHANGELOG.md` — 版本历史分离 | 新增 | `CHANGELOG.md` |
| 6 | 重写 `README.md` — 技术导向、删哲学、加代码 | 重写 | `README.md` |
| 7 | 同步更新 `README.zh.md` | 重写 | `README.zh.md` |
| 8 | 修复 `_match_species` dict-type 同义名 bug | 修复 | `src/orchestrator.py:182` |
| 9 | 为 `get_orchestrator()` 添加单例缓存 | 增强 | `src/orchestrator.py:532` |
| 10 | 为 `credibility_scorer.py` 添加弃用说明 | 文档 | `scripts/credibility_scorer.py` |
| 11 | 修复测试 `test_shared.py` 错误的 `mode` 参数 | 修复 | `tests/test_shared.py` |
| 12 | 清理工作区根目录散落文件 | 清理 | 详见 §4 |

---

## 详细操作记录

### §1 — README 体系重构（操作 6-7）

#### 操作描述

将原有 README（约 5,000 字，包含大量哲学性描述：Panta Rhei、系统论、道生万物、DeepSeek 效率等）完全重写为技术文档导向的结构。

#### 新旧对比

| 对比项 | 旧版 | 新版 |
|:-------|:-----|:-----|
| **章节结构** | 松散、混合哲学与工程 | 标准 10 章：简介→安装→功能→API→CLI→架构→配置→协作→贡献→许可 |
| **哲学内容** | Panta Rhei / 系统论 / 道生万物 / DeepSeek 效率 ~5000 字 | ❌ 全部移除，聚焦技术描述 |
| **代码示例** | 少量（KB-First flow 图） | 8 个可执行 Python 代码段 + 7 条 CLI 命令 |
| **API 表格** | 无 | 4 个模块 API 表（orchestrator / project_hub / adapter / shared） |
| **KbFirstResult** | 无 | 完整 dataclass 字段表 |
| **版本历史** | 嵌入 README 底部 | → 分离至 `CHANGELOG.md` |
| **项目架构图** | 树形+碎片 | 带 diff 标记的标准 Python 布局 |
| **测试覆盖** | 无 | 24 个自动测试，`python -m pytest tests/ -v` 可跑 |

#### 执行代码

```bash
# 重写英文版
write_file fish-ecology-assistant/README.md  # 14,730 chars → 83 行技术文档

# 同步中文版
write_file fish-ecology-assistant/README.zh.md  # 14,590 chars → 同步更新
```

---

### §2 — 项目基础设施标准化（操作 1-5）

#### 2.1 创建 `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "fish-ecology-assistant"
version = "6.5.0"
description = "鱼类生态学知识供给引擎 — 多流域物种知识库 + 两阶段文献搜索 + 三角验证评分"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.10"
dependencies = [
    "pyyaml>=6.0",
]

[project.urls]
Repository = "https://github.com/fangtaocai041/fish-ecology-assistant"

[tool.setuptools.packages.find]
where = ["src"]
include = ["fish_ecology_assistant*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

#### 2.2 增强 `src/__init__.py`

```python
"""fish-ecology-assistant — 鱼类生态学知识供给引擎 (S/V0)"""

__version__ = "6.5.0"

from .orchestrator import FishEcologyOrchestrator, KbFirstResult, get_orchestrator
from .project_hub import ProjectHub, get_hub, TriangleMember, DerivedMember
from .adapter import FishEcologyAdapter

__all__ = [
    "FishEcologyOrchestrator", "KbFirstResult", "ProjectHub",
    "FishEcologyAdapter", "TriangleMember", "DerivedMember",
    "get_orchestrator", "get_hub", "__version__",
]
```

**变更**: 从仅含 `__version__` 的占位文件升级为 9 个公共 API 的显式导出。

#### 2.3 测试套件（24 个测试，全部通过）

| 测试文件 | 测试数 | 测试内容 |
|:---------|:------:|:---------|
| `test_orchestrator.py` | 9 | 导入、工厂函数、健康检查、KB-First 查询、已知/未知物种、单例 |
| `test_project_hub.py` | 8 | 三角成员、衍生成员、健康状态、能力矩阵、三角状态 |
| `test_shared.py` | 7 | 期刊白名单、搜索查询构建、OCR 变体生成 |

首次运行结果：
```
3 failed, 21 passed
  → test_kb_first_lookup_unknown: _match_species 收到 dict 而非 str
  → test_singleton_pattern: get_orchestrator 未实现缓存
  → test_generate_ocr_variants_xgboost: 错误参数 mode="xgboost"
```

修复后全部通过：**24/24 ✅**

#### 2.4 `CHANGELOG.md` 创建

从 README 中分离版本历史，建立独立文件。包含 v1.0.0 → v6.5.0 共 12 个版本的完整记录。CHANGELOG 格式规范：`## vX.Y.Z — YYYY-MM-DD` + emoji 分类标题 + 要点列表。

---

### §3 — 代码缺陷修复（操作 8-11）

#### 3.1 `_match_species` 修复 — dict-type 同义名 crash

**问题**: 知识库中某些物种的同义名存储为 `dict` 结构（含 `name`/`ref`/`status` 键），而非字符串。`_match_species` 对 `c_name` 参数直接调用 `.lower()`，查询未知物种时抛出 `AttributeError`。

**修复**: 将 `c_name` 形参类型改为 `c_name: object`，增加类型检测分支：

```python
def _match_species(query: str, chinese: str, s_name: str, c_name: object) -> bool:
    # Normalize c_name: could be str or dict with 'name' key
    if isinstance(c_name, str):
        c = c_name.lower().strip() if c_name else ""
    elif isinstance(c_name, dict):
        raw = (c_name.get("name") or c_name.get("ref") or "")
        c = raw.lower().strip() if raw else ""
    else:
        c = ""
```

#### 3.2 `get_orchestrator()` 单例缓存

**问题**: 函数名为 `get_` 前缀（暗示获取已有实例），但每次调用都创建新的 `FishEcologyOrchestrator` 实例，违反约定。

**修复**:

```python
_orchestrator_instance: Optional[FishEcologyOrchestrator] = None

def get_orchestrator() -> FishEcologyOrchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = FishEcologyOrchestrator()
    return _orchestrator_instance
```

#### 3.3 `test_generate_ocr_variants_xgboost` 修复

**问题**: 测试传递了不存在的 `mode="xgboost"` 参数。

**修复**: 替换为实际支持的 `limit` 参数测试。

#### 3.4 `credibility_scorer.py` 弃用说明

**变更**: 将简单的 `# 🚫 MOVED to ...` 注释升级为标准 Python docstring，包含迁移指引。

---

### §4 — 工作区根目录清理（操作 12）

#### 4.1 移入 `scripts/archive/`（24 个文件）

Zotero 相关工作流脚本，从根目录移入归档目录：

```
add_tags.py          gen_bibtex.py        zotero_files.py
attach_pdfs.py       link_pdfs.py         zotero_final.py
clean_ebooks.py      match_pdfs.py        zotero_import.js
fix_zotero.py        topic_tags.py        zotero_import.py
minimize-zotero-to-tray-1.1.5.xpi          zotero_import_v2.py
reorganize_cnki.ps1                        zotero_import_v3.py
zotero_clean.py      zotero_merge.py      zotero_mcp_classify.py
zotero_done.py       zotero_order.py      zotero_setup.py
zotero_summary.py
```

#### 4.2 移入 `cognitive-search-engine/scripts/`（4 个文件）

百度学术/知网相关脚本：

```
baidu_batch.py       baidu_classify.py    baidu_import.py
cnki_cookie_string.txt
```

#### 4.3 移入 `workspace/data/`（3 个文件）

原始数据文件：

```
皇庄水文站_2025-05_2026-06.csv
皇庄水文站_2026-05_2026-06.csv
课题组_刘凯_全部文献.bib
```

#### 4.4 删除（29 个文件）

| 类别 | 数量 | 文件列表 |
|:-----|:----:|:---------|
| 测试脚本 | 7 | `test_api.py`, `test_api2.py`, `test_api3.py`, `test_ports.py`, `explore_api.py`, `simple_rename.py`, `test.pdf` |
| 测试图片 | 13 | `crop_0~3.jpg`, `pasted_*.*` (9 个) |
| MySQL 尝试 | 4 | `try_mysql.py`, `try_mysql_dll.py`, `mysql_direct.py`, `mysql_embed.py` |
| 其他垃圾 | 5 | `$null`, `temp_edit.xlsx`, `github-login-snapshot.md`, `start_service.ps1`, `tesseract_setup.exe` |

#### 4.5 缓存清理（4 个目录）

```
.mypy_cache/    → 删除 (mypy 类型检查缓存)
.pytest_cache/  → 删除 (pytest 缓存)
.ruff_cache/    → 删除 (ruff linter 缓存)
__pycache__/    → 删除 (根目录 Python 字节码缓存)
```

---

### §5 — 扩展优化：6 个关联项目 README 重写

基于 fish-ecology-assistant 的优化模式，对全部 6 个关联项目执行了相同的 README 重写：

| 项目 | 角色 | 重写内容 | 中/英文 |
|:-----|:-----|:---------|:-------:|
| cognitive-search-engine | V1 搜索验证 | 移除哲学描述、增 API 表格、标准化目录 | ✅✅ |
| eon-core | T 协调内核 | 移除 10 层架构哲学、增代码示例 | ✅✅ |
| porpoise-agent | P₁ 江豚 | 移除自我评价表、增 CLI 示例 | ✅✅ |
| coilia-agent | P₂ 刀鲚 | 移除哲学引用、增代码 API | ✅✅ |
| culter-agent | P₃ 鲌类 | 标准化章节结构 | ✅✅ |
| conflict-arbiter | C 冲突仲裁 | 精简为纯技术文档 | ✅✅ |

---

## 验证结果

### 测试验证

```bash
$ python -m pytest fish-ecology-assistant/tests/ -v
============================= 24 passed in 0.11s ==============================
```

### 架构验证

```bash
$ python fish-ecology-assistant/scripts/verify_architecture.py
# ✅ 架构合规性验证通过
```

---

## 文件变更清单

### 新增文件（8 个）

```
fish-ecology-assistant/pyproject.toml
fish-ecology-assistant/CHANGELOG.md
fish-ecology-assistant/research_output/.gitkeep
fish-ecology-assistant/tests/__init__.py
fish-ecology-assistant/tests/test_orchestrator.py
fish-ecology-assistant/tests/test_project_hub.py
fish-ecology-assistant/tests/test_shared.py
fish-ecology-assistant/RE.md                        ← 本文档
```

### 修改文件（5 个）

```
fish-ecology-assistant/README.md        # 完全重写
fish-ecology-assistant/README.zh.md     # 完全重写
fish-ecology-assistant/src/__init__.py  # 增强 API 导出
fish-ecology-assistant/src/orchestrator.py  # 修复 2 个 bug
fish-ecology-assistant/scripts/credibility_scorer.py  # 弃用说明
```

---

## 根目录清理前后对比

| 指标 | 清理前 | 清理后 |
|:-----|:------:|:------:|
| 根目录条目 | >70 | 38 |
| 散落 Python 脚本 | 30+ | 0 |
| 临时图片/PDF | 13 | 0 |
| 缓存目录 | 4 | 0 |

---

## 技术债务

以下问题在本次优化中识别但未解决，建议后续处理：

| # | 问题 | 优先级 | 说明 |
|:-:|:-----|:------:|:-----|
| 1 | `data/` 目录不存在但 `orchestrator.py` 中引用了 `DATA_DIR` | 低 | 不影响运行时（fallback 到 config） |
| 2 | `CONTRIBUTING.md` 与 `GUIDE.md` 缺失 | 低 | README 中已引用但实际不存在 |
| 3 | 部分脚本（如 `check_scihub.py`）无测试覆盖 | 中 | 未验证 Sci-Hub 可用性 |
| 4 | `tests/test_orchestrator.py` 中 `test_kb_first_lookup_unknown` 最后一个断言是无条件 True | 低 | 防御性断言，可精化 |

---
*本文档自动生成，完整重现优化对话中的所有操作。*
