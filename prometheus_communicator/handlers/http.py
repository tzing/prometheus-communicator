from __future__ import annotations

import enum
import logging
import typing

import httpx
import jinja2
from pydantic import Field, InstanceOf, field_validator

from prometheus_communicator.http import arequest
from prometheus_communicator.model import Handler

if typing.TYPE_CHECKING:
    from prometheus_communicator.model import PrometheusAlertWebhook

logger = logging.getLogger(__name__)


def _default_headers():
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


class HttpMethod(enum.StrEnum):
    Get = "GET"
    Post = "POST"
    Put = "PUT"
    Patch = "PATCH"
    Delete = "DELETE"


class HttpHandler(Handler):
    """
    Simple handler that forwards alerts to an HTTP endpoint.
    """

    url: InstanceOf[httpx.URL]
    """Endpoint to send the alert to."""
    method: HttpMethod = HttpMethod.Post
    """HTTP method to use."""
    headers: dict[str, str] = Field(default_factory=_default_headers)
    """Headers to send with the request. Defaults to JSON content type."""
    template: InstanceOf[jinja2.Template]
    """Jinja template to use for the request body."""
    timeout: float = 10.0
    """Timeout for the request."""
    max_attempt_number: int = 3
    """Maximum number of attempts to send the alert."""
    wait_multiplier: float = 2.0
    """Multiplier for the wait time between attempts."""

    async def handle(self, payload: PrometheusAlertWebhook) -> None:
        content = self.template.render(payload.model_dump())
        response = await arequest(
            method=self.method,
            url=self.url,
            content=content,
            timeout=self.timeout,
            max_attempt_number=self.max_attempt_number,
            wait_multiplier=self.wait_multiplier,
        )
        if not response.is_success:
            logger.error(
                "Failed to send alert to %s: %s %s",
                self.url,
                response.status_code,
                response.text,
            )

    @field_validator("url", mode="before")
    @classmethod
    def _cast_url(cls, value: str) -> httpx.URL:
        return httpx.URL(value)

    @field_validator("template", mode="before")
    @classmethod
    def _cast_template(cls, value: str) -> jinja2.Template:
        return jinja2.Template(value)
