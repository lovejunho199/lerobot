#!/usr/bin/env python

from dataclasses import dataclass

from ..config import TeleoperatorConfig
from ..so101_leader.config_so101_leader import SO101LeaderConfig


@TeleoperatorConfig.register_subclass("so101_dual_leader")
@dataclass
class SO101DualLeaderConfig(TeleoperatorConfig):
    """Configuration for a dual SO101 leader teleoperator composed of two single arms."""

    left: SO101LeaderConfig
    right: SO101LeaderConfig
