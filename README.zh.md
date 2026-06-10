<p align="center">
  🇬🇧 <a href="README.md">English</a>
</p>

# eon-workspace

> **三生万物 v8.1 — 七项目统一**
> 三角核心: fish + cognitive + eon-core (闭环, arity=3)
> 万物衍生: P₁(porpoise) · P₂(coilia) · P₃(culter) · C(conflict) (开放, arity≥0)

```
eon-core/                   → ☯️ 协调内核 [三角核心]
fish-ecology-assistant/     → 三角 V0: 知识供给
cognitive-search-engine/    → 三角 V1: 搜索验证
porpoise-agent/             → 衍生 P₁: 江豚专研
coilia-agent/               → 衍生 P₂: 刀鲚专研
culter-agent/               → 衍生 P₃: 鲌类专研
conflict-arbiter/           → 衍生 C:  冲突仲裁
scripts/project_loader.py   → 统一 DirectLoader (7 适配器)
scripts/coordinator.py      → 统一协调器 (6 通路)
scripts/quality_gate.py     → 质控关卡 (5 关)
```

## 快速开始

```bash
# 质控验证 — 7 项目 5 关全检
python scripts/quality_gate.py

# 加载全部适配器 (7/7)
python -c "from scripts.project_loader import get_all_adapters; print({k:type(v).__name__ for k,v in get_all_adapters().items()})"

# 全栈健康检查 (7/7)
python -c "from scripts.coordinator import coordinator; [print(f'{p}: {coordinator.health(p)[\"status\"]}') for p in ['eon','fish','cognitive','porpoise','coilia','culter','conflict']]"
```

## 项目

| 项目 | 版本 | 架构层 | 角色 | 适配器 |
|------|:----:|:-----:|------|--------|
| [eon-core](eon-core/) | v8.0.0 | TriangleCore | 协调内核 (T) | `EonCoreAdapter` |
| [cognitive-search-engine](cognitive-search-engine/) | v5.5.0 | TriangleCore | 搜索验证 V1 | `CognitiveSearchAdapter` |
| [fish-ecology-assistant](fish-ecology-assistant/) | v6.3.0 | TriangleCore | 知识供给 V0 | `FishEcologyAdapter` |
| [porpoise-agent](porpoise-agent/) | v4.3.0 | Derived P₁ | 江豚专研 | `PorpoiseAdapter` |
| [coilia-agent](coilia-agent/) | v1.2.0 | Derived P₂ | 刀鲚专研 | `CoiliaAdapter` |
| [culter-agent](culter-agent/) | v2.0.0 | Derived P₃ | 鲌类专研 | `CulterAdapter` |
| [conflict-arbiter](conflict-arbiter/) | v1.0.0 | Derived C | 冲突仲裁 | `ConflictArbiterAdapter` |

## 架构

```
道 (用户) → 一 (IProjectAdapter) → 二 (阴阳两极)
→ 三角 (fish + cognitive + eon-core) → 万物 (P₁ P₂ P₃ ... C)
```

**6 条数据通路**: P1(fish→cognitive) · P2(cognitive→fish) · P3(cognitive→domain) · P4(health→karma) · P5(all→conflict) · P6(conflict→user)

## 文档

| 文档 | 说明 |
|------|------|
| [SANSHENG_WANWU.md](docs/SANSHENG_WANWU.md) | 唯一架构规范 |
| [ARCHITECTURE_OVERVIEW.md](docs/ARCHITECTURE_OVERVIEW.md) | 各模块职责 |
| [PROJECT_RELATIONSHIPS.md](docs/PROJECT_RELATIONSHIPS.md) | 项目间通路 |
| [EXECUTION_FLOW.md](docs/EXECUTION_FLOW.md) | 运行时执行流 |
| [VERSION.yaml](VERSION.yaml) | 单源版本真相 |
| [coordination.yaml](coordination.yaml) | 统一协调配置 |
