#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Collection of state objects for the RunsLikeACharm relations, apps and units."""

import logging
from typing import MutableMapping

from kazoo.exceptions import AuthFailedError, NoNodeError
from ops.model import Application, Relation, Unit
from tenacity import retry, retry_if_not_result, stop_after_attempt, wait_fixed

from literals import Substrate

logger = logging.getLogger(__name__)


class StateBase:
    """Base state object."""

    def __init__(
        self, relation: Relation | None, component: Unit | Application, substrate: Substrate
    ):
        self.relation = relation
        self.component = component
        self.substrate = substrate

    @property
    def relation_data(self) -> MutableMapping[str, str]:
        """The raw relation data."""
        if not self.relation:
            return {}

        return self.relation.data[self.component]

    def update(self, items: dict[str, str]) -> None:
        """Writes to relation_data."""
        if not self.relation:
            return

        self.relation_data.update(items)


class RunsLikeACharmCluster(StateBase):
    """State collection metadata for the peer relation."""

    def __init__(self, relation: Relation | None, component: Application, substrate: Substrate):
        super().__init__(relation, component, substrate)
        self.app = component


class RunsLikeACharm(StateBase):
    """State collection metadata for a charm unit."""

    def __init__(self, relation: Relation | None, component: Unit, substrate: Substrate):
        super().__init__(relation, component, substrate)
        self.unit = component

    @property
    def unit_id(self) -> int:
        """The id of the unit from the unit name.

        e.g kafka/2 --> 2
        """
        return int(self.component.name.split("/")[1])

    @property
    def host(self) -> str:
        """Return the hostname of a unit."""
        host = ""
        if self.substrate == "vm":
            for key in ["hostname", "ip", "private-address"]:
                if host := self.relation_data.get(key, ""):
                    break
        if self.substrate == "k8s":
            host = f"{self.component.name.split('/')[0]}-{self.unit_id}.{self.component.name.split('/')[0]}-endpoints"

        return host
