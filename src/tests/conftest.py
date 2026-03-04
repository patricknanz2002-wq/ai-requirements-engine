from typing import Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from api.main import app


class FakeEmbedder:
    def encode(self, texts):
        # Returns dummy vectors
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeStore:
    def search(self, query_vector, top_k):
        # Returns two fake results
        return [("1", 0.9), ("2", 0.8)][:top_k]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
def mock_app_state():
    from api.main import app

    app.state.embedder = FakeEmbedder()
    app.state.store = FakeStore()
    app.state.doc_lookup = {
        "1": "Requirement 1",
        "2": "Requirement 2",
    }

    yield


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
