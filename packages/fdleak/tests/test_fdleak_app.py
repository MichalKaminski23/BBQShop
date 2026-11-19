"""Testy endpointów demonstracji deskryptorów."""

from __future__ import annotations

import socket
from types import SimpleNamespace

import httpx
import pytest
from fastapi import FastAPI
from pytest import MonkeyPatch

from bbq_core.module import Variant
from bbq_fdleak.router import build_router
from bbq_fdleak.secure import repository as secure_repository
from bbq_fdleak.vulnerable import repository as vulnerable_repository


class FakeResource:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> FakeResource:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def install_fake_resources(monkeypatch: MonkeyPatch) -> list[FakeResource]:
    resources: list[FakeResource] = []

    def create_resource(*args: object, **kwargs: object) -> FakeResource:
        del args, kwargs
        resource = FakeResource()
        resources.append(resource)
        return resource

    monkeypatch.setattr(vulnerable_repository, "open", create_resource, raising=False)
    monkeypatch.setattr(secure_repository, "open", create_resource, raising=False)
    fake_socket_module = SimpleNamespace(
        socket=create_resource,
        AF_INET=socket.AF_INET,
        SOCK_STREAM=socket.SOCK_STREAM,
    )
    monkeypatch.setattr(vulnerable_repository, "socket", fake_socket_module)
    monkeypatch.setattr(secure_repository, "socket", fake_socket_module)
    return resources


@pytest.mark.parametrize(
    ("variant", "expected_closed"),
    [(Variant.VULNERABLE, False), (Variant.SECURE, True)],
    ids=["vulnerable", "secure"],
)
@pytest.mark.parametrize("resource_path", ["file", "socket"])
async def test_resource_endpoint_matches_selected_variant(
    monkeypatch: MonkeyPatch, variant: Variant, expected_closed: bool, resource_path: str
) -> None:
    resources = install_fake_resources(monkeypatch)
    app = FastAPI()
    app.include_router(build_router(variant), prefix="/api")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/api/fdleak/{resource_path}", params={"count": 3})

    assert response.status_code == 200
    assert response.json() == {
        "resource_type": resource_path,
        "opened_count": 3,
        "closed_count": 3 if expected_closed else 0,
    }
    assert len(resources) == 3
    assert all(resource.closed is expected_closed for resource in resources)


@pytest.mark.parametrize("resource_path", ["file", "socket"])
async def test_resource_endpoint_rejects_count_above_limit(
    monkeypatch: MonkeyPatch, resource_path: str
) -> None:
    resources = install_fake_resources(monkeypatch)
    app = FastAPI()
    app.include_router(build_router(Variant.SECURE), prefix="/api")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/api/fdleak/{resource_path}", params={"count": 101})

    assert response.status_code == 422
    assert resources == []
