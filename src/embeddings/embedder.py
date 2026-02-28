import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple


class RequirementsEmbedder:
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        ## Transform text into vector
        return self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
