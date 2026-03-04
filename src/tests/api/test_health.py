import pytest


# Health endpoint test
@pytest.mark.anyio
async def test_health_ready(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
