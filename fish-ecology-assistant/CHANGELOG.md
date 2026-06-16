# Changelog

> 版本变更记录。版本副本保存在 `.reasonix/readme-versions/`。

---

## v6.5.2 — 2026-06-17

### 📝 RE.md 工程优化记录

- 创建 `RE.md` — 完整重现对话中所有优化操作的工程记录文档
- 覆盖 12 项操作：README 重写、项目标准化、代码缺陷修复、测试体系搭建、根目录清理
- 24/24 测试全部通过验证

---

## v6.5.1 — 2026-06-17

### 🔄 灾难前快照恢复

- 从工作空间根仓库 `s-t-v-p-workspace` commit `7194383` 提取了灾难前最后一版完整快照
- 全部 113 个原始文件已存档至 `.reasonix/original-archive/`
- 原始 README 已加入 `.reasonix/readme-versions/` 作为 v0 (pre-disaster)
- git 提交历史无法恢复（`.git` 目录误删且未推送到 remote）

---

## v6.5.0 — 2026-06-12

### 🧬 KB-First 两阶段搜索

- KB-First 两阶段搜索架构：`kb_first_lookup()` 先查知识库 → 用户决策 → `continue_full_search()` 全量搜索
- `ProjectHub` 统一加载 5 个子系统（⊂cognitive ∥porpoise ∥coilia ⫛eon-core ⊢conflict）
- `search_species()` 统一入口方法
- `delegate_to()` 跨项目委托协议

### 🏠 宿主容器架构

- 宿主容器架构重写，`src/project_hub.py` 作为统一协调中枢
- `src/orchestrator.py` 精简为轻量级 API 层
- `TRIANGLE` + `DERIVED` 数据类规范定义三角/万物结构

---

## v6.4.0 — 2026-06-09

### 🔧 工程架构规范化

- 精确匹配器 `_match_species()`：支持学名/中文名/别名/同义名
- `taxonomy_log` 分类变更记录：含时间·期刊·作者证据
- `detect_taxonomy_discrepancy()` 跨项目分类一致性检测
- `verify_architecture.py` 架构合规性验证脚本
- 项目职责边界声明（工程语言而非哲学语言）

---

## v6.3.0 — 2026-06-08

### ☯️ 10 层同心架构

- 10 层同心架构集成（OriginKernel → YinYang → Vertices → ...）
- conflict-arbiter (V4) 冲突仲裁模块集成
- 三角核心密闭性检查 `is_triangle_complete()`

---

## v6.2.0 — 2026-06-08

### 🌊 S-T-V-P₁-P₂ 生态系统

- S-T-V-P₁-P₂ 五项目生态系统定义
- 长江 443 种鱼类知识库录入
- Meso-Cosmos 智能调度协议

---

## v6.1.0 — 2026-06-07

### 🔗 跨项目协同进化

- 跨项目协同进化协议
- S-T-V 三角角色增强定义
- `coordination.yaml` 统一协调配置

---

## v6.0.0 — 2026-06-07

### 🧠 Cognitive Search Engine DirectLoader

- CognitiveSearch DirectLoader 协议（`importlib` 零进程加载）
- 双模式搜索：轻量 `ParallelSearch` + 完整 `CognitiveAgent` BDI ReAct
- 知识图谱进化：`species_graph.yaml` 积累共享

---

## v5.0.0 — 2026-06-06

### 🔍 12 引擎搜索

- 12 搜索引擎并行（GS 优先 + 4 中文源）
- `cognitive-search-engine/scripts/search_api.py` 搜索编排器
- 搜索 v3.0 架构

---

## v4.0.0 — 2026-06-06

### 🧠 双核哲学

- 双核哲学引擎（Panta Rhei + 系统论）
- 18 条工程语法 WHEN→THEN 规则
- 全量代码映射

---

## v3.0.0 — 2026-06-05

### ⚙️ 工程化重写

- Panta Rhei 动态世界观集成
- 能力对比表 + 工程效率原则
- 稀疏激活（MoE 路由）

---

## v2.0.0 — 2026-06-05

### 🌊 Panta Rhei 集成

- 动态世界观整合
- 涌现检测
- Calibrated Language（校准语言）

---

## v1.0.0 — 2026-06-05

### 🎉 初始版本

- 鱼类生态学助手初始发布
- 5 搜索引擎 + 12 子智能体
- 基础物种知识库
