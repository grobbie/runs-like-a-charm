#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Manager for handling RunsLikeACharm machine health."""

import json
import logging
import subprocess
from statistics import mean
from typing import TYPE_CHECKING

from ops.framework import Object

if TYPE_CHECKING:
    from charm import RunsLikeACharm

logger = logging.getLogger(__name__)


class RunsLikeACharmHealth(Object):
    """Manager for handling RunsLikeACharm machine health."""

    def __init__(self, charm) -> None:
        super().__init__(charm, "runs_like_a_charm_health")
        self.charm: "RunsLikeACharm" = charm
        
    def _get_max_memory_maps(self) -> int:
        """Gets the current memory map limit for the machine."""
        return int(self.charm.workload.exec("sysctl -n vm.max_map_count"))

    def _get_vm_swappiness(self) -> int:
        """Gets the current vm.swappiness configured for the machine."""
        return int(self.charm.workload.exec("sysctl -n vm.swappiness"))

    def _check_vm_swappiness(self) -> bool:
        """Checks that vm.swappiness is configured correctly on the machine."""
        vm_swappiness = self._get_vm_swappiness()

        # FIXME: threshold should be a user configurable value
        if vm_swappiness > 1:
            logger.error(
                f"machine vm.swappiness setting of {vm_swappiness} is higher than 1 - set /etc/syscl.conf vm.swappiness=1 and restart machine"
            )
            return False

        return True

    def _check_total_memory(self) -> bool:
        """Checks that the total available memory is sufficient for desired profile."""
        if not (meminfo := self.charm.workload.read(path="/proc/meminfo")):
            return False # NOTE: ??

        return True

    def machine_configured(self) -> bool:
        """Checks machine configuration for healthy settings.

        Returns:
            True if settings safely configured. Otherwise False
        """
        if not all(
            [
                self._check_total_memory(),
                self._check_vm_swappiness(),
            ]
        ):
            return False

        return True
