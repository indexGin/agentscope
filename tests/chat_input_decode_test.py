# -*- coding: utf-8 -*-
"""Unit tests for decoding reference-backed queued chat inputs."""
import json

from agentscope.app._chat_input_store import decode_input

_PAYLOAD: dict[str, str] = {
    "id": "queued-1",
    "input_ref": "ref-1",
    "session_id": "session-1",
}


def test_scalar_payloads_are_discarded() -> None:
    """A payload that decodes to a scalar is corrupt and is dropped."""
    for raw in (
        "null",
        "true",
        "42",
        "3.5",
        '"oops"',
    ):
        assert decode_input(_PAYLOAD, raw) is None, raw


def test_object_payload_is_preserved() -> None:
    """Regression: a JSON object is a valid input and is kept verbatim."""
    for obj in (
        {},
        {"role": "user", "content": "hello"},
    ):
        result = decode_input(_PAYLOAD, json.dumps(obj))
        assert result is not None
        assert result["input"] == obj


def test_message_list_payload_is_preserved() -> None:
    """Regression: a list of message dicts is a valid batched input."""
    batch = [
        {"role": "user", "content": "hello"},
        {"role": "user", "content": "world"},
    ]
    result = decode_input(_PAYLOAD, json.dumps(batch))
    assert result is not None
    assert result["input"] == batch


def test_missing_and_malformed_payloads_are_discarded() -> None:
    """Regression: absent or malformed JSON is still omitted."""
    assert decode_input(_PAYLOAD, None) is None
    assert decode_input(_PAYLOAD, "{") is None
