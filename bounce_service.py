from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiClient


@dataclass(frozen=True)
class BuildEvent:
    build_id: str
    commit: str


@dataclass(frozen=True)
class ReleaseOperation:
    release_id: str
    environment: str


@dataclass(frozen=True)
class DeveloperDiagnostic:
    address: str
    action: str
    message: str


def handle_bounce(event: dict[str, Any], client: InfraiClient) -> DeveloperDiagnostic:
    address = str(event["recipient"])
    if event.get("type") != "hard_bounce":
        return DeveloperDiagnostic(address, "ignore", "Transient delivery event; no suppression change.")
    idempotency_key = "bounce-" + str(event["message_id"])
    client.add_suppression(address, "hard_bounce", idempotency_key)
    return DeveloperDiagnostic(address, "suppress", "Hard bounce recorded in the suppression list.")
