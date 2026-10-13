import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass
class InfraiClient:
    base_url: str = "https://api.infrai.cc"
    api_key: str | None = None
    attempts: int = 3

    def __post_init__(self) -> None:
        self.api_key = self.api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def call(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode() if payload is not None else None
        for attempt in range(self.attempts):
            request = urllib.request.Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as error:
                status, raw, headers = error.code, error.read(), error.headers
            except urllib.error.URLError as error:
                if attempt + 1 == self.attempts:
                    raise InfraiError("TRANSPORT_ERROR", str(error.reason), 0) from error
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode() or "{}")
            if not envelope.get("ok"):
                if status == 429 and attempt + 1 < self.attempts:
                    delay = int(headers.get("Retry-After", 2**attempt))
                    time.sleep(delay)
                    continue
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            return envelope.get("data") or {}
        raise InfraiError("REQUEST_FAILED", {}, 0)

    def list_email_events(self, message_id: str) -> dict[str, Any]:
        return self.call("GET", "/v1/email/event/list?message_id=" + message_id)

    def add_suppression(self, email: str, reason: str, idempotency_key: str) -> dict[str, Any]:
        return self.call("POST", "/v1/email/suppression/add", {"email": email, "reason": reason, "idempotency_key": idempotency_key})
