from __future__ import annotations

import logging
import os
import typing
from typing import Any

import yaml
from pydantic import BaseModel, Field

from prometheus_communicator.handlers import create_handler

if typing.TYPE_CHECKING:
    from prometheus_communicator.models import Handler


logger = logging.getLogger(__name__)

handlers: dict[str, Handler] = {}
"""
Dictionary of handlers.

The key is the name of the receiver and the value is the handler.
"""


class ReceiverConfig(BaseModel):
    """
    Receiver configuration.
    """

    name: str
    """Unique name of the receiver. This is used in the webhook URL."""
    handler: str
    """Handler type to use for this receiver."""
    params: dict[str, Any] = Field(default_factory=dict)
    """Parameters to pass to the handler."""


class Config(BaseModel):
    """
    Layout of the config file.
    """

    receivers: list[ReceiverConfig] = Field(default_factory=list)


def load_config() -> Config:
    path = os.getenv("PROMETHEUS_COMMUNICATOR_CONFIG_PATH", "./config.yaml")
    logger.debug(f"Loading config from {path}")

    if not os.path.isfile(path):
        return Config()

    with open(path, "r") as file:
        content = yaml.safe_load(file)

    return Config.model_validate(content)


def initialize() -> None:
    """
    Initialize the handlers from the config file.
    """
    config = load_config()
    if not config.receivers:
        logger.warning("No receivers found in config file")

    for receiver in config.receivers:
        logger.debug(
            "Creating handler '%s' with type '%s'", receiver.name, receiver.handler
        )
        handler = create_handler(receiver.handler, receiver.params)
        handlers[receiver.name] = handler

    logger.info("Initialized %d handlers", len(handlers))
