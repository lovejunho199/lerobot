#!/usr/bin/env python

import logging
from typing import Any

from ..so101_leader import SO101Leader
from ..teleoperator import Teleoperator
from .config_so101_dual_leader import SO101DualLeaderConfig

logger = logging.getLogger(__name__)


class SO101DualLeader(Teleoperator):
    """Dual teleoperator composed of two SO101 leader arms."""

    config_class = SO101DualLeaderConfig
    name = "so101_dual_leader"

    def __init__(self, config: SO101DualLeaderConfig):
        super().__init__(config)
        self.left = SO101Leader(config.left)
        self.right = SO101Leader(config.right)
        self.config = config

    def _prefix(self, d: dict[str, Any], prefix: str) -> dict[str, Any]:
        return {f"{prefix}.{k}": v for k, v in d.items()}

    @property
    def action_features(self) -> dict[str, type]:
        left = self._prefix(self.left.action_features, "left")
        right = self._prefix(self.right.action_features, "right")
        return {**left, **right}

    @property
    def feedback_features(self) -> dict[str, type]:
        return {}

    @property
    def is_connected(self) -> bool:
        return self.left.is_connected and self.right.is_connected

    def connect(self, calibrate: bool = True) -> None:
        self.left.connect(calibrate)
        self.right.connect(calibrate)
        logger.info(f"{self} connected")

    @property
    def is_calibrated(self) -> bool:
        return self.left.is_calibrated and self.right.is_calibrated

    def calibrate(self) -> None:
        self.left.calibrate()
        self.right.calibrate()

    def configure(self) -> None:
        self.left.configure()
        self.right.configure()

    def get_action(self) -> dict[str, Any]:
        left_act = self.left.get_action()
        right_act = self.right.get_action()
        return {**self._prefix(left_act, "left"), **self._prefix(right_act, "right")}

    def send_feedback(self, feedback: dict[str, Any]) -> None:
        # Not implemented
        pass

    def disconnect(self) -> None:
        self.left.disconnect()
        self.right.disconnect()
        logger.info(f"{self} disconnected")
