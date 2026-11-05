"""Live parity: the same request to the legacy and the target service.

Both URLs come from the environment. When either service does not answer,
every parity test is skipped: a parity test that did not run proves nothing.
"""

from __future__ import annotations

import os

import httpx
import pytest

LEGACY_URL = os.environ.get("LEGACY_URL", "http://127.0.0.1:8081")
TARGET_URL = os.environ.get("TARGET_URL", "http://127.0.0.1:8080")


def _up(url: str) -> bool:
    try:
        return httpx.get(f"{url}/health", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


@pytest.fixture(scope="session")
def both() -> tuple[httpx.Client, httpx.Client]:
    if not (_up(LEGACY_URL) and _up(TARGET_URL)):
        pytest.skip(f"parity needs both services: legacy {LEGACY_URL}, target {TARGET_URL}")
    with httpx.Client(base_url=LEGACY_URL) as legacy, httpx.Client(base_url=TARGET_URL) as target:
        yield legacy, target


def same(legacy: httpx.Response, target: httpx.Response) -> None:
    assert target.status_code == legacy.status_code, (legacy.status_code, legacy.text, target.status_code, target.text)
    assert target.json() == legacy.json()
