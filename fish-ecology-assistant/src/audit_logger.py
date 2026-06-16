"""
Fish Ecology Assistant — Audit Logger
借鉴 porpoise-agent 的 JSONL 审计追踪系统

记录每次研究会话的完整决策链，支持事后审计和可复现性验证。
"""

import json
import os
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Setup basic logging configuration."""
    level = os.getenv("FISH_ECO_LOG_LEVEL", "INFO")
    log_file = os.getenv("FISH_ECO_LOG_FILE", "./logs/fish-ecology.log")
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    import logging
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )


class AuditLogger:
    """
    JSONL 审计日志记录器。
    
    记录事件类型:
    - session_start / session_end
    - phase_routed / phase_start / phase_end
    - approval_required / approval_granted
    - emergence_signal
    - skill_invoked / skill_completed
    - tool_call / tool_result
    - error / retry
    """

    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = self.log_dir / f"audit_{self.session_id}.jsonl"
        self.event_count = 0

    def log(self, event_type: str, data: dict):
        """Record an audit event."""
        self.event_count += 1
        entry = {
            "event_id": self.event_count,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_emergence(self, pattern: str, sources: list[str], confidence: str):
        """Record an emergence detection event."""
        self.log("emergence_signal", {
            "pattern": pattern,
            "sources": sources,
            "source_count": len(sources),
            "confidence": confidence,
        })

    def log_phase_transition(self, from_phase: str, to_phase: str, reason: str = ""):
        """Record a phase transition."""
        self.log("phase_transition", {
            "from": from_phase,
            "to": to_phase,
            "reason": reason,
        })

    def get_summary(self) -> dict:
        """Return session summary statistics."""
        return {
            "session_id": self.session_id,
            "event_count": self.event_count,
            "log_path": str(self.log_path),
        }


# Global singleton
audit = AuditLogger()
