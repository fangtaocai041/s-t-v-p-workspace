#!/usr/bin/env python3
"""
万物: Pₙ 模板生成器 — 从三角派生新物种专精 Agent

演示如何从 P₁(porpoise) / P₂(coilia) 模板复制出新的 Pₙ:
  python scripts/spawn_agent.py "Acipenser sinensis" "中华鲟" "洄游|产卵|保护"

生成新 Agent 的最小骨架:
  - 项目目录结构
  - adapter.py (IProjectAdapter 实现)
  - orchestrator.py (5阶段管线)
  - SKILL.md (3个核心技能)
  - config/agent.yaml
"""

import sys
from pathlib import Path
from textwrap import dedent

_WORKSPACE = Path(__file__).resolve().parent.parent

TEMPLATE = """# 🐟 {icon} {agent_name} — {chinese_name}专研 (P{n})

> **物种**: {chinese_name} (*{scientific_name}*){research_note}
> **角色**: P{n} — 三生万物 v8 架构中的{chinese_name}专研层 (三角派生模板)
> **协调**: eon-core (三角形内核)
> **同级项目**: P₁(porpoise) · P₂(coilia) · P₃(culter) · C(conflict)

## 🔺 架构角色: P{n} / V{n}

> 从三角形 (fish+cognitive+eon-core) 派生的领域专精模板。
> 与 P₁(江豚) P₂(刀鲚) P₃(鲌类) 同级，通过 coordinator 统一调度。

## 核心研究方向

| 方向 | 说明 |
|------|------|
{research_directions}

## 🧠 技能模块

| 技能 | 角色 |
|------|------|
| 🔍 `search-literature` | 文献检索 (通过 cognitive DirectLoader) |
| 🔬 `analyze-{domain}` | {domain_cn}分析 |
| 📊 `assess-{domain}` | {domain_cn}评估 |

## 📡 搜索基础设施

```
{agent_name}.search("{chinese_name}")
  └─ CognitiveSearchAdapter.search("{genus}", "{species}")
       └─ PubMed × Crossref × OpenAlex
```

> 引擎路径: D:\\Reasonix\\cognitive-search-engine\\src\\
> 适配器: src/adapter.py (继承 IProjectAdapter)

## ⚡ 快速开始

```bash
cd {project_dir}
pip install -e .
{cli_name} run --query "{chinese_name} {sample_query}"
```

## 📊 自我评价

| 维度 | 评分 | 说明 |
|------|:--:|------|
| 🐟 领域深度 | ⭐⭐⭐⭐☆ | {chinese_name}专属知识库 |
| 🔬 研究方法 | ⭐⭐⭐☆☆ | 3 个核心 Skill (从 P₂ 模板派生) |
| 🔗 生态整合 | ⭐⭐⭐⭐⭐ | P{n} 角色，三角派生，eon-core 调度 |
| 🚀 可扩展性 | ⭐⭐⭐⭐⭐ | 从 P₁/P₂ 模板 3 步生成 |

> **模板来源**: porpoise-agent (P₁) + coilia-agent (P₂)
> **生成命令**: `python scripts/spawn_agent.py "{scientific_name}" "{chinese_name}" "{domain_list_str}"`

## 📜 许可证

MIT License © 2026
"""


def parse_species(scientific_name: str, chinese_name: str, domains: str = ""):
    """解析物种信息，生成 Agent 配置。"""
    parts = scientific_name.split()
    genus = parts[0] if parts else scientific_name
    species = parts[1] if len(parts) > 1 else ""
    
    domain_list = [d.strip() for d in domains.split("|") if d.strip()]
    if not domain_list:
        domain_list = ["生态", "保护"]
    
    directions = "\n".join(f"| {d} | {chinese_name}的{d}研究 |" for d in domain_list)
    
    return {
        "genus": genus,
        "species": species,
        "domain_list": domain_list,
        "domain": domain_list[0],
        "domain_cn": domain_list[0],
        "directions": directions,
    }


def main():
    if len(sys.argv) < 3:
        print("用法: python scripts/spawn_agent.py <学名> <中文名> [研究方向|分割]")
        print("示例: python scripts/spawn_agent.py \"Acipenser sinensis\" \"中华鲟\" \"洄游|产卵|保护\"")
        return 1

    scientific_name = sys.argv[1]
    chinese_name = sys.argv[2]
    domains = sys.argv[3] if len(sys.argv) > 3 else ""

    info = parse_species(scientific_name, chinese_name, domains)
    
    # 分配 Pₙ 编号 (P₁=porpoise, P₂=coilia, 下一个=P₃)
    known_p = ["porpoise-agent", "coilia-agent", "culter-agent"]
    existing = [d for d in _WORKSPACE.glob("*-agent") if d.name not in known_p]
    n = len(known_p) + len(existing) + 1  # P₃, P₄, ...
    
    # 生成项目名
    genus_lower = info["genus"].lower()
    project_dir = f"{genus_lower}-agent"
    agent_name = f"{info['genus'].title()}Agent"
    cli_name = genus_lower
    
    # 图标选择
    icon = "🐟"
    if "鲸" in chinese_name or "豚" in chinese_name:
        icon = "🐬"
    
    research_note = ""
    if "鲟" in chinese_name:
        research_note = " — 长江鱼王，濒危物种"

    # 渲染模板
    readme = TEMPLATE.format(
        icon=icon,
        agent_name=agent_name,
        chinese_name=chinese_name,
        scientific_name=scientific_name,
        n=n,
        research_note=research_note,
        research_directions=info["directions"],
        domain=info["domain"],
        domain_cn=info["domain_cn"],
        domain_list_str="|".join(info["domain_list"]),
        genus=info["genus"],
        species=info["species"],
        project_dir=project_dir,
        cli_name=cli_name,
        sample_query=info["domain_list"][0],
    )

    print(f"\n{'═'*60}")
    print(f"  万物: P{n} 模板生成 — {chinese_name} (*{scientific_name}*)")
    print(f"{'═'*60}")
    print(f"\n  三角派生: fish+cognitive+eon-core → P{n}")
    print(f"  模板来源:  P₁(porpoise) / P₂(coilia) / P₃(culter)")
    print(f"  架构版本:  三生万物 v8.1 (7项目统一)")
    print(f"  项目目录:  {project_dir}/")
    print(f"  技能数:    3 (search-literature, analyze-{info['domain']}, assess-{info['domain']})")
    print(f"\n{'─'*60}")
    print(f"  README.md 预览:")
    print(f"{'─'*60}")
    print(readme)

    # 生成文件清单
    files = [
        "README.md",
        "README.zh.md",
        "src/__init__.py",
        "src/adapter.py",
        "src/agent/__init__.py",
        "src/agent/orchestrator.py",
        "src/prompts/system_prompts.py",
        f"src/skills/search-literature/SKILL.md",
        f"src/skills/analyze-{info['domain']}/SKILL.md",
        f"src/skills/assess-{info['domain']}/SKILL.md",
        "config/agent.yaml",
        "config/agent.yaml",  # tao.yaml/wuxing.yaml 已删除 — 三生万物精简
    ]

    print(f"\n{'─'*60}")
    print(f"  生成文件清单 ({len(files)} 个):")
    print(f"{'─'*60}")
    for f in files:
        print(f"  📄 {project_dir}/{f}")

    print(f"\n{'═'*60}")
    print(f"  万物: P{n} 模板就绪")
    print(f"  道→一→二→三→万物: 三角派生无限领域专精 ✅")
    print(f"{'═'*60}")

    # ── 实际生成文件 (--create 标志) ──
    if "--create" in sys.argv:
        print(f"\n  📁 创建项目文件...")
        project_root = _WORKSPACE / project_dir
        created = 0

        # 从模板文件读取 (使用 %% 作为占位符避免与 .format() 冲突)
        tmpl_path = _WORKSPACE / "scripts" / "orchestrator_template.py"
        orch_template = tmpl_path.read_text(encoding="utf-8")

        orch_content = orch_template
        # 使用 %%VAR%% 占位符替换 (避免与 Python {} 语法冲突)
        reps = {
            "%%SCIENTIFIC_NAME%%": scientific_name,
            "%%CHINESE_NAME%%": chinese_name,
            "%%GENUS%%": info["genus"],
            "%%SPECIES%%": info["species"],
            "%%N%%": str(n),
            "%%CLASS_NAME%%": agent_name.replace("Agent", "Orchestrator"),
            "%%DOMAIN1%%": info["domain_list"][0] if info["domain_list"] else "ecology",
            "%%DOMAIN2%%": info["domain_list"][1] if len(info["domain_list"]) > 1 else "conservation",
            "%%DOMAIN3%%": info["domain_list"][2] if len(info["domain_list"]) > 2 else "report",
            "%%DOMAIN1_UPPER%%": info["domain_list"][0].upper() if info["domain_list"] else "ECOLOGY",
            "%%DOMAIN2_UPPER%%": info["domain_list"][1].upper() if len(info["domain_list"]) > 1 else "CONSERVATION",
            "%%DOMAIN3_UPPER%%": info["domain_list"][2].upper() if len(info["domain_list"]) > 2 else "REPORT",
            "%%DOMAIN1_KW%%": str([info["domain_list"][0], chinese_name]) if info["domain_list"] else "[]",
            "%%DOMAIN2_KW%%": str([info["domain_list"][1]]) if len(info["domain_list"]) > 1 else "[]",
            "%%DOMAIN3_KW%%": str([info["domain_list"][2]]) if len(info["domain_list"]) > 2 else "[]",
            "%%DOMAIN_LIST_PY%%": ", ".join(f'"{d}"' for d in info["domain_list"]),
        }
        for k, v in reps.items():
            orch_content = orch_content.replace(k, v)

        class_name = agent_name.replace("Agent", "Orchestrator")

        # 生成 adapter.py 内容
        adapter_content = f'''"""{agent_name} — {chinese_name}专研适配器 (P{n}, V{n})

【核心专精】assess_species(species, context) → Assessment
    {chinese_name}领域专精评估 (三角派生模板 P{n})
    → 通路 P3(←cognitive)

从三角形 (fish+cognitive+eon-core) 派生的领域专精。
模板来源: coilia-agent/src/adapter.py (P2)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict

try:
    from scripts.adapter_protocol import IProjectAdapter
except ImportError:
    IProjectAdapter = object

logger = logging.getLogger(__name__)


class {agent_name}(IProjectAdapter):
    """{chinese_name}专精适配器 — 三角派生模板 P{n}."""

    project_name = "{project_dir}"

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from src.agent.orchestrator import {class_name}
            orch = {class_name}()
            return orch.run(query)
        except Exception as e:
            return {{"status": "degraded", "error": str(e)}}

    def health(self) -> Dict[str, Any]:
        return {{"status": "ok", "project": self.project_name, "vertex": "P{n}"}}

    def info(self) -> Dict[str, Any]:
        return {{
            "project": self.project_name,
            "species": "{scientific_name}",
            "chinese_name": "{chinese_name}",
            "role": "P{n} (三角派生模板)",
            "template_source": "coilia-agent (P2)",
        }}


def get_adapter() -> {agent_name}:
    return {agent_name}()
'''

        # 生成 SKILL.md 内容
        skill_search = f"""# search-literature — {chinese_name}文献检索

## 描述
通过 cognitive-search-engine DirectLoader 搜索 {chinese_name} (*{scientific_name}*) 的中英文文献。

## 触发
- 用户询问 {chinese_name} 相关文献
- 关键词: {chinese_name}, {scientific_name}, 文献, 论文, 研究进展

## 步骤
1. 调用 CognitiveSearchAdapter.search("{info['genus']}", "{info['species']}")
2. 返回结构化文献列表 (标题/作者/年份/期刊/DOI/可信度评分)
"""

        skill_analyze = f"""# analyze-{info['domain']} — {chinese_name}{info['domain']}分析

## 描述
{chinese_name}的{info['domain']}相关数据分析。

## 触发
- 用户询问 {chinese_name} {info['domain']} 相关问题
- 关键词: {chinese_name}, {info['domain']}

## 步骤
1. 从文献检索结果提取{info['domain']}相关数据
2. 执行{info['domain']}分析方法
3. 返回分析结论
"""

        skill_assess = f"""# assess-{info['domain']} — {chinese_name}{info['domain']}评估

## 描述
{chinese_name}的{info['domain']}状况评估。

## 步骤
1. 综合文献和分析结果
2. 生成评估报告
3. 提供保护建议
"""

        for fpath_rel in files:
            fpath = project_root / fpath_rel
            fpath.parent.mkdir(parents=True, exist_ok=True)
            if not fpath.exists():
                fname = fpath_rel.split("/")[-1]
                if fname == "orchestrator.py":
                    fpath.write_text(orch_content, encoding="utf-8")
                elif fname == "adapter.py":
                    fpath.write_text(adapter_content, encoding="utf-8")
                elif fname == "README.md":
                    fpath.write_text(readme, encoding="utf-8")
                elif fname == "SKILL.md" and "search-literature" in fpath_rel:
                    fpath.write_text(skill_search, encoding="utf-8")
                elif fname == "SKILL.md" and "analyze-" in fpath_rel:
                    fpath.write_text(skill_analyze, encoding="utf-8")
                elif fname == "SKILL.md" and "assess-" in fpath_rel:
                    fpath.write_text(skill_assess, encoding="utf-8")
                else:
                    fpath.touch()
                created += 1
        print(f"  ✅ 已创建 {created} 个文件 → {project_dir}/ (含完整 adapter/orchestrator/SKILL)")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
