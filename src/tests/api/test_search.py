import pytest
from httpx import AsyncClient


# Happy path test
@pytest.mark.anyio
async def test_search_endpoint(async_client: AsyncClient):
    response = await async_client.post("/search", json={"query": "test", "top_k": 1})
    data = response.json()

    assert len(data) == 1
    assert response.status_code == 200


# Happy response structure test
@pytest.mark.anyio
async def test_search_response_structure(async_client):
    response = await async_client.post("/search", json={"query": "test", "top_k": 2})

    data = response.json()

    assert "id" in data[0]
    assert "similarity" in data[0]
    assert "text" in data[0]


# Missing requirement test
@pytest.mark.anyio
async def test_search_missing_query(async_client):
    response = await async_client.post("/search", json={"top_k": 2})

    assert response.status_code == 422


# top_k logic test
@pytest.mark.anyio
async def test_search_invalid_topk(async_client):
    response = await async_client.post(
        "/search", json={"query": "test", "top_k": "invalid"}
    )

    assert response.status_code == 422
