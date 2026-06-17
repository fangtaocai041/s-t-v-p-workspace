"""CoiliaReActLoop — lightweight ReAct cognitive loop for coilia-agent.

Adopted from porpoise-agent's ReAct pattern (src/cognitive/react_loop.py).
Wraps coilia-agent's scripts/ algorithms as executable Actions in a Think→Act→Observe→Reflect cycle.

Architecture:
  Think  = route question → select analysis script
  Act    = execute script via subprocess/import
  Observe = parse script output → extract findings
  Reflect = validate results → identify gaps → refine question

Cross-pollination: porpoise-agent (P1) → coilia-agent (P2)
"""

import sys, os, importlib, logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

# ── Types ──

class ReActState(str, Enum):
    THINK = "think"
    ACT = "act"
    OBSERVE = "observe"
    REFLECT = "reflect"
    DONE = "done"

@dataclass
class ThoughtOutput:
    """Result of Think phase."""
    selected_script: str = ""
    query_params: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

@dataclass  
class ActionResult:
    """Result of Act phase."""
    script_name: str = ""
    success: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    elapsed_ms: float = 0.0

@dataclass
class Observation:
    """Result of Observe phase."""
    findings: List[str] = field(default_factory=list)
    data_points: int = 0
    confidence: float = 0.0
    anomalies: List[str] = field(default_factory=list)

@dataclass
class Reflection:
    """Result of Reflect phase."""
    satisfied: bool = False
    gaps: List[str] = field(default_factory=list)
    followup_questions: List[str] = field(default_factory=list)
    need_reanalysis: bool = False

# ── Script-to-theme mapping ──

SCRIPT_MAP = {
    "洄游": {"script": "migration_analysis", "func": "analyze_migration", "keywords": ["洄游","migration","耳石","otolith","sr/ca","微化学","生活史"]},
    "遗传": {"script": "genetics_analysis", "func": "analyze_genetics", "keywords": ["遗传","genetic","dna","微卫星","snp","线粒体","基因组","群体"]},
    "资源": {"script": "stock_assessment", "func": "assess_stock", "keywords": ["资源","stock","cpue","评估","msy","种群","捕捞","产量"]},
    "食性": {"script": "feeding_analysis", "func": "analyze_feeding", "keywords": ["食性","feeding","营养","稳定同位素","胃含物","d13c","d15n"]},
    "早期": {"script": "early_life_analysis", "func": "analyze_early_life", "keywords": ["繁殖","spawning","产卵","仔鱼","早期","胚胎","补充"]},
    "文献": {"script": "literature_search", "func": "search_coilia", "keywords": ["文献","综述","搜索","检索","研究进展"]},
}


class CoiliaReActLoop:
    """Lightweight ReAct loop for coilia-agent domain analysis.

    Think → select script → Act → execute → Observe → parse output → Reflect → iterate.

    Usage:
        loop = CoiliaReActLoop()
        result = loop.run("分析刀鲚洄游生态")
    """

    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.state = ReActState.THINK
        self.history: List[Dict] = []
        self._iteration = 0

    def run(self, question: str, use_llm: bool = False) -> Dict[str, Any]:
        """Execute full ReAct cycle for a research question."""
        result = {"question": question, "iterations": 0, "findings": [], "state": "started"}

        for i in range(self.max_iterations):
            self._iteration = i + 1

            # Phase 1: THINK — route question to analysis script
            self.state = ReActState.THINK
            thought = self._think(question)
            self.history.append({"phase": "think", "output": thought})

            # Phase 2: ACT — execute the selected script
            self.state = ReActState.ACT
            action = self._act(thought)
            self.history.append({"phase": "act", "output": action})
            if not action.success:
                result["state"] = f"act_failed: {action.error}"
                break

            # Phase 3: OBSERVE — parse script output
            self.state = ReActState.OBSERVE
            obs = self._observe(action)
            result["findings"].extend(obs.findings)
            self.history.append({"phase": "observe", "output": obs})

            # Phase 4: REFLECT — validate and decide
            self.state = ReActState.REFLECT
            refl = self._reflect(obs, question)
            self.history.append({"phase": "reflect", "output": refl})

            if refl.satisfied:
                self.state = ReActState.DONE
                result["state"] = "completed"
                break
            elif refl.followup_questions:
                question = refl.followup_questions[0]  # Refine for next iteration

        result["iterations"] = i + 1
        return result

    def _think(self, question: str) -> ThoughtOutput:
        """Route question to the best-matching analysis script."""
        q = question.lower()
        best_match = None
        best_score = 0

        for theme, info in SCRIPT_MAP.items():
            score = sum(1 for kw in info["keywords"] if kw.lower() in q)
            if score > best_score:
                best_score = score
                best_match = theme

        if best_match and best_score > 0:
            info = SCRIPT_MAP[best_match]
            return ThoughtOutput(
                selected_script=info["script"],
                query_params={"theme": best_match, "use_example": False},
                reasoning=f"Matched theme '{best_match}' with {best_score} keywords"
            )
        
        # Default to literature search
        return ThoughtOutput(
            selected_script="literature_search",
            query_params={"query": question, "use_example": True},
            reasoning="No specific theme matched; defaulting to literature search"
        )

    def _act(self, thought: ThoughtOutput) -> ActionResult:
        """Execute the selected analysis script."""
        import time
        start = time.time()

        script_name = thought.selected_script
        info = None
        for theme, i in SCRIPT_MAP.items():
            if i["script"] == script_name:
                info = i
                break

        if not info:
            return ActionResult(script_name=script_name, success=False, 
                              error=f"Script '{script_name}' not found in SCRIPT_MAP")

        try:
            # Import the script module
            _reasonix = str(Path(__file__).resolve().parent.parent.parent.parent)
            if _reasonix not in sys.path:
                sys.path.insert(0, _reasonix)
            
            mod = importlib.import_module(f"scripts.{script_name}")
            func = getattr(mod, info["func"])
            
            # Execute
            kwargs = dict(thought.query_params)
            result = func(**kwargs)
            
            elapsed = (time.time() - start) * 1000
            return ActionResult(
                script_name=script_name, success=True,
                data={"result": result} if result else {},
                elapsed_ms=elapsed
            )
        except ImportError as e:
            logger.warning(f"Script import failed: {script_name} — {e}")
            return ActionResult(script_name=script_name, success=False, error=str(e))
        except Exception as e:
            logger.warning(f"Script execution failed: {script_name} — {e}")
            return ActionResult(script_name=script_name, success=False, error=str(e))

    def _observe(self, action: ActionResult) -> Observation:
        """Parse script output into structured findings."""
        findings = []
        anomalies = []

        if not action.success:
            anomalies.append(f"Script {action.script_name} failed: {action.error}")
            return Observation(findings=findings, anomalies=anomalies, confidence=0.0)

        data = action.data.get("result", {})
        if isinstance(data, dict):
            # Extract structured findings from script output
            for k, v in data.items():
                if v is not None and v != "":
                    findings.append(f"{k}: {str(v)[:200]}")
                    if isinstance(v, (int, float)):
                        findings.append(f"  (quantitative: {v})")

        # Detect anomalies
        if not findings:
            anomalies.append(f"No findings extracted from {action.script_name}")
            return Observation(findings=findings, anomalies=anomalies, confidence=0.1)

        return Observation(
            findings=findings,
            data_points=len(findings),
            confidence=min(0.8, 0.3 + 0.1 * len(findings)),
            anomalies=anomalies
        )

    def _reflect(self, obs: Observation, original_question: str) -> Reflection:
        """Validate findings and identify gaps."""
        refl = Reflection()

        if obs.confidence >= 0.6:
            refl.satisfied = True
        elif obs.anomalies:
            refl.need_reanalysis = True
            refl.followup_questions = [
                f"Refine analysis for {original_question} with broader search"
            ]
        else:
            refl.satisfied = True  # Accept even low-confidence results
            refl.gaps = ["Insufficient data — consider expanding search sources"]

        return refl


def get_react_loop() -> CoiliaReActLoop:
    """Factory function."""
    return CoiliaReActLoop()
