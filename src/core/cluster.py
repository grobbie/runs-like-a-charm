#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Objects representing the state of RunsLikeACharm."""

import os

from ops import Framework, Object, Relation

from core.models import RunsLikeACharm, RunsLikeACharmCluster
from literals import (
    PEER,
    Status,
    Substrate,
)


class ClusterState(Object):
    """Properties and relations of the charm."""

    def __init__(self, charm: Framework | Object, substrate: Substrate):
        super().__init__(parent=charm, key="charm_state")
        self.substrate: Substrate = substrate

    # --- RELATIONS ---

    @property
    def peer_relation(self) -> Relation | None:
        """The cluster peer relation."""
        return self.model.get_relation(PEER)

    # --- CORE COMPONENTS ---

    @property
    def node(self) -> RunsLikeACharm:
        """The server state of the current running Unit."""
        return RunsLikeACharm(
            relation=self.peer_relation, component=self.model.unit, substrate=self.substrate
        )

    @property
    def cluster(self) -> RunsLikeACharmCluster:
        """The cluster state of the current running App."""
        return RunsLikeACharmCluster(
            relation=self.peer_relation, component=self.model.app, substrate=self.substrate
        )

    @property
    def nodes(self) -> set[RunsLikeACharm]:
        """Grabs all nodes in the current peer relation, including the running unit node.

        Returns:
            Set of RunsLikeACharm in the current peer relation, including the running unit node.
        """
        if not self.peer_relation:
            return set()

        nodes = set()
        for unit in self.peer_relation.units:
            nodes.add(
                RunsLikeACharm(relation=self.peer_relation, component=unit, substrate=self.substrate)
            )
        nodes.add(self.node)

        return nodes

    # ---- GENERAL VALUES ----

    @property
    def unit_hosts(self) -> list[str]:
        """Return list of application unit hosts."""
        hosts = [node.host for node in self.nodes]
        return hosts

    @property
    def planned_units(self) -> int:
        """Return the planned units for the charm."""
        return self.model.app.planned_units()

    @property
    def ready_to_start(self) -> Status:
        """Currently not implemented

        Returns:
            NO_PEER_RELATION if clustered but not related
            ACTIVE in every other situation
        """
        if not self.peer_relation:
            return Status.NO_PEER_RELATION

        return Status.ACTIVE
