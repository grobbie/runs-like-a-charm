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

DebugLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
Substrate = Literal["vm", "k8s"]
CloudInitScript = "cloud-init-yaml"
DatabagScope = Literal["unit", "app"]

PATHS = {
    "CLOUDCFG": "/etc/cloud/cloud.cfg.d/zz99-runs-like-a-charm.cfg",
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
    CLOUD_INIT_FAIL = StatusLevel(
        BlockedStatus("cloud-init configuration cannot be set - check logs"),
        "ERROR",
    )
