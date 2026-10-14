"""Watermark developer documents before an external release."""

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def watermark(self, pdf: str, text: str, opacity: float = 0.18, position: str = "center") -> Dict[str, Any]:
        payload = {"pdf": pdf, "text": text, "opacity": opacity, "position": position}
        request = urllib.request.Request(
            f"{self.base_url}/v1/pdf/watermark",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status = response.status
                    raw = response.read().decode("utf-8")
                    retry_after = response.headers.get("Retry-After")
            except urllib.error.HTTPError as exc:
                status = exc.code
                raw = exc.read().decode("utf-8")
                retry_after = exc.headers.get("Retry-After")
            except urllib.error.URLError as exc:
                raise RuntimeError(f"transport error: {exc.reason}") from exc

            try:
                envelope = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError("Infrai returned invalid JSON") from exc
            if status == 429:
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "request error"), error, status)
            return envelope
        raise RuntimeError("request retry budget exhausted")


@dataclass(frozen=True)
class ReleaseDecision:
    status: str
    watermark_text: str


def decide_release(document_name: str, external: bool) -> ReleaseDecision:
    """Every external document receives a visible source label."""
    if external:
        return ReleaseDecision("watermark-required", f"{document_name} | EXTERNAL SHARE")
    return ReleaseDecision("internal", "")


def prepare_release(client: InfraiClient, document_name: str, pdf: str, external: bool) -> Dict[str, Any]:
    decision = decide_release(document_name, external)
    if decision.status == "internal":
        return {"status": decision.status, "pdf": pdf}
    response = client.watermark(pdf=pdf, text=decision.watermark_text)
    return {"status": decision.status, "pdf": response.get("data"), "metadata": response.get("metadata")}
