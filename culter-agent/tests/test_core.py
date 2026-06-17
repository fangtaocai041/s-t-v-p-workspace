"""Tests for culter-agent — Culter Domain Expert Engine (P3)."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestImports:
    """Test that all modules import correctly."""

    def test_knowledge_base_import(self):
        from src.knowledge_base import get_knowledge_base
        assert get_knowledge_base is not None

    def test_adapter_import(self):
        from src.adapter import CulterAdapter
        assert CulterAdapter is not None

    def test_main_import(self):
        from src.main import main
        assert main is not None


class TestCulterOrchestrator:
    """Test the 9-phase pipeline orchestrator."""

    def test_creation(self):
        from src.agent.orchestrator import CulterOrchestrator
        orch = CulterOrchestrator()
        assert orch is not None

    def test_species_profile(self):
        from src.agent.orchestrator import CulterOrchestrator
        orch = CulterOrchestrator()
        profile = orch._get_species_profile()
        assert isinstance(profile, dict)
        assert "primary_species" in profile

    def test_route_phase_default(self):
        from src.agent.orchestrator import CulterOrchestrator, ResearchPhase
        orch = CulterOrchestrator()
        phase = orch._route_phase("no matching keyword xyz123")
        assert phase == ResearchPhase.LITERATURE

    def test_route_phase_genomics(self):
        from src.agent.orchestrator import CulterOrchestrator, ResearchPhase
        orch = CulterOrchestrator()
        phase = orch._route_phase("whole genome sequencing assembly")
        assert phase == ResearchPhase.GENOMICS

    def test_route_phase_trophic(self):
        from src.agent.orchestrator import CulterOrchestrator, ResearchPhase
        orch = CulterOrchestrator()
        phase = orch._route_phase("stable isotope delta13c delta15n")
        assert phase == ResearchPhase.TROPHIC

    def test_run(self):
        from src.agent.orchestrator import CulterOrchestrator
        orch = CulterOrchestrator()
        result = orch.run("growth analysis of Culter alburnus")
        assert isinstance(result, dict)
        assert "agent" in result


class TestCulterAdapter:
    """Test cross-project adapter."""

    def test_import(self):
        from src.adapter import CulterAdapter
        assert CulterAdapter is not None

    def test_info(self):
        from src.adapter import CulterAdapter
        adapter = CulterAdapter()
        info = adapter.info()
        assert "project" in info

    def test_health(self):
        from src.adapter import CulterAdapter
        adapter = CulterAdapter()
        health = adapter.health()
        assert "status" in health


class TestCognitiveAnalyzer:
    """Test BDI cognitive analyzer (cross-pollination feature)."""

    def test_import(self):
        from src.agent.cognitive_analyzer import CognitiveAnalyzer
        assert CognitiveAnalyzer is not None

    def test_creation(self):
        from src.agent.cognitive_analyzer import CognitiveAnalyzer
        profile = {"primary_species": "Culter alburnus",
                   "chinese_name": "翘嘴鲌"}
        ca = CognitiveAnalyzer(profile)
        assert ca is not None

    def test_analyze_basic(self):
        from src.agent.cognitive_analyzer import CognitiveAnalyzer
        profile = {"primary_species": "Culter alburnus",
                   "chinese_name": "翘嘴鲌"}
        ca = CognitiveAnalyzer(profile)
        result = ca.analyze(
            question="growth parameters",
            phase_id="growth_analysis",
            depth="standard",
        )
        assert result is not None
        assert result.question == "growth parameters"
        assert len(result.findings) > 0

