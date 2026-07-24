"""Continual Learning Engine for scheme drift sensitivity recalibration."""

from __future__ import annotations

import numpy as np


class AdaptiveDriftLearner:
    """Continual Learning Engine: Recalibrates baseline sensitivity based on recent drift error telemetry."""

    def __init__(self, learning_rate: float = 0.05, initial_sensitivity: float = 1.0):
        self.eta = learning_rate
        self.sensitivity = initial_sensitivity
        self.error_history: list[float] = []

    def recalibrate(self, observed_drift: float, target_threshold: float) -> float:
        """Updates baseline sensitivity theta(t+1) using exponential error feedback."""
        drift_error = observed_drift - target_threshold
        self.error_history.append(drift_error)

        # 10-step rolling window gradient correction
        rolling_error = float(np.mean(self.error_history[-10:]))
        self.sensitivity = max(0.1, min(2.5, self.sensitivity - (self.eta * rolling_error)))

        return round(self.sensitivity, 4)


# Global persistent instance
learner = AdaptiveDriftLearner(learning_rate=0.03)

# Nominal ROM deviation band before CRITICAL PATHWAY DRIFT (percent points).
BASE_DRIFT_THRESHOLD = 15.0


def effective_drift_threshold(base: float = BASE_DRIFT_THRESHOLD) -> float:
    """Scale the static drift band by live learner sensitivity theta(t)."""
    return round(float(base) * float(learner.sensitivity), 4)
