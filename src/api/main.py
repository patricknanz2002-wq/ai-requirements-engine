from pathlib import Path

from fastapi import FastAPI, Request
from pydantic import BaseModel

from embedding.embedder import RequirementsEmbedder
from lm_output.LLMService import LLMService
from pipeline.retrieval_pipeline import load_documents_recursive
from retrieval.vector_Store import InMemoryVectorStore

app = FastAPI()


class Query(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    id: str
    similarity: float
    text: str


class AnalyzeResponse(BaseModel):
    results: list[SearchResult]
    llm_explanation: str


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
    app.state.llm = LLMService()

    app.state.doc_lookup = {doc["id"]: doc["text"] for doc in documents}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: Request, payload: Query):

    query_vector = request.app.state.embedder.encode([payload.query])[0]
    top_search_results = request.app.state.store.search(query_vector, payload.top_k)

    response = []
    lmArray = []

    for req_id, score in top_search_results:
        text = request.app.state.doc_lookup.get(req_id, "[Text not found]")

        response.append(
            SearchResult(
                id=req_id,
                similarity=float(score),
                text=text,
            )
        )
        lmArray.append((req_id, text, score))

    answer = request.app.state.llm.output_answer(payload.query, lmArray)

    return {"results": response, "llm_explanation": answer}


@app.get("/health")
def health():

    if (
        not hasattr(app.state, "embedder")
        or not hasattr(app.state, "store")
        or not hasattr(app.state, "doc_lookup")
    ):
        return {"status": "not_ready"}
    else:
        return {"status": "ready"}
