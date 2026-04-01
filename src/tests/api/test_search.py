import pytest
from httpx import AsyncClient


# Happy path test
@pytest.mark.anyio
async def test_search_endpoint(async_client: AsyncClient):
    response = await async_client.post("/analyze", json={"query": "test", "top_k": 1})
    data = response.json()

    assert len(data) == 3
    assert response.status_code == 200


# Happy response structure test
@pytest.mark.anyio
async def test_search_response_structure(async_client):
    response = await async_client.post("/analyze", json={"query": "test", "top_k": 2})

    response = response.json()
    detailed_results = response["results"][0]
    compliance = response["compliance_message"]

    assert "llm_explanation" in response
    assert "id" in detailed_results
    assert "similarity" in detailed_results
    assert "text" in detailed_results
    assert "ai_notice" in compliance
    assert "data_use_summary" in compliance
    assert "version" in compliance


# Missing requirement test
@pytest.mark.anyio
async def test_search_missing_query(async_client):
    response = await async_client.post("/analyze", json={"top_k": 2})

    assert response.status_code == 422


# top_k logic test
@pytest.mark.anyio
async def test_search_invalid_topk(async_client):
    response = await async_client.post(
        "/analyze", json={"query": "test", "top_k": "invalid"}
    )

    assert response.status_code == 422
