from __future__ import annotations

import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class PrometheusAlert(BaseModel):
    """
    Alert received from Prometheus alertmanager webhook.
    """

    status: Literal["resolved", "firing"]
    labels: dict[str, Any]
    annotations: dict[str, Any]
    startsAt: datetime.datetime
    endsAt: datetime.datetime
    generatorURL: str
    fingerprint: str


class PrometheusAlertWebhook(BaseModel):
    """
    Payload received from Alertmanager webhook.
    """

    version: Literal["4"]
    groupKey: str
    truncatedAlerts: int | None = Field(default=None)
    status: Literal["resolved", "firing"]
    receiver: str
    groupLabels: dict
    commonLabels: dict
    commonAnnotations: dict
    externalURL: str
    alerts: list[PrometheusAlert]


class Handler(BaseModel):
    """
    Base handler.
    """

    async def handle(self, payload: PrometheusAlertWebhook) -> None:
        """
        Handle the alert.
        """
        raise NotImplementedError
