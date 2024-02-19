#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Manager for handling RunsLikeACharm configuration."""

import logging
from typing import cast

from core.cluster import ClusterState
from core.structured_config import CharmConfig, LogLevel
from core.workload import WorkloadBase
from literals import (
    PATHS,
)

logger = logging.getLogger(__name__)

class RunsLikeACharmConfigManager:
    """Manager for handling RunsLikeACharm configuration."""

    def __init__(
        self,
        state: ClusterState,
        workload: WorkloadBase,
        config: CharmConfig,
    ):
        self.state = state
        self.workload = workload
        self.config = config
        self.interval = 0

    @property
    def setup_script_path(self) -> str:
        """Return the target path to the setup script
            file on the node
        """
        return PATHS["INSTALL_SCRIPT"]

    @property
    def setup_script(self) -> str:
        """Return the setup script provided by the user.

        Returns:
            a setup script file to be run on the host
        """
        return self.config.setup_script

