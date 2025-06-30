#!/usr/bin/env python

from dataclasses import dataclass

from ..config import RobotConfig
from ..so101_follower.config_so101_follower import SO101FollowerConfig


@RobotConfig.register_subclass("so101_dual_follower")
@dataclass
class SO101DualFollowerConfig(RobotConfig):
    """Configuration for a dual SO101 follower robot composed of two single arms."""

    left: SO101FollowerConfig
    right: SO101FollowerConfig
