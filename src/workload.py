#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""CloudInit class and methods."""

import logging
import os
import subprocess

from tenacity import retry
from tenacity.retry import retry_if_not_result
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed
from typing_extensions import override

from core.workload import WorkloadBase

logger = logging.getLogger(__name__)


class RunsLikeACharmWorkload(WorkloadBase):
    """Wrapper for performing common operations specific to the """
    """RunsLikeACharm user-defined CloudInit script."""

    @override
    def start(self) -> None:
        """Force runs cloud-init"""
        try:
            self.exec("/usr/bin/cloud-init modules")
        except Exception as e:
            logger.error(f"running cloud-init failed - stdout={e.stdout}, stderr={e.stderr}")
            raise e

    @override
    def stop(self) -> None:
        return

    @override
    def restart(self) -> None:
        """Same as start - force runs cloud-init"""
        try:
            self.exec("/usr/bin/cloud-init modules")
        except Exception as e:
            logger.error(f"running cloud-init failed - stdout={e.stdout}, stderr={e.stderr}")
            raise e

    @override
    def read(self, path: str) -> list[str]:
        if not os.path.exists(path):
            return []
        else:
            with open(path) as f:
                content = f.read().split("\n")

        return content

    @override
    def write(self, content: str, path: str, mode: str = "w") -> bool:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode) as f:
            f.write(content)

        # self.exec(f"chown -R {USER}:{GROUP} {path}")
        return True

    @override
    def exec(
        self, command: str, env: dict[str, str] | None = None, working_dir: str | None = None
    ) -> str:
        try:
            output = subprocess.check_output(
                command,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=True,
                cwd=working_dir,
            )
            logger.debug(f"{output=}")
            return output
        except subprocess.CalledProcessError as e:
            logger.debug(f"cmd failed - cmd={e.cmd}, stdout={e.stdout}, stderr={e.stderr}")
            raise e

    @retry(
        wait=wait_fixed(1),
        stop=stop_after_attempt(5),
        retry_error_callback=lambda state: state.outcome.result(),  # type: ignore
        retry=retry_if_not_result(lambda result: True if result else False),
    )
    @override
    def active(self) -> bool:
        return True

    @override
    def run_bin_command(self, bin_keyword: str, bin_args: list[str], opts: list[str] = []) -> str:
        return True
