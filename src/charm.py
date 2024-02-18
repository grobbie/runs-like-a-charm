#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charmed Machine Operator that runs anything™."""

import logging
import time

from charms.data_platform_libs.v0.data_models import TypedCharmBase
from charms.rolling_ops.v0.rollingops import RollingOpsManager, RunWithLock
from ops.framework import EventBase
from ops.main import main
from ops.model import ActiveStatus, StatusBase
from core.cluster import ClusterState
from core.structured_config import CharmConfig
from health import RunsLikeACharmHealth
from literals import (
    CHARM_KEY,
    GROUP,
    PEER,
    USER,
    Status,
    Substrate,
    CloudInitScript,
)
from managers.config import RunsLikeACharmConfigManager
from workload import RunsLikeACharmWorkload

logger = logging.getLogger(__name__)


class RunsLikeACharm(TypedCharmBase[CharmConfig]):
    """Charmed Operator that runs anything™."""

    config_type = CharmConfig

    def __init__(self, *args):
        super().__init__(*args)
        self.name = CHARM_KEY
        self.substrate: Substrate = "vm"
        self.workload = RunsLikeACharmWorkload()
        self.state = ClusterState(self, substrate=self.substrate)
        self.health = RunsLikeACharmHealth(self)

        # HANDLERS

        #self.run_command_action_events = RunCommandActionEvents(self)

        # MANAGERS

        self.config_manager = RunsLikeACharmConfigManager(
            self.state, self.workload, self.config
        )

        # LIB HANDLERS

        self.restart = RollingOpsManager(self, relation="restart", callback=self._restart)

        self.framework.observe(getattr(self.on, "install"), self._on_install)
        self.framework.observe(getattr(self.on, "start"), self._on_start)
        self.framework.observe(getattr(self.on, "config_changed"), self._on_config_changed)
        self.framework.observe(getattr(self.on, "update_status"), self._on_update_status)
        self.framework.observe(getattr(self.on, "remove"), self._on_remove)

        self.framework.observe(self.on[PEER].relation_changed, self._on_config_changed)

    def _on_install(self, _) -> None:
        """Handler for `install` event."""
        if self.workload.write(self.config_manager.cloud_init_yaml, self.config_manager.cloud_init_path):
            self.config_manager.set_environment()
        else:
            self._set_status(Status.CLOUD_INIT_FAIL)

    def _on_start(self, event: EventBase) -> None:
        """Handler for `start` event."""
        self._set_status(self.state.ready_to_start)
        if not isinstance(self.unit.status, ActiveStatus):
            event.defer()
            return

        # run cloud-init for the user defined module
        self.workload.start()
        logger.info("CloudInit script executed")

        # check for connection
        self._on_update_status(event)

        # only log once on successful 'on-start' run
        if isinstance(self.unit.status, ActiveStatus):
            logger.info(f'Node {self.unit.name.split("/")[1]} operational')

    def _on_config_changed(self, event: EventBase) -> None:
        """Generic handler for most `config_changed` events across relations."""
        # only overwrite cloud-init script if we're healthy
        if not self.healthy:
            event.defer()
            return

        # NOTE todo: check this bit
        # Load current properties set in the charm workload
        cloud_init_file = self.workload.read(self.config_manager.cloud_init_path)
        cloud_init_file_changed = set(cloud_init_file) ^ set(self.config_manager.cloud_init_yaml)

        if not cloud_init_file:
            # Event fired before charm has properly started
            event.defer()
            return
        # /todo

        # update environment
        self.config_manager.set_environment()

        if cloud_init_file_changed:
            logger.info(
                (
                    f'Node {self.unit.name.split("/")[1]} updating cloud-init yaml file'
                )
            )
            self.workload.write(self.config_manager.cloud_init_yaml, self.config_manager.cloud_init_path)

    def _on_update_status(self, event: EventBase) -> None:
        """Handler for `update-status` events."""
        if not self.healthy:
            return

        # If cloud-init script has changed, the node will restart.
        self._on_config_changed(event)

        self._set_status(Status.ACTIVE)

    def _on_remove(self, _) -> None:
        """Handler for stop."""
        return

    def _restart(self, event: EventBase) -> None:
        """Handler for `rolling_ops` restart events."""
        # only attempt restart if service is already active
        if not self.healthy:
            event.defer()
            return

        # FIXME
        time.sleep(10.0)
        self.workload.restart()

    def _disable_enable_restart(self, event: RunWithLock) -> None:
        """Handler for `rolling_ops` disable_enable restart events."""
        if not self.healthy:
            logger.warning(f"Node {self.unit.name.split('/')[1]} is not ready restart")
            event.defer()
            return

        # treated the same as _restart
        time.sleep(10.0)
        self.workload.restart()

    @property
    def healthy(self) -> bool:
        """Checks and updates various charm lifecycle states.

        Is slow to fail due to retries, to be used sparingly.

        Returns:
            True if service is alive and active. Otherwise False
        """
        self._set_status(self.state.ready_to_start)
        if not isinstance(self.unit.status, ActiveStatus):
            return False

        return True

    def _set_status(self, key: Status) -> None:
        """Sets charm status."""
        status: StatusBase = key.value.status
        log_level: DebugLevel = key.value.log_level

        getattr(logger, log_level.lower())(status.message)
        self.unit.status = status


if __name__ == "__main__":
    main(RunsLikeACharm)
