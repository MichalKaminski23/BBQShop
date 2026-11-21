"""Testy endpointu modułu Path Traversal."""

from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from pytest import MonkeyPatch

from bbq_core.module import Variant
from bbq_path_traversal import router


@pytest.fixture
def file_tree(tmp_path: Path, monkeypatch: MonkeyPatch) -> tuple[Path, Path]:
    base_dir = tmp_path / "public"
    base_dir.mkdir()
    (base_dir / "grill.txt").write_text("instrukcja grilla", encoding="utf-8")
    secret = tmp_path / "secret.txt"
    secret.write_text("sekret serwera", encoding="utf-8")
    monkeypatch.setattr(router, "BASE_DIR", base_dir)
    return base_dir, secret


@pytest.mark.parametrize("variant", [Variant.VULNERABLE, Variant.SECURE])
async def test_endpoint_reads_file_inside_base_directory(
    file_tree: tuple[Path, Path],
    variant: Variant,
) -> None:
    app = FastAPI()
    app.include_router(router.build_router(variant), prefix="/api")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/files", params={"path": "grill.txt"})

    assert response.status_code == 200
    assert response.json() == {
        "filename": "grill.txt",
        "content": "instrukcja grilla",
    }


async def test_vulnerable_endpoint_reads_outside_base_directory(
    file_tree: tuple[Path, Path],
) -> None:
    app = FastAPI()
    app.include_router(router.build_router(Variant.VULNERABLE), prefix="/api")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/files", params={"path": "../secret.txt"})

    assert response.status_code == 200
    assert response.json() == {
        "filename": "../secret.txt",
        "content": "sekret serwera",
    }


async def test_secure_endpoint_rejects_outside_base_directory(
    file_tree: tuple[Path, Path],
) -> None:
    app = FastAPI()
    app.include_router(router.build_router(Variant.SECURE), prefix="/api")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/files", params={"path": "../secret.txt"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Niedozwolona ścieżka pliku"


async def test_endpoint_returns_404_for_missing_file(
    file_tree: tuple[Path, Path],
) -> None:
    app = FastAPI()
    app.include_router(router.build_router(Variant.SECURE), prefix="/api")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/files", params={"path": "missing.txt"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Plik nie istnieje"


async def test_endpoint_returns_svg_as_file_response(
    file_tree: tuple[Path, Path],
) -> None:
    base_dir, _ = file_tree
    (base_dir / "grill.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg"></svg>',
        encoding="utf-8",
    )
    app = FastAPI()
    app.include_router(router.build_router(Variant.SECURE), prefix="/api")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/files", params={"path": "grill.svg"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
