import numpy as np
from pathlib import Path

from embedding.embedder import RequirementsEmbedder


class RequirementEncoder:
    def __init__(self):
        self.embedder = RequirementsEmbedder()

    def encode(self, texts: list) -> np.ndarray:
        return self.embedder.encode(texts)