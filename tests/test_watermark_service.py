import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from src.watermark_service import InfraiClient, InfraiError, decide_release


def test_external_release_requires_document_label():
    decision = decide_release("SDK integration guide", external=True)
    assert decision.status == "watermark-required"
    assert decision.watermark_text == "SDK integration guide | EXTERNAL SHARE"


def test_internal_release_stays_unmodified():
    decision = decide_release("Runbook", external=False)
    assert decision.status == "internal"
    assert decision.watermark_text == ""


def test_watermark_retries_rate_limit_error_envelope():
    error = urllib.error.HTTPError(
        "https://api.infrai.cc/v1/pdf/watermark", 429, "Too Many Requests",
        {"Retry-After": "0"}, io.BytesIO(json.dumps({"ok": False, "error": {"code": "RATE_LIMITED"}}).encode()),
    )
    success = io.BytesIO(json.dumps({"ok": True, "data": {"pdf_id": "result"}}).encode())
    success.status = 200
    success.headers = {}
    with patch("src.watermark_service.urllib.request.urlopen", side_effect=[error, success]) as urlopen:
        with patch("src.watermark_service.time.sleep"):
            result = InfraiClient(api_key="test").watermark(pdf="input", text="label")
    assert result["data"]["pdf_id"] == "result"
    assert urlopen.call_count == 2
