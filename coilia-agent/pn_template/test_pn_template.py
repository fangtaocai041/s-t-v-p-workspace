"""{{agent_id}} {{chinese_name}} 测试 — 继承共享基类.

使用方式:
  1. 复制此文件到新项目的 tests/ 目录
  2. 修改 TODO 标记的配置
  3. 运行: python -m pytest tests/
"""

import sys
import unittest
from pathlib import Path

# Add project root
_proj = str(Path(__file__).resolve().parent.parent)
if _proj not in sys.path:
    sys.path.insert(0, _proj)

# Add D:/Reasonix for shared test base + protocols
_reasonix = str(Path(__file__).resolve().parent.parent.parent)
if _reasonix not in sys.path:
    sys.path.insert(0, _reasonix)

from scripts.test_pn_base import (
    PnAdapterTestBase,
    PnOrchestratorTestBase,
    PnProtocolTestBase,
)

# TODO: 导入项目模块
# from src.adapter import <AdapterClass>
# from src.agent.orchestrator import <OrchestratorClass>


# ═══════════════════════════════════════════════════════════════
# TODO: 填写 Pn 物种配置
# ═══════════════════════════════════════════════════════════════

PN_CONFIG = {
    "agent_id": "P{n}",
    "agent_name": "{project}-agent · {chinese_name}",
    "species_scientific": "Species scientificus",
    "species_chinese": ["中文名"],
    "species_variants": [
        "OCR variant 1",
        "OCR variant 2",
    ],
    "profile": {
        "research_group": "研究机构",
    },
    "research_themes": {
        # "theme_id": {
        #     "label": "研究方向名",
        #     "keywords": ["关键词1", "keyword2"],
        # },
    },
    "themes_to_phases": {
    },
}


# ═══════════════════════════════════════════════════════════════
# 1. Adapter 测试 (IProjectAdapter 接口合规 — 继承基类)
# ═══════════════════════════════════════════════════════════════

class TestPnAdapter(PnAdapterTestBase):
    # TODO: 填写项目信息
    ADAPTER_CLASS = None  # 改为 <AdapterClass>
    PROJECT_NAME = "{project}-agent"
    SPECIES = "Species scientificus"
    ROLE = "P{n} · {chinese_name}专研"
    SEARCH_QUERY = "研究"


# ═══════════════════════════════════════════════════════════════
# 2. Orchestrator 测试 (路由 + 分析器)
# ═══════════════════════════════════════════════════════════════

class TestPnOrchestrator(PnOrchestratorTestBase):
    # TODO: 填写 orchestator 类和物种配置
    ORCHESTRATOR_CLASS = None  # 改为 <OrchestratorClass>
    SPECIES_CONFIG = PN_CONFIG
    RESEARCH_THEMES = PN_CONFIG["research_themes"]
    AGENT_ID = "P{n}"
    AGENT_NAME = "{project}-agent · {chinese_name}"

    # TODO: 添加物种特有关键词路由测试
    # def test_route_population(self):
    #     self._assert_route("种群动态", "population", "population_analysis")

    # TODO: 添加物种特有分析器测试
    # def test_analyze_population(self):
    #     self._assert_analysis("population", "种群动态分析", min_findings=3)


# ═══════════════════════════════════════════════════════════════
# 3. 协议引用 + 配置验证 (继承基类 — 无需修改)
# ═══════════════════════════════════════════════════════════════

class TestPnProtocol(PnProtocolTestBase):
    PROJECT_ROOT = Path(__file__).resolve().parent.parent


if __name__ == "__main__":
    unittest.main()
