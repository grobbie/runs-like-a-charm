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

    @property
    def cloud_init_path(self) -> str:
        """Return the target path to the cloud-init config
            file on the node
        """
        return PATHS["CLOUDCFG"]

    @property
    def cloud_init_yaml(self) -> str:
        """Return the cloud-init YAML provided by the user.

        Returns:
            cloud-init config string in YAML format
        """
        return self.config.cloud_init_yaml

    @property
    def environment_variables(self) -> list[str]:
        """Return the user-defined environment variables that
            need to be set

        Returns:
            List of environment variables to set
        """
        environment_variables = self.config.environment_variables.split(",")

    def set_environment(self) -> None:
        """Writes the env-vars requested by the user."""

        updated_env_list = self.environment_variables

        if updated_env_list is None:
            return

        def map_env(env: list[str]) -> dict[str, str]:
            map_env = {}
            for var in env:
                key = "".join(var.split("=", maxsplit=1)[0])
                value = "".join(var.split("=", maxsplit=1)[1:])
                if key:
                    # only check for keys, as we can have an empty value for a variable
                    map_env[key] = value
            return map_env

        raw_current_env = self.workload.read("/etc/environment")
        current_env = map_env(raw_current_env)

        updated_env = current_env | map_env(updated_env_list)
        content = "\n".join([f"{key}={value}" for key, value in updated_env.items()])
        self.workload.write(content=content, path="/etc/environment")
