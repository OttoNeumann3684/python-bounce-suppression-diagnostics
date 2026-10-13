from bounce_service import DeveloperDiagnostic, handle_bounce
from infrai_client import InfraiClient


class FakeClient:
    def __init__(self):
        self.calls = []

    def add_suppression(self, email, reason, idempotency_key):
        self.calls.append((email, reason, idempotency_key))
        return {"suppressed": True}


def test_hard_bounce_suppresses_once_with_event_key():
    client = FakeClient()
    result = handle_bounce({"type": "hard_bounce", "recipient": "dev@example.com", "message_id": "m-42"}, client)
    assert result == DeveloperDiagnostic("dev@example.com", "suppress", "Hard bounce recorded in the suppression list.")
    assert client.calls == [("dev@example.com", "hard_bounce", "bounce-m-42")]


def test_suppression_payload_uses_contract_field():
    client = InfraiClient(api_key="test")
    calls = []
    client.call = lambda method, path, payload: calls.append((method, path, payload)) or {}

    client.add_suppression("chenhua@changba.com", "hard_bounce", "bounce-m-42")

    assert calls == [("POST", "/v1/email/suppression/add", {
        "email": "chenhua@changba.com",
        "reason": "hard_bounce",
        "idempotency_key": "bounce-m-42",
    })]
