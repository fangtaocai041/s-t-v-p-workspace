"""Tests for conflict-arbiter — Conflict Arbitration Expert Engine (C)."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestConflictArbiter:
    """Test the conflict arbitration engine."""

    def test_import(self):
        from src.arbiter import ConflictArbiter
        assert ConflictArbiter is not None

    def test_creation(self):
        from src.arbiter import ConflictArbiter
        arbiter = ConflictArbiter()
        assert arbiter is not None

    def test_detect_conflicts_basic(self):
        from src.arbiter import ConflictArbiter
        arbiter = ConflictArbiter()
        result = arbiter.detect_conflicts(
            species_name="Coilia nasus",
            sources=[
                {"source": "iucn", "status": "EN"},
                {"source": "chinese_red_list", "status": "EN"},
            ],
        )
        assert isinstance(result, dict)

    def test_detect_conflicts_different(self):
        from src.arbiter import ConflictArbiter
        arbiter = ConflictArbiter()
        result = arbiter.detect_conflicts(
            species_name="Coilia nasus",
            sources=[
                {"source": "iucn", "status": "LC"},
                {"source": "chinese_red_list", "status": "EN"},
            ],
        )
        assert isinstance(result, dict)

    def test_arbitrate(self):
        from src.arbiter import ConflictArbiter
        arbiter = ConflictArbiter()
        result = arbiter.arbitrate(
            species_name="Coilia nasus",
            claims=[
                {"source": "iucn", "status": "LC", "year": 2023},
                {"source": "china_red_list", "status": "EN", "year": 2022},
            ],
        )
        assert isinstance(result, dict)

    def test_source_weights(self):
        from src.arbiter import ConflictArbiter
        arbiter = ConflictArbiter()
        assert "iucn" in arbiter._source_weights
        assert arbiter._source_weights["iucn"] > 0


class TestConflictArbiterAdapter:
    """Test cross-project adapter."""

    def test_import(self):
        from src.adapter import ConflictArbiterAdapter
        assert ConflictArbiterAdapter is not None

    def test_info(self):
        from src.adapter import ConflictArbiterAdapter
        adapter = ConflictArbiterAdapter()
        info = adapter.info()
        assert "project" in info

    def test_health(self):
        from src.adapter import ConflictArbiterAdapter
        adapter = ConflictArbiterAdapter()
        health = adapter.health()
        assert "status" in health

    def test_search(self):
        from src.adapter import ConflictArbiterAdapter
        adapter = ConflictArbiterAdapter()
        result = adapter.search("detect conflicts Coilia nasus")
        assert isinstance(result, dict)


