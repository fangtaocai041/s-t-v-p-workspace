"""
porpoise-agent Search 模块独立测试 (BFS/DFS/Beam/ToT/GoT)

运行: python -m pytest porpoise-agent/tests/test_search_standalone.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cognitive.search import (
    ThoughtNode, SearchStrategy, ThoughtTreeSearch, SearchConfig, SearchResult,
)


class TestThoughtNode:
    def test_create_node(self):
        node = ThoughtNode(id="n1", content="Yangtze porpoise population declining")
        assert node.id == "n1"
        assert node.score == 0.0
        assert node.visits == 0
        assert node.children_ids == []

    def test_node_with_parent(self):
        parent = ThoughtNode(id="root", content="research question")
        child = ThoughtNode(id="child", content="sub-question", parent_id="root")
        parent.children_ids.append("child")
        assert child.parent_id == "root"
        assert "child" in parent.children_ids

    def test_node_merge(self):
        node = ThoughtNode(id="merge", content="combined")
        node.merge_sources = ["branch_a", "branch_b"]
        assert len(node.merge_sources) == 2

    def test_node_scoring(self):
        node = ThoughtNode(id="n1", content="high quality answer")
        node.score = 0.9
        assert node.score == 0.9


class TestSearchStrategy:
    def test_strategy_values(self):
        assert SearchStrategy.BFS == "bfs"
        assert SearchStrategy.DFS == "dfs"
        assert SearchStrategy.BEAM == "beam"
        assert SearchStrategy.MCTS == "mcts"
        assert SearchStrategy.BEST_FIRST == "best_first"


class TestSearchConfig:
    def test_default_config(self):
        cfg = SearchConfig()
        assert cfg.max_depth == 5
        assert cfg.beam_width == 3
        assert cfg.branch_factor == 3

    def test_custom_config(self):
        cfg = SearchConfig(max_depth=3, beam_width=2, timeout_ms=5000)
        assert cfg.max_depth == 3
        assert cfg.beam_width == 2


class TestThoughtTreeSearch:
    def dummy_expand(self, node):
        children = []
        for i in range(2):
            child = ThoughtNode(
                id=f"{node.id}_c{i}",
                content=f"expanded {node.id} child {i}",
                parent_id=node.id,
                score=0.5 + 0.1 * i,
            )
            children.append(child)
        return children

    def dummy_evaluate(self, node):
        return node.score

    def test_bfs_finds_result(self):
        root = ThoughtNode(id="root", content="start")
        searcher = ThoughtTreeSearch(
            expand_fn=self.dummy_expand,
            evaluate_fn=self.dummy_evaluate,
            config=SearchConfig(strategy=SearchStrategy.BFS, max_depth=2),
        )
        result = searcher.search(root)
        assert isinstance(result, SearchResult)
        assert result.nodes_explored >= 1
        assert hasattr(result, 'best_path')

    def test_dfs_finds_result(self):
        root = ThoughtNode(id="root", content="start")
        searcher = ThoughtTreeSearch(
            expand_fn=self.dummy_expand,
            evaluate_fn=self.dummy_evaluate,
            config=SearchConfig(strategy=SearchStrategy.DFS, max_depth=2),
        )
        result = searcher.search(root)
        assert isinstance(result, SearchResult)

    def test_beam_search(self):
        root = ThoughtNode(id="root", content="start")
        searcher = ThoughtTreeSearch(
            expand_fn=self.dummy_expand,
            evaluate_fn=self.dummy_evaluate,
            config=SearchConfig(strategy=SearchStrategy.BEAM, max_depth=2, beam_width=2),
        )
        result = searcher.search(root)
        assert isinstance(result, SearchResult)

    def test_empty_expand_returns_result(self):
        root = ThoughtNode(id="root", content="dead end", score=0.9)
        searcher = ThoughtTreeSearch(
            expand_fn=lambda n: [],
            evaluate_fn=lambda n: n.score,
            config=SearchConfig(strategy=SearchStrategy.BFS, max_depth=1),
        )
        result = searcher.search(root)
        assert isinstance(result, SearchResult)

    def test_max_depth_limit(self):
        root = ThoughtNode(id="root", content="start", score=0.5)
        searcher = ThoughtTreeSearch(
            expand_fn=self.dummy_expand,
            evaluate_fn=self.dummy_evaluate,
            config=SearchConfig(strategy=SearchStrategy.BFS, max_depth=1),
        )
        result = searcher.search(root)
        assert result.nodes_explored <= 10  # limited by depth=1

    def test_default_strategy_works(self):
        root = ThoughtNode(id="root", content="start", score=0.5)
        searcher = ThoughtTreeSearch(
            expand_fn=self.dummy_expand,
            evaluate_fn=self.dummy_evaluate,
        )
        result = searcher.search(root)
        assert isinstance(result, SearchResult)

    def test_best_score_after_search(self):
        root = ThoughtNode(id="root", content="start", score=0.5)
        searcher = ThoughtTreeSearch(
            expand_fn=self.dummy_expand,
            evaluate_fn=self.dummy_evaluate,
        )
        result = searcher.search(root)
        assert result.best_score >= 0.0
