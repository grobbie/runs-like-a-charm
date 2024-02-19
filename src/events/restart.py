#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Event handlers for password-related Juju Actions."""
import logging
from typing import TYPE_CHECKING

from ops.charm import ActionEvent
from ops.framework import Object

if TYPE_CHECKING:
    from charm import RunsLikeACharm

logger = logging.getLogger(__name__)


class RollingRestartActionEvents(Object):
    """Event handlers for password-related Juju Actions."""

    def __init__(self, charm):
        super().__init__(charm, "restart")
        self.charm: "RunsLikeACharm" = charm

        self.framework.observe(
            getattr(self.charm.on, "rolling_restart_action"), self._rolling_restart_action
        )

    def _rolling_restart_action(self, event: ActionEvent) -> None:
        """Handler for rolling restart action.

        Trigger a rolling restart of the node group
        """
        if not self.model.unit.is_leader():
            msg = "Rolling restart must be called on leader unit"
            logger.error(msg)
            event.fail(msg)
            return

        if not self.charm.healthy:
            msg = "Unit is not healthy"
            logger.error(msg)
            event.fail(msg)
            return

        try:
            self.charm.on[self.charm.restart_manager.name].acquire_lock.emit()
        except Exception as e:
            logger.error(str(e))
            event.fail(f"unable to initiate rolling restart")
            return
