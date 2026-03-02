from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from src.pipeline.run import load_documents_recursive
from src.embedding.embedder import RequirementsEmbedder
from src.retrieval.vector_Store import InMemoryVectorStore
from fastapi import Request

app = FastAPI()

class Query(BaseModel):
    query: str
    top_k: int = 5
    
class SearchResult(BaseModel):
    id: str
    similarity: float
    text: str
    
@app.on_event("startup")
def startup_event():
    
    base_path = Path(__file__).resolve().parent.parent.parent
    target_path = (base_path / "data/raw").resolve()

    documents = load_documents_recursive(target_path)

    ids = [doc["id"] for doc in documents]
    texts = [doc["text"] for doc in documents]

    app.state.embedder = RequirementsEmbedder()
    vectors = app.state.embedder.encode(texts)

    app.state.store = InMemoryVectorStore()
    app.state.store.add(ids, vectors)

    app.state.doc_lookup = {doc["id"]: doc["text"] for doc in documents}


@app.post("/search", response_model=list[SearchResult])
def search(request: Request, payload: Query):

    query_vector = request.app.state.embedder.encode([payload.query])[0]
    results = request.app.state.store.search(query_vector, payload.top_k)

    response = []

    for req_id, score in results:
        response.append(SearchResult(
        id=req_id,
        similarity=float(score),
        text=request.app.state.doc_lookup[req_id]
        ))

    return response
    

@app.get("/health")
def health():

    if (not hasattr(app.state, "embedder") or not hasattr(app.state, "store") or not hasattr(app.state, "doc_lookup")):
        return {"status": "not_ready"}
    else:
        return {"status": "ready"}