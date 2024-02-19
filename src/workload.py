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
from literals import PATHS, CMD_TIMEOUT
from core.workload import WorkloadBase

logger = logging.getLogger(__name__)


class RunsLikeACharmWorkload(WorkloadBase):
    """Wrapper for performing common operations specific to the 
        RunsLikeACharm user-defined script.
    """

    @override
    def start(self) -> None:
        """Runs the setup script"""
        the_script = PATHS["INSTALL_SCRIPT"]
        try:
            self.exec(f"/bin/sh {the_script}")
        except Exception as e:
            logger.error(f"running setup script failed - stdout={e.stdout}, stderr={e.stderr}")
            raise e

    @override
    def stop(self) -> None:
        return

    @override
    def restart(self) -> None:
        """Reboots the node"""
        self.exec("reboot")

    @override
    def read(self, path: str) -> list[str]:
        if not os.path.exists(path):
            return []
        else:
            with open(path) as f:
                content = f.read().split("\n")

        return content

    @override
    def write(self, content: str, path: str, mode: str = "w") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode) as f:
            f.write(content)

        self.exec(f"chmod +x {path}")

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
                timeout=CMD_TIMEOUT
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
