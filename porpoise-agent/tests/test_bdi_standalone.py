"""
porpoise-agent BDI 模块独立测试
BDI 状态机: Belief / Desire / Intention / BDIStatus / BDICoordinator

运行: python -m pytest porpoise-agent/tests/test_bdi.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cognitive.bdi import (
    Belief, Desire, Intention, PlanStep,
    BDIStatus, BDICoordinator,
)


class TestPlanStep:
    def test_create_step(self):
        s = PlanStep(name="search", tool="scholar", params={"q": "test"})
        assert s.name == "search"
        assert s.tool == "scholar"
        assert s.status == "pending"

    def test_step_defaults(self):
        s = PlanStep(name="analyze")
        assert s.tool is None
        assert s.params == {}
        assert s.result is None
        assert s.error is None
        assert s.status == "pending"

    def test_step_status_transitions(self):
        s = PlanStep(name="test")
        s.status = "running"
        assert s.status == "running"
        s.status = "done"
        assert s.status == "done"
        s.status = "failed"
        assert s.status == "failed"

    def test_step_serialize(self):
        s = PlanStep(name="search", tool="tavily", params={"q": "porpoise"})
        d = s.__dict__ if hasattr(s, '__dict__') else {}
        assert d.get('name') == 'search'


class TestBelief:
    def test_default_belief(self):
        b = Belief()
        assert b.user_query == ""
        assert b.last_observation is None
        assert b.errors == []

    def test_update_observation(self):
        b = Belief()
        b.update_observation({"result": "found 5 papers"})
        assert b.last_observation == {"result": "found 5 papers"}
        assert len(b.observation_history) == 1

    def test_error_tracking(self):
        b = Belief()
        b.errors.append("timeout")
        b.errors.append("rate_limit")
        assert len(b.errors) == 2
        assert "timeout" in b.errors

    def test_context_summary(self):
        b = Belief()
        b.user_query = "长江江豚种群数量"
        b.relevant_knowledge = [{"source": "IUCN", "status": "CR"}]
        summary = b.context_summary()
        assert isinstance(summary, str)
        assert "长江江豚" in summary or "IUCN" in summary or len(summary) > 0

    def test_confidence_scores(self):
        b = Belief()
        b.confidence_scores = {"pop_estimate": 0.85}
        b.confidence_scores["habitat_quality"] = 0.6
        assert b.confidence_scores["pop_estimate"] == 0.85

    def test_tool_results(self):
        b = Belief()
        b.tool_results = {"scholar": 10, "ncbi": 5}
        assert b.tool_results["scholar"] == 10

    def test_phase_tracking(self):
        b = Belief()
        b.phase = "search"
        assert b.phase == "search"


class TestDesire:
    def test_default_desire(self):
        d = Desire()
        assert isinstance(d.goals, list)
        assert d.priority == "medium"

    def test_configure(self):
        d = Desire()
        d.configure(goals=["assess population trend"], priority="high")
        assert "assess population trend" in d.goals
        assert d.priority == "high"

    def test_summarize(self):
        d = Desire()
        d.configure(goals=["monitor porpoise habitat"])
        s = d.summarize()
        assert isinstance(s, str)
        assert len(s) > 0


class TestIntention:
    def test_empty_intention(self):
        i = Intention()
        assert i.current_step == 0
        assert i.plan == []

    def test_set_plan(self):
        i = Intention()
        steps = [
            PlanStep(name="search"),
            PlanStep(name="analyze"),
            PlanStep(name="report"),
        ]
        i.set_plan(steps)
        assert len(i.plan) == 3
        assert i.current_step == 0

    def test_advance(self):
        i = Intention()
        i.set_plan([PlanStep(name="s1"), PlanStep(name="s2")])
        assert i.advance()  # step 0→1
        assert i.current_step == 1
        assert i.advance()  # step 1→2 (done)
        assert i.current_step == 2
        assert not i.advance()  # already done

    def test_retreat(self):
        i = Intention()
        i.set_plan([PlanStep(name="s1"), PlanStep(name="s2")])
        i.advance()
        assert i.retreat()
        assert i.current_step == 0
        assert not i.retreat()  # at start

    def test_progress(self):
        i = Intention()
        i.set_plan([PlanStep(name="s1"), PlanStep(name="s2")])
        assert i.progress() == 0.0
        i.advance()
        assert i.progress() == 0.5
        i.advance()
        assert i.progress() == 1.0

    def test_current_action(self):
        i = Intention()
        s = PlanStep(name="search_scholar")
        i.set_plan([s])
        assert i.current_action() is s
        i.advance()
        assert i.current_action() is None


class TestBDICoordinator:
    def test_initial_state(self):
        c = BDICoordinator()
        assert c.status == BDIStatus.IDLE

    def test_configure_desire(self):
        c = BDICoordinator()
        c.configure_desire(goals=["test"])
        assert c.desire.goals == ["test"]

    def test_perceive(self):
        c = BDICoordinator()
        c.perceive(observation={"data": "test"})
        assert c.belief.last_observation == {"data": "test"}

    def test_deliberate(self):
        c = BDICoordinator()
        c.configure_desire(goals=["find literature"])
        plan = c.deliberate()
        assert isinstance(plan, list)

    def test_alignment_check(self):
        c = BDICoordinator()
        # should not raise for normal actions
        assert c.check_alignment(["search", "analyze"]) is True

    def test_alignment_detects_forbidden(self):
        c = BDICoordinator()
        # forbidden actions should be detected
        result = c.check_alignment(["delete_database"])
        assert result is False

    def test_snapshot(self):
        c = BDICoordinator()
        snap = c.get_state_snapshot()
        assert "belief" in snap
        assert "desire" in snap
        assert "intention" in snap
        assert "status" in snap

    def test_full_cycle(self):
        c = BDICoordinator()
        c.configure_desire(goals=["assess porpoise population"])
        c.perceive({"query": "Neophocaena population Yangtze"})
        plan = c.deliberate()
        assert len(plan) > 0
        c.status = BDIStatus.DONE
        assert c.status == BDIStatus.DONE

    def test_status_enum(self):
        assert BDIStatus.IDLE.value == "idle"
        assert BDIStatus.DONE.value == "done"
        assert BDIStatus.FAILED.value == "failed"
