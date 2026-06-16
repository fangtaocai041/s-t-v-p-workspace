"""
声学分析 Agent (Acoustic Agent)
─────────────────────────────────
负责被动声学监测 (PAM) 数据处理。

能力:
- 声学文件加载与验证
- NBHF click 脉冲检测 (110-150 kHz)
- Click Train 提取与分类
- Buzz 检测与觅食行为推断
- 昼夜节律分析
- 声学特征提取 (18+ 特征)
"""

import logging
from typing import Any

from src.agents.base import BaseAgent
from src.cognitive.bdi import Desire

logger = logging.getLogger(__name__)


class AcousticAgent(BaseAgent):
    """声学分析 Agent — 江豚 NBHF 声信号处理专家"""

    def __init__(self, model: str = "deepseek-chat", memory: Any = None):
        super().__init__(name="acoustic", model=model, memory=memory)

    def _init_desire(self):
        self.bdi.desire = Desire(
            primary_goal="精确检测和分类江豚 NBHF 声信号",
            constraints=[
                "检测 Accuracy > 90%",
                "虚警率 FPR < 5%",
                "手动验证 >= 10% 样本",
                "所有参数和版本记录完整",
            ],
            quality_thresholds={
                "min_accuracy": 0.90,
                "max_fpr": 0.05,
                "min_validation_pct": 0.10,
            },
        )

    def _init_tools(self):
        self.tools.register(
            name="load_acoustic_file",
            description="Load acoustic recording and return metadata",
            parameters={"path": {"type": "string"}},
            fn=self._load_file,
            category="acoustic",
        )
        self.tools.register(
            name="detect_clicks",
            description="Detect NBHF clicks using SPL threshold",
            parameters={
                "audio_path": {"type": "string"},
                "threshold_db": {"type": "number"},
            },
            fn=self._detect_clicks,
            category="acoustic",
        )

    async def handle_message(self, message: Any) -> dict:
        """
        处理声学分析请求

        输入: {"action": "detect_clicks", "audio_path": "...", ...}
        输出: {"n_clicks": ..., "n_buzzes": ..., "features": {...}}
        """
        self._call_count += 1

        content = message.content if hasattr(message, 'content') else message
        if isinstance(content, str):
            content = {"query": content}

        action = content.get("action", "detect_clicks")
        audio_path = content.get("audio_path", content.get("query", ""))

        logger.info(f"AcousticAgent[{self.node_id}]: {action} on {audio_path}")

        try:
            if action == "load":
                result = self._load_file(audio_path)
            elif action == "detect_clicks":
                result = self._detect_clicks(
                    audio_path,
                    threshold_db=content.get("threshold_db", -134.0),
                )
            else:
                result = {"error": f"Unknown action: {action}"}

            return {
                "agent": "acoustic",
                "action": action,
                **result,
            }

        except Exception as e:
            self._error_count += 1
            logger.error(f"AcousticAgent failed: {e}")
            return {"agent": "acoustic", "error": str(e)}

    def _load_file(self, path: str) -> dict:
        """加载声学文件"""
        try:
            import soundfile as sf
            info = sf.info(path)
            return {
                "path": path,
                "samplerate": info.samplerate,
                "channels": info.channels,
                "duration": info.duration,
                "format": info.format,
            }
        except ImportError:
            return {"path": path, "status": "soundfile not installed"}
        except Exception as e:
            return {"path": path, "error": str(e)}

    def _detect_clicks(
        self, audio_path: str, threshold_db: float = -134.0
    ) -> dict:
        """检测 NBHF click 脉冲"""
        try:
            import numpy as np
            import librosa

            y, sr = librosa.load(audio_path, sr=None)

            if sr < 500000:
                return {
                    "warning": f"Sample rate {sr} Hz may be too low for NBHF (need ≥500 kHz)",
                    "n_clicks": 0,
                    "n_buzzes": 0,
                }

            # 带通滤波 100-180 kHz
            from scipy.signal import butter, filtfilt
            nyq = sr / 2
            b, a = butter(4, [100000/nyq, 180000/nyq], btype='band')
            y_filt = filtfilt(b, a, y)

            # RMS 能量
            frame_length = 256
            hop_length = 128
            rms = librosa.feature.rms(
                y=y_filt, frame_length=frame_length, hop_length=hop_length
            )[0]
            rms_db = 20 * np.log10(rms + 1e-10)

            # 阈值检测
            above_threshold = rms_db > threshold_db
            transitions = np.diff(above_threshold.astype(int))
            starts = np.where(transitions == 1)[0]
            ends = np.where(transitions == -1)[0]

            n_clicks = min(len(starts), len(ends))

            # Buzz 检测 (ICI < 10ms)
            n_buzzes = 0
            if n_clicks > 1:
                start_times = starts * hop_length / sr
                if len(start_times) > 1:
                    icis = np.diff(start_times)
                    n_buzzes = int(np.sum(icis < 0.010))  # ICI < 10ms

            return {
                "audio_path": audio_path,
                "samplerate": sr,
                "threshold_db": threshold_db,
                "n_clicks": n_clicks,
                "n_buzzes": n_buzzes,
                "foraging_index": n_buzzes / max(n_clicks, 1),
                "rms_range_db": [float(np.min(rms_db)), float(np.max(rms_db))],
            }

        except ImportError as e:
            return {"error": f"Missing dependency: {e}", "n_clicks": 0, "n_buzzes": 0}
        except Exception as e:
            return {"error": str(e), "n_clicks": 0, "n_buzzes": 0}

    def can_handle(self, intent: str) -> bool:
        return intent in ("acoustic_analysis", "click_detection")
