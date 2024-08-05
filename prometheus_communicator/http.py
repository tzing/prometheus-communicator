"""
Helper functions for making HTTP requests.
"""

from __future__ import annotations

import typing

import httpx
import prometheus_client
import tenacity

if typing.TYPE_CHECKING:
    from typing import Any

counter_http_requests = prometheus_client.Counter(
    "http_requests_total",
    "Total number of HTTP requests made",
    ["method", "host", "status_code"],
)


async def arequest(
    method: str,
    url: httpx.URL | str,
    *,
    headers: dict[str, Any] | None = None,
    content: str | bytes | None = None,
    json: dict[str, Any] | None = None,
    timeout: float = 60.0,
    max_attempt_number: int = 3,
    wait_multiplier: float = 2.0,
) -> httpx.Response:
    """
    Make an async HTTP request.
    """

    async def _request():
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method,
                url,
                content=content,
                headers=headers,
                json=json,
                timeout=timeout,
            )

        counter_http_requests.labels(
            method=method,
            host=resp.url.host,
            status_code=resp.status_code,
        ).inc()

        resp.raise_for_status()
        return resp

    async for attempt in tenacity.AsyncRetrying(
        stop=tenacity.stop_after_attempt(max_attempt_number),
        wait=tenacity.wait_exponential(multiplier=wait_multiplier),
        retry=tenacity.retry_if_exception_type(httpx.HTTPError),
    ):
        with attempt:
            return await _request()


async def apost(
    url: httpx.URL | str,
    *,
    headers: dict[str, Any] | None = None,
    content: str | bytes | None = None,
    json: dict[str, Any] | None = None,
    timeout: float = 60.0,
    max_attempt_number: int = 3,
    wait_multiplier: int = 5,
) -> httpx.Response:
    return await arequest(
        "POST",
        url=url,
        content=content,
        headers=headers,
        json=json,
        max_attempt_number=max_attempt_number,
        timeout=timeout,
        wait_multiplier=wait_multiplier,
    )
