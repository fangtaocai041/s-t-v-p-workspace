"""KalmanEmergence — Kalman Filter for emergence signal detection.

Replaces static threshold emergence detection with Bayesian state estimation.
Tracks hidden state (species population health) from noisy observations.
Detects emergence when observation diverges from predicted state.

Mathematics:
  Predict: x_k = F * x_{k-1} + B * u_k
  Update: x_k = x_k + K * (z_k - H * x_k)
  Kalman gain: K = P * H^T * (H * P * H^T + R)^{-1}

Usage:
    kf = KalmanEmergence()
    kf.update(observation=0.7)  # observed population index
    if kf.is_emerging():
        print(f"Emergence detected! Divergence: {kf.divergence:.2f}")
"""

import json, os, time, math
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class KalmanState:
    x: float = 0.5      # estimated state (population health, 0=extinct, 1=thriving)
    P: float = 1.0      # estimate uncertainty
    Q: float = 0.01     # process noise
    R: float = 0.1      # measurement noise
    F: float = 1.0      # state transition
    H: float = 1.0      # observation mapping
    history: List[float] = None
    
    def __post_init__(self):
        self.history = self.history or []


class KalmanEmergence:
    """Kalman Filter for emergence signal detection in ecological monitoring."""

    def __init__(self, state_file: str = None):
        self._states: dict = {}
        self._divergences: dict = {}
        self._state_file = state_file

    def update(self, species_id: str, observation: float, 
               process_noise: float = 0.01, measurement_noise: float = 0.1) -> float:
        """Update Kalman filter with new observation. Returns estimated state."""
        state = self._states.get(species_id, KalmanState())
        state.Q = process_noise
        state.R = measurement_noise

        # Predict
        x_pred = state.F * state.x
        P_pred = state.F * state.P * state.F + state.Q

        # Update
        y = observation - state.H * x_pred  # Innovation
        S = state.H * P_pred * state.H + state.R
        K = P_pred * state.H / S if S > 0 else 0  # Kalman gain
        state.x = x_pred + K * y
        state.P = (1 - K * state.H) * P_pred

        state.history.append(state.x)
        if len(state.history) > 100:
            state.history = state.history[-50:]

        self._states[species_id] = state
        self._divergences[species_id] = abs(y) / max(abs(state.x), 0.01)
        return state.x

    def is_emerging(self, species_id: str, threshold: float = 2.0) -> bool:
        """Detect emergence: observation diverges > N standard deviations from prediction."""
        divergence = self._divergences.get(species_id, 0)
        return divergence > threshold

    def get_trend(self, species_id: str) -> str:
        """Get population trend from Kalman state history."""
        state = self._states.get(species_id)
        if not state or len(state.history) < 3:
            return "unknown"
        recent = state.history[-3:]
        if recent[-1] > recent[0] * 1.1:
            return "increasing"
        elif recent[-1] < recent[0] * 0.9:
            return "decreasing"
        return "stable"

    def get_state(self, species_id: str) -> Optional[KalmanState]:
        return self._states.get(species_id)

    @property
    def emergence_summary(self) -> dict:
        return {
            sid: {"estimated_state": round(s.x, 3), "divergence": round(self._divergences.get(sid, 0), 3),
                  "trend": self.get_trend(sid), "emerging": self.is_emerging(sid)}
            for sid, s in self._states.items()
        }
