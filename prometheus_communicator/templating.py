from __future__ import annotations

import jinja2
from pydantic import AfterValidator

from prometheus_communicator.model import PrometheusAlert, PrometheusAlertWebhook


def validate_template(template: jinja2.Template) -> jinja2.Template:
    """
    Validates the template. Raises an exception if the template is invalid.
    """
    # case: minimal payload
    payload = PrometheusAlertWebhook(
        version="4",
        groupKey="",
        status="firing",
        receiver="",
        groupLabels={},
        commonLabels={},
        commonAnnotations={},
        externalURL="https://example.com/",
        alerts=[],
    )

    try:
        template.render(payload.model_dump())
    except jinja2.exceptions.UndefinedError as e:
        raise ValueError(f"Invalid template: {e}")

    # case: with alerts
    payload = PrometheusAlertWebhook(
        version="4",
        groupKey="{}",
        status="firing",
        receiver="test",
        groupLabels={
            "alertname": "test",
        },
        commonLabels={
            "alertname": "test",
            "job": "test",
            "severity": "critical",
        },
        commonAnnotations={
            "summary": "test",
        },
        externalURL="https://example.com/",
        alerts=[
            PrometheusAlert(
                status="firing",
                labels={
                    "alertname": "test",
                    "job": "test",
                    "severity": "critical",
                    "env": "production",
                    "instance": "node1.summit",
                    "notify_room": "test",
                    "type": "nodeexporter",
                },
                annotations={
                    "summary": "test",
                },
                startsAt="2021-01-01T00:00:00Z",
                endsAt="2021-01-01T00:00:00Z",
                generatorURL="https://example.com/",
                fingerprint="e4ad109767ee663f",
            )
        ],
    )

    try:
        template.render(payload.model_dump())
    except jinja2.exceptions.UndefinedError as e:
        raise ValueError(f"Invalid template: {e}")

    return template


ValidateTemplate = AfterValidator(validate_template)
