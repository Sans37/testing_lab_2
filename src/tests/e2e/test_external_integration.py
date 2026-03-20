import os
import pytest
from httpx import AsyncClient, ASGITransport

from src.api.main import app


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_external_integration_with_mock():
    if os.getenv("EXTERNAL_SERVICE_MODE", "mock").lower() != "mock":
        pytest.skip("Mock mode disabled")

    os.environ.setdefault("EXTERNAL_POSTS_BASE_URL", "http://mock-external:8081")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v2/integrations/posts/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert data["title"].startswith("Mock post")


@pytest.mark.e2e
@pytest.mark.external
@pytest.mark.asyncio
async def test_external_integration_with_real_service():
    if os.getenv("RUN_EXTERNAL_SERVICE_TESTS", "false").lower() != "true":
        pytest.skip("External service tests disabled")

    os.environ["EXTERNAL_POSTS_BASE_URL"] = "https://jsonplaceholder.typicode.com"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v2/integrations/posts/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
