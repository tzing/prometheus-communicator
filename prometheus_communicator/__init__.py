from __future__ import annotations

from http import HTTPStatus
from typing import Annotated

import prometheus_fastapi_instrumentator
from fastapi import FastAPI, HTTPException, Path, Response

import prometheus_communicator.config
from prometheus_communicator.models import PrometheusAlertWebhook

prometheus_communicator.config.initialize()

app = FastAPI(
    title="Prometheus Communicator",
    summary="Forwards Prometheus alerts to the pre-configured destinations",
)

prometheus_fastapi_instrumentator.Instrumentator().instrument(app).expose(app)


@app.post(
    "/v1/webhook/{name}",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    responses={
        HTTPStatus.NOT_FOUND: {"description": "Unknown receiver"},
    },
)
async def receive_webhook(
    payload: PrometheusAlertWebhook,
    name: Annotated[str, Path(description="Receiver name")],
) -> None:
    """
    Receive Prometheus Alertmanager webhook and forward it to the pre-configured destination.
    """
    handler = prometheus_communicator.config.handlers.get(name)
    if not handler:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Unknown receiver '{name}'")

    await handler.handle(payload)
