"""BDI 状态机单元测试"""
import pytest
import sys
sys.path.insert(0, ".")

from src.cognitive.bdi import (
    BDICoordinator, BDIStatus, Belief, Desire, Intention,
    PlanStep, StepStatus
)


class TestPlanStep:
    def test_create_step(self):
        step = PlanStep(id="s1", description="搜索文献", action="search")
        assert step.id == "s1"
        assert step.status == StepStatus.PENDING
        assert step.retries == 0
        assert str(step) == "[pending] s1: 搜索文献"

    def test_step_defaults(self):
        step = PlanStep(id="x", description="", action="noop")
        assert step.params == {}
        assert step.dependencies == []
        assert step.max_retries == 3


class TestBelief:
    def test_update_observation(self):
        b = Belief(user_query="test")
        b.update_observation({"result": "ok", "data": [1, 2, 3]})
        assert b.last_observation == {"result": "ok", "data": [1, 2, 3]}
        assert len(b.observation_history) == 1

    def test_error_tracking(self):
        b = Belief()
        b.update_observation({"error": "timeout"})
        assert "timeout" in b.errors

    def test_context_summary(self):
        b = Belief(user_query="搜索江豚")
        b.relevant_knowledge = [{"title": "江豚保护进展"}]
        summary = b.get_context_summary()
        assert "搜索江豚" in summary
        assert "江豚保护进展" in summary


class TestDesire:
    def test_configure(self):
        d = Desire(
            primary_goal="完成文献综述",
            constraints=["2020年后", "中英文"],
            quality_thresholds={"min_papers": 10},
        )
        assert d.primary_goal == "完成文献综述"
        assert len(d.constraints) == 2
        assert d.quality_thresholds["min_papers"] == 10

    def test_summarize(self):
        d = Desire(primary_goal="搜索", constraints=["c1"])
        s = d.summarize()
        assert "搜索" in s
        assert "c1" in s


class TestIntention:
    def test_empty_intention(self):
        i = Intention()
        assert i.is_complete
        assert i.current_step is None
        assert i.get_progress()["total_steps"] == 0

    def test_advance(self):
        plan = [
            PlanStep(id="s1", description="Step 1", action="a1"),
            PlanStep(id="s2", description="Step 2", action="a2"),
        ]
        i = Intention(plan=plan)
        assert not i.is_complete
        assert i.current_step.id == "s1"

        i.advance()
        assert i.current_step_index == 1
        assert i.current_step.id == "s2"
        assert i.completed_steps[0].status == StepStatus.COMPLETED

        i.advance()
        assert i.is_complete

    def test_retreat(self):
        plan = [PlanStep(id="s1", description="S1", action="a1")]
        i = Intention(plan=plan)
        i.advance()
        assert i.current_step_index == 1
        i.retreat()
        assert i.current_step_index == 0
        assert i.current_step.status == StepStatus.RETRYING

    def test_progress(self):
        plan = [
            PlanStep(id="s1", description="S1", action="a1"),
            PlanStep(id="s2", description="S2", action="a2"),
        ]
        i = Intention(plan=plan)
        p = i.get_progress()
        assert p["total_steps"] == 2
        assert p["completed"] == 0
        assert p["progress_pct"] == 0.0


class TestBDICoordinator:
    def test_initial_state(self):
        bdi = BDICoordinator()
        assert bdi.status == BDIStatus.IDLE

    def test_configure_desire(self):
        bdi = BDICoordinator()
        bdi.configure_desire("test goal", constraints=["c1"])
        assert bdi.desire.primary_goal == "test goal"

    def test_perceive(self):
        bdi = BDICoordinator()
        bdi.perceive({"result": "ok"})
        assert len(bdi.belief.observation_history) == 1
        assert bdi.status == BDIStatus.PERCEIVING

    def test_deliberate(self):
        bdi = BDICoordinator()
        plan = [PlanStep(id="s1", description="Step", action="search")]
        bdi.deliberate(plan, method="cot")
        assert len(bdi.intention.plan) == 1
        assert bdi.intention.decomposition_method == "cot"

    def test_alignment_check(self):
        bdi = BDICoordinator()
        assert bdi.check_alignment()

    def test_alignment_detects_forbidden(self):
        bdi = BDICoordinator()
        bdi.configure_desire("test", forbidden_actions=["delete_data"])
        plan = [PlanStep(id="s1", description="Delete", action="delete_data")]
        bdi.deliberate(plan)
        assert not bdi.check_alignment()

    def test_snapshot(self):
        bdi = BDICoordinator()
        bdi.configure_desire("goal")
        snap = bdi.get_state_snapshot()
        assert "status" in snap
        assert snap["belief"]["user_query"] == ""

    def test_full_cycle(self):
        """端到端 BDI 循环: perceive → deliberate → advance → retreat"""
        bdi = BDICoordinator()
        bdi.configure_desire("完成搜索", quality_thresholds={"min_papers": 5})

        # 感知
        bdi.perceive({"query": "江豚", "result": {"papers_found": 3}})

        # 决策
        plan = [
            PlanStep(id="s1", description="搜索PubMed", action="search_pubmed"),
            PlanStep(id="s2", description="下载全文", action="download"),
        ]
        bdi.deliberate(plan, method="cot")

        # 执行 + 前进
        assert bdi.intention.current_step.id == "s1"
        bdi.intention.advance()
        assert bdi.intention.current_step.id == "s2"

        # 错误 → 回退
        bdi.perceive({"error": "download failed"})
        bdi.intention.retreat()
        assert bdi.intention.current_step.id == "s1"
        assert bdi.intention.current_step.status == StepStatus.RETRYING
