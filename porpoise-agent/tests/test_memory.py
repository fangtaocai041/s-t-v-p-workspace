"""记忆系统单元测试"""
import pytest
import sys
sys.path.insert(0, ".")

from src.memory.short_term import ShortTermMemory, MemoryPriority, MemoryItem
from src.memory.long_term import LongTermMemory
from src.memory.manager import MemoryManager


class TestMemoryPriority:
    def test_enum_values(self):
        assert MemoryPriority.CRITICAL == 5
        assert MemoryPriority.TRANSIENT == 1

    def test_int_conversion(self):
        assert MemoryPriority(4) == MemoryPriority.HIGH
        assert MemoryPriority(1) == MemoryPriority.TRANSIENT


class TestShortTermMemory:
    def test_add_and_count(self):
        stm = ShortTermMemory(max_tokens=8000)
        stm.add("hello world", role="user", priority=MemoryPriority.HIGH)
        stm.add("tool result", role="tool", priority=MemoryPriority.MEDIUM)
        assert len(stm.items) == 2
        assert stm._token_count > 0

    def test_get_context(self):
        stm = ShortTermMemory(max_tokens=500)
        stm.add("user query about porpoise", role="user", priority=MemoryPriority.HIGH)
        ctx = stm.get_context()
        assert "porpoise" in ctx

    def test_get_recent(self):
        stm = ShortTermMemory(max_tokens=8000)
        for i in range(10):
            stm.add(f"item {i}", priority=MemoryPriority.LOW)
        recent = stm.get_recent(3)
        assert len(recent) == 3
        assert "item 9" in recent[-1].content

    def test_clear(self):
        stm = ShortTermMemory()
        stm.add("test")
        stm.clear()
        assert len(stm.items) == 0
        assert stm._token_count == 0

    def test_compression_triggers(self):
        stm = ShortTermMemory(max_tokens=100, compression_threshold=0.3)
        for i in range(30):
            stm.add(f"memory item {i} with padding " + "x " * 10,
                    priority=MemoryPriority.LOW)
        # Either items were compressed or count reduced
        assert len(stm.items) < 30 or stm._compressed_summary

    def test_stats(self):
        stm = ShortTermMemory(max_tokens=1000)
        stm.add("test", priority=MemoryPriority.HIGH)
        s = stm.stats()
        assert s["n_items"] == 1
        assert s["token_count"] > 0

    def test_effective_priority_decays(self):
        item = MemoryItem(content="old", priority=MemoryPriority.HIGH)
        # Manually age the item
        item.timestamp = 0  # very old
        eff = item.effective_priority()
        assert eff < MemoryPriority.HIGH.value


class TestLongTermMemory:
    def test_init(self):
        ltm = LongTermMemory(persist_dir="./data/test_unit")
        assert ltm is not None
        assert ltm.backend is not None

    def test_add_and_search(self):
        ltm = LongTermMemory(persist_dir="./data/test_unit")
        ltm.add("literature", "江豚在长江中下游的分布研究",
                metadata={"year": 2024})

        results = ltm.search("literature", "江豚分布", top_k=3)
        assert isinstance(results, list)

    def test_rag_context(self):
        ltm = LongTermMemory(persist_dir="./data/test_unit")
        ltm.add("literature", "Finless porpoise acoustic monitoring in Yangtze",
                metadata={"year": 2023})
        rag = ltm.get_rag_context("porpoise acoustic", max_tokens=500)
        assert isinstance(rag, str)
        assert len(rag) > 0

    def test_clear_collection(self):
        ltm = LongTermMemory(persist_dir="./data/test_unit")
        ltm.add("notes", "test note")
        ltm.clear_collection("notes")
        assert ltm.stats()["cached_documents"] >= 0  # should not crash


class TestMemoryManager:
    def test_init(self):
        mm = MemoryManager(max_stm_tokens=2000, persist_dir="./data/test_unit")
        assert mm.stm is not None
        assert mm.ltm is not None

    def test_remember(self):
        mm = MemoryManager(max_stm_tokens=2000, persist_dir="./data/test_unit")
        mm.remember("user input", role="user", priority=MemoryPriority.HIGH)
        assert mm.stm._token_count > 0

    def test_recall(self):
        mm = MemoryManager(max_stm_tokens=2000, persist_dir="./data/test_unit")
        mm.remember("user wants papers about porpoise", role="user",
                    priority=MemoryPriority.HIGH)
        result = mm.recall("porpoise")
        assert "stm_results" in result
        assert len(result["stm_results"]) > 0

    def test_persist(self):
        mm = MemoryManager(max_stm_tokens=2000, persist_dir="./data/test_unit")
        mm.persist("literature", "test paper about cetaceans",
                   metadata={"year": 2024})
        assert mm.ltm.stats()["cached_documents"] >= 1

    def test_flush(self):
        mm = MemoryManager(max_stm_tokens=2000, persist_dir="./data/test_unit")
        mm.remember("important", priority=MemoryPriority.HIGH)
        mm.flush()  # should not crash

    def test_clear(self):
        mm = MemoryManager(max_stm_tokens=2000, persist_dir="./data/test_unit")
        mm.remember("test")
        mm.clear("all")
        assert mm.stm._token_count == 0
