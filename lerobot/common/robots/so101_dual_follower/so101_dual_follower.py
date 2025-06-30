#!/usr/bin/env python

import logging
from functools import cached_property
from typing import Any

from ..robot import Robot
from ..so101_follower import SO101Follower
from ..utils import ensure_safe_goal_position
from .config_so101_dual_follower import SO101DualFollowerConfig

logger = logging.getLogger(__name__)


class SO101DualFollower(Robot):
    """Dual-arm robot composed of two SO101 follower arms."""

    config_class = SO101DualFollowerConfig
    name = "so101_dual_follower"

    def __init__(self, config: SO101DualFollowerConfig):
        super().__init__(config)
        self.left = SO101Follower(config.left)
        self.right = SO101Follower(config.right)
        self.config = config

    def _prefix(self, d: dict[str, Any], prefix: str) -> dict[str, Any]:
        return {f"{prefix}.{k}": v for k, v in d.items()}

    @cached_property
    def observation_features(self) -> dict[str, Any]:
        left = self._prefix(self.left.observation_features, "left")
        right = self._prefix(self.right.observation_features, "right")
        return {**left, **right}

    @cached_property
    def action_features(self) -> dict[str, Any]:
        left = self._prefix(self.left.action_features, "left")
        right = self._prefix(self.right.action_features, "right")
        return {**left, **right}

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

    def _split_action(self, action: dict[str, Any]):
        left = {k.removeprefix("left."): v for k, v in action.items() if k.startswith("left.")}
        right = {k.removeprefix("right."): v for k, v in action.items() if k.startswith("right.")}
        return left, right

    def get_observation(self) -> dict[str, Any]:
        left_obs = self.left.get_observation()
        right_obs = self.right.get_observation()
        return {**self._prefix(left_obs, "left"), **self._prefix(right_obs, "right")}

    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        left_action, right_action = self._split_action(action)

        if self.config.left.max_relative_target is not None:
            present_pos = self.left.bus.sync_read("Present_Position")
            left_goal_present = {k: (left_action[k], present_pos[k]) for k in left_action}
            left_action = ensure_safe_goal_position(left_goal_present, self.config.left.max_relative_target)

        if self.config.right.max_relative_target is not None:
            present_pos_r = self.right.bus.sync_read("Present_Position")
            right_goal_present = {k: (right_action[k], present_pos_r[k]) for k in right_action}
            right_action = ensure_safe_goal_position(
                right_goal_present, self.config.right.max_relative_target
            )

        left_sent = self.left.send_action({f"{k}.pos": v for k, v in left_action.items()})
        right_sent = self.right.send_action({f"{k}.pos": v for k, v in right_action.items()})
        return {**self._prefix(left_sent, "left"), **self._prefix(right_sent, "right")}

    def disconnect(self) -> None:
        self.left.disconnect()
        self.right.disconnect()
        logger.info(f"{self} disconnected")
