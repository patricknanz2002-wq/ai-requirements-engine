import numpy as np

from embedding.embedder import RequirementsEmbedder


def test_embedder_returns_correct_number_of_vectors():
    embedder = RequirementsEmbedder()
    texts = ["hello", "world"]

    vectors = embedder.encode(texts)

    assert isinstance(vectors, np.ndarray)
    assert vectors.shape[0] == len(texts)


def test_embedder_vector_dimensions_consistent():
    embedder = RequirementsEmbedder()
    texts = ["a", "b"]

    vectors = embedder.encode(texts)

    assert isinstance(vectors, np.ndarray)

    dim = vectors.shape[1]

    for vec in vectors:
        assert len(vec) == dim


def test_embedder_vector_dimension_positive():
    embedder = RequirementsEmbedder()
    vectors = embedder.encode(["hello"])

    assert vectors.shape[1] > 0


def test_embedder_handles_empty_input():
    embedder = RequirementsEmbedder()
    vectors = embedder.encode([])

    assert isinstance(vectors, np.ndarray)
    assert vectors.shape[0] == 0
