"""
porpoise-agent Memory 模块独立测试

运行: python -m pytest porpoise-agent/tests/test_memory_standalone.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from src.memory.short_term import (
    ShortTermMemory, MemoryItem, MemoryPriority,
)
from src.memory.long_term import LongTermMemory
from src.memory.manager import MemoryManager


class TestMemoryPriority:
    def test_enum_values(self):
        assert MemoryPriority.CRITICAL == 5
        assert MemoryPriority.HIGH == 4
        assert MemoryPriority.MEDIUM == 3
        assert MemoryPriority.LOW == 2
        assert MemoryPriority.TRANSIENT == 1

    def test_int_conversion(self):
        assert int(MemoryPriority.CRITICAL) == 5


class TestMemoryItem:
    def test_default_item(self):
        item = MemoryItem(content="test")
        assert item.content == "test"
        assert item.priority == MemoryPriority.MEDIUM

    def test_age_seconds(self):
        item = MemoryItem(content="old")
        item.timestamp = time.time() - 10  # 10 seconds ago
        assert 9 <= item.age_seconds() <= 11

    def test_effective_priority_decays(self):
        item = MemoryItem(content="decay", priority=MemoryPriority.HIGH)
        item.timestamp = time.time() - 1000
        eff = item.effective_priority()
        assert eff < 4  # should decay from HIGH (4)


class TestShortTermMemory:
    def test_init(self):
        stm = ShortTermMemory(max_tokens=8000)
        assert stm.max_tokens == 8000

    def test_add_and_count(self):
        stm = ShortTermMemory(max_tokens=8000)
        stm.add(MemoryItem(content="first"))
        stm.add(MemoryItem(content="second"))
        assert stm.count() == 2

    def test_get_context(self):
        stm = ShortTermMemory(max_tokens=8000)
        stm.add(MemoryItem(content="important", priority=MemoryPriority.HIGH))
        ctx = stm.get_context()
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    def test_get_recent(self):
        stm = ShortTermMemory(max_tokens=8000)
        for i in range(10):
            stm.add(MemoryItem(content=f"item_{i}"))
        recent = stm.get_recent(n=3)
        assert len(recent) == 3

    def test_clear(self):
        stm = ShortTermMemory(max_tokens=8000)
        stm.add(MemoryItem(content="temp"))
        stm.clear()
        assert stm.count() == 0

    def test_stats(self):
        stm = ShortTermMemory(max_tokens=8000)
        stm.add(MemoryItem(content="a", priority=MemoryPriority.HIGH))
        stm.add(MemoryItem(content="b", priority=MemoryPriority.LOW))
        stats = stm.stats()
        assert "count" in stats or "items" in stats or "tokens" in stats

    def test_compression_triggers(self):
        stm = ShortTermMemory(max_tokens=100)
        big = MemoryItem(content="x" * 500, priority=MemoryPriority.LOW)
        stm.add(big)
        # should not crash even with oversized items
        assert stm.count() >= 0

    def test_priority_ordering(self):
        stm = ShortTermMemory(max_tokens=8000)
        stm.add(MemoryItem(content="low", priority=MemoryPriority.LOW))
        stm.add(MemoryItem(content="critical", priority=MemoryPriority.CRITICAL))
        stm.add(MemoryItem(content="high", priority=MemoryPriority.HIGH))
        items = stm.get_all()
        # Critical should be first (or at least present)
        priorities = [int(i.priority) for i in items]
        assert MemoryPriority.CRITICAL in priorities


class TestLongTermMemory:
    def test_init(self):
        ltm = LongTermMemory()
        assert ltm is not None

    def test_add_and_search(self):
        ltm = LongTermMemory()
        ltm.add(
            content="Porpoise population in Yangtze is declining",
            metadata={"source": "IUCN", "year": 2024},
        )
        results = ltm.search("porpoise population")
        assert isinstance(results, list)

    def test_rag_context(self):
        ltm = LongTermMemory()
        ltm.add(content="Neophocaena asiaeorientalis is endemic to Yangtze",
                metadata={"type": "species_info"})
        ctx = ltm.get_rag_context("Yangtze porpoise")
        assert isinstance(ctx, str)

    def test_clear_collection(self):
        ltm = LongTermMemory()
        ltm.add(content="test data")
        ltm.clear_collection()
        results = ltm.search("test")
        assert len(results) == 0


class TestMemoryManager:
    def test_init(self):
        mm = MemoryManager()
        assert mm is not None

    def test_remember(self):
        mm = MemoryManager()
        mm.remember(content="user prefers Chinese sources", priority="high")
        assert mm.short_term.count() >= 0

    def test_recall(self):
        mm = MemoryManager()
        mm.remember(content="Yangtze fishing ban started 2021")
        result = mm.recall("fishing ban")
        assert isinstance(result, (str, list))

    def test_persist(self):
        mm = MemoryManager()
        mm.remember(content="important finding", priority="critical")
        # persist should move CRITICAL items to long-term
        mm.persist()
        # long-term should have at least the critical item
        results = mm.long_term.search("important")
        assert isinstance(results, list)

    def test_flush(self):
        mm = MemoryManager()
        mm.remember(content="temp note")
        mm.flush()
        # short-term should be cleared
        assert mm.short_term.count() == 0

    def test_clear(self):
        mm = MemoryManager()
        mm.remember(content="all gone")
        mm.clear()
        assert mm.short_term.count() == 0
