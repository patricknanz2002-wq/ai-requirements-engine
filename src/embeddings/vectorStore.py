import numpy as np  


class InMemoryVectorStore:

    def __init__(self):
        self.ids = []
        self.vectors = None


    def add(self, ids: list[str], vectors: np.ndarray):
        # Load IDs and Vectors in RAM
        if len(ids) != len(vectors):
            raise ValueError("IDs and vectors must have same length.")
        
        # Vectors are already np objects. Therefore they are loaded directly into ram.
        if self.vectors is None:
            self.vectors = vectors
        else:
            self.vectors = np.vstack([self.vectors, vectors])

        self.ids.extend(ids)


    def search(self, query_vector, top_k):

        if(self.vectors is None):
            raise RuntimeError("Vector store is empty. Call add() first.")  

        # Vector Multiplication calculates similarity score
        ids = self.ids
        matrix = self.vectors
        similarities = matrix @ query_vector

        # argsort keeps connection between matrix and ids
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [(ids[i], similarities[i]) for i in top_indices]
            