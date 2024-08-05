from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from prometheus_communicator.models import Handler


def create_handler(type: str, config: dict) -> Handler:
    """
    Create a handler from the config.
    """
    if type == "http":
        from prometheus_communicator.handlers.http import HttpHandler

        return HttpHandler.model_validate(config)

    raise NotImplementedError(f"Handler {type} is not implemented")
