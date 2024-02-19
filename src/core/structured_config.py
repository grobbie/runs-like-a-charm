#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Structured configuration for the RunsLikeACharm charm."""
import logging
import re
from enum import Enum

from charms.data_platform_libs.v0.data_models import BaseConfigModel
from pydantic import validator
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


class LogMessageTimestampType(str, Enum):
    """Enum for the `log_message_timestamp_type` field."""

    CREATE_TIME = "CreateTime"
    LOG_APPEND_TIME = "LogAppendTime"


class LogCleanupPolicy(str, Enum):
    """Enum for the `log_cleanup_policy` field."""

    COMPACT = "compact"
    DELETE = "delete"


class CompressionType(str, Enum):
    """Enum for the `compression_type` field."""

    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"
    ZSTD = "zstd"
    UNCOMPRESSED = "uncompressed"
    PRODUCER = "producer"


class LogLevel(str, Enum):
    """Enum for the `log_level` field."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


class CharmConfig(BaseConfigModel):
    """Manager for the structured configuration."""

    environment_variables: Optional[str] = None
    setup_script: Optional[str] = None

    @validator("*", pre=True)
    @classmethod
    def blank_string(cls, value):
        """Check for empty strings."""
        if value == "":
            return None
        return value

    @validator("environment_variables")
    @classmethod
    def environment_variables_validator(cls, value: str) -> str | None:
        """Check validity of `environment_variables` field."""
        if value is None:
            return ""

        pat = re.compile(r"(?<pair>(?<key>.+?)(?:=)(?<value>[^=]+)(?:,|$))")
        matches = re.findall(pat, value)
        for match in matches:
            try:
                re.compile(match)
            except re.error:
                raise ValueError("Invalid environment variable provided")
        return value

    @validator("setup_script")
    @classmethod
    def setup_script_validator(cls, value: str) -> str | None:
        """Check validity of `setup-script` field."""
        if value is None:
            return ""

        # no validation, for now
        return value
