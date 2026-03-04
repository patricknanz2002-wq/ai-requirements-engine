import numpy as np
import pytest

from retrieval.vector_Store import InMemoryVectorStore


def test_vector_store_add_and_search_returns_correct_id():
    store = InMemoryVectorStore()
    ids = ["1", "2"]
    vectors = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
        ]
    )
    store.add(ids, vectors)
    results = store.search(np.array([1.0, 0.0]), top_k=1)

    assert len(results) == 1
    assert results[0][0] == "1"


def test_vector_store_respects_top_k():
    store = InMemoryVectorStore()
    ids = ["1", "2", "3"]
    vectors = np.array(
        [
            [1.0, 0.0],
            [0.9, 0.1],
            [0.0, 1.0],
        ]
    )
    store.add(ids, vectors)
    results = store.search(np.array([1.0, 0.0]), top_k=2)

    assert len(results) == 2


def test_vector_store_topk_exceeds_dataset_size():
    store = InMemoryVectorStore()
    store.add(["1"], np.array([[1.0, 0.0]]))
    results = store.search(np.array([1.0, 0.0]), top_k=10)

    assert len(results) == 1


def test_vector_store_raises_on_empty_store():
    store = InMemoryVectorStore()
    with pytest.raises(RuntimeError):
        store.search(np.array([1.0, 0.0]), top_k=5)


def test_vector_store_add_mismatched_lengths_raises_error():
    store = InMemoryVectorStore()
    ids = ["1", "2"]
    vectors = np.array([[1.0, 0.0]])  # mismatch
    with pytest.raises(Exception):
        store.add(ids, vectors)
