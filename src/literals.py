#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Collection of globals common to the RunsLikeACharm."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, StatusBase, WaitingStatus

CHARM_KEY = "runs-like-a-charm"
CONTAINER = "runslikeacharm"

PEER = "cluster"

SUBSTRATE = "vm"
USER = "runslikeacharm"
GROUP = "runslikeacharm"

CMD_TIMEOUT=180

DebugLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
Substrate = Literal["vm", "k8s"]
DatabagScope = Literal["unit", "app"]

PATHS = {
    "INSTALL_SCRIPT": "/opt/user-install-script",
    "ENVIRONMENT": "/etc/environment",
}

@dataclass
class StatusLevel:
    """Status object helper."""

    status: StatusBase
    log_level: DebugLevel

class Status(Enum):
    """Collection of possible statuses for the charm."""

    ACTIVE = StatusLevel(ActiveStatus(), "DEBUG")
    NO_PEER_RELATION = StatusLevel(MaintenanceStatus("no peer relation yet"), "DEBUG")
    ZK_NO_DATA = StatusLevel(WaitingStatus("zookeeper credentials not created yet"), "DEBUG")
    ADDED_STORAGE = StatusLevel(
        ActiveStatus("user filesystem added to node at /opt/data"),
        "DEBUG",
    )
    INIT_FAIL = StatusLevel(
        BlockedStatus("setup configuration cannot be set - check logs"),
        "ERROR",
    )
