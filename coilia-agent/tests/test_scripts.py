"""脚本层测试 — species_kb.py + fish_kb_add_species.py.

测试关键功能路径，外部文件路径使用 mock 避免依赖 D:/Reasonix。
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add project root + D:/Reasonix to path
_proj = str(Path(__file__).resolve().parent.parent)
if _proj not in sys.path:
    sys.path.insert(0, _proj)
_reasonix = str(Path(__file__).resolve().parent.parent.parent)
if _reasonix not in sys.path:
    sys.path.insert(0, _reasonix)

# These imports need the project root on sys.path
import scripts.species_kb as skb
import scripts.fish_kb_add_species as fkas


# ══════════════════════════════════════════════════════════════
# species_kb.py 测试
# ══════════════════════════════════════════════════════════════

class TestSpeciesKB(unittest.TestCase):
    """测试 species_kb.py 的加载、查询、格式化功能。"""

    SAMPLE_KB = """---
species:
  id: "Coilia_nasus"
  chinese: "刀鲚"
  scientific: "Coilia nasus"
  conservation:
    iucn: "濒危(EN)"
  biology:
    migration_type: "溯河洄游"
    spawning_season: "4-6月"
  population_trend:
    historical_peak: "1973年 3750t"
    current_status: "资源量仅为历史峰值的1-3%"

research_themes:
  - theme: "耳石微化学与洄游履历"
    methods: ["LA-ICP-MS", "Sr/Ca 比分析"]
    key_questions:
      - "刀鲚个体洄游履历如何重建？"
      - "水利工程对洄游通道的阻断程度？"
  - theme: "群体遗传学与种群结构"
    methods: ["微卫星(SSR)", "SNP"]
    key_questions:
      - "长江刀鲚群体结构？"
  - theme: "资源评估与管理"
    methods: ["CPUE标准化"]
    key_questions:
      - "禁捕后恢复速率？"

key_research_groups:
  - institution: "淡水渔业研究中心"
    researchers: ["刘凯", "徐东坡"]
    focus: "资源评估、洄游生态"
"""

    @patch("scripts.species_kb._KB_PATH", Path("/fake/coilia-nasus.md"))
    @patch("scripts.species_kb.Path.is_file", return_value=True)
    @patch("scripts.species_kb.Path.read_text", return_value=SAMPLE_KB)
    def test_load_kb(self, mock_read, mock_isfile):
        """load_kb 能正确解析 species、themes、groups。"""
        data = skb.load_kb()
        self.assertIn("species", data)
        self.assertEqual(data["species"]["scientific"], "Coilia nasus")
        self.assertIn("research_themes", data)
        self.assertEqual(len(data["research_themes"]), 3)
        self.assertIn("key_research_groups", data)
        self.assertEqual(len(data["key_research_groups"]), 1)

    @patch("scripts.species_kb._KB_PATH", Path("/fake/coilia-nasus.md"))
    @patch("scripts.species_kb.Path.is_file", return_value=True)
    @patch("scripts.species_kb.Path.read_text", return_value=SAMPLE_KB)
    def test_load_kb_file_missing(self, mock_read, mock_isfile):
        """文件不存在时返回 error dict。"""
        mock_isfile.return_value = False
        data = skb.load_kb()
        self.assertIn("error", data)
        self.assertIn("不存在", data["error"])

    @patch("scripts.species_kb._KB_PATH", Path("/fake/coilia-nasus.md"))
    @patch("scripts.species_kb.Path.is_file", return_value=True)
    @patch("scripts.species_kb.Path.read_text", return_value=SAMPLE_KB)
    def test_query_theme_by_chinese(self, mock_read, mock_isfile):
        """按中文关键词查询研究方向。"""
        data = skb.load_kb()
        t = skb.query_theme(data, "耳石")
        self.assertIsNotNone(t)
        self.assertIn("洄游", t["theme"])

    @patch("scripts.species_kb._KB_PATH", Path("/fake/coilia-nasus.md"))
    @patch("scripts.species_kb.Path.is_file", return_value=True)
    @patch("scripts.species_kb.Path.read_text", return_value=SAMPLE_KB)
    def test_query_theme_by_english(self, mock_read, mock_isfile):
        """按英文关键词 (migration/otolith/genetic) 查询。"""
        data = skb.load_kb()
        t = skb.query_theme(data, "migration")
        self.assertIsNotNone(t)
        self.assertIn("洄游", t["theme"])

    @patch("scripts.species_kb._KB_PATH", Path("/fake/coilia-nasus.md"))
    @patch("scripts.species_kb.Path.is_file", return_value=True)
    @patch("scripts.species_kb.Path.read_text", return_value=SAMPLE_KB)
    def test_query_theme_not_found(self, mock_read, mock_isfile):
        """不存在的关键词返回 None。"""
        data = skb.load_kb()
        t = skb.query_theme(data, "量子力学")
        self.assertIsNone(t)

    @patch("scripts.species_kb._KB_PATH", Path("/fake/coilia-nasus.md"))
    @patch("scripts.species_kb.Path.is_file", return_value=True)
    @patch("scripts.species_kb.Path.read_text", return_value=SAMPLE_KB)
    def test_format_summary(self, mock_read, mock_isfile):
        """format_summary 输出包含关键字段。"""
        data = skb.load_kb()
        summary = skb.format_summary(data)
        self.assertIn("Coilia nasus", summary)
        self.assertIn("濒危", summary)
        self.assertIn("3750t", summary)
        self.assertIn("溯河", summary)

    @patch("scripts.species_kb._KB_PATH", Path("/fake/coilia-nasus.md"))
    @patch("scripts.species_kb.Path.is_file", return_value=True)
    @patch("scripts.species_kb.Path.read_text", return_value=SAMPLE_KB)
    def test_main_json_output(self, mock_read, mock_isfile):
        """--json 输出有效 JSON。"""
        # Simulate argparse
        with patch.object(sys, "argv", ["species_kb.py", "--json"]):
            with patch("scripts.species_kb.print") as mock_print:
                skb.main()
                # Should have called print with JSON string
                call_args = mock_print.call_args[0]
                if call_args:
                    output = call_args[0]
                    parsed = json.loads(output)
                    self.assertIn("species", parsed)


# ══════════════════════════════════════════════════════════════
# fish_kb_add_species.py 测试
# ══════════════════════════════════════════════════════════════

class TestFishKBAddSpecies(unittest.TestCase):
    """测试 fish_kb_add_species.py 的加载、列表、添加功能。"""

    SAMPLE_KB = {
        "metadata": {"title": "test"},
        "species": [
            {
                "id": "coilia_brachygnathus",
                "name": "短颌鲚",
                "scientific": "Coilia brachygnathus",
                "distribution": {"basins": ["长江流域"]},
            }
        ],
    }

    def setUp(self):
        self.entry = fkas.COILIA_NASUS.copy()

    @patch("scripts.fish_kb_add_species._KB_PATH", Path("/fake/fish_species_kb.yaml"))
    @patch("yaml.safe_load", return_value=SAMPLE_KB)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.read_text", return_value="")
    def test_load_kb(self, mock_read, mock_isfile, mock_yaml):
        """load_kb 返回已解析的 YAML dict。"""
        kb = fkas.load_kb()
        self.assertEqual(len(kb["species"]), 1)
        self.assertEqual(kb["species"][0]["scientific"], "Coilia brachygnathus")

    @patch("scripts.fish_kb_add_species._KB_PATH", Path("/fake/fish_species_kb.yaml"))
    @patch("pathlib.Path.is_file", return_value=False)
    def test_load_kb_missing(self, mock_isfile):
        """文件不存在时 sys.exit(1)。"""
        with self.assertRaises(SystemExit):
            fkas.load_kb()

    @patch("scripts.fish_kb_add_species._KB_PATH", Path("/fake/fish_species_kb.yaml"))
    def test_add_species_new(self):
        """add_species 添加新物种条目 (去重通过)。"""
        kb = {"species": [{"scientific": "Coilia brachygnathus"}]}
        result = fkas.add_species(kb, self.entry)
        self.assertTrue(result)
        self.assertEqual(len(kb["species"]), 2)

    @patch("scripts.fish_kb_add_species._KB_PATH", Path("/fake/fish_species_kb.yaml"))
    def test_add_species_duplicate(self):
        """add_species 检测到学名已存在时跳过 (去重)。"""
        kb = {"species": [{"scientific": "Coilia nasus"}]}
        result = fkas.add_species(kb, self.entry)
        self.assertFalse(result)
        self.assertEqual(len(kb["species"]), 1)

    @patch("scripts.fish_kb_add_species._KB_PATH", Path("/fake/fish_species_kb.yaml"))
    @patch("yaml.safe_load", return_value=SAMPLE_KB)
    @patch("pathlib.Path.is_file", return_value=True)
    @patch("pathlib.Path.read_text", return_value="")
    def test_list_species(self, mock_read, mock_isfile, mock_yaml):
        """list_species 打印每个物种的信息 (不抛异常)。"""
        kb = fkas.load_kb()
        try:
            fkas.list_species(kb)
        except Exception as e:
            self.fail(f"list_species raised {e}")

    @patch("scripts.fish_kb_add_species._KB_PATH", Path("/fake/fish_species_kb.yaml"))
    def test_list_species_empty(self):
        """空列表不抛异常。"""
        try:
            fkas.list_species({"species": []})
        except Exception as e:
            self.fail(f"list_species(empty) raised {e}")

    def test_coilia_nasus_entry_structure(self):
        """COILIA_NASUS 条目包含所有必要字段。"""
        required = ["id", "name", "scientific", "family", "conservation",
                     "distribution", "taxonomy_log", "species_graph_id"]
        for field in required:
            self.assertIn(field, self.entry, f"缺少字段: {field}")
        self.assertIn("basins", self.entry["distribution"])
        self.assertGreaterEqual(len(self.entry["taxonomy_log"]), 1)
        self.assertEqual(self.entry["id"], "coilia_nasus")
        self.assertEqual(self.entry["scientific"], "Coilia nasus")


if __name__ == "__main__":
    unittest.main()
