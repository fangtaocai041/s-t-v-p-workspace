"""
porpoise-agent BDI 模块独立测试
BDI 状态机: Belief / Desire / Intention / BDIStatus / BDICoordinator

运行: python -m pytest porpoise-agent/tests/test_bdi_standalone.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cognitive.bdi import (
    Belief, Desire, Intention, PlanStep, StepStatus,
    BDIStatus, BDICoordinator,
)


class TestPlanStep:
    def test_create_step(self):
        s = PlanStep(id="search", description="search", action="scholar", params={"q": "test"})
        assert s.id == "search"
        assert s.action == "scholar"
        assert s.status == StepStatus.PENDING

    def test_step_defaults(self):
        s = PlanStep(id="analyze", description="analyze", action="")
        assert s.action == ""
        assert s.params == {}
        assert s.result is None
        assert s.status == StepStatus.PENDING

    def test_step_status_transitions(self):
        s = PlanStep(id="test", description="test", action="test")
        s.status = StepStatus.IN_PROGRESS
        assert s.status == StepStatus.IN_PROGRESS
        s.status = StepStatus.COMPLETED
        assert s.status == StepStatus.COMPLETED
        s.status = StepStatus.FAILED
        assert s.status == StepStatus.FAILED

    def test_step_serialize(self):
        s = PlanStep(id="search", description="search", action="tavily", params={"q": "porpoise"})
        d = s.__dict__ if hasattr(s, '__dict__') else {}
        assert d.get('id') == 'search'

    def test_step_dependencies(self):
        s = PlanStep(id="s2", description="step 2", action="analyze", dependencies=["s1"])
        assert "s1" in s.dependencies

    def test_step_retries(self):
        s = PlanStep(id="retry", description="test retry", action="test", max_retries=5)
        assert s.max_retries == 5
        assert s.retries == 0


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
        summary = b.get_context_summary()
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
        assert isinstance(d.primary_goal, str)
        assert isinstance(d.constraints, list)

    def test_configure_via_fields(self):
        d = Desire()
        d.primary_goal = "assess population trend"
        d.quality_thresholds = {"min_papers": 10}
        assert d.primary_goal == "assess population trend"
        assert d.quality_thresholds["min_papers"] == 10

    def test_summarize(self):
        d = Desire()
        d.primary_goal = "monitor porpoise habitat"
        s = d.summarize()
        assert isinstance(s, str)
        assert len(s) > 0

    def test_constraints(self):
        d = Desire()
        d.constraints = ["only 2020+", "Chinese and English"]
        assert len(d.constraints) == 2

    def test_forbidden_actions(self):
        d = Desire()
        d.forbidden_actions = ["delete_data", "external_write"]
        assert "delete_data" in d.forbidden_actions


class TestIntention:
    def test_empty_intention(self):
        i = Intention()
        assert i.current_step_index == 0
        assert i.plan == []
        assert i.current_step is None

    def test_set_plan(self):
        i = Intention()
        steps = [
            PlanStep(id="search", description="search", action="scholar"),
            PlanStep(id="analyze", description="analyze", action="analysis"),
            PlanStep(id="report", description="report", action="write_report"),
        ]
        i.plan = steps
        assert len(i.plan) == 3
        assert i.current_step_index == 0

    def test_advance(self):
        i = Intention()
        i.plan = [PlanStep(id="s1", description="s1", action="a1"),
                   PlanStep(id="s2", description="s2", action="a2")]
        assert i.current_step_index == 0
        i.advance()  # step 0→1
        assert i.current_step_index == 1
        i.advance()  # step 1→2 (done)
        assert i.current_step_index == 2
        assert i.is_complete is True

    def test_retreat(self):
        i = Intention()
        i.plan = [PlanStep(id="s1", description="s1", action="a1"),
                   PlanStep(id="s2", description="s2", action="a2")]
        i.advance()
        assert i.current_step_index == 1
        i.retreat()
        assert i.current_step_index == 0
        # retreat at start is a no-op (no crash)
        i.retreat()
        assert i.current_step_index == 0

    def test_progress(self):
        i = Intention()
        i.plan = [PlanStep(id="s1", description="s1", action="a1"),
                   PlanStep(id="s2", description="s2", action="a2")]
        info = i.get_progress()
        assert info["progress_pct"] == 0.0
        i.advance()
        info = i.get_progress()
        assert info["progress_pct"] == 50.0
        i.advance()
        info = i.get_progress()
        assert info["progress_pct"] == 100.0

    def test_current_action(self):
        i = Intention()
        s = PlanStep(id="search_scholar", description="search", action="scholar")
        i.plan = [s]
        assert i.current_step is s
        i.advance()
        assert i.current_step is None

    def test_completed_steps(self):
        i = Intention()
        i.plan = [PlanStep(id="s1", description="s1", action="a1"),
                   PlanStep(id="s2", description="s2", action="a2")]
        i.advance()
        assert len(i.completed_steps) == 1
        assert i.completed_steps[0].id == "s1"


class TestBDICoordinator:
    def test_initial_state(self):
        c = BDICoordinator()
        assert c.status == BDIStatus.IDLE

    def test_configure_desire(self):
        c = BDICoordinator()
        c.configure_desire(primary_goal="test goal")
        assert c.desire.primary_goal == "test goal"

    def test_configure_desire_full(self):
        c = BDICoordinator()
        c.configure_desire(
            primary_goal="assess population",
            constraints=["only peer-reviewed"],
            quality_thresholds={"min_papers": 5},
            forbidden_actions=["delete_database"],
        )
        assert c.desire.primary_goal == "assess population"
        assert "only peer-reviewed" in c.desire.constraints
        assert c.desire.quality_thresholds["min_papers"] == 5
        assert "delete_database" in c.desire.forbidden_actions

    def test_perceive(self):
        c = BDICoordinator()
        c.perceive(observation={"data": "test"})
        assert c.belief.last_observation == {"data": "test"}

    def test_deliberate(self):
        c = BDICoordinator()
        c.configure_desire(primary_goal="find literature")
        plan = [PlanStep(id="s1", description="search", action="scholar")]
        c.deliberate(new_plan=plan)
        assert len(c.intention.plan) == 1
        assert c.intention.plan[0].id == "s1"

    def test_alignment_check(self):
        c = BDICoordinator()
        # Set up a plan with a normal action
        plan = [PlanStep(id="s1", description="search", action="scholar")]
        c.deliberate(new_plan=plan)
        # should not flag normal actions
        assert c.check_alignment() is True

    def test_alignment_detects_forbidden(self):
        c = BDICoordinator()
        # Set up a plan with a forbidden action
        c.configure_desire(
            primary_goal="test",
            forbidden_actions=["delete_database"],
        )
        plan = [PlanStep(id="s1", description="delete", action="delete_database")]
        c.deliberate(new_plan=plan)
        # forbidden action should be detected
        result = c.check_alignment()
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
        c.configure_desire(primary_goal="assess porpoise population")
        c.perceive({"query": "Neophocaena population Yangtze"})
        plan = [PlanStep(id="s1", description="search", action="scholar")]
        c.deliberate(new_plan=plan)
        assert len(c.intention.plan) > 0
        c.status = BDIStatus.DONE
        assert c.status == BDIStatus.DONE

    def test_status_enum(self):
        assert BDIStatus.IDLE.value == "idle"
        assert BDIStatus.DONE.value == "done"
        assert BDIStatus.FAILED.value == "failed"

    def test_revise_intention(self):
        c = BDICoordinator()
        old_plan = [PlanStep(id="old", description="old", action="old_action")]
        c.deliberate(new_plan=old_plan)
        new_plan = [PlanStep(id="new", description="new", action="new_action")]
        c.revise_intention(revised_plan=new_plan)
        assert len(c.intention.plan) == 1
        assert c.intention.plan[0].id == "new"
        assert c.intention.current_step_index == 0
