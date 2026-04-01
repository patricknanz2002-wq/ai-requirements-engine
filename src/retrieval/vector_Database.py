from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import numpy as np


class DatabaseVectorStore:
    def __init__(self, collection_name: str):
        self.client = self._connect_with_retry()
        self.collection_name = collection_name


    # Waits for qdrant service.
    def _connect_with_retry(self):
        import time

        for i in range(30):
            try:
                client = QdrantClient(host="qdrant", port=6333)
                client.get_collections()  # Health check
                print("Connected to Qdrant")
                return client
            except Exception:
                print(f"Waiting for Qdrant... ({i+1}/30)")
                time.sleep(2)

        raise Exception("Could not connect to Qdrant after retries")


    # Check if the target collection already exists in Qdrant
    # Used to avoid recreating collections during startup
    def collection_exists(self) -> bool:
        collections = self.client.get_collections().collections
        names = [c.name for c in collections]
        return self.collection_name in names


    # Create collection if it does not exist yet
    # Defines vector size and similarity metric (COSINE for semantic search)
    def create_collection(self) -> None:
        if not self.collection_exists():
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )
            print(f"Collection '{self.collection_name}' created!")
        else:
            print(f"Collection '{self.collection_name}' exists.")


    # Development helper: completely removes the collection
    # Not used in production workflows
    def delete_collection(self) -> None:
        self.client.delete_collection(self.collection_name)
        print(f"Collection '{self.collection_name}' deleted!")


    # Store embeddings in Qdrant
    # Each vector is linked to its original ID and text via 
    def add(self, ids:list[str], texts:list[str], vectors: np.ndarray) -> None:
        
        points = []

        for i in range(len(ids)):
            point = {
                # Use hashed ID to convert string IDs into numeric format required by Qdrant
                "id": abs(hash(ids[i])),
                "vector": vectors[i].tolist(),
                "payload": {
                    "original_id": ids[i],
                    "text": texts[i]
                    }
            }
            points.append(point)

        # Upsert ensures existing entries are updated instead of duplicated
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )


    # Perform semantic similarity search using query embedding
    # Returns top_k most similar entries with their scores
    def search(self, query_vector : np.ndarray, top_k: int) -> list[tuple[str, str, float]]:

        results = self.client.query_points(
        collection_name=self.collection_name,
        query=query_vector,
        limit=top_k
        )
        
        return [
        (
            p.payload["original_id"],
            p.payload["text"],
            p.score
        )
        for p in results.points
        ]


    # Retrieve all stored requirement IDs from the collection
    # Uses pagination (scroll) to handle large datasets
    def get_req_ids_of_collection(self) -> set[str]:
        req_ids = []
        offset = None

        while True:
            points, offset = self.client.scroll(
                collection_name=self.collection_name,
                with_payload=True,
                limit=100,
                offset=offset
            )

            req_ids.extend([p.payload["original_id"] for p in points])

            if offset is None:
                break

        return set(req_ids)