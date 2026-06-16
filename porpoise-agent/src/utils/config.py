# Configuration management

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"


def load_yaml(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class Config:
    """Unified configuration entry point"""

    def __init__(self):
        self._agent_config = load_yaml(CONFIG_DIR / "agent.yaml")
        self._model_config = load_yaml(CONFIG_DIR / "models.yaml")

    @property
    def agent(self) -> dict:
        return self._agent_config.get("agent", {})

    @property
    def orchestrator(self) -> dict:
        """兼容旧接口 — 已迁移到 cognitive.react_loop"""
        return self._agent_config.get("cognitive", {}).get("react_loop", {})

    # ── 五层模型属性 ──────────────────────────────────

    @property
    def interaction(self) -> dict:
        return self._agent_config.get("interaction", {})

    @property
    def cognitive(self) -> dict:
        return self._agent_config.get("cognitive", {})

    @property
    def memory_config(self) -> dict:
        return self._agent_config.get("memory", {})

    @property
    def mapping(self) -> dict:
        return self._agent_config.get("mapping", {})

    @property
    def execution(self) -> dict:
        return self._agent_config.get("execution", {})

    @property
    def topology(self) -> dict:
        return self._agent_config.get("topology", {})

    @property
    def integration(self) -> dict:
        return self._agent_config.get("integration", {})

    @property
    def cognitive_search(self) -> dict:
        return self._agent_config.get("integration", {}).get("cognitive_search", {})

    @property
    def agents(self) -> dict:
        return self._agent_config.get("agents", {})

    @property
    def models(self) -> dict:
        return self._model_config.get("providers", {})

    @property
    def reasonix(self) -> dict:
        return self._model_config.get("reasonix", {})

    @property
    def deepseek_api_key(self) -> str:
        return os.getenv("DEEPSEEK_API_KEY", "")

    @property
    def deepseek_base_url(self) -> str:
        return os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    @property
    def default_model(self) -> str:
        return os.getenv("PORPOISE_DEFAULT_MODEL", "deepseek-chat")

    @property
    def reasoning_model(self) -> str:
        return os.getenv("PORPOISE_REASONING_MODEL", "deepseek-reasoner")

    @property
    def lab_name(self) -> str:
        return os.getenv("LAB_NAME", "FFRC-LiuKai-Lab")

    @property
    def data_dir(self) -> Path:
        return Path(os.getenv("PORPOISE_DATA_DIR", str(DATA_DIR)))


config = Config()
